"""
Model evaluation module.
Calculates performance metrics, confusion matrices with HR labels,
threshold trade-offs, and logs experiment runs.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
    classification_report
)

from src.database import save_experiment


def evaluate_test_performance(
    trained_pipelines: Dict[str, Any],
    X_test: pd.DataFrame,
    y_test: pd.Series,
    dataset_name: str = "SnackRush_Complete_Dataset.xlsx",
    dataset_fingerprint: str = "default"
) -> Dict[str, Any]:
    """
    Evaluate all models strictly on held-out test data.
    Returns comparison DataFrame, individual metric dictionaries, and confusion matrices.
    """
    comparison_records = []
    model_details = {}

    for name, pipe in trained_pipelines.items():
        y_pred = pipe.predict(X_test)
        y_prob = None
        if hasattr(pipe, "predict_proba"):
            y_prob = pipe.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        # ROC-AUC & PR-AUC
        roc = np.nan
        pr_auc = np.nan
        if y_prob is not None and len(np.unique(y_test)) > 1:
            try:
                roc = roc_auc_score(y_test, y_prob)
                pr_auc = average_precision_score(y_test, y_prob)
            except Exception:
                pass

        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
        elif cm.shape == (1, 1):
            if y_test.iloc[0] == 0:
                tn, fp, fn, tp = cm[0, 0], 0, 0, 0
            else:
                tn, fp, fn, tp = 0, 0, 0, cm[0, 0]
        else:
            tn, fp, fn, tp = 0, 0, 0, 0

        # HR-Specific Confusion Matrix Breakdown
        hr_cm = {
            "True_Negatives_Retained": int(tn),
            "False_Positives_Flagged_Wrongly": int(fp),
            "False_Negatives_Missed_Exits": int(fn),
            "True_Positives_Identified_Exits": int(tp),
            "Labels": {
                "TN": "Correctly identified employees who stayed",
                "FP": "Employees incorrectly flagged as likely to leave",
                "FN": "Exits missed by model (Costly false negatives)",
                "TP": "Correctly identified exits (Actionable true positives)"
            }
        }

        # Save to comparison list
        record = {
            "Model": name,
            "Accuracy": round(acc, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1_Score": round(f1, 4),
            "ROC_AUC": round(roc, 4) if not np.isnan(roc) else None,
            "PR_AUC": round(pr_auc, 4) if not np.isnan(pr_auc) else None,
            "True_Positives": int(tp),
            "False_Negatives": int(fn),
            "False_Positives": int(fp),
            "True_Negatives": int(tn)
        }
        comparison_records.append(record)

        # Store model details
        model_details[name] = {
            "metrics": record,
            "y_pred": y_pred,
            "y_prob": y_prob,
            "confusion_matrix": cm,
            "hr_confusion_matrix": hr_cm,
            "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        }

    comparison_df = pd.DataFrame(comparison_records).sort_values(by="F1_Score", ascending=False)

    # Identify best model based on F1-score & ROC-AUC
    # We exclude dummy baseline from candidate selection
    candidate_df = comparison_df[comparison_df["Model"] != "Dummy (Baseline)"]
    best_model_name = candidate_df.iloc[0]["Model"] if not candidate_df.empty else comparison_df.iloc[0]["Model"]

    # Log to SQLite
    for rec in comparison_records:
        save_experiment({
            "experiment_id": f"EXP_{dataset_fingerprint}_{rec['Model'].replace(' ', '_')}",
            "dataset_name": dataset_name,
            "dataset_fingerprint": dataset_fingerprint,
            "model_name": rec["Model"],
            "test_accuracy": rec["Accuracy"],
            "test_precision": rec["Precision"],
            "test_recall": rec["Recall"],
            "test_f1": rec["F1_Score"],
            "test_roc_auc": rec["ROC_AUC"],
            "test_pr_auc": rec["PR_AUC"],
            "is_selected": (rec["Model"] == best_model_name),
            "notes": "Automated evaluation run on held-out test data."
        })

    return {
        "comparison_df": comparison_df,
        "model_details": model_details,
        "best_model_name": best_model_name,
        "test_sample_count": len(y_test),
        "test_positive_count": int(y_test.sum()),
        "test_negative_count": int((y_test == 0).sum())
    }


def compute_threshold_tuning_table(
    y_test: pd.Series,
    y_prob: np.ndarray,
    cost_false_negative: float = 100000.0,  # Cost of unplanned attrition replacement (INR)
    cost_false_positive: float = 15000.0    # Cost of unnecessary retention intervention (INR)
) -> pd.DataFrame:
    """
    Evaluate precision, recall, and business cost across classification thresholds from 0.10 to 0.90.
    """
    thresholds = np.arange(0.10, 0.95, 0.05)
    records = []

    for t in thresholds:
        preds = (y_prob >= t).astype(int)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)
        cm = confusion_matrix(y_test, preds)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
        else:
            tn, fp, fn, tp = 0, 0, 0, 0

        total_cost = (fn * cost_false_negative) + (fp * cost_false_positive)

        records.append({
            "Threshold": round(float(t), 2),
            "Precision": round(float(prec), 3),
            "Recall": round(float(rec), 3),
            "F1_Score": round(float(f1), 3),
            "True_Positives": int(tp),
            "False_Negatives": int(fn),
            "False_Positives": int(fp),
            "Estimated_Total_Cost_INR": round(float(total_cost), 0)
        })

    return pd.DataFrame(records)
