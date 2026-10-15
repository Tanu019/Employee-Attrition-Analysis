"""
Model explainability module.
Computes global tree feature importance, permutation feature importance,
and SHAP value summaries and individual local contributions.
"""
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
import shap


def compute_tree_feature_importance(
    pipeline: Any,
    transformed_feature_names: List[str],
    top_n: int = 15
) -> pd.DataFrame:
    """
    Extract native tree feature importance from Random Forest or Decision Tree.
    """
    clf = pipeline.named_steps.get("classifier")
    if not hasattr(clf, "feature_importances_"):
        return pd.DataFrame()

    importances = clf.feature_importances_
    # Match length of names with importances
    min_len = min(len(transformed_feature_names), len(importances))
    df_imp = pd.DataFrame({
        "Feature": transformed_feature_names[:min_len],
        "Importance": importances[:min_len]
    }).sort_values(by="Importance", ascending=False).head(top_n)

    # Clean feature names for presentation
    df_imp["CleanFeature"] = df_imp["Feature"].apply(
        lambda f: f.replace("num__", "").replace("cat__", "").replace("_", " ").title()
    )
    return df_imp


def compute_permutation_importance_metrics(
    pipeline: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    top_n: int = 15,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Compute model-agnostic permutation feature importance on held-out test data.
    Measures drop in ROC-AUC when a feature is shuffled.
    """
    perm = permutation_importance(
        pipeline,
        X_test,
        y_test,
        scoring="roc_auc",
        n_repeats=5,
        random_state=random_state
    )

    df_perm = pd.DataFrame({
        "Feature": X_test.columns,
        "Mean_Importance": perm.importances_mean,
        "Std_Importance": perm.importances_std
    }).sort_values(by="Mean_Importance", ascending=False).head(top_n)

    df_perm["CleanFeature"] = df_perm["Feature"].apply(
        lambda f: f.replace("_", " ").title()
    )
    return df_perm


def compute_shap_explanations(
    pipeline: Any,
    X_sample: pd.DataFrame,
    max_samples: int = 100
) -> Tuple[Optional[np.ndarray], Optional[Any], List[str]]:
    """
    Compute SHAP values using TreeExplainer (for trees) or KernelExplainer / LinearExplainer.
    Returns: (shap_values, explainer, feature_names)
    """
    preprocessor = pipeline.named_steps["preprocessor"]
    clf = pipeline.named_steps["classifier"]

    # Transform features
    X_trans = preprocessor.transform(X_sample.head(max_samples))
    try:
        feature_names = list(preprocessor.get_feature_names_out())
    except Exception:
        feature_names = [f"Feature_{i}" for i in range(X_trans.shape[1])]

    # Use TreeExplainer if tree-based
    if hasattr(clf, "estimators_") or "DecisionTree" in type(clf).__name__:
        try:
            explainer = shap.TreeExplainer(clf)
            shap_values = explainer.shap_values(X_trans)
            # Handle binary classification output formats in SHAP
            if isinstance(shap_values, list) and len(shap_values) == 2:
                # Class 1 (Attrition)
                return shap_values[1], explainer, feature_names
            elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
                return shap_values[:, :, 1], explainer, feature_names
            return shap_values, explainer, feature_names
        except Exception:
            pass

    # Fallback to linear or sample background
    try:
        explainer = shap.Explainer(clf, X_trans)
        shap_vals = explainer(X_trans)
        return shap_vals.values, explainer, feature_names
    except Exception:
        return None, None, feature_names


def get_local_prediction_contributors(
    input_series: pd.Series,
    pipeline: Any
) -> List[Dict[str, Any]]:
    """
    Derive top business-interpretable factors pushing an individual employee's attrition probability up or down.
    """
    contributors = []

    # Check key stress/burnout drivers
    if "BurnoutRiskScore" in input_series and input_series["BurnoutRiskScore"] > 60:
        contributors.append({
            "factor": "Elevated Burnout Risk",
            "value": f"{input_series['BurnoutRiskScore']}/100",
            "impact": "Increases Risk",
            "severity": "High"
        })

    if "Overtime" in input_series and str(input_series["Overtime"]).lower() == "yes":
        ot_hours = input_series.get("OvertimeHoursMonthly", "Active")
        contributors.append({
            "factor": "Frequent Overtime Demands",
            "value": f"{ot_hours} hrs/mo",
            "impact": "Increases Risk",
            "severity": "Moderate"
        })

    if "JobSatisfaction" in input_series and input_series["JobSatisfaction"] <= 2:
        contributors.append({
            "factor": "Low Job Satisfaction Rating",
            "value": f"{input_series['JobSatisfaction']}/5",
            "impact": "Increases Risk",
            "severity": "High"
        })

    if "WorkLifeBalance" in input_series and input_series["WorkLifeBalance"] <= 2:
        contributors.append({
            "factor": "Sub-optimal Work-Life Balance",
            "value": f"{input_series['WorkLifeBalance']}/5",
            "impact": "Increases Risk",
            "severity": "Moderate"
        })

    if "YearsSinceLastPromotion" in input_series and input_series["YearsSinceLastPromotion"] >= 3.5:
        contributors.append({
            "factor": "Prolonged Role Stagnation",
            "value": f"{input_series['YearsSinceLastPromotion']} yrs since promotion",
            "impact": "Increases Risk",
            "severity": "Moderate"
        })

    # Mitigating factors (lowering risk)
    if "JobSatisfaction" in input_series and input_series["JobSatisfaction"] >= 4:
        contributors.append({
            "factor": "High Job Satisfaction",
            "value": f"{input_series['JobSatisfaction']}/5",
            "impact": "Lowers Risk",
            "severity": "Protective"
        })

    if "EmployeeEngagementScore" in input_series and input_series["EmployeeEngagementScore"] >= 75:
        contributors.append({
            "factor": "Strong Organizational Engagement",
            "value": f"{input_series['EmployeeEngagementScore']}/100",
            "impact": "Lowers Risk",
            "severity": "Protective"
        })

    return contributors
