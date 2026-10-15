"""
Tests for workforce attrition rate calculator.
"""
import pytest
import pandas as pd
from src.attrition_calculator import calculate_attrition_metrics, derive_headcount_from_dates
from src.data_loader import get_default_master_data


def test_standard_attrition_formula():
    # Example: Opening 2500, Closing 2050, Exits 450
    # Avg Headcount = (2500 + 2050)/2 = 2275
    # Attrition Rate = (450 / 2275) * 100 = 19.78%
    res = calculate_attrition_metrics(
        opening_headcount=2500,
        closing_headcount=2050,
        total_exits=450,
        voluntary_exits=370,
        involuntary_exits=80
    )
    assert res["average_headcount"] == 2275.0
    assert res["attrition_rate_percent"] == 19.78
    assert res["voluntary_attrition_rate_percent"] == 16.26
    assert res["involuntary_attrition_rate_percent"] == 3.52
    assert len(res["calculation_steps"]) == 4


def test_invalid_zero_headcount_raises_error():
    with pytest.raises(ValueError):
        calculate_attrition_metrics(
            opening_headcount=0,
            closing_headcount=0,
            total_exits=10
        )


def test_date_derived_headcount():
    df = get_default_master_data()
    res = derive_headcount_from_dates(
        df=df,
        start_date=pd.Timestamp("2025-01-01"),
        end_date=pd.Timestamp("2026-09-30"),
        department="All Departments"
    )
    assert res["average_headcount"] > 0
    assert res["total_exits"] == 450
    assert res["voluntary_exits"] == 370
    assert res["involuntary_exits"] == 80
