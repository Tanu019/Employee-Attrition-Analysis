"""
Database persistence module using SQLite.
Stores model experiment history, predictions, and validation logs.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

from config.settings import DATABASE_PATH


def get_db_connection() -> sqlite3.Connection:
    """Ensure database directory exists and return a SQLite connection."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database tables for experiments, predictions, and uploads."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Experiments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_experiments (
        experiment_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        dataset_name TEXT NOT NULL,
        dataset_fingerprint TEXT NOT NULL,
        model_name TEXT NOT NULL,
        hyperparameters TEXT,
        cv_accuracy REAL,
        cv_f1 REAL,
        cv_roc_auc REAL,
        test_accuracy REAL,
        test_precision REAL,
        test_recall REAL,
        test_f1 REAL,
        test_roc_auc REAL,
        test_pr_auc REAL,
        is_selected INTEGER DEFAULT 0,
        notes TEXT
    )
    """)

    # Predictions log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prediction_history (
        prediction_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        model_name TEXT NOT NULL,
        department TEXT,
        job_role TEXT,
        monthly_salary REAL,
        overtime TEXT,
        predicted_class INTEGER NOT NULL,
        predicted_probability REAL NOT NULL,
        risk_band TEXT NOT NULL,
        contributing_factors TEXT
    )
    """)

    # Uploads tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dataset_uploads (
        upload_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_size_bytes INTEGER,
        row_count INTEGER,
        col_count INTEGER,
        target_column TEXT,
        attrition_rate REAL
    )
    """)

    conn.commit()
    conn.close()


def save_experiment(experiment: Dict[str, Any]):
    """Save a model experiment run to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO model_experiments (
        experiment_id, timestamp, dataset_name, dataset_fingerprint,
        model_name, hyperparameters, cv_accuracy, cv_f1, cv_roc_auc,
        test_accuracy, test_precision, test_recall, test_f1, test_roc_auc,
        test_pr_auc, is_selected, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        experiment.get("experiment_id"),
        experiment.get("timestamp", datetime.now().isoformat()),
        experiment.get("dataset_name", "SnackRush_Complete_Dataset.xlsx"),
        experiment.get("dataset_fingerprint", "default"),
        experiment.get("model_name"),
        json.dumps(experiment.get("hyperparameters", {})),
        experiment.get("cv_accuracy"),
        experiment.get("cv_f1"),
        experiment.get("cv_roc_auc"),
        experiment.get("test_accuracy"),
        experiment.get("test_precision"),
        experiment.get("test_recall"),
        experiment.get("test_f1"),
        experiment.get("test_roc_auc"),
        experiment.get("test_pr_auc"),
        1 if experiment.get("is_selected", False) else 0,
        experiment.get("notes", "")
    ))
    conn.commit()
    conn.close()


def get_all_experiments() -> pd.DataFrame:
    """Retrieve all model experiments as a DataFrame."""
    init_database()
    conn = get_db_connection()
    query = "SELECT * FROM model_experiments ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def log_prediction(pred_data: Dict[str, Any]):
    """Log an employee attrition prediction for audit and tracking."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO prediction_history (
        prediction_id, timestamp, model_name, department, job_role,
        monthly_salary, overtime, predicted_class, predicted_probability,
        risk_band, contributing_factors
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pred_data.get("prediction_id", f"PRED_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"),
        pred_data.get("timestamp", datetime.now().isoformat()),
        pred_data.get("model_name", "Random Forest"),
        pred_data.get("department", "Unknown"),
        pred_data.get("job_role", "Unknown"),
        pred_data.get("monthly_salary", 0.0),
        pred_data.get("overtime", "No"),
        int(pred_data.get("predicted_class", 0)),
        float(pred_data.get("predicted_probability", 0.0)),
        pred_data.get("risk_band", "Low"),
        json.dumps(pred_data.get("contributing_factors", []))
    ))
    conn.commit()
    conn.close()


def get_prediction_history() -> pd.DataFrame:
    """Retrieve recent predictions as a DataFrame."""
    init_database()
    conn = get_db_connection()
    query = "SELECT * FROM prediction_history ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
