"""
Module 11: Retention Strategy Planner & Decision Support.
Translates empirical dataset findings into organizational human capital interventions
with target segments, KPIs, timelines, and financial ROI estimation.
"""
import streamlit as st
import pandas as pd

from src.retention_planner import generate_retention_strategies


def render_module_retention(df_master: pd.DataFrame):
    """Render Module 11: Retention Strategy Planner."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">📋 Strategic Retention Planner & Human Capital Interventions</div>
        <div class="card-subtitle">
            Evidence-grounded organizational interventions directly tied to empirical dataset patterns.
            Designed for HR Business Partners and executive leadership to implement targeted, systemic retention initiatives.
        </div>
    </div>
    """, unsafe_allow_html=True)

    strategies = generate_retention_strategies(df_master)

    tabs = st.tabs(["🏛️ Evidence-Based Strategic Pillars", "💰 Retention ROI & Financial Cost-Benefit Simulator"])

    with tabs[0]:
        st.markdown("#### Strategic Intervention Roadmaps")
        for idx, strat in enumerate(strategies):
            st.markdown(f"""
            <div class="content-card" style="border-left: 4px solid var(--accent-copper); margin-bottom: 1.2rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary);">
                        {idx + 1}. {strat['pillar']}
                    </div>
                    <span class="badge badge-neutral">{strat['target_timeline']} Horizon</span>
                </div>
                <div style="background: #201a17; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 0.8rem; font-size: 0.85rem; border: 1px solid var(--border-subtle);">
                    <strong style="color: #ffb74d;">Empirical Finding from Dataset:</strong> {strat['empirical_evidence']}
                </div>
                <div style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 0.6rem;">
                    <strong>Proposed Organizational Action Plan:</strong> {strat['action_plan']}
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.6rem; font-size: 0.82rem; margin-top: 0.8rem;">
                    <div><strong style="color: var(--accent-copper);">Targeted Departments:</strong> {strat['target_segments']}</div>
                    <div><strong style="color: var(--accent-copper);">Monitoring Metric (KPI):</strong> {strat['primary_kpi']}</div>
                    <div><strong style="color: var(--accent-copper);">Operational Assumption:</strong> {strat['assumptions_and_limits']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tabs[1]:
        st.markdown("#### Retention Intervention Financial ROI Simulator")
        st.markdown("""
        Estimate the financial return on investment (ROI) of proactive retention programs by comparing
        intervention implementation costs against avoided replacement expenses:
        """)

        col_roi1, col_roi2 = st.columns(2)
        with col_roi1:
            n_target_employees = st.slider("Target Segment Employee Cohort Size:", 50, 500, 150, step=25)
            historical_attrition_pct = st.slider("Baseline Cohort Attrition Rate (%):", 10.0, 35.0, 18.5, step=0.5)
            replacement_cost_per_exit = st.number_input("Average Replacement & Onboarding Cost per Exit (INR):", min_value=30000, value=120000, step=10000)

        with col_roi2:
            cost_per_employee_intervention = st.number_input("Intervention Budget Allocated per Employee (INR):", min_value=1000, value=12000, step=1000)
            projected_attrition_reduction_pct = st.slider("Hypothesized Relative Attrition Reduction (%):", 5.0, 50.0, 25.0, step=5.0)

        # Computations
        baseline_exits = (n_target_employees * (historical_attrition_pct / 100.0))
        post_intervention_exits = baseline_exits * (1.0 - (projected_attrition_reduction_pct / 100.0))
        exits_prevented = baseline_exits - post_intervention_exits

        gross_savings = exits_prevented * replacement_cost_per_exit
        program_cost = n_target_employees * cost_per_employee_intervention
        net_financial_benefit = gross_savings - program_cost
        roi_ratio = (net_financial_benefit / program_cost) * 100 if program_cost > 0 else 0.0

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-label">Exits Prevented</div>
                <div class="kpi-value" style="color: #81c784;">{exits_prevented:.1f}</div>
                <div class="kpi-subtext">Baseline: {baseline_exits:.1f} down to {post_intervention_exits:.1f}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Gross Turnover Savings</div>
                <div class="kpi-value">INR {gross_savings:,.0f}</div>
                <div class="kpi-subtext">Avoided recruitment/loss</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Program Investment</div>
                <div class="kpi-value">INR {program_cost:,.0f}</div>
                <div class="kpi-subtext">Total intervention cost</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Net Financial Value</div>
                <div class="kpi-value" style="color: {'#81c784' if net_financial_benefit > 0 else '#e57373'};">
                    INR {net_financial_benefit:,.0f}
                </div>
                <div class="kpi-subtext">ROI: {roi_ratio:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("Note: Financial modeling provides illustrative decision support based on user parameters. Actual savings depend on implementation fidelity.")
