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
APP_TITLE = "EMPLOYEES ATTRITION ANALYSIS"
APP_SUBTITLE = "An Interactive HR Analytics and Machine Learning Decision Support System"
PROJECT_CONTEXT = "MBA Business Analytics Capstone Project"
ORGANIZATION_NAME = "SnackRush Enterprise Solutions"

# Color Palette (Warm Cocoa / Charcoal / Copper Theme)
THEME_COLORS = {
    "background": "#181513",
    "card_bg": "#241f1c",
    "card_hover": "#2e2723",
    "border": "#3a322c",
    "accent": "#c86d51",        # Muted copper / terracotta
    "accent_hover": "#d97d62",
    "text_primary": "#f7f3eb",   # Warm ivory
    "text_secondary": "#aba398", # Neutral grey
    "text_muted": "#7d756b",
    "risk_low": "#388e3c",      # Emerald green
    "risk_moderate": "#f57c00", # Warm amber
    "risk_high": "#d32f2f",     # Crimson terracotta
    "chart_palette": [
        "#c86d51", "#d9822b", "#5b8c85", "#8c6d97", "#d1a853",
        "#6b8e23", "#4682b4", "#cd853f", "#bc8f8f", "#708090"
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
