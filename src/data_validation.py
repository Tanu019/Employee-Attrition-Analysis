"""
Data validation and data quality profiling module.
Implements schema mapping, target detection, validation checks, and data quality reporting.
"""
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

from config.settings import LEAKAGE_AND_POST_EXIT_COLUMNS, SENSITIVE_DEMOGRAPHIC_COLUMNS


def identify_target_column(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    """
    Identify the primary attrition target column and its positive class label.
    Supports 'Attrition', 'EmploymentStatus', 'Turnover', 'Left', 'Status'.
    """
    candidates = ["Attrition", "EmploymentStatus", "turnover", "left", "status", "attrition"]
    for col in candidates:
        matching = [c for c in df.columns if c.lower() == col.lower()]
        if matching:
            target_col = matching[0]
            val_counts = df[target_col].dropna().astype(str).str.strip().str.lower().value_counts()
            # Determine positive label
            pos_label = None
            for p in ["yes", "exited", "1", "true", "left", "terminated"]:
                if p in val_counts:
                    pos_label = df[target_col].dropna().loc[
                        df[target_col].dropna().astype(str).str.strip().str.lower() == p
                    ].iloc[0]
                    break
            return target_col, pos_label

    return None, None


def map_schema(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Categorize columns in the dataset into functional analytical roles.
    """
    target_col, _ = identify_target_column(df)
    cols = df.columns.tolist()

    schema_map = {
        "identifiers": [c for c in cols if any(k in c.lower() for k in ["id", "key"]) and c != target_col],
        "target": [target_col] if target_col else [],
        "demographics": [c for c in cols if c in SENSITIVE_DEMOGRAPHIC_COLUMNS or any(k in c.lower() for k in ["gender", "marital", "age", "education", "distance"])],
        "job_attributes": [c for c in cols if any(k in c.lower() for k in ["dept", "department", "role", "level", "businessunit", "arrangement", "location", "city", "state"])],
        "compensation": [c for c in cols if any(k in c.lower() for k in ["salary", "hike", "bonus", "compensation"])],
        "workload_performance": [c for c in cols if any(k in c.lower() for k in ["overtime", "hours", "workload", "projects", "rating", "performance", "absent", "late", "productivity"])],
        "satisfaction_wellbeing": [c for c in cols if any(k in c.lower() for k in ["satisfaction", "balance", "manager", "peer", "engagement", "stress", "burnout", "intent"])],
        "tenure_progression": [c for c in cols if any(k in c.lower() for k in ["years", "tenure", "promotion", "transfer", "experience", "companies"])],
        "leakage_post_exit": [c for c in cols if c in LEAKAGE_AND_POST_EXIT_COLUMNS and c != target_col]
    }
    return schema_map


def generate_data_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate dynamic data dictionary from the current DataFrame columns."""
    records = []
    target_col, _ = identify_target_column(df)

    for col in df.columns:
        dtype_str = str(df[col].dtype)
        num_unique = df[col].nunique()
        num_missing = int(df[col].isnull().sum())
        pct_missing = round((num_missing / len(df)) * 100, 2) if len(df) > 0 else 0.0

        # Suggested usage classification
        if col == target_col:
            intended_use = "Supervised Target Variable (Ground Truth)"
        elif col in LEAKAGE_AND_POST_EXIT_COLUMNS:
            intended_use = "Excluded: Post-exit outcome / leakage risk"
        elif col in SENSITIVE_DEMOGRAPHIC_COLUMNS:
            intended_use = "Protected Demographic: EDA & fairness auditing only"
        elif any(k in col.lower() for k in ["id", "key"]):
            intended_use = "Non-predictive Identifier"
        elif pd.api.types.is_numeric_dtype(df[col]):
            intended_use = "Numeric Feature / Predictive Variable"
        else:
            intended_use = "Categorical Feature / Predictive Variable"

        sample_vals = ", ".join([str(v) for v in df[col].dropna().unique()[:4]])
        if num_unique > 4:
            sample_vals += "..."

        records.append({
            "ColumnName": col,
            "DataType": dtype_str,
            "UniqueValues": num_unique,
            "MissingValues": num_missing,
            "MissingPercent": f"{pct_missing}%",
            "SampleValues": sample_vals,
            "IntendedUse": intended_use
        })

    return pd.DataFrame(records)


def perform_data_quality_checks(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Run comprehensive quality checks and return a summary report with outcomes.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    duplicate_rows = int(df.duplicated().sum())
    total_cells = total_rows * total_cols
    total_missing = int(df.isnull().sum().sum())
    missing_pct = round((total_missing / total_cells) * 100, 4) if total_cells > 0 else 0.0

    target_col, pos_label = identify_target_column(df)
    target_distribution = {}
    attrition_rate = 0.0
    if target_col:
        vc = df[target_col].value_counts(dropna=False).to_dict()
        target_distribution = {str(k): int(v) for k, v in vc.items()}
        if pos_label and pos_label in df[target_col].values:
            pos_count = (df[target_col] == pos_label).sum()
            attrition_rate = round((pos_count / total_rows) * 100, 2)

    # Detailed rule-based checks
    checks = []

    # Check 1: Empty dataset
    checks.append({
        "Check": "Non-Empty Dataset",
        "Result": "PASS" if total_rows > 0 and total_cols > 0 else "FAIL",
        "Details": f"{total_rows} rows, {total_cols} columns observed."
    })

    # Check 2: Identifier Uniqueness
    id_col = next((c for c in df.columns if "employeeid" in c.lower()), None)
    if id_col:
        unq_ids = df[id_col].nunique()
        checks.append({
            "Check": "Unique Employee Identifiers",
            "Result": "PASS" if unq_ids == total_rows else "FAIL",
            "Details": f"{unq_ids} unique values out of {total_rows} rows in '{id_col}'."
        })

    # Check 3: Attrition Target Variable
    checks.append({
        "Check": "Attrition Target Identification",
        "Result": "PASS" if target_col is not None else "FAIL",
        "Details": f"Target identified as '{target_col}' (positive label: '{pos_label}')" if target_col else "No target identified."
    })

    # Check 4: Target Class Balance & Diversity
    if target_col:
        n_classes = df[target_col].dropna().nunique()
        checks.append({
            "Check": "Binary Target Class Diversity",
            "Result": "PASS" if n_classes == 2 else ("WARN" if n_classes > 2 else "FAIL"),
            "Details": f"Target has {n_classes} distinct classes ({target_distribution})."
        })

    # Check 5: Active vs Exit Date Consistency (if ExitDate exists)
    if "ExitDate" in df.columns and target_col:
        active_with_exit = df[(df[target_col] != pos_label) & df["ExitDate"].notnull()]
        exited_without_exit = df[(df[target_col] == pos_label) & df["ExitDate"].isnull()]
        is_consistent = len(active_with_exit) == 0 and len(exited_without_exit) == 0
        checks.append({
            "Check": "Exit Date and Status Consistency",
            "Result": "PASS" if is_consistent else "FAIL",
            "Details": f"{len(active_with_exit)} active with exit date, {len(exited_without_exit)} exited without exit date."
        })

    # Check 6: Salary Consistency (Annual = Monthly * 12)
    if "MonthlySalaryINR" in df.columns and "AnnualSalaryINR" in df.columns:
        salary_mismatch = (df["AnnualSalaryINR"] != df["MonthlySalaryINR"] * 12).sum()
        checks.append({
            "Check": "Salary Multiplier Consistency (Annual = Monthly x 12)",
            "Result": "PASS" if salary_mismatch == 0 else "FAIL",
            "Details": f"{salary_mismatch} records have mismatched annual salary."
        })

    # Check 7: Satisfaction Rating Boundaries (1 to 5)
    satisfaction_cols = [c for c in df.columns if "satisfaction" in c.lower() and pd.api.types.is_numeric_dtype(df[c])]
    out_of_bounds = 0
    for sc in satisfaction_cols:
        out_of_bounds += ((df[sc] < 1) | (df[sc] > 5)).sum()
    if satisfaction_cols:
        checks.append({
            "Check": "Likert Scale Boundaries (1 to 5)",
            "Result": "PASS" if out_of_bounds == 0 else "FAIL",
            "Details": f"{len(satisfaction_cols)} satisfaction fields checked; {out_of_bounds} out-of-bound values found."
        })

    # Check 8: Data Leakage Risk Detection
    leakage_found = [c for c in df.columns if c in LEAKAGE_AND_POST_EXIT_COLUMNS and c != target_col]
    checks.append({
        "Check": "Post-Outcome Leakage Identification",
        "Result": "INFO",
        "Details": f"{len(leakage_found)} post-exit / outcome-equivalent columns detected and flagged for model exclusion."
    })

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "duplicate_rows": duplicate_rows,
        "total_cells": total_cells,
        "total_missing": total_missing,
        "missing_pct": missing_pct,
        "target_col": target_col,
        "positive_label": pos_label,
        "target_distribution": target_distribution,
        "attrition_rate": attrition_rate,
        "checks": checks,
        "checks_df": pd.DataFrame(checks)
    }
