"""
Module 12: Model Comparison and Experiment Tracking History.
Retrieves and compares historical model runs stored in the persistent SQLite database.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.settings import THEME_COLORS
from src.database import get_all_experiments
from src.chart_utils import apply_theme_layout


def render_module_experiments():
    """Render Module 12: Model Comparison and Experiment History."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">📜 Machine Learning Experiment History & Registry</div>
        <div class="card-subtitle">
            Auditable tracking repository backed by persistent SQLite storage.
            Every training run, cross-validation baseline, held-out test metric, and dataset fingerprint is permanently registered.
        </div>
    </div>
    """, unsafe_allow_html=True)

    exp_df = get_all_experiments()

    if exp_df.empty:
        st.info("No prior experiment records logged. Visit Modules 7 & 8 to execute and register model evaluations.")
        return

    st.markdown(f"**Logged Experiment Records:** {len(exp_df)} runs recorded.")

    # Format dataframe columns
    display_cols = [
        "experiment_id", "timestamp", "model_name", "dataset_name",
        "test_accuracy", "test_precision", "test_recall", "test_f1",
        "test_roc_auc", "test_pr_auc", "is_selected"
    ]
    avail_cols = [c for c in display_cols if c in exp_df.columns]
    
    st.dataframe(
        exp_df[avail_cols].style.format({
            "test_accuracy": "{:.4f}",
            "test_precision": "{:.4f}",
            "test_recall": "{:.4f}",
            "test_f1": "{:.4f}",
            "test_roc_auc": "{:.4f}",
            "test_pr_auc": "{:.4f}"
        }),
        use_container_width=True,
        height=350
    )

    # Chart comparing test F1 and Recall across models
    if "test_f1" in exp_df.columns and "test_recall" in exp_df.columns:
        fig_exp = px.scatter(
            exp_df,
            x="test_recall",
            y="test_precision",
            size="test_f1",
            color="model_name",
            hover_name="experiment_id",
            hover_data=["test_accuracy", "test_roc_auc"],
            title="Precision vs Recall Trade-Off Across Historical Experiments"
        )
        fig_exp = apply_theme_layout(fig_exp, title="Model Registry: Precision vs Recall Frontier", height=380)
        st.plotly_chart(fig_exp, use_container_width=True)

    # Download CSV of experiments
    csv_exp = exp_df.to_csv(index=False)
    st.download_button(
        "📥 Export Complete Experiment History (CSV)",
        data=csv_exp,
        file_name="model_experiments_registry.csv",
        mime="text/csv"
    )
