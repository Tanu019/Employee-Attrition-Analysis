"""
EMPLOYEES ATTRITION ANALYSIS
An Interactive HR Analytics and Machine Learning Decision Support System
MBA Business Analytics Capstone Application
"""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Add project root to system path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import (
    APP_TITLE,
    APP_SUBTITLE,
    ORGANIZATION_NAME,
    PROJECT_CONTEXT,
    DEFAULT_DATA_FILE
)
from src.data_loader import load_workbook_data
from src.database import init_database
from src.modules.mod1_overview import render_module_overview
from src.modules.mod2_upload import render_module_upload
from src.modules.mod3_dashboard import render_module_dashboard
from src.modules.mod4_analysis import render_module_analysis
from src.modules.mod5_calculator import render_module_calculator
from src.modules.mod6_preprocessing import render_module_preprocessing
from src.modules.mod7_mod8_training_eval import render_module_training_and_eval
from src.modules.mod9_prediction import render_module_prediction
from src.modules.mod10_explainability import render_module_explainability
from src.modules.mod11_retention import render_module_retention
from src.modules.mod12_experiments import render_module_experiments
from src.modules.mod13_reports import render_module_reports
from src.modules.mod14_methodology import render_module_methodology


def load_custom_css():
    """Inject custom warm cocoa / charcoal / copper CSS into Streamlit."""
    css_path = BASE_DIR / "styles" / "custom.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="EMPLOYEES ATTRITION ANALYSIS",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    load_custom_css()
    init_database()

    # Initialize session state dataset
    if "workbook" not in st.session_state:
        with st.spinner("Initializing SnackRush Enterprise Dataset..."):
            workbook, fingerprint = load_workbook_data(DEFAULT_DATA_FILE)
            st.session_state["workbook"] = workbook
            st.session_state["fingerprint"] = fingerprint
            st.session_state["dataset_name"] = "SnackRush_Complete_Dataset.xlsx"
            st.session_state["models_trained"] = False

    workbook = st.session_state["workbook"]
    fingerprint = st.session_state["fingerprint"]
    dataset_name = st.session_state.get("dataset_name", "SnackRush_Complete_Dataset.xlsx")

    # Primary employee master DataFrame
    df_master = workbook.get("Employee Master", next(iter(workbook.values())))

    # Sidebar Navigation & Enterprise Branding
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-brand">
            <div style="font-size: 1.15rem; font-weight: 800; color: #f7f3eb; letter-spacing: -0.01em;">
                💼 HR DECISION SUPPORT
            </div>
            <div class="sidebar-tagline">
                {ORGANIZATION_NAME}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation menu
        module_options = [
            "1. Project Overview",
            "2. Data Upload & Validation",
            "3. Executive HR Dashboard",
            "4. Employee Attrition Analysis",
            "5. Attrition Rate Calculator",
            "6. Data Cleaning & Feature Eng.",
            "7. ML Model Training & Evaluation",
            "8. Attrition Flight Risk Prediction",
            "9. Explainability & SHAP",
            "10. Retention Strategy Planner",
            "11. Model History & Registry",
            "12. Reports & Analytical Exports",
            "13. Methodology & Documentation"
        ]

        selected_page = st.radio("Navigation Menu", module_options, index=0)

        st.markdown("---")

        # Persistent Dataset Status Card
        total_rows = len(df_master)
        total_cols = len(df_master.columns)
        st.markdown(f"""
        <div class="sidebar-status-card">
            <div style="font-weight: 700; color: #f7f3eb; margin-bottom: 0.3rem;">
                <span class="status-dot status-active"></span>Active Dataset Status
            </div>
            <div style="color: var(--accent-copper); font-weight: 600;">{dataset_name}</div>
            <div style="color: var(--text-secondary); margin-top: 0.2rem;">
                • Records: <strong>{total_rows:,}</strong> employees<br>
                • Features: <strong>{total_cols}</strong> attributes<br>
                • Fingerprint: <code>{fingerprint}</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Persistent Model Status Card
        models_trained = st.session_state.get("models_trained", False)
        eval_results = st.session_state.get("eval_results", {})
        model_status_text = "Pending"
        if models_trained and "comparison_df" in eval_results:
            best_m = eval_results.get("best_model_name", "Random Forest")
            best_f1 = eval_results["comparison_df"].iloc[0]["F1_Score"]
            model_status_text = f"{best_m} (F1: {best_f1:.3f})"

        st.markdown(f"""
        <div class="sidebar-status-card" style="margin-top: 0.5rem;">
            <div style="font-weight: 700; color: #f7f3eb; margin-bottom: 0.3rem;">
                <span class="status-dot {'status-active' if models_trained else ''}" style="background-color: {'#4caf50' if models_trained else '#7d756b'};"></span>ML Model Pipeline
            </div>
            <div style="color: {'#81c784' if models_trained else 'var(--text-muted)'}; font-weight: 600;">
                {model_status_text}
            </div>
            <div style="color: var(--text-secondary); margin-top: 0.2rem;">
                • Evaluation: Held-Out 20% Test<br>
                • Baseline Acc: 82.0% (Dummy)
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption(f"{PROJECT_CONTEXT} • Version 1.0.0")

    # Main Canvas Routing
    if "1. Project Overview" in selected_page:
        render_module_overview()

    elif "2. Data Upload & Validation" in selected_page:
        render_module_upload(workbook, fingerprint)

    elif "3. Executive HR Dashboard" in selected_page:
        render_module_dashboard(df_master, eval_results)

    elif "4. Employee Attrition Analysis" in selected_page:
        render_module_analysis(df_master)

    elif "5. Attrition Rate Calculator" in selected_page:
        render_module_calculator(df_master)

    elif "6. Data Cleaning & Feature Eng." in selected_page:
        render_module_preprocessing(df_master)

    elif "7. ML Model Training & Evaluation" in selected_page:
        render_module_training_and_eval(df_master)

    elif "8. Attrition Flight Risk Prediction" in selected_page:
        render_module_prediction(df_master)

    elif "9. Explainability & SHAP" in selected_page:
        render_module_explainability()

    elif "10. Retention Strategy Planner" in selected_page:
        render_module_retention(df_master)

    elif "11. Model History & Registry" in selected_page:
        render_module_experiments()

    elif "12. Reports & Analytical Exports" in selected_page:
        render_module_reports(df_master, dataset_name)

    elif "13. Methodology & Documentation" in selected_page:
        render_module_methodology()


if __name__ == "__main__":
    main()
