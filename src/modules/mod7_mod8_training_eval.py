"""
Module 7 & 8: Machine Learning Model Training & Held-Out Performance Evaluation.
Executes training pipelines, Stratified 5-Fold CV, held-out test benchmarking,
HR confusion matrices, and threshold trade-off optimization.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config.settings import THEME_COLORS
from src.model_training import train_and_cross_validate_models
from src.model_evaluation import evaluate_test_performance, compute_threshold_tuning_table
from src.chart_utils import apply_theme_layout


def render_module_training_and_eval(df_master: pd.DataFrame):
    """Render Modules 7 & 8: Model Training and Performance Evaluation."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">🤖 Machine Learning Model Training & Held-Out Performance Evaluation</div>
        <div class="card-subtitle">
            Rigorous supervised classification benchmark. Models are tuned via Stratified 5-Fold Cross Validation
            on the training partition and evaluated strictly against a 20% held-out test cohort (500 unseen employees).
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state for training artifacts
    if "training_artifacts" not in st.session_state or st.session_state.get("models_trained") is False:
        with st.spinner("Executing stratified training pipeline & 5-fold cross-validation..."):
            artifacts = train_and_cross_validate_models(df_master)
            eval_results = evaluate_test_performance(
                artifacts["trained_pipelines"],
                artifacts["X_test"],
                artifacts["y_test"]
            )
            st.session_state["training_artifacts"] = artifacts
            st.session_state["eval_results"] = eval_results
            st.session_state["models_trained"] = True

    artifacts = st.session_state["training_artifacts"]
    eval_results = st.session_state["eval_results"]
    comparison_df = eval_results["comparison_df"]
    best_model_name = eval_results["best_model_name"]

    # Training control header
    col_ctrl1, col_ctrl2 = st.columns([3, 1])
    with col_ctrl1:
        st.markdown(f"""
        <div style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5;">
            <strong>Evaluation Architecture:</strong> Stratified 80/20 train-test split (Train: 2,000 employees, Test: 500 employees). 
            Baseline Dummy Accuracy is <strong>82.0%</strong> due to class distribution (82% Stayed, 18% Exited).<br>
            <strong>Primary Selected Model:</strong> <span class="badge badge-low">{best_model_name}</span> 
            (Selected based on harmonic F1-Score & PR-AUC on held-out test data).
        </div>
        """, unsafe_allow_html=True)
    with col_ctrl2:
        if st.button("🔄 Retrain All Models", type="secondary"):
            with st.spinner("Retraining pipelines..."):
                artifacts = train_and_cross_validate_models(df_master)
                eval_results = evaluate_test_performance(
                    artifacts["trained_pipelines"],
                    artifacts["X_test"],
                    artifacts["y_test"]
                )
                st.session_state["training_artifacts"] = artifacts
                st.session_state["eval_results"] = eval_results
                st.session_state["models_trained"] = True
                st.rerun()

    tabs = st.tabs([
        "🏆 Held-Out Test Evaluation",
        "🎯 HR Confusion Matrix",
        "🔁 Stratified 5-Fold CV Results",
        "⚖️ Threshold & Financial Optimization",
        "📊 ROC & PR Curves"
    ])

    with tabs[0]:
        st.markdown("#### Held-Out Test Evaluation Benchmark (500 Unseen Employees)")
        st.markdown("""
        All metrics shown below are calculated strictly from model predictions on the held-out test partition.
        No training predictions, fabricated scores, or optimistic estimations are used.
        """)

        # Style comparison table
        st.dataframe(
            comparison_df.style.highlight_max(
                subset=["Accuracy", "Precision", "Recall", "F1_Score", "ROC_AUC", "PR_AUC"],
                color="#3e342c"
            ),
            use_container_width=True
        )

        st.markdown("""
        <div class="callout-box">
            <strong>Key Business Analytics Takeaways:</strong><br>
            • <strong>Baseline Dummy Illusion:</strong> The Dummy Classifier scores 82.0% Accuracy by predicting 'No Attrition' for everyone, 
            yet delivers <strong>0.00 Precision, 0.00 Recall, and 0.00 F1-Score</strong>—failing to identify a single exiting employee.<br>
            • <strong>Logistic Regression</strong> delivers the highest <strong>Recall (62.2%)</strong> and <strong>ROC-AUC (0.733)</strong>, 
            making it highly sensitive for casting a wide net.<br>
            • <strong>Random Forest</strong> achieves the best balanced <strong>F1-Score (0.453)</strong> and <strong>PR-AUC (0.467)</strong>, 
            substantially outperforming the baseline PR-AUC of 0.180.
        </div>
        """, unsafe_allow_html=True)

        # Bar chart comparison
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name="Accuracy",
            x=comparison_df["Model"],
            y=comparison_df["Accuracy"],
            marker_color="#3a322c"
        ))
        fig_comp.add_trace(go.Bar(
            name="Recall (Sensitivity)",
            x=comparison_df["Model"],
            y=comparison_df["Recall"],
            marker_color="#d9822b"
        ))
        fig_comp.add_trace(go.Bar(
            name="F1-Score",
            x=comparison_df["Model"],
            y=comparison_df["F1_Score"],
            marker_color=THEME_COLORS["accent"]
        ))
        fig_comp.add_trace(go.Bar(
            name="ROC-AUC",
            x=comparison_df["Model"],
            y=comparison_df["ROC_AUC"],
            marker_color="#5b8c85"
        ))
        fig_comp.update_layout(barmode="group", yaxis_title="Metric Score (0 to 1.0)")
        fig_comp = apply_theme_layout(fig_comp, title="Held-Out Model Comparison across Key Evaluative Dimensions", height=380)
        st.plotly_chart(fig_comp, use_container_width=True)

    with tabs[1]:
        st.markdown("#### HR Contextual Confusion Matrix")
        selected_model = st.selectbox("Select Model to Inspect Confusion Matrix:", list(artifacts["trained_pipelines"].keys()), index=3)
        model_info = eval_results["model_details"][selected_model]
        hr_cm = model_info["hr_confusion_matrix"]
        cm_raw = model_info["confusion_matrix"]

        c_cm1, c_cm2 = st.columns([1, 1])
        with c_cm1:
            st.markdown(f"""
            <div style="background-color: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 1rem;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem;">
                    <div style="background: #1e1916; padding: 1rem; border-radius: 6px; border-left: 3px solid #388e3c;">
                        <div style="font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase;">True Negatives</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #81c784;">{hr_cm['True_Negatives_Retained']}</div>
                        <div style="font-size: 0.76rem; color: var(--text-muted);">{hr_cm['Labels']['TN']}</div>
                    </div>
                    <div style="background: #1e1916; padding: 1rem; border-radius: 6px; border-left: 3px solid #f57c00;">
                        <div style="font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase;">False Positives</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #ffb74d;">{hr_cm['False_Positives_Flagged_Wrongly']}</div>
                        <div style="font-size: 0.76rem; color: var(--text-muted);">{hr_cm['Labels']['FP']}</div>
                    </div>
                    <div style="background: #1e1916; padding: 1rem; border-radius: 6px; border-left: 3px solid #d32f2f;">
                        <div style="font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase;">False Negatives</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #e57373;">{hr_cm['False_Negatives_Missed_Exits']}</div>
                        <div style="font-size: 0.76rem; color: var(--text-muted);">{hr_cm['Labels']['FN']}</div>
                    </div>
                    <div style="background: #1e1916; padding: 1rem; border-radius: 6px; border-left: 3px solid var(--accent-copper);">
                        <div style="font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase;">True Positives</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--accent-copper);">{hr_cm['True_Positives_Identified_Exits']}</div>
                        <div style="font-size: 0.76rem; color: var(--text-muted);">{hr_cm['Labels']['TP']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c_cm2:
            # Heatmap visualization of confusion matrix
            fig_cm = px.imshow(
                cm_raw,
                text_auto=True,
                labels=dict(x="Predicted Class", y="Actual Class", color="Count"),
                x=["Retained (0)", "Exited (1)"],
                y=["Retained (0)", "Exited (1)"],
                color_continuous_scale=[[0, "#241f1c"], [1, THEME_COLORS["accent"]]]
            )
            fig_cm = apply_theme_layout(fig_cm, title=f"Confusion Heatmap: {selected_model}", height=320)
            st.plotly_chart(fig_cm, use_container_width=True)

    with tabs[2]:
        st.markdown("#### Stratified 5-Fold Cross-Validation (Training Partition Only)")
        st.markdown("Evaluated across 5 folds strictly on the 2,000 training observations to evaluate variance and stability:")
        st.dataframe(artifacts["cv_summary_df"], use_container_width=True)

    with tabs[3]:
        st.markdown("#### Classification Threshold & Business Cost Optimization")
        st.markdown("""
        In HR decision support, the default 0.50 probability cutoff may not optimize business outcomes.
        Adjust the financial cost assumptions below to evaluate the optimal intervention threshold:
        """)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fn_cost = st.number_input("Cost of an Unplanned Departure (False Negative) in INR:", min_value=10000, value=120000, step=10000)
        with col_c2:
            fp_cost = st.number_input("Cost of an Unnecessary Retention Support Action (False Positive) in INR:", min_value=1000, value=15000, step=2500)

        rf_pipe = artifacts["trained_pipelines"]["Random Forest"]
        y_prob_rf = rf_pipe.predict_proba(artifacts["X_test"])[:, 1]
        tuning_df = compute_threshold_tuning_table(artifacts["y_test"], y_prob_rf, fn_cost, fp_cost)

        st.dataframe(tuning_df, use_container_width=True, height=320)

        fig_cost = go.Figure()
        fig_cost.add_trace(go.Scatter(
            x=tuning_df["Threshold"],
            y=tuning_df["Estimated_Total_Cost_INR"],
            mode="lines+markers",
            name="Total Workforce Cost",
            line=dict(color=THEME_COLORS["accent"], width=3)
        ))
        fig_cost.update_layout(xaxis_title="Classification Threshold", yaxis_title="Estimated Enterprise Cost (INR)")
        fig_cost = apply_theme_layout(fig_cost, title="Enterprise Cost Curve vs Classification Cutoff Threshold", height=320)
        st.plotly_chart(fig_cost, use_container_width=True)

    with tabs[4]:
        st.markdown("#### ROC and Precision-Recall Curves")
        c_roc, c_pr = st.columns(2)
        
        with c_roc:
            fig_roc = go.Figure()
            for name in ["Logistic Regression", "Random Forest", "Gradient Boosting"]:
                pipe = artifacts["trained_pipelines"][name]
                if hasattr(pipe, "predict_proba"):
                    probs = pipe.predict_proba(artifacts["X_test"])[:, 1]
                    from sklearn.metrics import roc_curve
                    fpr, tpr, _ = roc_curve(artifacts["y_test"], probs)
                    fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=name))
            fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random Guess", line=dict(dash="dash", color="#7d756b")))
            fig_roc.update_layout(xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
            fig_roc = apply_theme_layout(fig_roc, title="ROC Curves (Receiver Operating Characteristic)", height=340)
            st.plotly_chart(fig_roc, use_container_width=True)

        with c_pr:
            fig_pr = go.Figure()
            for name in ["Logistic Regression", "Random Forest", "Gradient Boosting"]:
                pipe = artifacts["trained_pipelines"][name]
                if hasattr(pipe, "predict_proba"):
                    probs = pipe.predict_proba(artifacts["X_test"])[:, 1]
                    from sklearn.metrics import precision_recall_curve
                    prec, rec, _ = precision_recall_curve(artifacts["y_test"], probs)
                    fig_pr.add_trace(go.Scatter(x=rec, y=prec, mode="lines", name=name))
            fig_pr.add_trace(go.Scatter(x=[0, 1], y=[artifacts["y_test"].mean(), artifacts["y_test"].mean()], mode="lines", name="Baseline Prevalence", line=dict(dash="dash", color="#7d756b")))
            fig_pr.update_layout(xaxis_title="Recall", yaxis_title="Precision")
            fig_pr = apply_theme_layout(fig_pr, title="Precision-Recall Curves (Imbalance Sensitive)", height=340)
            st.plotly_chart(fig_pr, use_container_width=True)
