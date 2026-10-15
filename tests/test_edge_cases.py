"""
Edge cases and error handling tests.
"""
import pytest
import pandas as pd
from src.data_validation import identify_target_column, perform_data_quality_checks
from src.preprocessing import prepare_features_and_target
from src.attrition_calculator import calculate_attrition_metrics
from src.database import init_database, save_experiment, get_all_experiments, log_prediction, get_prediction_history


def test_empty_dataframe_quality_checks():
    empty_df = pd.DataFrame()
    summary = perform_data_quality_checks(empty_df)
    assert summary["total_rows"] == 0
    assert summary["total_cols"] == 0
    assert summary["target_col"] is None


def test_missing_target_column():
    df_no_target = pd.DataFrame({
        "Department": ["Sales", "HR"],
        "MonthlySalaryINR": [40000, 45000]
    })
    target_col, pos_label = identify_target_column(df_no_target)
    assert target_col is None
    assert pos_label is None

    with pytest.raises(ValueError, match="valid attrition target column"):
        prepare_features_and_target(df_no_target)


def test_single_class_target_check():
    df_single = pd.DataFrame({
        "EmployeeID": ["E1", "E2", "E3"],
        "Attrition": ["No", "No", "No"]
    })
    summary = perform_data_quality_checks(df_single)
    checks_df = summary["checks_df"]
    # Binary class diversity should fail when only 1 class is present
    div_check = checks_df[checks_df["Check"] == "Binary Target Class Diversity"]
    assert not div_check.empty
    assert div_check.iloc[0]["Result"] == "FAIL"


def test_database_persistence_roundtrip():
    init_database()
    test_exp = {
        "experiment_id": "TEST_EXP_001",
        "dataset_name": "Test.xlsx",
        "dataset_fingerprint": "testfp123456",
        "model_name": "Test Random Forest",
        "test_accuracy": 0.825,
        "test_precision": 0.50,
        "test_recall": 0.45,
        "test_f1": 0.47,
        "test_roc_auc": 0.73,
        "test_pr_auc": 0.44,
        "is_selected": True,
        "notes": "Pytest verification"
    }
    save_experiment(test_exp)
    exp_df = get_all_experiments()
    assert not exp_df.empty
    assert "TEST_EXP_001" in exp_df["experiment_id"].values

    test_pred = {
        "model_name": "Random Forest",
        "department": "Engineering",
        "job_role": "Software Engineer",
        "monthly_salary": 50000.0,
        "overtime": "No",
        "predicted_class": 0,
        "predicted_probability": 0.185,
        "risk_band": "Low Risk",
        "contributing_factors": ["High Satisfaction"]
    }
    log_prediction(test_pred)
    pred_history = get_prediction_history()
    assert not pred_history.empty
    assert (pred_history["department"] == "Engineering").any()
