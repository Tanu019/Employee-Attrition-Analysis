"""
Module 3: Executive HR Dashboard.
Interactive workforce KPIs, dynamic multi-dimensional filters, and reactive visual analytics.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config.settings import THEME_COLORS
from src.attrition_analysis import compute_executive_kpis, compute_breakdown_table
from src.chart_utils import apply_theme_layout, create_donut_chart, create_horizontal_bar
from src.data_validation import identify_target_column


def render_module_dashboard(df_master: pd.DataFrame, model_eval_summary: Optional[Dict[str, Any]] = None):
    """Render Module 3: Executive HR Dashboard."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">📊 Executive HR Analytics Dashboard</div>
        <div class="card-subtitle">
            Enterprise overview of workforce stability, attrition distribution, and demographic segmentations.
            All KPIs and charts dynamically synchronize with the interactive filter controls below.
        </div>
    </div>
    """, unsafe_allow_html=True)

    target_col, pos_label = identify_target_column(df_master)
    if not target_col:
        st.error("No valid attrition target column detected in active dataset.")
        return

    # Filter Controls Expandable / Bar
    with st.expander("🎛️ Interactive Workforce Filter Controls", expanded=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)

        with col_f1:
            depts = ["All"] + sorted([str(d) for d in df_master["Department"].dropna().unique()])
            sel_dept = st.selectbox("Department:", depts)

        with col_f2:
            levels = ["All"] + sorted([str(lvl) for lvl in df_master["JobLevel"].dropna().unique()])
            sel_level = st.selectbox("Job Level:", levels)

        with col_f3:
            cities = ["All"] + sorted([str(c) for c in df_master["City"].dropna().unique()]) if "City" in df_master.columns else ["All"]
            sel_city = st.selectbox("City / Location:", cities)

        with col_f4:
            arrangements = ["All"] + sorted([str(a) for a in df_master["WorkArrangement"].dropna().unique()]) if "WorkArrangement" in df_master.columns else ["All"]
            sel_arrangement = st.selectbox("Work Arrangement:", arrangements)

    # Apply filters
    filtered_df = df_master.copy()
    if sel_dept != "All":
        filtered_df = filtered_df[filtered_df["Department"] == sel_dept]
    if sel_level != "All":
        filtered_df = filtered_df[filtered_df["JobLevel"].astype(str) == sel_level]
    if sel_city != "All" and "City" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["City"] == sel_city]
    if sel_arrangement != "All" and "WorkArrangement" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["WorkArrangement"] == sel_arrangement]

    if filtered_df.empty:
        st.warning("No employee records match the selected filter combination. Please broaden your selection.")
        return

    # Compute KPIs on filtered data
    kpis = compute_executive_kpis(filtered_df)

    # Model accuracy metrics if available
    model_acc_str = "Pending"
    model_f1_str = "Pending"
    if model_eval_summary and "comparison_df" in model_eval_summary:
        best_row = model_eval_summary["comparison_df"].iloc[0]
        model_acc_str = f"{best_row['Accuracy']*100:.1f}%"
        model_f1_str = f"{best_row['F1_Score']:.3f}"

    # Render Executive KPI Cards
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Filtered Headcount</div>
            <div class="kpi-value">{kpis['total_employees']:,}</div>
            <div class="kpi-subtext">Active: {kpis['active_employees']:,} | Left: {kpis['exited_employees']:,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Overall Attrition Rate</div>
            <div class="kpi-value" style="color: {'var(--risk-high)' if kpis['attrition_rate_percent'] > 18 else 'var(--accent-copper)'};">
                {kpis['attrition_rate_percent']}%
            </div>
            <div class="kpi-subtext">Voluntary: {kpis['voluntary_attrition_rate_percent'] or 'N/A'}%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Average Monthly Salary</div>
            <div class="kpi-value">INR {kpis['avg_salary_inr']:,.0f}</div>
            <div class="kpi-subtext">Base compensation</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Company Tenure</div>
            <div class="kpi-value">{kpis['avg_tenure_years']} yrs</div>
            <div class="kpi-subtext">Avg age: {kpis['avg_age']} yrs</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Satisfaction</div>
            <div class="kpi-value">{kpis['avg_job_satisfaction']} / 5.0</div>
            <div class="kpi-subtext">Work-Life: {kpis['avg_work_life_balance']} / 5.0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Model Accuracy / F1</div>
            <div class="kpi-value" style="font-size: 1.35rem; color: #81c784;">{model_acc_str}</div>
            <div class="kpi-subtext">Held-out F1: {model_f1_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Row 1 Charts: Attrition Distribution & Department Breakdown
    c1, c2 = st.columns([1, 2])

    with c1:
        # Donut Chart of Status
        val_counts = filtered_df[target_col].value_counts()
        labels = [f"Retained ({val_counts.get('No', val_counts.get('Active', 0))})" ,
                  f"Exited ({val_counts.get('Yes', val_counts.get('Exited', 0))})"]
        values = [val_counts.get('No', val_counts.get('Active', 0)),
                  val_counts.get('Yes', val_counts.get('Exited', 0))]
        fig_donut = create_donut_chart(
            labels=labels,
            values=values,
            title="Workforce Retention Distribution",
            colors=["#3a322c", THEME_COLORS["accent"]]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        # Attrition by Department
        dept_tbl = compute_breakdown_table(filtered_df, "Department")
        if not dept_tbl.empty:
            fig_dept = go.Figure(go.Bar(
                x=dept_tbl["AttritionRatePercent"],
                y=dept_tbl["Department"],
                orientation="h",
                marker=dict(
                    color=dept_tbl["AttritionRatePercent"],
                    colorscale=[[0, "#3a322c"], [1, THEME_COLORS["accent"]]],
                    line=dict(color="#e08369", width=1)
                ),
                text=[f"{r:.1f}% ({e}/{t})" for r, e, t in zip(dept_tbl["AttritionRatePercent"], dept_tbl["ExitedEmployees"], dept_tbl["TotalEmployees"])],
                textposition="outside",
                textfont=dict(size=10, color=THEME_COLORS["text_primary"])
            ))
            fig_dept.update_layout(xaxis_title="Attrition Rate (%)", yaxis=dict(autorange="reversed"))
            fig_dept = apply_theme_layout(fig_dept, title="Attrition Rate by Department (Exits / Total)", height=340)
            st.plotly_chart(fig_dept, use_container_width=True)

    # Row 2 Charts: Overtime & Job Satisfaction
    c3, c4 = st.columns(2)

    with c3:
        if "Overtime" in filtered_df.columns:
            ot_tbl = compute_breakdown_table(filtered_df, "Overtime")
            fig_ot = go.Figure(go.Bar(
                x=ot_tbl["Overtime"],
                y=ot_tbl["AttritionRatePercent"],
                marker=dict(color=[THEME_COLORS["border"], THEME_COLORS["accent"]]),
                text=[f"{r:.1f}% ({e}/{t})" for r, e, t in zip(ot_tbl["AttritionRatePercent"], ot_tbl["ExitedEmployees"], ot_tbl["TotalEmployees"])],
                textposition="outside",
                textfont=dict(size=11, color=THEME_COLORS["text_primary"])
            ))
            fig_ot.update_layout(yaxis_title="Attrition Rate (%)", xaxis_title="Overtime Status")
            fig_ot = apply_theme_layout(fig_ot, title="Attrition Impact: Overtime vs Standard Hours", height=320)
            st.plotly_chart(fig_ot, use_container_width=True)

    with c4:
        if "JobSatisfaction" in filtered_df.columns:
            sat_tbl = compute_breakdown_table(filtered_df, "JobSatisfaction")
            sat_tbl = sat_tbl.sort_values(by="JobSatisfaction")
            fig_sat = go.Figure(go.Bar(
                x=[f"Rating {s}" for s in sat_tbl["JobSatisfaction"]],
                y=sat_tbl["AttritionRatePercent"],
                marker=dict(color=sat_tbl["AttritionRatePercent"], colorscale="Reds_r"),
                text=[f"{r:.1f}%" for r in sat_tbl["AttritionRatePercent"]],
                textposition="outside",
                textfont=dict(size=11, color=THEME_COLORS["text_primary"])
            ))
            fig_sat.update_layout(yaxis_title="Attrition Rate (%)", xaxis_title="Satisfaction Score")
            fig_sat = apply_theme_layout(fig_sat, title="Attrition Rate by Job Satisfaction Score", height=320)
            st.plotly_chart(fig_sat, use_container_width=True)

    # Row 3 Charts: Tenure & Salary Band
    c5, c6 = st.columns(2)

    with c5:
        if "YearsAtCompany" in filtered_df.columns:
            # Create tenure buckets
            filtered_df["TenureBucket"] = pd.cut(
                filtered_df["YearsAtCompany"],
                bins=[-0.1, 1, 2, 4, 10, 50],
                labels=["< 1 Year", "1-2 Years", "2-4 Years", "4-10 Years", "10+ Years"]
            )
            tenure_tbl = compute_breakdown_table(filtered_df, "TenureBucket")
            fig_ten = go.Figure(go.Bar(
                x=tenure_tbl["TenureBucket"].astype(str),
                y=tenure_tbl["AttritionRatePercent"],
                marker=dict(color="#5b8c85"),
                text=[f"{r:.1f}% ({e}/{t})" for r, e, t in zip(tenure_tbl["AttritionRatePercent"], tenure_tbl["ExitedEmployees"], tenure_tbl["TotalEmployees"])],
                textposition="outside",
                textfont=dict(size=11, color=THEME_COLORS["text_primary"])
            ))
            fig_ten.update_layout(yaxis_title="Attrition Rate (%)", xaxis_title="Tenure Band")
            fig_ten = apply_theme_layout(fig_ten, title="Attrition Propensity Across Company Tenure", height=320)
            st.plotly_chart(fig_ten, use_container_width=True)

    with c6:
        if "SalaryBand" in filtered_df.columns:
            sal_tbl = compute_breakdown_table(filtered_df, "SalaryBand")
            fig_sal = go.Figure(go.Bar(
                x=sal_tbl["SalaryBand"],
                y=sal_tbl["AttritionRatePercent"],
                marker=dict(color="#d1a853"),
                text=[f"{r:.1f}%" for r in sal_tbl["AttritionRatePercent"]],
                textposition="outside",
                textfont=dict(size=11, color=THEME_COLORS["text_primary"])
            ))
            fig_sal.update_layout(yaxis_title="Attrition Rate (%)", xaxis_title="Salary Band")
            fig_sal = apply_theme_layout(fig_sal, title="Attrition Rate Across Compensation Bands", height=320)
            st.plotly_chart(fig_sal, use_container_width=True)
