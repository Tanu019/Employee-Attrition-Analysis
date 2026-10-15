"""
Tests for model training, evaluation, and prediction inference.
"""
import pytest
import pandas as pd
from src.data_loader import get_default_master_data
from src.model_training import train_and_cross_validate_models
from src.model_evaluation import evaluate_test_performance, compute_threshold_tuning_table
from src.prediction import predict_single_employee, predict_batch_employees, assign_risk_band


@pytest.fixture(scope="module")
def training_output():
    df = get_default_master_data()
    return train_and_cross_validate_models(df, save_artifacts=False)


def test_model_training_outputs(training_output):
    pipes = training_output["trained_pipelines"]
    assert "Dummy (Baseline)" in pipes
    assert "Logistic Regression" in pipes
    assert "Decision Tree" in pipes
    assert "Random Forest" in pipes
    assert "Gradient Boosting" in pipes

    cv_df = training_output["cv_summary_df"]
    assert not cv_df.empty
    assert "CV_Accuracy_Mean" in cv_df.columns
    assert "CV_F1_Mean" in cv_df.columns


def test_model_evaluation_metrics(training_output):
    eval_results = evaluate_test_performance(
        training_output["trained_pipelines"],
        training_output["X_test"],
        training_output["y_test"]
    )
    comp_df = eval_results["comparison_df"]
    assert not comp_df.empty
    assert len(comp_df) == 5

    # Check Dummy baseline has 0 recall
    dummy_row = comp_df[comp_df["Model"] == "Dummy (Baseline)"].iloc[0]
    assert dummy_row["Accuracy"] == 0.82
    assert dummy_row["Recall"] == 0.0
    assert dummy_row["F1_Score"] == 0.0

    # Best model should have positive F1 and ROC-AUC
    best_m = eval_results["best_model_name"]
    best_row = comp_df[comp_df["Model"] == best_m].iloc[0]
    assert best_row["F1_Score"] > 0.35
    assert best_row["ROC_AUC"] > 0.65


def test_prediction_single_employee(training_output):
    rf_pipe = training_output["trained_pipelines"]["Random Forest"]
    sample_employee = {
        "Department": "Operations",
        "BusinessUnit": "B2C Quick Commerce",
        "JobRole": "Operations Associate",
        "JobLevel": 2,
        "EmploymentType": "Full Time",
        "WorkLocation": "Bengaluru",
        "City": "Bengaluru",
        "State": "Karnataka",
        "EducationLevel": "Bachelor's Degree",
        "EducationField": "Commerce",
        "TotalWorkExperienceYears": 3,
        "PreviousCompanies": 1,
        "DistanceFromHomeKm": 10.0,
        "WorkArrangement": "On-site",
        "MonthlySalaryINR": 35000,
        "SalaryBand": "Mid",
        "SalaryHikePercent": 8.0,
        "BonusPercent": 5.0,
        "Overtime": "Yes",
        "BenefitsSatisfaction": 2,
        "CompensationSatisfaction": 2,
        "PromotionLastFiveYears": "No",
        "YearsSinceLastPromotion": 2.5,
        "DailyWorkingHours": 9.5,
        "WeeklyWorkingHours": 47.5,
        "OvertimeHoursMonthly": 30,
        "ProjectsHandled": 5,
        "AverageWorkloadScore": 4,
        "PerformanceRating": 3,
        "ProductivityScore": 70,
        "AbsenteeismDaysLastYear": 5,
        "LateArrivalsLastMonth": 2,
        "ManagerRating": 3,
        "JobSatisfaction": 2,
        "EnvironmentSatisfaction": 2,
        "WorkLifeBalance": 2,
        "RelationshipWithManager": 2,
        "PeerRelationshipScore": 3,
        "CareerGrowthSatisfaction": 2,
        "RecognitionSatisfaction": 2,
        "EmployeeEngagementScore": 55,
        "StressLevel": 4,
        "BurnoutRiskScore": 75,
        "IntentToLeaveScore": 65,
        "YearsAtCompany": 2.0,
        "YearsInCurrentRole": 1.5,
        "YearsWithCurrentManager": 1.5,
        "InternalTransfers": 0,
        "TrainingHoursLastYear": 15,
        "CertificationsCompleted": 0,
        "CareerDevelopmentParticipation": "No",
        "RecruitmentSource": "Direct",
        "RecruitmentCostINR": 20000,
        "TimeToFillDays": 25,
        "OnboardingSatisfaction": 3,
        "ReferralHire": "No"
    }

    pred_res = predict_single_employee(rf_pipe, sample_employee, model_name="Random Forest")
    assert "predicted_class" in pred_res
    assert "attrition_probability" in pred_res
    assert 0.0 <= pred_res["attrition_probability"] <= 1.0
    assert pred_res["risk_band"] in ["Low Risk", "Moderate Risk", "High Risk", "Critical Risk"]
    assert len(pred_res["suggested_actions"]) > 0


def test_assign_risk_band():
    band_low, _ = assign_risk_band(0.15)
    band_mod, _ = assign_risk_band(0.35)
    band_high, _ = assign_risk_band(0.60)
    band_crit, _ = assign_risk_band(0.85)

    assert band_low == "Low Risk"
    assert band_mod == "Moderate Risk"
    assert band_high == "High Risk"
    assert band_crit == "Critical Risk"
