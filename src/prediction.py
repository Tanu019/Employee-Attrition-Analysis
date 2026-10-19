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


_BASELINE_EMPLOYEE_RECORD: Optional[Dict[str, Any]] = None


def get_baseline_employee_record() -> Dict[str, Any]:
    global _BASELINE_EMPLOYEE_RECORD
    if _BASELINE_EMPLOYEE_RECORD is not None:
        return _BASELINE_EMPLOYEE_RECORD.copy()
    try:
        from src.data_loader import get_default_master_data
        df = get_default_master_data()
        _BASELINE_EMPLOYEE_RECORD = df.iloc[0].to_dict()
    except Exception:
        _BASELINE_EMPLOYEE_RECORD = {}
    return _BASELINE_EMPLOYEE_RECORD.copy()


def estimate_retention_runway(prob: float, tenure_years: float, satisfaction: float) -> Dict[str, str]:
    """Estimate time-to-attrition horizon based on current flight probability and satisfaction."""
    if prob >= 0.70:
        return {
            "horizon": "Immediate (1 – 3 Months)",
            "urgency": "Critical",
            "narrative": "Urgent flight risk window. Departures in this tier historically occur within 90 days if unaddressed."
        }
    elif prob >= 0.40:
        return {
            "horizon": "Near-Term (3 – 6 Months)",
            "urgency": "Elevated",
            "narrative": "Disengagement inflection point. Proactive intervention in next review cycle can reverse attrition."
        }
    elif prob >= 0.20:
        return {
            "horizon": "Medium-Term (6 – 12 Months)",
            "urgency": "Moderate",
            "narrative": "Stable in current role; vulnerable to external recruitment poaching or promotion delay."
        }
    else:
        return {
            "horizon": "Long-Term (2+ Years)",
            "urgency": "Low",
            "narrative": "High retention stability. Target for internal leadership pipelines and mentorship roles."
        }


def compute_counterfactual_scenarios(
    pipeline: Any,
    merged_features: Dict[str, Any],
    base_prob: float,
    thresholds: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Simulate actionable counterfactual interventions to project how policy changes
    (overtime elimination, equity boost, wellness support) decrease attrition risk.
    """
    scenarios = []
    th = thresholds or DEFAULT_RISK_THRESHOLDS

    def score_variation(variant_dict: Dict[str, Any]) -> Tuple[float, str, str]:
        var_df = pd.DataFrame([variant_dict])
        var_df = engineer_hr_features(var_df)
        if hasattr(pipeline, "predict_proba"):
            p = float(pipeline.predict_proba(var_df)[0, 1])
        else:
            p = float(pipeline.predict(var_df)[0])
        r_band, b_class = assign_risk_band(p, th)
        return p, r_band, b_class

    curr_salary = float(merged_features.get("MonthlySalaryINR", 40000.0))

    # Scenario 1: Eliminate Overtime
    if str(merged_features.get("Overtime", "No")).lower() == "yes" or float(merged_features.get("OvertimeHoursMonthly", 0)) > 5:
        s1 = merged_features.copy()
        s1["Overtime"] = "No"
        s1["OvertimeHoursMonthly"] = 0.0
        p1, band1, badge1 = score_variation(s1)
        drop1 = round((base_prob - p1) * 100, 1)
        scenarios.append({
            "name": "Zero-Overtime Cap",
            "description": "Institute a hard cap on overtime hours and eliminate mandatory weekend shifts.",
            "changes": ["Overtime: No", "Overtime Hours: 0 hrs/mo"],
            "new_probability_pct": round(p1 * 100, 1),
            "risk_drop_pct": drop1,
            "new_risk_band": band1,
            "badge_class": badge1,
            "feasibility": "High (Operational adjustment)"
        })

    # Scenario 2: +12% Targeted Compensation Adjustment
    s2 = merged_features.copy()
    s2["MonthlySalaryINR"] = round(curr_salary * 1.12, 2)
    p2, band2, badge2 = score_variation(s2)
    drop2 = round((base_prob - p2) * 100, 1)
    scenarios.append({
        "name": "Targeted Comp Adjustment (+12%)",
        "description": f"Award a +12% base salary raise (+₹{int(curr_salary * 0.12):,}/mo) to restore competitive market parity.",
        "changes": [f"Salary: ₹{int(curr_salary * 1.12):,} (was ₹{int(curr_salary):,})"],
        "new_probability_pct": round(p2 * 100, 1),
        "risk_drop_pct": drop2,
        "new_risk_band": band2,
        "badge_class": badge2,
        "feasibility": "Medium (Budget approval required)"
    })

    # Scenario 3: Burnout & Fatigue Reset
    s3 = merged_features.copy()
    s3["WorkLifeBalance"] = 4.0
    if "AverageWorkloadScore" in s3:
        s3["AverageWorkloadScore"] = max(35.0, float(s3["AverageWorkloadScore"]) * 0.80)
    if "BurnoutRiskScore" in s3:
        s3["BurnoutRiskScore"] = max(25.0, float(s3["BurnoutRiskScore"]) * 0.70)
    p3, band3, badge3 = score_variation(s3)
    drop3 = round((base_prob - p3) * 100, 1)
    scenarios.append({
        "name": "Burnout & Fatigue Reset",
        "description": "Reallocate active accounts to decrease workload by 20% and provide hybrid schedule flexibility.",
        "changes": ["Work-Life Balance: 4.0/5", "Burnout Score: Reduced ~30%"],
        "new_probability_pct": round(p3 * 100, 1),
        "risk_drop_pct": drop3,
        "new_risk_band": band3,
        "badge_class": badge3,
        "feasibility": "High (Manager reallocation)"
    })

    # Scenario 4: Combined Retention Package (All levers)
    s4 = merged_features.copy()
    s4["Overtime"] = "No"
    s4["OvertimeHoursMonthly"] = 0.0
    s4["MonthlySalaryINR"] = round(curr_salary * 1.10, 2)
    s4["WorkLifeBalance"] = 4.0
    s4["JobSatisfaction"] = min(5.0, float(s4.get("JobSatisfaction", 3.0)) + 1.0)
    if "AverageWorkloadScore" in s4:
        s4["AverageWorkloadScore"] = max(35.0, float(s4["AverageWorkloadScore"]) * 0.80)
    if "BurnoutRiskScore" in s4:
        s4["BurnoutRiskScore"] = max(25.0, float(s4["BurnoutRiskScore"]) * 0.65)
    p4, band4, badge4 = score_variation(s4)
    drop4 = round((base_prob - p4) * 100, 1)
    scenarios.append({
        "name": "Comprehensive Retention Package",
        "description": "Integrated intervention: overtime relief, +10% equity raise, and manager alignment check-in.",
        "changes": ["Overtime Cap", "+10% Salary", "Workload Rebalance", "Manager Check-in"],
        "new_probability_pct": round(p4 * 100, 1),
        "risk_drop_pct": drop4,
        "new_risk_band": band4,
        "badge_class": badge4,
        "feasibility": "Strategic (Maximum impact)"
    })

    return scenarios


def predict_single_employee(
    pipeline: Any,
    feature_dict: Dict[str, Any],
    model_name: str = "Random Forest",
    thresholds: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Execute single employee inference through trained pipeline.
    """
    merged_features = get_baseline_employee_record()
    merged_features.update({k: v for k, v in feature_dict.items() if v is not None})
    input_df = pd.DataFrame([merged_features])
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

    # Prescriptive Counterfactual Scenarios & Retention Runway
    counterfactuals = compute_counterfactual_scenarios(pipeline, merged_features, prob, th)
    retention_runway = estimate_retention_runway(
        prob,
        float(feature_dict.get("YearsAtCompany", 2.0)),
        float(feature_dict.get("JobSatisfaction", 3.0))
    )

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
        "counterfactual_scenarios": counterfactuals,
        "retention_runway": retention_runway,
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
