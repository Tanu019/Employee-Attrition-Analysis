"""
Tests for data validation and schema profiling module.
"""
import pytest
import pandas as pd
from src.data_loader import get_default_master_data
from src.data_validation import (
    identify_target_column,
    map_schema,
    generate_data_dictionary,
    perform_data_quality_checks
)


@pytest.fixture
def master_df():
    return get_default_master_data()


def test_identify_target_column(master_df):
    target_col, pos_label = identify_target_column(master_df)
    assert target_col == "Attrition"
    assert pos_label == "Yes"


def test_map_schema(master_df):
    schema = map_schema(master_df)
    assert "target" in schema
    assert "Attrition" in schema["target"]
    assert "demographics" in schema
    assert "leakage_post_exit" in schema
    assert "ExitDate" in schema["leakage_post_exit"]


def test_generate_data_dictionary(master_df):
    dd = generate_data_dictionary(master_df)
    assert not dd.empty
    assert len(dd) == len(master_df.columns)
    assert "ColumnName" in dd.columns
    assert "IntendedUse" in dd.columns


def test_perform_data_quality_checks(master_df):
    summary = perform_data_quality_checks(master_df)
    assert summary["total_rows"] == 2500
    assert summary["total_cols"] == 70
    assert summary["duplicate_rows"] == 0
    assert summary["target_col"] == "Attrition"
    assert summary["attrition_rate"] == 18.0

    checks_df = summary["checks_df"]
    # Verify non-empty dataset passes
    assert "Non-Empty Dataset" in checks_df["Check"].values
    assert checks_df.loc[checks_df["Check"] == "Non-Empty Dataset", "Result"].values[0] == "PASS"
