"""
Module 14: Academic Methodology & Project Documentation.
Comprehensive technical and MBA capstone documentation covering the analytical lifecycle,
leakage protocols, metric formulas, and governance.
"""
import streamlit as st


def render_module_methodology():
    """Render Module 14: Methodology and Project Documentation."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">📚 Academic Methodology & Technical Documentation</div>
        <div class="card-subtitle">
            Rigorous documentation of the analytics lifecycle, machine learning architecture,
            leakage prevention rules, and ethical AI constraints conforming to MBA Business Analytics standards.
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "🔬 Lifecycle & Architecture",
        "🛡️ Data Leakage Rules",
        "📐 Metrics & Formulas",
        "⚖️ Ethical AI & Governance",
        "💻 Setup & Run Instructions"
    ])

    with tabs[0]:
        st.markdown("""
        ### 1. Analytics Lifecycle (CRISP-DM Standard)
        This project follows the **Cross-Industry Standard Process for Data Mining (CRISP-DM)**, adapted for Human Capital Analytics:
        
        1. **Business Understanding:** Diagnosing the systemic and financial impact of unplanned employee turnover in fast-paced quick-commerce enterprises.
        2. **Data Understanding:** Auditing the multi-sheet 2.65MB SnackRush dataset (2,500 employees, 70 master columns, 26,115 longitudinal monthly records).
        3. **Data Preparation:** Building an automated ColumnTransformer pipeline with median numeric imputation, mode categorical imputation, standard scaling, and one-hot encoding.
        4. **Modeling:** Training a benchmark suite consisting of Dummy Baseline, Logistic Regression, Decision Tree, Random Forest, and HistGradientBoosting.
        5. **Evaluation:** Assessing models strictly on 20% held-out test data using F1-score, Precision-Recall AUC, and ROC-AUC rather than misleading accuracy.
        6. **Deployment & Decision Support:** Delivering an interactive, high-fidelity Streamlit platform with explainability (SHAP & Permutation Importance) and ROI simulation.
        """)

    with tabs[1]:
        st.markdown("""
        ### 2. Mandatory Data Leakage Prevention Rules
        Data leakage occurs when information unavailable at the operational prediction cutoff is erroneously included in the model training feature matrix.
        We enforce strict architectural safeguards:
        
        - **Prediction Cutoff Definition:** Predictions are evaluated as of an active employee's pre-resignation review period.
        - **Target Encodings Excluded:** `EmploymentStatus` ('Active' vs 'Exited') is an exact synonym of `Attrition` and is strictly excluded from predictors.
        - **Post-Outcome Dates Excluded:** `ExitDate` is only populated upon departure and would provide a 100% artificial signal; it is excluded.
        - **Exit Classifications Excluded:** `ExitType`, `AttritionCategory`, `ExitReasonCategory`, `TenureAtExitYears`, and `ExitInterviewCompleted` are captured during offboarding and are excluded.
        - **Identifiers Excluded:** `EmployeeID` is a non-predictive surrogate key.
        - **Constant Features Dropped:** `ProbationCompleted` has 100% identical values (zero variance) and is dropped.
        - **Collinear Duplicates Removed:** `AnnualSalaryINR` is an exact collinear 12x multiple of `MonthlySalaryINR` and is excluded to protect linear stability.
        - **Training-Only Preprocessing:** Scalers, encoders, and imputers are fitted strictly on training data folds to prevent test set contamination.
        """)

    with tabs[2]:
        st.markdown("""
        ### 3. Mathematical Metric Definitions
        
        #### A. Workforce Attrition Rates
        $$\\text{Average Headcount} = \\frac{\\text{Opening Headcount} + \\text{Closing Headcount}}{2}$$
        $$\\text{Attrition Rate (\\%)} = \\left( \\frac{\\text{Total Exits During Period}}{\\text{Average Headcount}} \\right) \\times 100$$
        $$\\text{Voluntary Attrition Rate (\\%)} = \\left( \\frac{\\text{Voluntary Resignations}}{\\text{Average Headcount}} \\right) \\times 100$$
        $$\\text{Retention Rate (\\%)} = 100\\% - \\text{Attrition Rate (\\%)}$$
        
        #### B. Machine Learning Classification Metrics
        $$\\text{Accuracy} = \\frac{TP + TN}{TP + TN + FP + FN}$$
        $$\\text{Precision} = \\frac{TP}{TP + FP} \\quad (\\text{Accuracy of Positive Attrition Flags})$$
        $$\\text{Recall (Sensitivity)} = \\frac{TP}{TP + FN} \\quad (\\text{Coverage of Actual Exiting Employees})$$
        $$\\text{F1-Score} = 2 \\times \\frac{\\text{Precision} \\times \\text{Recall}}{\\text{Precision} + \\text{Recall}} \\quad (\\text{Harmonic Mean})$$
        $$\\text{ROC-AUC} = \\text{Area Under the Receiver Operating Characteristic Curve (Ranking Ability)}$$
        $$\\text{PR-AUC} = \\text{Area Under Precision-Recall Curve (Crucial for Imbalanced Classes)}$$
        """)

    with tabs[3]:
        st.markdown("""
        ### 4. Ethical AI & Human Capital Governance
        - **Demographic Parity & Non-Discrimination:** Protected classes (Gender, Marital Status, Age) are kept out of operational prediction features.
        - **Prohibition of Punitive Use:** Predictions must never be used to justify demotions, withholding of bonuses, or termination.
        - **Human Oversight (Human-in-the-Loop):** Model outputs serve exclusively as early advisory alerts to trigger empathetic stay interviews and workload adjustments.
        - **Data Privacy:** Employee records are processed in session isolation, and persistent tracking logs are stored in a local SQLite database without cloud leakage.
        """)

    with tabs[4]:
        st.markdown("""
        ### 5. Installation, Execution & Deployment Guide
        
        #### Local Execution:
        ```bash
        # 1. Clone repository or navigate to workspace
        cd "D:/Projects/Employee Attrtion Rate Analysis"

        # 2. Install dependencies
        pip install -r requirements.txt

        # 3. Run automated pytest test suite
        python -m pytest tests/ -v

        # 4. Launch Streamlit Application
        streamlit run app.py
        ```
        
        #### Deployment Options:
        - **Streamlit Community Cloud:** Connect GitHub repo, specify `app.py` as main entry point.
        - **Docker Container:** Package with Python 3.11+, expose port 8501.
        """)
