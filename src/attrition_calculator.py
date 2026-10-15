"""
Transparent Attrition Rate Calculator.
Implements standard HR workforce formulas with date-based derivation and manual entry mode.
"""
from typing import Dict, Any, Optional
from datetime import date, datetime
import pandas as pd
import numpy as np


def calculate_attrition_metrics(
    opening_headcount: float,
    closing_headcount: float,
    total_exits: int,
    voluntary_exits: Optional[int] = None,
    involuntary_exits: Optional[int] = None,
    new_hires: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate standard HR attrition metrics based on opening and closing headcounts.
    Formula:
      Average Headcount = (Opening + Closing) / 2
      Attrition Rate = (Total Exits / Average Headcount) * 100
    """
    if opening_headcount <= 0 and closing_headcount <= 0:
        raise ValueError("Opening and closing headcounts cannot both be zero or negative.")

    avg_headcount = (opening_headcount + closing_headcount) / 2.0
    if avg_headcount <= 0:
        raise ValueError("Average headcount must be strictly positive.")

    attrition_rate = (total_exits / avg_headcount) * 100.0

    vol_rate = None
    if voluntary_exits is not None and voluntary_exits >= 0:
        vol_rate = (voluntary_exits / avg_headcount) * 100.0

    invol_rate = None
    if involuntary_exits is not None and involuntary_exits >= 0:
        invol_rate = (involuntary_exits / avg_headcount) * 100.0

    # Retention rate (based on opening cohort if new_hires is known)
    retention_rate = None
    if new_hires is not None and opening_headcount > 0:
        retained_from_opening = closing_headcount - new_hires
        retention_rate = max(0.0, (retained_from_opening / opening_headcount) * 100.0)
    else:
        # Standard complement approximation
        retention_rate = max(0.0, 100.0 - attrition_rate)

    return {
        "opening_headcount": float(opening_headcount),
        "closing_headcount": float(closing_headcount),
        "average_headcount": round(avg_headcount, 2),
        "total_exits": int(total_exits),
        "voluntary_exits": int(voluntary_exits) if voluntary_exits is not None else None,
        "involuntary_exits": int(involuntary_exits) if involuntary_exits is not None else None,
        "attrition_rate_percent": round(attrition_rate, 2),
        "voluntary_attrition_rate_percent": round(vol_rate, 2) if vol_rate is not None else None,
        "involuntary_attrition_rate_percent": round(invol_rate, 2) if invol_rate is not None else None,
        "retention_rate_percent": round(retention_rate, 2) if retention_rate is not None else None,
        "calculation_steps": [
            f"1. Average Headcount = ({opening_headcount:.0f} + {closing_headcount:.0f}) / 2 = {avg_headcount:.2f}",
            f"2. Total Attrition Rate = ({total_exits} / {avg_headcount:.2f}) × 100 = {attrition_rate:.2f}%",
            f"3. Voluntary Rate = ({voluntary_exits if voluntary_exits else 0} / {avg_headcount:.2f}) × 100 = {vol_rate:.2f}%" if vol_rate is not None else "3. Voluntary exits breakdown not available",
            f"4. Involuntary Rate = ({involuntary_exits if involuntary_exits else 0} / {avg_headcount:.2f}) × 100 = {invol_rate:.2f}%" if invol_rate is not None else "4. Involuntary exits breakdown not available"
        ]
    }


def derive_headcount_from_dates(
    df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    department: Optional[str] = None
) -> Dict[str, Any]:
    """
    Derive opening headcount, closing headcount, and period exits from employee master dates.
    """
    data = df.copy()
    if department and department != "All Departments" and "Department" in data.columns:
        data = data[data["Department"] == department]

    if "JoiningDate" not in data.columns:
        raise ValueError("Dataset does not contain 'JoiningDate' required for headcount derivation.")

    # Convert dates to Timestamp
    data["JoiningDate"] = pd.to_datetime(data["JoiningDate"])
    exit_dates = pd.to_datetime(data["ExitDate"]) if "ExitDate" in data.columns else pd.Series(pd.NaT, index=data.index)

    # Opening headcount: Joined on or before start_date, and (no exit date OR exit date >= start_date)
    opening_mask = (data["JoiningDate"] <= start_date) & (exit_dates.isna() | (exit_dates >= start_date))
    opening_hc = opening_mask.sum()

    # Closing headcount: Joined on or before end_date, and (no exit date OR exit date > end_date)
    closing_mask = (data["JoiningDate"] <= end_date) & (exit_dates.isna() | (exit_dates > end_date))
    closing_hc = closing_mask.sum()

    # Exits during period: ExitDate between start_date and end_date (inclusive)
    period_exits_mask = (exit_dates >= start_date) & (exit_dates <= end_date)
    period_exits = period_exits_mask.sum()

    # New hires during period
    new_hires = ((data["JoiningDate"] >= start_date) & (data["JoiningDate"] <= end_date)).sum()

    # Voluntary vs Involuntary
    vol_exits = None
    invol_exits = None
    if "ExitType" in data.columns:
        vol_exits = ((period_exits_mask) & (data["ExitType"].str.lower() == "voluntary")).sum()
        invol_exits = ((period_exits_mask) & (data["ExitType"].str.lower() == "involuntary")).sum()

    return calculate_attrition_metrics(
        opening_headcount=opening_hc,
        closing_headcount=closing_hc,
        total_exits=period_exits,
        voluntary_exits=vol_exits,
        involuntary_exits=invol_exits,
        new_hires=new_hires
    )
