"""
HR analytics and exploratory data analysis module.
Computes cross-tabulations, distributions, stayer-vs-leaver comparisons,
and dynamic dataset-driven insights.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from src.data_validation import identify_target_column


def compute_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate executive-level workforce KPIs from the active dataset."""
    total_employees = len(df)
    target_col, pos_label = identify_target_column(df)

    active_count = None
    exited_count = None
    attrition_rate = None
    voluntary_rate = None

    if target_col and pos_label:
        is_exited = (df[target_col] == pos_label)
        exited_count = int(is_exited.sum())
        active_count = total_employees - exited_count
        attrition_rate = round((exited_count / total_employees) * 100, 2) if total_employees > 0 else 0.0

        if "ExitType" in df.columns:
            vol_exits = ((is_exited) & (df["ExitType"].astype(str).str.lower() == "voluntary")).sum()
            voluntary_rate = round((vol_exits / total_employees) * 100, 2) if total_employees > 0 else 0.0

    # Averages
    avg_age = round(float(df["Age"].mean()), 1) if "Age" in df.columns and pd.api.types.is_numeric_dtype(df["Age"]) else None
    avg_salary = round(float(df["MonthlySalaryINR"].mean()), 2) if "MonthlySalaryINR" in df.columns and pd.api.types.is_numeric_dtype(df["MonthlySalaryINR"]) else None
    avg_tenure = round(float(df["YearsAtCompany"].mean()), 1) if "YearsAtCompany" in df.columns and pd.api.types.is_numeric_dtype(df["YearsAtCompany"]) else None
    avg_satisfaction = round(float(df["JobSatisfaction"].mean()), 2) if "JobSatisfaction" in df.columns and pd.api.types.is_numeric_dtype(df["JobSatisfaction"]) else None
    avg_work_life = round(float(df["WorkLifeBalance"].mean()), 2) if "WorkLifeBalance" in df.columns and pd.api.types.is_numeric_dtype(df["WorkLifeBalance"]) else None
    avg_burnout = round(float(df["BurnoutRiskScore"].mean()), 1) if "BurnoutRiskScore" in df.columns and pd.api.types.is_numeric_dtype(df["BurnoutRiskScore"]) else None

    return {
        "total_employees": total_employees,
        "active_employees": active_count,
        "exited_employees": exited_count,
        "attrition_rate_percent": attrition_rate,
        "voluntary_attrition_rate_percent": voluntary_rate,
        "avg_age": avg_age,
        "avg_salary_inr": avg_salary,
        "avg_tenure_years": avg_tenure,
        "avg_job_satisfaction": avg_satisfaction,
        "avg_work_life_balance": avg_work_life,
        "avg_burnout_risk": avg_burnout
    }


def compute_breakdown_table(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """
    Compute structured breakdown table with Total, Stayed, Exited, and Attrition Rate (%)
    ensuring exact denominators are transparent.
    """
    target_col, pos_label = identify_target_column(df)
    if not target_col or group_col not in df.columns:
        return pd.DataFrame()

    is_exit = (df[target_col] == pos_label) if pos_label else df[target_col].astype(int) == 1

    grouped = df.groupby(group_col).agg(
        TotalEmployees=(group_col, "count"),
        ExitedEmployees=(target_col, lambda s: is_exit.loc[s.index].sum())
    ).reset_index()

    grouped["ActiveEmployees"] = grouped["TotalEmployees"] - grouped["ExitedEmployees"]
    grouped["AttritionRatePercent"] = ((grouped["ExitedEmployees"] / grouped["TotalEmployees"]) * 100).round(2)
    grouped = grouped.sort_values(by="AttritionRatePercent", ascending=False)
    return grouped


def compute_stayers_vs_leavers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare central tendencies (mean & median) between employees who stayed vs those who exited.
    """
    target_col, pos_label = identify_target_column(df)
    if not target_col:
        return pd.DataFrame()

    is_exit = (df[target_col] == pos_label) if pos_label else df[target_col].astype(int) == 1
    numeric_cols = [
        c for c in df.select_dtypes(include=[np.number]).columns
        if c not in ["EmployeeID", "AnnualSalaryINR"] and not c.lower().endswith("id")
    ]

    records = []
    for col in numeric_cols:
        stay_mean = df.loc[~is_exit, col].mean()
        exit_mean = df.loc[is_exit, col].mean()
        diff = exit_mean - stay_mean
        pct_diff = (diff / (stay_mean + 1e-5)) * 100 if stay_mean != 0 else 0.0

        records.append({
            "Metric": col,
            "StayersMean": round(stay_mean, 2),
            "LeaversMean": round(exit_mean, 2),
            "AbsoluteDifference": round(diff, 2),
            "PercentChange": round(pct_diff, 1)
        })

    result_df = pd.DataFrame(records)
    # Sort by absolute percent change descending
    result_df["AbsChange"] = result_df["PercentChange"].abs()
    result_df = result_df.sort_values(by="AbsChange", ascending=False).drop(columns=["AbsChange"])
    return result_df


def compute_correlations_with_target(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Pearson correlation of numeric features with binary attrition target."""
    target_col, pos_label = identify_target_column(df)
    if not target_col:
        return pd.DataFrame()

    target_numeric = ((df[target_col] == pos_label).astype(int)) if pos_label else df[target_col].astype(int)
    num_df = df.select_dtypes(include=[np.number])

    corrs = []
    for col in num_df.columns:
        if col.lower().endswith("id") or col in ["AnnualSalaryINR"]:
            continue
        corr_val = num_df[col].corr(target_numeric)
        if not np.isnan(corr_val):
            corrs.append({
                "Feature": col,
                "Correlation": round(corr_val, 4),
                "Direction": "Increases Attrition" if corr_val > 0 else "Decreases Attrition",
                "AbsCorrelation": abs(corr_val)
            })

    corr_df = pd.DataFrame(corrs).sort_values(by="AbsCorrelation", ascending=False).drop(columns=["AbsCorrelation"])
    return corr_df


def generate_data_driven_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Derive dynamic textual insights computed directly from dataset calculations.
    No hardcoded statistics!
    """
    insights = []
    target_col, pos_label = identify_target_column(df)
    if not target_col:
        return insights

    is_exit = (df[target_col] == pos_label) if pos_label else df[target_col].astype(int) == 1
    total_rate = ((is_exit.sum() / len(df)) * 100).round(2)

    # 1. Department insight
    if "Department" in df.columns:
        dept_tbl = compute_breakdown_table(df, "Department")
        if not dept_tbl.empty:
            highest_dept = dept_tbl.iloc[0]
            lowest_dept = dept_tbl.iloc[-1]
            insights.append({
                "category": "Department Attrition Disparity",
                "finding": (
                    f"Highest attrition is observed in '{highest_dept['Department']}' at {highest_dept['AttritionRatePercent']}% "
                    f"({highest_dept['ExitedEmployees']} exits out of {highest_dept['TotalEmployees']} employees), compared to "
                    f"'{lowest_dept['Department']}' at {lowest_dept['AttritionRatePercent']}%. "
                    f"The department exceeds company average by {round(highest_dept['AttritionRatePercent'] - total_rate, 2)} percentage points."
                ),
                "action": "Conduct targeted stay interviews and operational workflow reviews in high-turnover departments."
            })

    # 2. Overtime insight
    if "Overtime" in df.columns:
        ot_tbl = compute_breakdown_table(df, "Overtime")
        if len(ot_tbl) >= 2:
            ot_yes = ot_tbl[ot_tbl["Overtime"].astype(str).str.lower() == "yes"]
            ot_no = ot_tbl[ot_tbl["Overtime"].astype(str).str.lower() == "no"]
            if not ot_yes.empty and not ot_no.empty:
                r_yes = ot_yes.iloc[0]["AttritionRatePercent"]
                r_no = ot_no.iloc[0]["AttritionRatePercent"]
                multiplier = round(r_yes / (r_no + 1e-5), 2)
                insights.append({
                    "category": "Overtime & Workload Impact",
                    "finding": (
                        f"Employees working overtime exhibit an attrition rate of {r_yes}% vs {r_no}% for non-overtime staff "
                        f"({multiplier}x relative exit likelihood)."
                    ),
                    "action": "Implement overtime hour caps and compensatory off-time policies to alleviate cumulative strain."
                })

    # 3. Job Satisfaction insight
    if "JobSatisfaction" in df.columns and pd.api.types.is_numeric_dtype(df["JobSatisfaction"]):
        low_sat = df[df["JobSatisfaction"] <= 2]
        high_sat = df[df["JobSatisfaction"] >= 4]
        if len(low_sat) > 0 and len(high_sat) > 0:
            rate_low = round((is_exit.loc[low_sat.index].sum() / len(low_sat)) * 100, 2)
            rate_high = round((is_exit.loc[high_sat.index].sum() / len(high_sat)) * 100, 2)
            insights.append({
                "category": "Employee Satisfaction Gradient",
                "finding": (
                    f"Employees with low job satisfaction (Rating 1-2) experience {rate_low}% attrition ({is_exit.loc[low_sat.index].sum()}/{len(low_sat)}), "
                    f"whereas satisfied employees (Rating 4-5) record only {rate_high}% attrition ({is_exit.loc[high_sat.index].sum()}/{len(high_sat)})."
                ),
                "action": "Deploy rapid-pulse engagement surveys and manager check-ins when satisfaction falls below rating 3."
            })

    # 4. Burnout and Stress insight
    if "BurnoutRiskScore" in df.columns and pd.api.types.is_numeric_dtype(df["BurnoutRiskScore"]):
        stayers_burnout = df.loc[~is_exit, "BurnoutRiskScore"].mean()
        leavers_burnout = df.loc[is_exit, "BurnoutRiskScore"].mean()
        diff = round(leavers_burnout - stayers_burnout, 1)
        insights.append({
            "category": "Burnout & Wellbeing Divergence",
            "finding": (
                f"Exited personnel demonstrated an average burnout score of {leavers_burnout:.1f} vs {stayers_burnout:.1f} "
                f"among retained employees (+{diff} points higher burnout risk before departure)."
            ),
            "action": "Introduce wellness interventions, workload balancing, and mental health resources."
        })

    return insights
