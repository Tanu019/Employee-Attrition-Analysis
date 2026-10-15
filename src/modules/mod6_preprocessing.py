"""
Module 6: Data Cleaning & Feature Engineering.
Documents preprocessing steps, outlier audits, domain feature derivations,
and strict data leakage prevention protocols.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from config.settings import LEAKAGE_AND_POST_EXIT_COLUMNS, SENSITIVE_DEMOGRAPHIC_COLUMNS
from src.preprocessing import prepare_features_and_target, build_preprocessor_pipeline
from src.feature_engineering import engineer_hr_features
from src.chart_utils import apply_theme_layout


def render_module_preprocessing(df_master: pd.DataFrame):
    """Render Module 6: Data Cleaning and Feature Engineering."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">⚙️ Preprocessing, Feature Engineering & Leakage Prevention</div>
        <div class="card-subtitle">
            A reproducible, scikit-learn pipeline transforming raw workforce data into model-ready features
            while rigorously enforcing operational cutoff boundaries.
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "🛡️ Data Leakage Prevention Protocol",
        "🔬 Engineered Domain Features",
        "📊 Outlier Inspection & Robust Scaling",
        "🔄 Pipeline Before & After Audit"
    ])

    with tabs[0]:
        st.markdown("#### Strict Leakage Prevention & Ethical Exclusion Criteria")
        st.markdown("""
        To prevent artificially inflated model accuracy and ensure operational realism, every attribute
        recorded *after* an employee's decision to exit is permanently excluded from model training.
        """)

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.markdown("##### 🚫 Excluded Post-Outcome & Identifier Columns")
            leak_records = []
            for col in LEAKAGE_AND_POST_EXIT_COLUMNS:
                exists = col in df_master.columns
                reason = "Post-exit recording / Outcome synonym" if col != "EmployeeID" else "Non-predictive identifier"
                if col == "ProbationCompleted":
                    reason = "Zero variance (constant across all records)"
                elif col == "AnnualSalaryINR":
                    reason = "Exact collinear replica of MonthlySalaryINR (12x)"
                leak_records.append({"Column Name": col, "Present in Dataset": "Yes" if exists else "No", "Exclusion Rationale": reason})
            st.dataframe(pd.DataFrame(leak_records), use_container_width=True)

        with col_l2:
            st.markdown("##### ⚖️ Governed Sensitive Demographics")
            st.markdown("""
            In compliance with ethical AI standards for HR decision systems, protected demographic attributes
            are excluded from operational prediction features to prevent proxy discrimination:
            """)
            dem_records = []
            for col in SENSITIVE_DEMOGRAPHIC_COLUMNS:
                dem_records.append({
                    "Protected Attribute": col,
                    "Policy": "Excluded from predictive feature matrix; retained strictly for fairness auditing."
                })
            st.dataframe(pd.DataFrame(dem_records), use_container_width=True)

    with tabs[1]:
        st.markdown("#### HR Domain-Engineered Features")
        st.markdown("We derive composite behavioral indicators grounded in organizational psychology research:")
        
        feat_df = engineer_hr_features(df_master)
        engineered_cols = [
            "OvertimeRatio", "SalaryPerExpYear", "WorkloadBalanceIndex",
            "CompositeSatisfactionScore", "RoleTenureRatio", "ManagerTenureRatio"
        ]
        present_eng = [c for c in engineered_cols if c in feat_df.columns]

        if present_eng:
            st.dataframe(feat_df[present_eng].describe().round(3).T, use_container_width=True)
            
            sel_eng = st.selectbox("Inspect Feature Distribution:", present_eng)
            fig_hist = px.histogram(
                feat_df,
                x=sel_eng,
                nbins=35,
                color="Attrition" if "Attrition" in feat_df.columns else None,
                color_discrete_map={"No": "#3a322c", "Yes": "#c86d51"},
                title=f"Distribution of {sel_eng}"
            )
            fig_hist = apply_theme_layout(fig_hist, title=f"Engineered Metric Distribution: {sel_eng}", height=320)
            st.plotly_chart(fig_hist, use_container_width=True)

    with tabs[2]:
        st.markdown("#### Outlier Analysis (IQR Method)")
        st.markdown("""
        In workforce analytics, high salaries or long working hours represent valid enterprise variance, not measurement errors.
        Rather than deleting valid outliers, we audit them and apply robust scaling:
        """)

        num_cols = df_master.select_dtypes(include=[np.number]).columns
        clean_num_cols = [c for c in num_cols if not c.lower().endswith("id") and c != "AnnualSalaryINR"]

        outlier_records = []
        for c in clean_num_cols[:12]:
            q25 = df_master[c].quantile(0.25)
            q75 = df_master[c].quantile(0.75)
            iqr = q75 - q25
            lower_bound = q25 - (1.5 * iqr)
            upper_bound = q75 + (1.5 * iqr)
            n_outliers = int(((df_master[c] < lower_bound) | (df_master[c] > upper_bound)).sum())
            pct_outliers = round((n_outliers / len(df_master)) * 100, 2)
            outlier_records.append({
                "Feature": c,
                "Q25": round(q25, 2),
                "Median": round(df_master[c].median(), 2),
                "Q75": round(q75, 2),
                "IQR": round(iqr, 2),
                "Outlier Count": n_outliers,
                "Outlier %": f"{pct_outliers}%"
            })
        st.dataframe(pd.DataFrame(outlier_records), use_container_width=True)

    with tabs[3]:
        st.markdown("#### Before and After Preprocessing Pipeline Audit")
        X, y, num_f, cat_f = prepare_features_and_target(df_master)
        preprocessor = build_preprocessor_pipeline(num_f, cat_f)
        X_trans = preprocessor.fit_transform(X)

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-label">Raw Dataset Columns</div>
                <div class="kpi-value">{len(df_master.columns)}</div>
                <div class="kpi-subtext">Original sheet attributes</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Retained Predictors</div>
                <div class="kpi-value">{len(X.columns)}</div>
                <div class="kpi-subtext">{len(num_f)} numeric, {len(cat_f)} categorical</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">One-Hot Encoded Dim</div>
                <div class="kpi-value">{X_trans.shape[1]}</div>
                <div class="kpi-subtext">Transformed model matrix</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Target Balance</div>
                <div class="kpi-value">{y.mean()*100:.1f}%</div>
                <div class="kpi-subtext">{y.sum()} positive (Attrition)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.info("The fitted ColumnTransformer pipeline is serialized and reapplied during single employee predictions and batch scoring.")
