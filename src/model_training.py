"""
Model training suite for employee attrition prediction.
Trains baseline dummy, linear, tree, and ensemble classifiers with leakage-safe cross-validation.
"""
from typing import Dict, Any, Tuple, Optional
import os
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier

from config.settings import RANDOM_STATE, CV_FOLDS, MODELS_DIR
from src.preprocessing import (
    prepare_features_and_target,
    build_preprocessor_pipeline,
    create_train_test_split,
    get_feature_names_from_preprocessor
)
from src.database import save_experiment


def get_candidate_classifiers(random_state: int = RANDOM_STATE) -> Dict[str, Any]:
    """Return initialized classifier instances configured for imbalanced attrition modeling."""
    return {
        "Dummy (Baseline)": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=random_state
        ),
        "Decision Tree": DecisionTreeClassifier(
            class_weight="balanced",
            max_depth=5,
            min_samples_leaf=20,
            random_state=random_state
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            min_samples_leaf=10,
            class_weight="balanced",
            random_state=random_state
        ),
        "Gradient Boosting": HistGradientBoostingClassifier(
            class_weight="balanced",
            max_iter=40,
            early_stopping=True,
            random_state=random_state
        )
    }


def train_and_cross_validate_models(
    df: pd.DataFrame,
    exclude_sensitive: bool = True,
    apply_feature_engineering: bool = True,
    save_artifacts: bool = True
) -> Dict[str, Any]:
    """
    Execute full training workflow:
    1. Separate features and target (leakage-free).
    2. Stratified train/test split.
    3. Stratified 5-Fold Cross-Validation on training data ONLY.
    4. Fit candidate pipelines on X_train.
    5. Save pipelines and metadata.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    X, y, numeric_features, categorical_features = prepare_features_and_target(
        df,
        exclude_sensitive=exclude_sensitive,
        apply_feature_engineering=apply_feature_engineering
    )

    X_train, X_test, y_train, y_test = create_train_test_split(X, y)

    preprocessor = build_preprocessor_pipeline(numeric_features, categorical_features)
    classifiers = get_candidate_classifiers()

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    cv_metrics = ["accuracy", "precision", "recall", "f1", "roc_auc"]

    trained_pipelines = {}
    cv_results_summary = []

    for name, clf in classifiers.items():
        pipe = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])

        # Cross-validation evaluated strictly on training folds
        scores = cross_validate(
            pipe, X_train, y_train,
            cv=cv,
            scoring=cv_metrics,
            return_train_score=False,
            error_score="raise"
        )

        cv_mean_acc = float(np.mean(scores["test_accuracy"]))
        cv_mean_f1 = float(np.mean(scores["test_f1"]))
        cv_mean_roc = float(np.mean(scores["test_roc_auc"]))
        cv_mean_rec = float(np.mean(scores["test_recall"]))
        cv_mean_prec = float(np.mean(scores["test_precision"]))

        # Fit final pipeline on complete training set
        pipe.fit(X_train, y_train)
        trained_pipelines[name] = pipe

        cv_results_summary.append({
            "Model": name,
            "CV_Accuracy_Mean": round(cv_mean_acc, 4),
            "CV_Accuracy_Std": round(float(np.std(scores["test_accuracy"])), 4),
            "CV_F1_Mean": round(cv_mean_f1, 4),
            "CV_F1_Std": round(float(np.std(scores["test_f1"])), 4),
            "CV_Recall_Mean": round(cv_mean_rec, 4),
            "CV_Precision_Mean": round(cv_mean_prec, 4),
            "CV_ROC_AUC_Mean": round(cv_mean_roc, 4)
        })

    # Transform feature names for interpretability
    fitted_preprocessor = trained_pipelines["Random Forest"].named_steps["preprocessor"]
    transformed_feature_names = get_feature_names_from_preprocessor(
        fitted_preprocessor, numeric_features, categorical_features
    )

    # Save best models to disk
    if save_artifacts:
        for name, pipe in trained_pipelines.items():
            filename = MODELS_DIR / f"{name.lower().replace(' ', '_').replace('(', '').replace(')', '')}_pipeline.joblib"
            joblib.dump(pipe, filename)

    return {
        "trained_pipelines": trained_pipelines,
        "cv_summary_df": pd.DataFrame(cv_results_summary),
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "transformed_feature_names": transformed_feature_names,
        "feature_cols": list(X.columns)
    }
