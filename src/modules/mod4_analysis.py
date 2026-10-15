"""
Module 4: Deep Employee Attrition Exploratory Analysis.
Provides diagnostic breakdowns, stayer-vs-leaver comparisons, statistical correlation matrices,
and dynamically computed data-driven findings.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config.settings import THEME_COLORS
from src.attrition_analysis import (
    compute_breakdown_table,
    compute_stayers_vs_leavers,
    compute_correlations_with_target,
    generate_data_driven_insights
)
from src.chart_utils import apply_theme_layout
from src.data_validation import identify_target_column


def render_module_analysis(df_master: pd.DataFrame):
    """Render Module 4: Employee Attrition Analysis."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">🔬 Deep Empirical Attrition Analysis</div>
        <div class="card-subtitle">
            Multivariate diagnostic exploration into organizational drivers, stayer-vs-leaver central tendencies,
            correlation structures, and calculated analytical insights.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="callout-box callout-warning">
        <strong>⚠️ Crucial Methodological Principle:</strong> Statistical correlation does <em>not</em> imply causation.
        Observed correlations quantify historical co-occurrence between employee attributes and exits. They identify
        operational friction points for empathetic HR investigation rather than deterministic individual causes.
    </div>
    """, unsafe_allow_html=True)

    target_col, pos_label = identify_target_column(df_master)
    if not target_col:
        st.error("No valid attrition target column found.")
        return

    # Section 1: Dynamically Derived Insights
    st.markdown("### 💡 Automatically Calculated Empirical Insights")
    insights = generate_data_driven_insights(df_master)
    col_ins1, col_ins2 = st.columns(2)
    for idx, ins in enumerate(insights):
        col = col_ins1 if idx % 2 == 0 else col_ins2
        with col:
            st.markdown(f"""
            <div style="background-color: var(--bg-card); border-left: 3px solid var(--accent-copper); padding: 0.9rem 1.1rem; border-radius: 4px; margin-bottom: 0.8rem; border-top: 1px solid var(--border-subtle); border-right: 1px solid var(--border-subtle); border-bottom: 1px solid var(--border-subtle);">
                <div style="font-weight: 700; color: var(--accent-copper); font-size: 0.88rem; margin-bottom: 0.3rem;">{ins['category']}</div>
                <div style="color: var(--text-primary); font-size: 0.84rem; line-height: 1.5; margin-bottom: 0.4rem;">{ins['finding']}</div>
                <div style="color: var(--text-secondary); font-size: 0.78rem;"><strong>Action:</strong> {ins['action']}</div>
            </div>
            """, unsafe_allow_html=True)

    tabs = st.tabs([
        "⚖️ Stayers vs Leavers Comparison",
        "📈 Correlation Analysis",
        "🏢 Department & Job Roles",
        "⏳ Tenure & Progression",
        "⏱️ Workload & Burnout"
    ])

    with tabs[0]:
        st.markdown("#### Comparative Central Tendencies: Retained vs Exited Personnel")
        st.markdown("This audit compares average attribute metrics between employees who remained versus those who exited:")
        stayers_leavers_df = compute_stayers_vs_leavers(df_master)
        st.dataframe(stayers_leavers_df, use_container_width=True, height=420)

    with tabs[1]:
        st.markdown("#### Statistical Pearson Correlations with Attrition Target")
        corrs_df = compute_correlations_with_target(df_master)
        
        c_chart, c_table = st.columns([3, 2])
        with c_chart:
            # Bar chart of top 12 correlations
            top_corrs = corrs_df.head(12)
            fig_corr = go.Figure(go.Bar(
                x=top_corrs["Correlation"],
                y=top_corrs["Feature"],
                orientation="h",
                marker=dict(
                    color=top_corrs["Correlation"],
                    colorscale="RdBu_r",
                    cmin=-0.3,
                    cmax=0.3
                ),
                text=[f"{v:+.3f}" for v in top_corrs["Correlation"]],
                textposition="outside",
                textfont=dict(size=10, color=THEME_COLORS["text_primary"])
            ))
            fig_corr.update_layout(xaxis_title="Pearson Correlation Coefficient", yaxis=dict(autorange="reversed"))
            fig_corr = apply_theme_layout(fig_corr, title="Top Predictive Metric Correlations", height=380)
            st.plotly_chart(fig_corr, use_container_width=True)

        with c_table:
            st.dataframe(corrs_df, use_container_width=True, height=380)

    with tabs[2]:
        st.markdown("#### Department & Job Role Granular Breakdown")
        col_role1, col_role2 = st.columns(2)
        with col_role1:
            dept_tbl = compute_breakdown_table(df_master, "Department")
            st.dataframe(dept_tbl, use_container_width=True)
        with col_role2:
            if "JobRole" in df_master.columns:
                role_tbl = compute_breakdown_table(df_master, "JobRole").head(10)
                fig_role = go.Figure(go.Bar(
                    x=role_tbl["AttritionRatePercent"],
                    y=role_tbl["JobRole"],
                    orientation="h",
                    marker=dict(color=THEME_COLORS["accent"]),
                    text=[f"{r:.1f}% ({e}/{t})" for r, e, t in zip(role_tbl["AttritionRatePercent"], role_tbl["ExitedEmployees"], role_tbl["TotalEmployees"])],
                    textposition="outside"
                ))
                fig_role.update_layout(xaxis_title="Attrition Rate (%)", yaxis=dict(autorange="reversed"))
                fig_role = apply_theme_layout(fig_role, title="Top 10 High-Attrition Job Roles", height=380)
                st.plotly_chart(fig_role, use_container_width=True)

    with tabs[3]:
        st.markdown("#### Organizational Tenure & Promotion Velocity")
        if "YearsSinceLastPromotion" in df_master.columns and "YearsAtCompany" in df_master.columns:
            fig_scatter = px.scatter(
                df_master.sample(min(800, len(df_master)), random_state=42),
                x="YearsAtCompany",
                y="YearsSinceLastPromotion",
                color=target_col,
                color_discrete_map={"No": "#3a322c", "Yes": THEME_COLORS["accent"], "Active": "#3a322c", "Exited": THEME_COLORS["accent"]},
                opacity=0.7,
                title="Tenure vs Years Since Last Promotion"
            )
            fig_scatter = apply_theme_layout(fig_scatter, title="Tenure vs Promotion Stagnation (Leavers Highlighted in Copper)", height=380)
            st.plotly_chart(fig_scatter, use_container_width=True)

    with tabs[4]:
        st.markdown("#### Workload Stress vs Burnout Risk Distribution")
        if "AverageWorkloadScore" in df_master.columns and "BurnoutRiskScore" in df_master.columns:
            fig_box = px.box(
                df_master,
                x=target_col,
                y="BurnoutRiskScore",
                color=target_col,
                color_discrete_map={"No": "#3a322c", "Yes": THEME_COLORS["accent"], "Active": "#3a322c", "Exited": THEME_COLORS["accent"]},
                points="outliers"
            )
            fig_box = apply_theme_layout(fig_box, title="Burnout Risk Score Distribution: Retained vs Exited", height=360)
            st.plotly_chart(fig_box, use_container_width=True)
