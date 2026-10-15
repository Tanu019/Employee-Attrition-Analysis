"""
Tests for data leakage prevention and feature preprocessing.
"""
import pytest
import pandas as pd
from src.data_loader import get_default_master_data
from src.preprocessing import prepare_features_and_target, build_preprocessor_pipeline, create_train_test_split
from config.settings import LEAKAGE_AND_POST_EXIT_COLUMNS, SENSITIVE_DEMOGRAPHIC_COLUMNS


@pytest.fixture
def master_df():
    return get_default_master_data()


def test_leakage_columns_strictly_excluded(master_df):
    X, y, num_f, cat_f = prepare_features_and_target(master_df, exclude_sensitive=True)

    # Assert no post-outcome columns exist in predictor matrix
    for col in LEAKAGE_AND_POST_EXIT_COLUMNS:
        assert col not in X.columns, f"Data leakage violation! '{col}' was found in feature matrix X."

    # Assert target is not in X
    assert "Attrition" not in X.columns
    assert "EmploymentStatus" not in X.columns


def test_sensitive_demographics_excluded(master_df):
    X, y, num_f, cat_f = prepare_features_and_target(master_df, exclude_sensitive=True)

    for col in SENSITIVE_DEMOGRAPHIC_COLUMNS:
        assert col not in X.columns, f"Sensitive demographic '{col}' was not excluded from operational predictors."


def test_train_test_split_stratification(master_df):
    X, y, num_f, cat_f = prepare_features_and_target(master_df)
    X_train, X_test, y_train, y_test = create_train_test_split(X, y, test_size=0.20, random_state=42)

    assert len(X_train) == 2000
    assert len(X_test) == 500

    # Verify stratified class proportion (18.0% attrition in both splits)
    assert abs(y_train.mean() - 0.18) < 0.005
    assert abs(y_test.mean() - 0.18) < 0.005


def test_preprocessor_pipeline_transformation(master_df):
    X, y, num_f, cat_f = prepare_features_and_target(master_df)
    X_train, X_test, y_train, y_test = create_train_test_split(X, y)

    preprocessor = build_preprocessor_pipeline(num_f, cat_f)
    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    assert X_train_trans.shape[0] == 2000
    assert X_test_trans.shape[0] == 500
    assert X_train_trans.shape[1] == X_test_trans.shape[1]
    assert not pd.isna(X_train_trans).any()
