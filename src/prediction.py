"""
Inference and prediction engine for employee attrition.
Supports individual employee evaluation, batch inference, risk classification,
and tailored retention support suggestions.
"""
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

from config.settings import DEFAULT_RISK_THRESHOLDS
from src.database import log_prediction
from src.explainability import get_local_prediction_contributors
from src.feature_engineering import engineer_hr_features


def assign_risk_band(probability: float, thresholds: Optional[Dict[str, float]] = None) -> Tuple[str, str]:
    """
    Categorize predicted probability into actionable HR risk tiers.
    Returns: (risk_band, badge_class)
    """
    th = thresholds or DEFAULT_RISK_THRESHOLDS
    if probability < th["low"]:
        return "Low Risk", "badge-low"
    elif probability < th["moderate"]:
        return "Moderate Risk", "badge-mod"
    elif probability < th["high"]:
        return "High Risk", "badge-high"
    else:
        return "Critical Risk", "badge-high"


def recommend_support_actions(risk_band: str, employee_features: Dict[str, Any]) -> List[str]:
    """
    Generate proactive organizational support actions tailored to employee profile and risk tier.
    """
    actions = []
    ot = str(employee_features.get("Overtime", "No")).lower() == "yes"
    sat = float(employee_features.get("JobSatisfaction", 3.0))
    wlb = float(employee_features.get("WorkLifeBalance", 3.0))
    burnout = float(employee_features.get("BurnoutRiskScore", 45.0))
    promotion_gap = float(employee_features.get("YearsSinceLastPromotion", 1.0))

    if risk_band in ["High Risk", "Critical Risk"]:
        actions.append("Schedule a confidential one-on-one 'Stay Interview' with an HR Business Partner within 14 days.")
        if burnout > 55 or ot:
            actions.append("Initiate immediate workload review: reassess active project allocations and cap mandatory overtime.")
        if sat <= 2:
            actions.append("Conduct an exploratory compensation and internal mobility check with department leadership.")
        if promotion_gap >= 3.0:
            actions.append("Review career progression pathway and eligibility for professional certification sponsorship.")
    elif risk_band == "Moderate Risk":
        actions.append("Include in the quarterly employee engagement check-in with immediate people manager.")
        if wlb <= 2:
            actions.append("Discuss flexible work arrangements (e.g. hybrid options or flexible core hours).")
        actions.append("Offer skill development and lateral growth opportunities.")
    else:
        actions.append("Recognize consistent contributions and sustain current engagement routines.")
        actions.append("Consider employee as a candidate for peer mentorship or leadership development pipelines.")

    return actions


def predict_single_employee(
    pipeline: Any,
    feature_dict: Dict[str, Any],
    model_name: str = "Random Forest",
    thresholds: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Execute single employee inference through trained pipeline.
    """
    input_df = pd.DataFrame([feature_dict])
    input_df = engineer_hr_features(input_df)

    # Probability estimation
    if hasattr(pipeline, "predict_proba"):
        prob_array = pipeline.predict_proba(input_df)
        prob = float(prob_array[0, 1])
    else:
        pred_raw = pipeline.predict(input_df)
        prob = float(pred_raw[0])

    # Assign class based on threshold
    th = thresholds or DEFAULT_RISK_THRESHOLDS
    pred_class = 1 if prob >= th["moderate"] else 0
    risk_band, badge_class = assign_risk_band(prob, th)

    # Local contributing factors
    contributors = get_local_prediction_contributors(input_df.iloc[0], pipeline)
    suggested_actions = recommend_support_actions(risk_band, feature_dict)

    # Log to SQLite
    log_prediction({
        "model_name": model_name,
        "department": str(feature_dict.get("Department", "Unknown")),
        "job_role": str(feature_dict.get("JobRole", "Unknown")),
        "monthly_salary": float(feature_dict.get("MonthlySalaryINR", 0.0)),
        "overtime": str(feature_dict.get("Overtime", "No")),
        "predicted_class": pred_class,
        "predicted_probability": round(prob, 4),
        "risk_band": risk_band,
        "contributing_factors": [c["factor"] for c in contributors]
    })

    return {
        "predicted_class": pred_class,
        "predicted_label": "Likely to Leave (Attrition)" if pred_class == 1 else "Likely to Stay (Retained)",
        "attrition_probability": round(prob, 4),
        "probability_percent": round(prob * 100, 1),
        "risk_band": risk_band,
        "badge_class": badge_class,
        "contributing_factors": contributors,
        "suggested_actions": suggested_actions,
        "disclaimer": (
            "Model predictions represent probabilistic risk estimates derived from historical patterns, "
            "not deterministic forecasts. In accordance with ethical HR AI guidelines, this output must never "
            "be used to justify adverse employment actions, denial of benefits, or punitive measures."
        )
    }


def predict_batch_employees(
    pipeline: Any,
    df: pd.DataFrame,
    thresholds: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Run batch inference on a DataFrame of employees.
    Appends Predicted_Probability, Predicted_Attrition, and Risk_Band columns.
    """
    data = engineer_hr_features(df.copy())
    if hasattr(pipeline, "predict_proba"):
        probs = pipeline.predict_proba(data)[:, 1]
    else:
        probs = pipeline.predict(data).astype(float)

    th = thresholds or DEFAULT_RISK_THRESHOLDS
    preds = (probs >= th["moderate"]).astype(int)

    data["Predicted_Probability"] = np.round(probs, 4)
    data["Predicted_Attrition"] = np.where(preds == 1, "Yes", "No")
    data["Risk_Band"] = [assign_risk_band(p, th)[0] for p in probs]

    return data
