"""
Module 5: Attrition Rate Calculator.
Provides transparent workforce attrition rate computation using standard HR formulas,
supporting both historical date-derived calculation and user-provided manual entry.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date

from src.attrition_calculator import calculate_attrition_metrics, derive_headcount_from_dates


def render_module_calculator(df_master: pd.DataFrame):
    """Render Module 5: Attrition Rate Calculator."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">🧮 Standard Workforce Attrition Rate Calculator</div>
        <div class="card-subtitle">
            Enterprise headcount-based rate calculations conforming to recognized Human Resources analytics standards.
            Supports date-based automatic derivation from employee records or authorized manual entry.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="callout-box">
        <strong>Standard HR Metric Definition:</strong><br>
        • <strong>Average Headcount:</strong> <code>(Opening Headcount + Closing Headcount) / 2</code><br>
        • <strong>Attrition Rate (%):</strong> <code>(Total Exits During Reporting Period / Average Headcount) × 100</code><br>
        • <strong>Voluntary Attrition Rate (%):</strong> <code>(Voluntary Resignations / Average Headcount) × 100</code>
    </div>
    """, unsafe_allow_html=True)

    calc_mode = st.radio(
        "Select Calculation Mode:",
        ["📅 Date-Driven Derivation (from Active Dataset)", "✍️ Manual Parameter Entry Mode"],
        horizontal=True
    )

    if calc_mode == "📅 Date-Driven Derivation (from Active Dataset)":
        if "JoiningDate" not in df_master.columns:
            st.error("The current dataset lacks a 'JoiningDate' field required for automated headcount derivation.")
            return

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            depts = ["All Departments"] + sorted([str(d) for d in df_master["Department"].dropna().unique()])
            sel_dept = st.selectbox("Department Filter:", depts)

        # Date boundaries
        min_date = pd.to_datetime(df_master["JoiningDate"]).min().date()
        max_date = pd.to_datetime(df_master["ObservationDate"]).max().date() if "ObservationDate" in df_master.columns else date.today()

        with col_d2:
            start_date = st.date_input("Period Start Date:", value=date(2025, 1, 1), min_value=min_date, max_value=max_date)
        with col_d3:
            end_date = st.date_input("Period End Date:", value=date(2026, 9, 30), min_value=min_date, max_value=max_date)

        if start_date >= end_date:
            st.error("Period Start Date must strictly precede Period End Date.")
            return

        try:
            results = derive_headcount_from_dates(
                df=df_master,
                start_date=pd.Timestamp(start_date),
                end_date=pd.Timestamp(end_date),
                department=sel_dept
            )
            display_calculator_results(results, mode_label=f"Dataset Derived ({sel_dept})")
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")

    else:
        st.markdown("#### User-Provided Manual Workforce Entry")
        st.caption("Inputs entered in this section are user-provided assumptions and do not alter the underlying dataset.")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            opening_hc = st.number_input("Opening Headcount (Start of Period):", min_value=1, value=2500, step=10)
            closing_hc = st.number_input("Closing Headcount (End of Period):", min_value=1, value=2050, step=10)
            new_hires = st.number_input("New Hires Onboarded During Period (Optional):", min_value=0, value=0, step=5)

        with col_m2:
            total_exits = st.number_input("Total Departures / Exits During Period:", min_value=0, value=450, step=5)
            voluntary_exits = st.number_input("Voluntary Exits (Resignations):", min_value=0, value=370, step=5)
            involuntary_exits = st.number_input("Involuntary Exits (Separations / Terminations):", min_value=0, value=80, step=5)

        if st.button("Calculate Workforce Metrics", type="primary"):
            if voluntary_exits + involuntary_exits > total_exits:
                st.warning("Note: Sum of voluntary and involuntary exits exceeds total exits. Please verify inputs.")

            try:
                results = calculate_attrition_metrics(
                    opening_headcount=opening_hc,
                    closing_headcount=closing_hc,
                    total_exits=total_exits,
                    voluntary_exits=voluntary_exits,
                    involuntary_exits=involuntary_exits,
                    new_hires=new_hires if new_hires > 0 else None
                )
                display_calculator_results(results, mode_label="User Manual Entry")
            except Exception as e:
                st.error(f"Input validation error: {str(e)}")


def display_calculator_results(res: Dict[str, Any], mode_label: str):
    """Render structured metrics and step-by-step mathematical breakdown."""
    st.markdown(f"### 📋 Calculation Summary: {mode_label}")

    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Average Headcount</div>
            <div class="kpi-value">{res['average_headcount']:,}</div>
            <div class="kpi-subtext">Opening: {res['opening_headcount']:.0f} | Closing: {res['closing_headcount']:.0f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Total Attrition Rate</div>
            <div class="kpi-value" style="color: var(--accent-copper);">{res['attrition_rate_percent']}%</div>
            <div class="kpi-subtext">{res['total_exits']} total exits recorded</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Voluntary Attrition Rate</div>
            <div class="kpi-value">{res['voluntary_attrition_rate_percent'] or 'N/A'}%</div>
            <div class="kpi-subtext">{res['voluntary_exits'] or 0} voluntary exits</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Involuntary Rate</div>
            <div class="kpi-value">{res['involuntary_attrition_rate_percent'] or 'N/A'}%</div>
            <div class="kpi-subtext">{res['involuntary_exits'] or 0} terminations</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Workforce Retention Rate</div>
            <div class="kpi-value" style="color: #81c784;">{res['retention_rate_percent']}%</div>
            <div class="kpi-subtext">Retained capacity ratio</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-card">
        <div class="card-title">📝 Transparent Mathematical Verification Steps</div>
    """, unsafe_allow_html=True)
    for step in res["calculation_steps"]:
        st.markdown(f"- `{step}`")
    st.markdown("</div>", unsafe_allow_html=True)
