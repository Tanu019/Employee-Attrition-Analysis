"""
Module 13: Executive Reports & Analytical Exports.
Generates MBA-grade markdown/HTML reports, data quality summaries,
and raw tabular data export bundles.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from src.reporting import generate_executive_markdown_report
from src.attrition_analysis import compute_executive_kpis, generate_data_driven_insights
from src.retention_planner import generate_retention_strategies
from src.database import get_prediction_history


def render_module_reports(df_master: pd.DataFrame, dataset_name: str = "SnackRush_Complete_Dataset.xlsx"):
    """Render Module 13: Reports and Exports."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">📑 Executive Reports & Analytical Export Center</div>
        <div class="card-subtitle">
            Generate and export MBA Business Analytics executive briefings, data quality reports,
            model performance tables, and logged prediction audits.
        </div>
    </div>
    """, unsafe_allow_html=True)

    kpi_dict = compute_executive_kpis(df_master)
    insights = generate_data_driven_insights(df_master)
    strategies = generate_retention_strategies(df_master)
    eval_results = st.session_state.get("eval_results")

    tabs = st.tabs([
        "📄 Executive Briefing Report",
        "📊 Raw Data & Export Bundles",
        "📋 Model Prediction Audit Trail"
    ])

    with tabs[0]:
        st.markdown("#### Comprehensive Executive Briefing Preview")
        md_content = generate_executive_markdown_report(
            kpi_dict=kpi_dict,
            model_eval_dict=eval_results,
            insights=insights,
            strategies=strategies,
            dataset_name=dataset_name
        )

        st.markdown(md_content)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                "📥 Download Executive Report (Markdown .md)",
                data=md_content,
                file_name=f"executive_attrition_report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
        with col_d2:
            html_content = f"<html><head><title>Executive HR Report</title><style>body{{font-family:sans-serif;padding:2rem;line-height:1.6;}}</style></head><body><pre>{md_content}</pre></body></html>"
            st.download_button(
                "📥 Download Executive Report (HTML .html)",
                data=html_content,
                file_name=f"executive_attrition_report_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html"
            )

    with tabs[1]:
        st.markdown("#### Analytical Dataset Exports")
        st.write("Export verified datasets for external reporting or auditing:")

        c1, c2, c3 = st.columns(3)
        with c1:
            csv_master = df_master.to_csv(index=False)
            st.download_button(
                "📥 Export Active Employee Master (CSV)",
                data=csv_master,
                file_name="employee_master_export.csv",
                mime="text/csv"
            )
        with c2:
            if eval_results and "comparison_df" in eval_results:
                csv_models = eval_results["comparison_df"].to_csv(index=False)
                st.download_button(
                    "📥 Export Model Evaluation Benchmark (CSV)",
                    data=csv_models,
                    file_name="model_evaluation_metrics.csv",
                    mime="text/csv"
                )
            else:
                st.info("Train models to export metrics.")
        with c3:
            strat_df = pd.DataFrame(strategies)
            csv_strat = strat_df.to_csv(index=False)
            st.download_button(
                "📥 Export Retention Roadmaps (CSV)",
                data=csv_strat,
                file_name="retention_strategy_roadmaps.csv",
                mime="text/csv"
            )

    with tabs[2]:
        st.markdown("#### Auditable Prediction Log (SQLite Persistence)")
        pred_history = get_prediction_history()
        if not pred_history.empty:
            st.dataframe(pred_history, use_container_width=True, height=350)
            csv_pred = pred_history.to_csv(index=False)
            st.download_button(
                "📥 Export Prediction History (CSV)",
                data=csv_pred,
                file_name="employee_prediction_audit_history.csv",
                mime="text/csv"
            )
        else:
            st.info("No individual employee predictions have been logged yet. Run predictions in Module 9.")
