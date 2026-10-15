"""
Module 9: Individual Employee Flight Risk Prediction & Batch Scoring.
Interactive decision support form, risk categorization, and tailored support recommendations.
"""
import streamlit as st
import pandas as pd
import json

from config.settings import THEME_COLORS
from src.prediction import predict_single_employee, predict_batch_employees


def render_module_prediction(df_master: pd.DataFrame):
    """Render Module 9: Attrition Prediction."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">🔮 Employee Flight Risk Prediction Engine</div>
        <div class="card-subtitle">
            Simulate or evaluate an employee profile using the trained machine learning pipeline.
            Estimates attrition risk probability, assigns actionable risk tiers, and recommends organizational retention measures.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "training_artifacts" not in st.session_state or not st.session_state.get("models_trained"):
        st.warning("⚠️ Machine learning models have not yet been trained. Please visit Module 7 & 8 to initialize pipelines.")
        return

    artifacts = st.session_state["training_artifacts"]
    eval_results = st.session_state.get("eval_results", {})
    best_model_name = eval_results.get("best_model_name", "Random Forest")
    pipelines = artifacts["trained_pipelines"]

    tabs = st.tabs(["👤 Individual Employee Simulation", "📁 Batch Employee Scoring (CSV)"])

    with tabs[0]:
        st.markdown("#### Configure Employee Profile Parameters")

        # Select inference model
        col_m, col_sample = st.columns([2, 2])
        with col_m:
            chosen_model_name = st.selectbox(
                "Prediction Model Pipeline:",
                [m for m in pipelines.keys() if m != "Dummy (Baseline)"],
                index=list([m for m in pipelines.keys() if m != "Dummy (Baseline)"]).index(best_model_name)
                if best_model_name in pipelines else 0
            )
        with col_sample:
            st.caption("Tip: Select an actual sample employee profile from the dataset to prefill inputs:")
            sample_ids = ["Custom Input"] + df_master["EmployeeID"].head(10).tolist()
            sel_sample = st.selectbox("Load Sample Profile:", sample_ids)

        # Build default profile
        sample_row = None
        if sel_sample != "Custom Input":
            sample_row = df_master[df_master["EmployeeID"] == sel_sample].iloc[0]

        with st.form("employee_prediction_form"):
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown("**1. Role & Organization**")
                depts = sorted(df_master["Department"].dropna().unique().tolist())
                dept_val = sample_row["Department"] if sample_row is not None else depts[0]
                dept = st.selectbox("Department:", depts, index=depts.index(dept_val) if dept_val in depts else 0)

                roles = sorted(df_master[df_master["Department"] == dept]["JobRole"].dropna().unique().tolist())
                if not roles:
                    roles = sorted(df_master["JobRole"].dropna().unique().tolist())
                role_val = sample_row["JobRole"] if sample_row is not None and sample_row["JobRole"] in roles else roles[0]
                job_role = st.selectbox("Job Role:", roles, index=roles.index(role_val) if role_val in roles else 0)

                job_level = st.slider("Job Level:", 1, 5, int(sample_row["JobLevel"]) if sample_row is not None else 2)
                bus_unit = st.selectbox("Business Unit:", ["B2C Quick Commerce", "B2B Enterprise", "Central Corporate"])
                work_loc = st.selectbox("Work Location:", ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Pune", "Ahmedabad", "Nashik"])
                work_arr = st.selectbox("Work Arrangement:", ["On-site", "Hybrid", "Remote"])

            with c2:
                st.markdown("**2. Compensation & Workload**")
                monthly_salary = st.number_input(
                    "Monthly Salary (INR):",
                    min_value=15000, max_value=250000,
                    value=int(sample_row["MonthlySalaryINR"]) if sample_row is not None else 42000,
                    step=2500
                )
                overtime = st.selectbox("Works Overtime?:", ["No", "Yes"], index=1 if sample_row is not None and str(sample_row["Overtime"]).lower() == "yes" else 0)
                ot_hours = st.slider("Monthly Overtime Hours:", 0, 80, int(sample_row["OvertimeHoursMonthly"]) if sample_row is not None else (15 if overtime == "Yes" else 0))
                workload_score = st.slider("Average Workload Score (1-5):", 1, 5, int(sample_row["AverageWorkloadScore"]) if sample_row is not None else 3)
                burnout_score = st.slider("Burnout Risk Score (0-100):", 0, 100, int(sample_row["BurnoutRiskScore"]) if sample_row is not None else 48)
                daily_hours = st.number_input("Daily Working Hours:", min_value=6.0, max_value=14.0, value=float(sample_row["DailyWorkingHours"]) if sample_row is not None else 8.5, step=0.5)

            with c3:
                st.markdown("**3. Satisfaction & Tenure**")
                job_sat = st.slider("Job Satisfaction (1-5):", 1, 5, int(sample_row["JobSatisfaction"]) if sample_row is not None else 3)
                wlb = st.slider("Work-Life Balance (1-5):", 1, 5, int(sample_row["WorkLifeBalance"]) if sample_row is not None else 3)
                mgr_rel = st.slider("Relationship With Manager (1-5):", 1, 5, int(sample_row["RelationshipWithManager"]) if sample_row is not None else 3)
                comp_sat = st.slider("Compensation Satisfaction (1-5):", 1, 5, int(sample_row["CompensationSatisfaction"]) if sample_row is not None else 3)
                years_co = st.number_input("Years at Company:", min_value=0.0, max_value=40.0, value=float(sample_row["YearsAtCompany"]) if sample_row is not None else 2.5, step=0.5)
                years_promo = st.number_input("Years Since Last Promotion:", min_value=0.0, max_value=15.0, value=float(sample_row["YearsSinceLastPromotion"]) if sample_row is not None else 1.2, step=0.5)
                engagement = st.slider("Employee Engagement Score (0-100):", 0, 100, int(sample_row["EmployeeEngagementScore"]) if sample_row is not None else 65)

            submitted = st.form_submit_button("⚡ Predict Flight Risk", type="primary")

        if submitted:
            # Build feature dictionary matching dataset schema
            input_features = {
                "Department": dept,
                "BusinessUnit": bus_unit,
                "JobRole": job_role,
                "JobLevel": job_level,
                "EmploymentType": "Full Time",
                "WorkLocation": work_loc,
                "City": work_loc,
                "State": "Maharashtra" if work_loc in ["Mumbai", "Pune", "Nashik"] else "Karnataka",
                "EducationLevel": "Bachelor's Degree",
                "EducationField": "Engineering",
                "TotalWorkExperienceYears": int(years_co + 2),
                "PreviousCompanies": 1,
                "DistanceFromHomeKm": 12.0,
                "WorkArrangement": work_arr,
                "MonthlySalaryINR": monthly_salary,
                "SalaryBand": "Mid",
                "SalaryHikePercent": 10.0,
                "BonusPercent": 8.0,
                "Overtime": overtime,
                "BenefitsSatisfaction": 3,
                "CompensationSatisfaction": comp_sat,
                "PromotionLastFiveYears": "Yes" if years_promo <= 5 else "No",
                "YearsSinceLastPromotion": years_promo,
                "DailyWorkingHours": daily_hours,
                "WeeklyWorkingHours": daily_hours * 5,
                "OvertimeHoursMonthly": ot_hours,
                "ProjectsHandled": 4,
                "AverageWorkloadScore": workload_score,
                "PerformanceRating": 3,
                "ProductivityScore": 75,
                "AbsenteeismDaysLastYear": 4,
                "LateArrivalsLastMonth": 1,
                "ManagerRating": 3,
                "JobSatisfaction": job_sat,
                "EnvironmentSatisfaction": 3,
                "WorkLifeBalance": wlb,
                "RelationshipWithManager": mgr_rel,
                "PeerRelationshipScore": 3,
                "CareerGrowthSatisfaction": 3,
                "RecognitionSatisfaction": 3,
                "EmployeeEngagementScore": engagement,
                "StressLevel": 3 if burnout_score < 60 else 4,
                "BurnoutRiskScore": burnout_score,
                "IntentToLeaveScore": int(burnout_score * 0.8),
                "YearsAtCompany": years_co,
                "YearsInCurrentRole": min(years_co, 1.5),
                "YearsWithCurrentManager": min(years_co, 1.5),
                "InternalTransfers": 0,
                "TrainingHoursLastYear": 24,
                "CertificationsCompleted": 1,
                "CareerDevelopmentParticipation": "Yes",
                "RecruitmentSource": "LinkedIn",
                "RecruitmentCostINR": 25000,
                "TimeToFillDays": 30,
                "OnboardingSatisfaction": 4,
                "ReferralHire": "No"
            }

            pipe = pipelines[chosen_model_name]
            pred_res = predict_single_employee(pipe, input_features, model_name=chosen_model_name)

            # Display prediction results card
            st.markdown(f"""
            <div class="content-card" style="border-top: 4px solid {'#d32f2f' if pred_res['risk_band'] in ['High Risk', 'Critical Risk'] else ('#f57c00' if pred_res['risk_band'] == 'Moderate Risk' else '#388e3c')};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                    <div>
                        <span class="badge {pred_res['badge_class']}">{pred_res['risk_band']}</span>
                        <span style="font-size: 0.85rem; color: var(--text-muted); margin-left: 0.5rem;">Pipeline: {chosen_model_name}</span>
                    </div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: var(--text-primary);">
                        {pred_res['probability_percent']}% <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 400;">Attrition Probability</span>
                    </div>
                </div>
                <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">
                    Classification: {pred_res['predicted_label']}
                </div>
                <div style="color: var(--text-secondary); font-size: 0.84rem; line-height: 1.5;">
                    {pred_res['disclaimer']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown("##### 🔍 Key Risk Factors Driving This Score")
                if pred_res["contributing_factors"]:
                    for factor in pred_res["contributing_factors"]:
                        color = "#e57373" if factor["impact"] == "Increases Risk" else "#81c784"
                        st.markdown(f"- <strong style='color:{color};'>{factor['factor']}</strong>: `{factor['value']}` ({factor['impact']})", unsafe_allow_html=True)
                else:
                    st.info("No single extreme factor observed; baseline demographic and tenure patterns apply.")

            with col_res2:
                st.markdown("##### 💡 Recommended Organizational Interventions")
                for action in pred_res["suggested_actions"]:
                    st.markdown(f"- {action}")

            # Download single prediction summary
            json_str = json.dumps(pred_res, indent=2, default=str)
            st.download_button(
                "📥 Download Prediction Summary (JSON)",
                data=json_str,
                file_name=f"attrition_prediction_{dept.replace(' ', '_')}_{job_role.replace(' ', '_')}.json",
                mime="application/json"
            )

    with tabs[1]:
        st.markdown("#### Batch Employee Scoring Engine")
        st.caption("Upload a roster of employees in CSV format to compute attrition risk probabilities for all personnel.")

        batch_file = st.file_uploader("Upload Roster CSV for Scoring:", type=["csv"])
        if batch_file is not None:
            batch_df = pd.read_csv(batch_file)
            st.write(f"Loaded {len(batch_df)} employee records. Running inference with `{best_model_name}`...")
            scored_df = predict_batch_employees(pipelines[best_model_name], batch_df)
            st.dataframe(scored_df[["Predicted_Attrition", "Predicted_Probability", "Risk_Band"] + [c for c in scored_df.columns if c not in ["Predicted_Attrition", "Predicted_Probability", "Risk_Band"]]].head(20), use_container_width=True)

            csv_batch = scored_df.to_csv(index=False)
            st.download_button(
                "📥 Download Scored Employee Roster (CSV)",
                data=csv_batch,
                file_name="batch_scored_attrition_roster.csv",
                mime="text/csv"
            )
        else:
            st.info("Download a sample template from Module 2 or test batch scoring using the active dataset.")
