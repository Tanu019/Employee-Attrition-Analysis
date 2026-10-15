"""
Module 1: Project Overview & Executive Briefing.
"""
import streamlit as st
from config.settings import APP_TITLE, APP_SUBTITLE, PROJECT_CONTEXT, ORGANIZATION_NAME


def render_module_overview():
    """Render Module 1: Project Overview."""
    st.markdown(f"""
    <div class="main-header">
        <h1 class="main-title">{APP_TITLE}</h1>
        <div class="main-subtitle">{APP_SUBTITLE}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="callout-box">
        <strong>Academic & Enterprise Context:</strong> This platform is designed as an MBA Business Analytics Capstone Decision Support System.
        It bridges empirical workforce data science, predictive machine learning, and strategic human capital management to provide
        actionable, evidence-backed retention intelligence.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("""
        <div class="content-card">
            <div class="card-title">📌 Executive Problem Statement</div>
            <p style="color: var(--text-secondary); line-height: 1.6; font-size: 0.92rem;">
                Unplanned employee turnover poses significant operational and financial risks to modern enterprises. 
                According to industry benchmarks, replacing a specialized employee costs between <strong>50% to 150% of their annual salary</strong> 
                in direct recruitment, onboarding expenses, and lost productivity.
            </p>
            <p style="color: var(--text-secondary); line-height: 1.6; font-size: 0.92rem;">
                Traditional HR departments operate reactively—conducting exit interviews only after resignation letters have been submitted.
                This decision support system transforms human capital strategy into a <strong>proactive, data-driven intervention discipline</strong>, 
                detecting flight risks early while diagnosing systemic organizational drivers like overtime strain, burnout, and compensation disparities.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="content-card">
            <div class="card-title">🎯 Core Analytical Objectives</div>
            <ul style="color: var(--text-secondary); line-height: 1.8; font-size: 0.88rem; padding-left: 1.2rem;">
                <li><strong>Empirical Profiling:</strong> Uncover the structural, demographic, and behavioral correlations associated with employee departures.</li>
                <li><strong>Workforce Rate Quantification:</strong> Accurately calculate attrition and retention rates using standardized average-headcount formulas.</li>
                <li><strong>Leakage-Safe Machine Learning:</strong> Train and rigorously evaluate supervised classification models on held-out test data.</li>
                <li><strong>Transparent Decision Support:</strong> Provide granular explainability (SHAP & Permutation Importance) to demystify algorithmic outputs.</li>
                <li><strong>Actionable Retention Planning:</strong> Translate diagnostic patterns into targeted, departmental intervention roadmaps.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="content-card">
            <div class="card-title">🏢 Enterprise Dataset Architecture</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6;">
                <p>The analytics engine is powered by the verified <strong>SnackRush Enterprise Dataset</strong> (2.65 MB multi-sheet workbook):</p>
                <ul style="padding-left: 1.1rem; margin-top: 0.4rem;">
                    <li><strong>Employee Master:</strong> 2,500 full-profile workforce records across 70 attributes.</li>
                    <li><strong>Monthly History:</strong> 26,115 longitudinal monthly records across 12 operational months.</li>
                    <li><strong>Satisfaction Surveys:</strong> 2,500 comprehensive climate and engagement ratings.</li>
                    <li><strong>Attrition Events:</strong> 450 verified departure records with exit dates and reason categories.</li>
                    <li><strong>Verified Quality Baseline:</strong> Cross-validated referential integrity and zero artificial data drift.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="content-card">
            <div class="card-title">⚖️ Ethical AI & Governance Principles</div>
            <div style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.6;">
                <p><strong>1. Zero Automated Adverse Action:</strong> Risk classifications inform supportive interventions, never dismissals or penalties.</p>
                <p><strong>2. Demographic Protection:</strong> Sensitive attributes (Gender, Age, Marital Status) are excluded from operational prediction features.</p>
                <p><strong>3. Probabilistic Humility:</strong> Results represent historical risk propensities, not deterministic certainty.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-card">
        <div class="card-title">🗺️ Platform Navigation Guide</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.8rem; font-size: 0.84rem;">
            <div style="background: #201b18; padding: 0.8rem; border-radius: 6px; border: 1px solid #3a322c;">
                <strong style="color: var(--accent-copper);">1. Data Validation</strong><br>
                Inspect schema, missing values, referential integrity, and quality checks.
            </div>
            <div style="background: #201b18; padding: 0.8rem; border-radius: 6px; border: 1px solid #3a322c;">
                <strong style="color: var(--accent-copper);">2. Executive Dashboard</strong><br>
                High-level KPIs, interactive multi-dimensional filters, and cross-sectional charts.
            </div>
            <div style="background: #201b18; padding: 0.8rem; border-radius: 6px; border: 1px solid #3a322c;">
                <strong style="color: var(--accent-copper);">3. Attrition Calculator</strong><br>
                Date-based or manual workforce rate derivation with transparent formulas.
            </div>
            <div style="background: #201b18; padding: 0.8rem; border-radius: 6px; border: 1px solid #3a322c;">
                <strong style="color: var(--accent-copper);">4. ML Model Evaluation</strong><br>
                Held-out test metrics, confusion matrix, baseline comparison, and threshold curves.
            </div>
            <div style="background: #201b18; padding: 0.8rem; border-radius: 6px; border: 1px solid #3a322c;">
                <strong style="color: var(--accent-copper);">5. Individual Prediction</strong><br>
                Evaluate employee flight risk, inspect contributing drivers, and view support actions.
            </div>
            <div style="background: #201b18; padding: 0.8rem; border-radius: 6px; border: 1px solid #3a322c;">
                <strong style="color: var(--accent-copper);">6. Retention Planner</strong><br>
                Actionable interventions grounded in dataset findings with target KPIs.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
