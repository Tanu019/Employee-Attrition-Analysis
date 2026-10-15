"""
Configuration and settings for the Employee Attrition Analysis application.
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_FILE = BASE_DIR / "SnackRush_Complete_Dataset.xlsx"
DATABASE_PATH = BASE_DIR / "data" / "attrition_analytics.db"
REPORTS_DIR = BASE_DIR / "reports"
MODELS_DIR = BASE_DIR / "models"

# App Metadata
PRODUCT_NAME = "People Intelligence"
APP_TITLE = "Employees Attrition Analysis"
APP_SUBTITLE = "An Explainable HR Analytics and Predictive Decision Support Platform"
PROJECT_CONTEXT = "An Explainable HR Analytics and Predictive Decision Support Platform"
ORGANIZATION_NAME = "SnackRush"
ORGANIZATION_NOTE = "Fictional quick-commerce company (synthetic demonstration data)"
TAGLINE = "Understand workforce trends. Identify retention opportunities. Make evidence-based HR decisions."

# Color Palette (Refined Warm Neutrals with Muted Terracotta)
THEME_COLORS = {
    "background": "#211E1B",
    "card_bg": "#302923",
    "card_hover": "#3a322b",
    "border": "#494038",
    "accent": "#C47C5A",        # Muted terracotta
    "accent_hover": "#d18a67",
    "text_primary": "#F5F0E8",   # Warm ivory
    "text_secondary": "#B8ADA2", # Muted grey
    "text_muted": "#8a7f74",
    "risk_low": "#8FA58B",      # Positive soft sage
    "risk_moderate": "#D49B5B", # Muted amber
    "risk_high": "#C85A5A",     # Restrained red
    "chart_palette": [
        "#C47C5A", "#8FA58B", "#D49B5B", "#C85A5A", "#7B8FA1",
        "#A87B65", "#6B8E7D", "#B88E52", "#9E6565", "#5E7182"
    ]
}

# Strict Data Leakage Prevention Configuration
LEAKAGE_AND_POST_EXIT_COLUMNS = [
    "EmployeeID",              # Unique identifier, non-predictive
    "ObservationDate",         # Fixed cutoff date
    "ExitDate",                # Available only after exit (direct outcome leakage)
    "EmploymentStatus",        # Direct outcome synonym (Active vs Exited)
    "ExitType",                # Post-exit classification (Voluntary / Involuntary)
    "AttritionCategory",       # Synonym of ExitType
    "ExitReasonCategory",      # Recorded post-exit
    "TenureAtExitYears",       # Post-exit metric
    "RehireEligible",          # Determined at exit
    "ExitInterviewCompleted",  # Administered during exit
    "DepartmentAtExit",        # Captured upon termination
    "JobLevelAtExit",          # Captured upon termination
    "ProbationCompleted",      # Constant (zero variance)
    "AnnualSalaryINR",         # Exact 12x collinear replica of MonthlySalaryINR
]

# Sensitive Demographics (Protected by Default for Governed Fairness Auditing)
SENSITIVE_DEMOGRAPHIC_COLUMNS = [
    "Gender",
    "MaritalStatus",
    "Age"
]

# Model Parameters
RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5

# Risk Thresholds
DEFAULT_RISK_THRESHOLDS = {
    "low": 0.25,
    "moderate": 0.50,
    "high": 0.75
}
