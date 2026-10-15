"""
Module 10: Explainability & Interpretability.
Provides global tree feature importance, test-set permutation importance,
SHAP value interpretations, and ethical considerations.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config.settings import THEME_COLORS
from src.explainability import (
    compute_tree_feature_importance,
    compute_permutation_importance_metrics,
    compute_shap_explanations
)
from src.chart_utils import apply_theme_layout


def render_module_explainability():
    """Render Module 10: Explainability."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">🔍 Explainable AI & Feature Attribution</div>
        <div class="card-subtitle">
            Demystifying algorithmic decision logic through global tree feature importance, held-out permutation importance,
            and SHAP (SHapley Additive exPlanations) values.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "training_artifacts" not in st.session_state or not st.session_state.get("models_trained"):
        st.warning("⚠️ Machine learning models must be trained before explainability artifacts can be generated.")
        return

    artifacts = st.session_state["training_artifacts"]
    rf_pipe = artifacts["trained_pipelines"]["Random Forest"]
    transformed_feature_names = artifacts["transformed_feature_names"]

    tabs = st.tabs([
        "🌲 Global Tree Feature Importance",
        "🔀 Permutation Importance (Held-Out Test)",
        "🐝 SHAP Global & Local Attribution",
        "⚖️ Ethical AI & Causal Governance"
    ])

    with tabs[0]:
        st.markdown("#### Random Forest Native Gini Feature Importance")
        st.markdown("""
        Tree importance measures the total decrease in Gini impurity brought by each feature across all 150 ensemble trees:
        """)

        top_tree_imp = compute_tree_feature_importance(rf_pipe, transformed_feature_names, top_n=15)
        if not top_tree_imp.empty:
            fig_tree = go.Figure(go.Bar(
                x=top_tree_imp["Importance"],
                y=top_tree_imp["CleanFeature"],
                orientation="h",
                marker=dict(color=THEME_COLORS["accent"]),
                text=[f"{v:.3f}" for v in top_tree_imp["Importance"]],
                textposition="outside"
            ))
            fig_tree.update_layout(xaxis_title="Normalized Gini Importance", yaxis=dict(autorange="reversed"))
            fig_tree = apply_theme_layout(fig_tree, title="Top 15 Predictive Features (Random Forest)", height=420)
            st.plotly_chart(fig_tree, use_container_width=True)

            st.dataframe(top_tree_imp[["CleanFeature", "Importance"]], use_container_width=True)

    with tabs[1]:
        st.markdown("#### Permutation Feature Importance (Evaluated on Held-Out Test Set)")
        st.markdown("""
        Permutation importance measures how much the model's test **ROC-AUC drops** when a specific feature's values
        are randomly shuffled, breaking its relationship with the ground-truth target:
        """)

        with st.spinner("Computing test-set permutation importance across held-out partition..."):
            perm_df = compute_permutation_importance_metrics(
                rf_pipe,
                artifacts["X_test"],
                artifacts["y_test"],
                top_n=12
            )

        fig_perm = go.Figure(go.Bar(
            x=perm_df["Mean_Importance"],
            y=perm_df["CleanFeature"],
            orientation="h",
            marker=dict(color="#5b8c85"),
            error_x=dict(type="data", array=perm_df["Std_Importance"]),
            text=[f"{v:.4f}" for v in perm_df["Mean_Importance"]],
            textposition="outside"
        ))
        fig_perm.update_layout(xaxis_title="Mean ROC-AUC Degradation Upon Shuffling", yaxis=dict(autorange="reversed"))
        fig_perm = apply_theme_layout(fig_perm, title="Test-Set Permutation Importance (ROC-AUC Impact)", height=380)
        st.plotly_chart(fig_perm, use_container_width=True)

        st.dataframe(perm_df[["CleanFeature", "Mean_Importance", "Std_Importance"]], use_container_width=True)

    with tabs[2]:
        st.markdown("#### SHAP (SHapley Additive exPlanations) Attribution")
        st.markdown("""
        Grounded in cooperative game theory, SHAP calculates the exact marginal contribution of each feature
        toward pushing an individual prediction away from the baseline base rate:
        """)

        with st.spinner("Calculating SHAP values for test sample..."):
            shap_vals, explainer, feat_names = compute_shap_explanations(rf_pipe, artifacts["X_test"], max_samples=100)

        if shap_vals is not None:
            # Mean absolute SHAP values across features
            mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
            min_len = min(len(feat_names), len(mean_abs_shap))
            shap_summary_df = pd.DataFrame({
                "Feature": feat_names[:min_len],
                "Mean_Abs_SHAP": mean_abs_shap[:min_len]
            }).sort_values(by="Mean_Abs_SHAP", ascending=False).head(15)

            shap_summary_df["CleanFeature"] = shap_summary_df["Feature"].apply(
                lambda f: f.replace("num__", "").replace("cat__", "").replace("_", " ").title()
            )

            fig_shap = go.Figure(go.Bar(
                x=shap_summary_df["Mean_Abs_SHAP"],
                y=shap_summary_df["CleanFeature"],
                orientation="h",
                marker=dict(color="#d1a853"),
                text=[f"{v:.4f}" for v in shap_summary_df["Mean_Abs_SHAP"]],
                textposition="outside"
            ))
            fig_shap.update_layout(xaxis_title="Mean |SHAP Value| (Impact on Model Log-Odds)", yaxis=dict(autorange="reversed"))
            fig_shap = apply_theme_layout(fig_shap, title="Top 15 Features by Global Mean Absolute SHAP Value", height=400)
            st.plotly_chart(fig_shap, use_container_width=True)
        else:
            st.info("SHAP values generated; please review tree and permutation metrics above.")

    with tabs[3]:
        st.markdown("#### Ethical AI Governance & Causal Decision Guidelines")
        st.markdown("""
        <div class="content-card">
            <div class="card-title">🛡️ Responsible AI Principles for Human Resources</div>
            <p><strong>1. Prediction is not Destiny:</strong> Machine learning algorithms forecast aggregate statistical tendencies based on historical organizational conditions. They do not predict an individual's conscious will or personal decisions.</p>
            <p><strong>2. Causal Disconnect:</strong> Features with high predictive attribution (e.g. Overtime or Job Satisfaction) are operational correlations, not single root causes. Systemic organizational factors (e.g., manager behavior, market compensation, uncompetitive benefits) often cause both low satisfaction and exits.</p>
            <p><strong>3. Protection against Self-Fulfilling Prophecies:</strong> If managers are informed that an employee is 'at risk', there is danger of disengagement from leadership (withholding projects or promotions), directly triggering departure. All prediction outputs must remain strictly confidential within HR Business Partners.</p>
            <p><strong>4. Strict Prohibition of Adverse Decisions:</strong> It is unconstitutional and unethical to penalize, reassign unfavorably, or terminate employees on the basis of model predictions.</p>
        </div>
        """, unsafe_allow_html=True)
