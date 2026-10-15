"""
Reproducible data preprocessing and leakage-prevention pipeline.
Builds Scikit-learn ColumnTransformer pipelines with training-only fitting.
"""
from typing import Tuple, List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from config.settings import (
    LEAKAGE_AND_POST_EXIT_COLUMNS,
    SENSITIVE_DEMOGRAPHIC_COLUMNS,
    RANDOM_STATE,
    TEST_SIZE
)
from src.data_validation import identify_target_column
from src.feature_engineering import engineer_hr_features


def prepare_features_and_target(
    df: pd.DataFrame,
    exclude_sensitive: bool = True,
    apply_feature_engineering: bool = True
) -> Tuple[pd.DataFrame, pd.Series, List[str], List[str]]:
    """
    Separates predictors and binary target while strictly eliminating leakage and sensitive demographics.
    Returns: (X, y, numeric_features, categorical_features)
    """
    target_col, pos_label = identify_target_column(df)
    if not target_col:
        raise ValueError("Could not locate a valid attrition target column in dataset.")

    # Target conversion: 1 for attrition, 0 for retained
    if pos_label is not None:
        y = (df[target_col] == pos_label).astype(int)
    else:
        y = df[target_col].astype(int)

    # Optional domain feature engineering
    data = engineer_hr_features(df) if apply_feature_engineering else df.copy()

    # Identify columns to drop (Leakage, identifiers, constant fields, target)
    cols_to_drop = set(LEAKAGE_AND_POST_EXIT_COLUMNS)
    cols_to_drop.add(target_col)

    # Add any columns with ID in the name
    for col in data.columns:
        if col.lower().endswith("id") or col.lower() == "id":
            cols_to_drop.add(col)

    # Drop zero-variance (constant) columns and datetime columns
    for col in data.columns:
        if data[col].nunique(dropna=False) <= 1 or pd.api.types.is_datetime64_any_dtype(data[col]) or "date" in col.lower():
            cols_to_drop.add(col)

    # Demographics exclusion
    if exclude_sensitive:
        for col in SENSITIVE_DEMOGRAPHIC_COLUMNS:
            if col in data.columns:
                cols_to_drop.add(col)

    # Final feature matrix
    feature_cols = [c for c in data.columns if c not in cols_to_drop]
    X = data[feature_cols].copy()

    # Separate numeric and categorical
    numeric_features = [
        c for c in X.columns
        if pd.api.types.is_numeric_dtype(X[c])
    ]
    categorical_features = [
        c for c in X.columns
        if not pd.api.types.is_numeric_dtype(X[c])
    ]

    return X, y, numeric_features, categorical_features


def build_preprocessor_pipeline(
    numeric_features: List[str],
    categorical_features: List[str]
) -> ColumnTransformer:
    """
    Build Scikit-learn ColumnTransformer with robust imputers and encoders.
    """
    numeric_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features)
        ],
        remainder="drop"
    )
    return preprocessor


def create_train_test_split(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Perform stratified train-test split to preserve attrition class ratio.
    """
    return train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )


def get_feature_names_from_preprocessor(
    fitted_preprocessor: ColumnTransformer,
    numeric_features: List[str],
    categorical_features: List[str]
) -> List[str]:
    """
    Extract transformed feature names after One-Hot Encoding for model interpretability.
    """
    try:
        # scikit-learn 1.0+ get_feature_names_out
        return list(fitted_preprocessor.get_feature_names_out())
    except Exception:
        # Fallback manual reconstruction
        cat_names = []
        if "cat" in fitted_preprocessor.named_transformers_:
            cat_encoder = fitted_preprocessor.named_transformers_["cat"].named_steps.get("encoder")
            if cat_encoder and hasattr(cat_encoder, "categories_"):
                for col, cats in zip(categorical_features, cat_encoder.categories_):
                    for val in cats:
                        cat_names.append(f"{col}_{val}")
        return numeric_features + cat_names
