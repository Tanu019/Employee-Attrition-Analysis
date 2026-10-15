"""
Feature engineering module for HR analytics.
Derives domain-specific ratios and composite indicators while strictly avoiding data leakage.
"""
import pandas as pd
import numpy as np


def engineer_hr_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate domain-specific, leakage-safe HR features.
    Operates on a copy of the DataFrame.
    """
    data = df.copy()

    # 1. Overtime to Standard Monthly Hours Ratio
    if "OvertimeHoursMonthly" in data.columns and "WeeklyWorkingHours" in data.columns:
        estimated_monthly_hours = data["WeeklyWorkingHours"] * 4.33
        data["OvertimeRatio"] = (data["OvertimeHoursMonthly"] / (estimated_monthly_hours + 1e-5)).round(4)

    # 2. Salary per Year of Total Experience
    if "MonthlySalaryINR" in data.columns and "TotalWorkExperienceYears" in data.columns:
        data["SalaryPerExpYear"] = (data["MonthlySalaryINR"] / (data["TotalWorkExperienceYears"] + 1)).round(2)

    # 3. Workload-to-Balance Stress Index
    if "AverageWorkloadScore" in data.columns and "WorkLifeBalance" in data.columns:
        data["WorkloadBalanceIndex"] = (data["AverageWorkloadScore"] / (data["WorkLifeBalance"] + 0.5)).round(3)

    # 4. Composite Well-being & Satisfaction Score (average of core Likert fields)
    satisfaction_components = [
        c for c in ["JobSatisfaction", "EnvironmentSatisfaction", "WorkLifeBalance",
                    "RelationshipWithManager", "CompensationSatisfaction", "CareerGrowthSatisfaction"]
        if c in data.columns and pd.api.types.is_numeric_dtype(data[c])
    ]
    if satisfaction_components:
        data["CompositeSatisfactionScore"] = data[satisfaction_components].mean(axis=1).round(2)

    # 5. Role Stability Ratio (tenure in current role relative to company tenure)
    if "YearsInCurrentRole" in data.columns and "YearsAtCompany" in data.columns:
        data["RoleTenureRatio"] = (data["YearsInCurrentRole"] / (data["YearsAtCompany"] + 0.5)).round(3)

    # 6. Manager Stability Ratio
    if "YearsWithCurrentManager" in data.columns and "YearsAtCompany" in data.columns:
        data["ManagerTenureRatio"] = (data["YearsWithCurrentManager"] / (data["YearsAtCompany"] + 0.5)).round(3)

    return data
