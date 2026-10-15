"""
FastAPI Server for Employees Attrition Analysis Application.
Exposes REST API endpoints for all analytical calculations, machine learning
predictions, explainability, reports, and serves the bespoke web application frontend.
"""
import io
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config.settings import (
    BASE_DIR, DEFAULT_DATA_FILE, DATABASE_PATH, MODELS_DIR, REPORTS_DIR,
    LEAKAGE_AND_POST_EXIT_COLUMNS, SENSITIVE_DEMOGRAPHIC_COLUMNS
)
from src.database import init_database, get_all_experiments, get_prediction_history
from src.data_loader import (
    get_default_master_data,
    load_workbook_data,
    compute_file_fingerprint
)
from src.data_validation import (
    identify_target_column,
    map_schema,
    generate_data_dictionary,
    perform_data_quality_checks
)
from src.feature_engineering import engineer_hr_features
from src.preprocessing import prepare_features_and_target, create_train_test_split
from src.attrition_analysis import (
    compute_executive_kpis,
    compute_breakdown_table,
    compute_stayers_vs_leavers,
    compute_correlations_with_target,
    generate_data_driven_insights
)
from src.attrition_calculator import (
    calculate_attrition_metrics,
    derive_headcount_from_dates
)
from src.model_evaluation import (
    evaluate_test_performance,
    compute_threshold_tuning_table
)
from src.prediction import (
    predict_single_employee,
    predict_batch_employees,
    assign_risk_band
)
from src.explainability import (
    compute_tree_feature_importance,
    compute_permutation_importance_metrics
)
from src.retention_planner import (
    generate_retention_strategies
)
from src.reporting import (
    generate_executive_markdown_report
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AttritionServer")

app = FastAPI(
    title="Employees Attrition Analysis API",
    description="HR Decision Support & Machine Learning System",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory cache for models & evaluations
APP_CACHE: Dict[str, Any] = {
    "master_df": None,
    "trained_pipelines": {},
    "evaluation_results": None,
    "X_test": None,
    "y_test": None,
    "feature_cols": []
}


def load_application_state():
    """Initialize database, dataset, and trained machine learning pipelines."""
    init_database()
    logger.info("Initializing dataset from disk...")
    df = get_default_master_data()
    APP_CACHE["master_df"] = df

    # Load pre-trained models from models directory
    model_names = {
        "Dummy (Baseline)": "dummy_baseline_pipeline.joblib",
        "Logistic Regression": "logistic_regression_pipeline.joblib",
        "Decision Tree": "decision_tree_pipeline.joblib",
        "Random Forest": "random_forest_pipeline.joblib",
        "Gradient Boosting": "gradient_boosting_pipeline.joblib"
    }

    pipes = {}
    for name, filename in model_names.items():
        path = MODELS_DIR / filename
        if path.exists():
            try:
                pipes[name] = joblib.load(path)
            except Exception as e:
                logger.warning(f"Could not load {name}: {e}")

    APP_CACHE["trained_pipelines"] = pipes

    if pipes and "Random Forest" in pipes:
        try:
            X, y, num_cols, cat_cols = prepare_features_and_target(df)
            _, X_test, _, y_test = create_train_test_split(X, y)
            eval_res = evaluate_test_performance(pipes, X_test, y_test)
            APP_CACHE["evaluation_results"] = eval_res
            APP_CACHE["X_test"] = X_test
            APP_CACHE["y_test"] = y_test
            APP_CACHE["feature_cols"] = list(X.columns)

            perm_df = compute_permutation_importance_metrics(pipes["Random Forest"], X_test, y_test, top_n=12)
            perm_records = []
            for r in perm_df.to_dict(orient="records"):
                perm_records.append({
                    "Feature": r["CleanFeature"],
                    "Importance_Mean": round(float(r["Mean_Importance"]), 4),
                    "Importance_Std": round(float(r["Std_Importance"]), 4)
                })
            APP_CACHE["permutation_importance"] = perm_records
            logger.info("Evaluation metrics and Permutation Importance successfully computed on held-out test data.")
        except Exception as e:
            logger.error(f"Error computing initial model evaluation: {e}")


@app.on_event("startup")
def on_startup():
    load_application_state()


# -------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------

@app.get("/api/status")
def get_system_status():
    """Return health status, dataset stats, and trained models available."""
    df = APP_CACHE.get("master_df")
    pipes = APP_CACHE.get("trained_pipelines", {})
    best_model = APP_CACHE.get("evaluation_results", {}).get("best_model_name", "Random Forest")
    return {
        "status": "online",
        "dataset_loaded": df is not None,
        "rows": len(df) if df is not None else 0,
        "columns": len(df.columns) if df is not None else 0,
        "models_available": list(pipes.keys()),
        "best_model": best_model
    }


@app.get("/api/dataset/overview")
def get_dataset_info():
    """Return comprehensive data dictionary and quality validation report."""
    df = APP_CACHE.get("master_df")
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not loaded.")
    
    data_dict = generate_data_dictionary(df)
    quality_res = perform_data_quality_checks(df)
    schema_map = map_schema(df)

    departments = sorted([str(d) for d in df["Department"].dropna().unique()]) if "Department" in df.columns else []
    roles = sorted([str(r) for r in df["JobRole"].dropna().unique()]) if "JobRole" in df.columns else []

    # Format dictionary for frontend
    dict_records = []
    for r in data_dict.to_dict(orient="records"):
        dict_records.append({
            "Column_Name": r["ColumnName"],
            "Data_Type": r["DataType"],
            "Non_Null_Count": len(df) - int(r["MissingValues"]),
            "Unique_Values": r["UniqueValues"],
            "Sample_Values": r["SampleValues"],
            "Analytical_Category": r["IntendedUse"]
        })

    return {
        "validation": {
            "total_rows": quality_res["total_rows"],
            "total_cols": quality_res["total_cols"],
            "duplicate_rows": quality_res["duplicate_rows"],
            "attrition_rate": quality_res["attrition_rate"],
            "target_col": quality_res["target_col"],
            "checks": quality_res["checks"]
        },
        "schema_map": schema_map,
        "data_dictionary": dict_records,
        "quality_report": quality_res["checks_df"].to_dict(orient="records"),
        "filter_options": {
            "departments": ["All"] + departments,
            "roles": ["All"] + roles
        }
    }


@app.get("/api/analytics/kpis")
def get_executive_kpis(
    department: str = Query("All"),
    job_role: str = Query("All"),
    tenure_band: str = Query("All")
):
    """Compute executive KPI cards based on active interactive filters."""
    df = APP_CACHE.get("master_df")
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not loaded.")

    filtered_df = df.copy()
    if department != "All" and "Department" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Department"] == department]
    if job_role != "All" and "JobRole" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["JobRole"] == job_role]
    if tenure_band != "All" and "TenureBand" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["TenureBand"] == tenure_band]

    raw_kpis = compute_executive_kpis(filtered_df)

    kpis = {
        "Total_Employees": raw_kpis.get("total_employees", len(filtered_df)),
        "Active_Employees": raw_kpis.get("active_employees", 0) or 0,
        "Employees_Who_Left": raw_kpis.get("exited_employees", 0) or 0,
        "Overall_Attrition_Rate_Pct": raw_kpis.get("attrition_rate_percent", 0.0) or 0.0,
        "Voluntary_Attrition_Rate_Pct": raw_kpis.get("voluntary_attrition_rate_percent", 0.0) or 0.0,
        "Average_Salary": raw_kpis.get("avg_salary_inr", 65000.0) or 65000.0,
        "Average_Tenure_Years": raw_kpis.get("avg_tenure_years", 4.5) or 4.5,
        "Average_Satisfaction": raw_kpis.get("avg_job_satisfaction", 3.0) or 3.0
    }

    eval_res = APP_CACHE.get("evaluation_results")
    if eval_res and "comparison_df" in eval_res:
        rf_row = eval_res["comparison_df"][eval_res["comparison_df"]["Model"] == "Random Forest"]
        if not rf_row.empty:
            kpis["Model_Accuracy_Pct"] = round(float(rf_row.iloc[0]["Accuracy"]) * 100, 1)
            kpis["Model_F1_Score"] = round(float(rf_row.iloc[0]["F1_Score"]), 3)
            kpis["Model_ROC_AUC"] = round(float(rf_row.iloc[0]["ROC_AUC"]), 3)

    return {
        "kpis": kpis,
        "filtered_count": len(filtered_df),
        "total_count": len(df)
    }


@app.get("/api/analytics/charts")
def get_chart_data(
    department: str = Query("All"),
    job_role: str = Query("All")
):
    """Aggregate data for interactive Plotly charts."""
    df = APP_CACHE.get("master_df")
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not loaded.")

    filtered_df = df.copy()
    if department != "All" and "Department" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Department"] == department]
    if job_role != "All" and "JobRole" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["JobRole"] == job_role]

    dept_tbl = compute_breakdown_table(filtered_df, "Department") if "Department" in filtered_df.columns else pd.DataFrame()
    dept_data = []
    if not dept_tbl.empty:
        for r in dept_tbl.to_dict(orient="records"):
            dept_data.append({
                "Department": r["Department"],
                "Attrition_Rate_Pct": r["AttritionRatePercent"],
                "Total_Employees": r["TotalEmployees"],
                "Exited_Employees": r["ExitedEmployees"]
            })

    role_tbl = compute_breakdown_table(filtered_df, "JobRole") if "JobRole" in filtered_df.columns else pd.DataFrame()
    role_data = []
    if not role_tbl.empty:
        for r in role_tbl.to_dict(orient="records"):
            role_data.append({
                "JobRole": r["JobRole"],
                "Attrition_Rate_Pct": r["AttritionRatePercent"],
                "Total_Employees": r["TotalEmployees"],
                "Exited_Employees": r["ExitedEmployees"]
            })

    # Tenure breakdown
    tenure_col = "TenureBand" if "TenureBand" in filtered_df.columns else None
    if not tenure_col and "YearsAtCompany" in filtered_df.columns:
        filtered_df["TenureBand"] = pd.cut(
            filtered_df["YearsAtCompany"],
            bins=[-0.1, 1, 3, 5, 10, 50],
            labels=["< 1 Year", "1-3 Years", "3-5 Years", "6-10 Years", "10+ Years"]
        )
        tenure_col = "TenureBand"

    tenure_data = []
    if tenure_col:
        tenure_tbl = compute_breakdown_table(filtered_df, tenure_col)
        for r in tenure_tbl.to_dict(orient="records"):
            tenure_data.append({
                "TenureBand": str(r[tenure_col]),
                "Attrition_Rate_Pct": r["AttritionRatePercent"],
                "Total_Employees": r["TotalEmployees"]
            })

    # Overtime breakdown
    ot_col = next((c for c in ["OverTime", "Overtime"] if c in filtered_df.columns), None)
    overtime_data = []
    if ot_col:
        ot_tbl = compute_breakdown_table(filtered_df, ot_col)
        for r in ot_tbl.to_dict(orient="records"):
            overtime_data.append({
                "OverTime": str(r[ot_col]),
                "AttritionRate": r["AttritionRatePercent"],
                "Headcount": r["TotalEmployees"]
            })

    attrition_counts = filtered_df["Attrition"].value_counts().to_dict() if "Attrition" in filtered_df.columns else {}

    return {
        "overall_distribution": [
            {"label": "Active Stayers (No)", "value": int(attrition_counts.get("No", 0))},
            {"label": "Departed Employees (Yes)", "value": int(attrition_counts.get("Yes", 0))}
        ],
        "department_breakdown": dept_data,
        "role_breakdown": role_data,
        "tenure_breakdown": tenure_data,
        "overtime_breakdown": overtime_data
    }


@app.get("/api/analytics/stayers-vs-leavers")
def get_stayers_vs_leavers():
    """Return comparative statistical metrics between employees who stayed vs left."""
    df = APP_CACHE.get("master_df")
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not loaded.")
    
    comp_df = compute_stayers_vs_leavers(df)
    comp_records = []
    for r in comp_df.to_dict(orient="records"):
        comp_records.append({
            "Metric": r["Metric"],
            "Stayers_Mean": r["StayersMean"],
            "Leavers_Mean": r["LeaversMean"],
            "Difference": f"{r['AbsoluteDifference']:+} ({r['PercentChange']}%)",
            "Interpretation": "Higher in Leavers" if r["AbsoluteDifference"] > 0 else "Lower in Leavers"
        })

    corrs = compute_correlations_with_target(df)
    insights_raw = generate_data_driven_insights(df)
    insights_text = [f"<strong>{i.get('category')}:</strong> {i.get('finding')} <em>Suggested Action: {i.get('action')}</em>" for i in insights_raw]

    return {
        "comparison_table": comp_records,
        "correlations": corrs.to_dict(orient="records"),
        "insights": insights_text
    }


class CalculatorRequest(BaseModel):
    opening_headcount: Optional[float] = None
    closing_headcount: Optional[float] = None
    exits: Optional[int] = None
    department: Optional[str] = "All"
    calculation_mode: str = "dataset"


@app.post("/api/calculator")
def run_attrition_calculator(req: CalculatorRequest):
    """Execute transparent average-headcount attrition formula."""
    df = APP_CACHE.get("master_df")

    if req.calculation_mode == "manual":
        if req.opening_headcount is None or req.closing_headcount is None or req.exits is None:
            raise HTTPException(status_code=400, detail="Manual mode requires opening_headcount, closing_headcount, and exits.")
        res = calculate_attrition_metrics(
            opening_headcount=req.opening_headcount,
            closing_headcount=req.closing_headcount,
            total_exits=req.exits
        )
        return {
            "attrition_rate_pct": res["attrition_rate_percent"],
            "source": "Manual Enterprise Input",
            "opening_headcount": res["opening_headcount"],
            "closing_headcount": res["closing_headcount"],
            "average_headcount": res["average_headcount"],
            "employees_left": res["total_exits"],
            "steps": res.get("calculation_steps", [])
        }

    if df is None:
        raise HTTPException(status_code=404, detail="Master dataset not available.")

    calc_df = df.copy()
    if req.department and req.department != "All" and "Department" in calc_df.columns:
        calc_df = calc_df[calc_df["Department"] == req.department]

    total_employees = len(calc_df)
    target_col, pos_label = identify_target_column(calc_df)
    exits_count = int((calc_df[target_col] == pos_label).sum()) if target_col else 0
    active_count = total_employees - exits_count

    res = calculate_attrition_metrics(
        opening_headcount=float(total_employees),
        closing_headcount=float(active_count),
        total_exits=exits_count
    )

    return {
        "attrition_rate_pct": res["attrition_rate_percent"],
        "source": "Observed Workforce Headcount (Cumulative)",
        "opening_headcount": res["opening_headcount"],
        "closing_headcount": res["closing_headcount"],
        "average_headcount": res["average_headcount"],
        "employees_left": res["total_exits"],
        "steps": res.get("calculation_steps", [])
    }


@app.get("/api/models/evaluation")
def get_model_evaluation():
    """Return held-out test evaluation benchmarks, cross-validation, and confusion matrices."""
    eval_res = APP_CACHE.get("evaluation_results")
    if not eval_res:
        raise HTTPException(status_code=404, detail="Model evaluation not computed yet.")

    comp_df = eval_res["comparison_df"]
    rf_details = eval_res["model_details"].get("Random Forest", {})
    lr_details = eval_res["model_details"].get("Logistic Regression", {})

    return {
        "best_model_name": eval_res["best_model_name"],
        "comparison_table": comp_df.to_dict(orient="records"),
        "test_sample_count": len(APP_CACHE["y_test"]) if APP_CACHE["y_test"] is not None else 500,
        "selected_model_confusion_matrix": rf_details.get("confusion_matrix_labels", {}),
        "selected_model_classification_report": rf_details.get("classification_report", {}),
        "logistic_regression_matrix": lr_details.get("confusion_matrix_labels", {}),
        "leakage_safeguards": {
            "excluded_post_exit_columns": LEAKAGE_AND_POST_EXIT_COLUMNS,
            "protected_demographics_excluded": SENSITIVE_DEMOGRAPHIC_COLUMNS,
            "validation_method": "Stratified 5-Fold Cross Validation strictly inside training folds"
        }
    }


class EmployeePredictionInput(BaseModel):
    Department: str = "Sales"
    BusinessUnit: Optional[str] = "B2C Quick Commerce"
    JobRole: str = "Sales Executive"
    JobLevel: int = 2
    Age: Optional[int] = 32
    MonthlySalaryINR: Optional[float] = 48000.0
    MonthlyIncome: Optional[float] = 48000.0
    TotalWorkingYears: float = 6.0
    YearsAtCompany: float = 2.0
    YearsInCurrentRole: float = 1.5
    YearsSinceLastPromotion: float = 2.0
    YearsWithCurrManager: Optional[float] = 1.0
    Overtime: Optional[str] = "Yes"
    OverTime: Optional[str] = "Yes"
    JobSatisfaction: int = 2
    EnvironmentSatisfaction: Optional[int] = 2
    WorkLifeBalance: int = 1
    RelationshipSatisfaction: Optional[int] = 3
    JobInvolvement: Optional[int] = 2
    PerformanceRating: Optional[int] = 3
    DistanceFromHomeKM: Optional[float] = 18.0
    NumCompaniesWorked: Optional[int] = 3
    TrainingTimesLastYear: Optional[int] = 1
    BurnoutRiskScore: Optional[float] = 58.0


@app.post("/api/predict/single")
def predict_single(emp: EmployeePredictionInput):
    """Predict attrition probability and risk band for a single employee."""
    pipe = APP_CACHE.get("trained_pipelines", {}).get("Random Forest")
    if not pipe:
        raise HTTPException(status_code=500, detail="Predictive model pipeline is not loaded.")

    emp_dict = emp.dict()
    # Normalize salary and overtime
    if "MonthlySalaryINR" in emp_dict and emp_dict["MonthlySalaryINR"] is not None:
        emp_dict["MonthlyIncome"] = emp_dict["MonthlySalaryINR"]
    else:
        emp_dict["MonthlySalaryINR"] = emp_dict.get("MonthlyIncome", 48000.0)

    if emp_dict.get("Overtime") is not None:
        emp_dict["OverTime"] = emp_dict["Overtime"]

    result = predict_single_employee(pipe, emp_dict)
    
    # Flatten drivers and actions for frontend
    drivers = [c.get("description", c.get("factor", "")) for c in result.get("contributing_factors", [])]
    actions = result.get("suggested_actions", [])

    return {
        "predicted_class": result["predicted_class"],
        "attrition_probability": result["attrition_probability"],
        "probability_percent": result["probability_percent"],
        "risk_band": result["risk_band"],
        "badge_class": result["badge_class"],
        "top_risk_drivers": drivers,
        "suggested_interventions": actions
    }


@app.get("/api/explainability")
def get_explainability():
    """Return top feature importances and permutation importance rankings."""
    perm_records = APP_CACHE.get("permutation_importance", [])

    return {
        "permutation_importance": perm_records,
        "causation_warning": (
            "Predictive association does NOT equal causation. Feature importances indicate "
            "variables that aid the model's classification accuracy across historical observations, "
            "not proven unilateral causes of resignation. HR interventions should be validated via "
            "controlled feedback and qualitative pulse surveys."
        )
    }


@app.get("/api/retention/strategies")
def get_retention_strategies():
    """Return evidence-based retention action plans."""
    df = APP_CACHE.get("master_df")
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not loaded.")
    
    strategies_raw = generate_retention_strategies(df)
    strategies = []
    for s in strategies_raw:
        strategies.append({
            "Observed_Issue": s.get("pillar"),
            "Dataset_Evidence": s.get("empirical_evidence"),
            "Target_Segment": s.get("target_segments"),
            "Suggested_Action": s.get("action_plan"),
            "Progress_KPI": f"{s.get('primary_kpi')} ({s.get('target_timeline')})"
        })
    return {"strategies": strategies}


class RoiRequest(BaseModel):
    high_risk_count: int = 150
    avg_annual_salary: float = 65000.0
    turnover_cost_pct: float = 1.5
    intervention_success_rate: float = 0.35
    intervention_cost_per_emp: float = 1800.0


@app.post("/api/retention/roi-simulator")
def simulate_retention_roi(req: RoiRequest):
    """Calculate financial ROI of targeted retention interventions."""
    cost_per_turnover = req.avg_annual_salary * req.turnover_cost_pct
    gross_exposure = req.high_risk_count * cost_per_turnover
    retained_count = int(round(req.high_risk_count * req.intervention_success_rate))
    total_program_cost = req.high_risk_count * req.intervention_cost_per_emp
    gross_turnover_savings = retained_count * cost_per_turnover
    net_savings = gross_turnover_savings - total_program_cost
    roi_pct = ((net_savings / total_program_cost) * 100.0) if total_program_cost > 0 else 0.0

    return {
        "gross_turnover_exposure_cost": gross_exposure,
        "projected_retained_employees": retained_count,
        "turnover_cost_per_employee": cost_per_turnover,
        "total_intervention_cost": total_program_cost,
        "gross_savings": gross_turnover_savings,
        "net_savings": net_savings,
        "roi_percentage": round(roi_pct, 1)
    }


@app.get("/api/experiments")
def get_experiment_history():
    """Return logged machine learning experiments from SQLite database."""
    df_exp = get_all_experiments()
    if df_exp.empty:
        return {"experiments": []}
    return {"experiments": df_exp.head(25).to_dict(orient="records")}


@app.get("/api/reports/download-html")
def download_html_report():
    """Generate and return styled HTML report."""
    df = APP_CACHE.get("master_df")
    eval_res = APP_CACHE.get("evaluation_results", {})
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not loaded.")

    kpis = compute_executive_kpis(df)
    insights = generate_data_driven_insights(df)
    strategies = generate_retention_strategies(df)
    md_content = generate_executive_markdown_report(kpis, eval_res, insights, strategies)

    # Render simple clean standalone HTML document
    html_page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Executive Report - Employee Attrition Analysis</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 40px auto; padding: 0 20px; color: #222; background: #fff; }}
h1, h2, h3 {{ color: #1c1917; }}
h1 {{ border-bottom: 2px solid #d97757; padding-bottom: 8px; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
th {{ background-color: #f7f3eb; color: #333; }}
code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
</style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: inherit;">{md_content}</pre>
</body>
</html>"""

    return HTMLResponse(
        content=html_page,
        headers={"Content-Disposition": "attachment; filename=Attrition_Analysis_Executive_Report.html"}
    )


@app.get("/api/reports/download-markdown")
def download_markdown_report():
    """Generate and return markdown audit report."""
    df = APP_CACHE.get("master_df")
    eval_res = APP_CACHE.get("evaluation_results", {})
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not loaded.")

    kpis = compute_executive_kpis(df)
    insights = generate_data_driven_insights(df)
    strategies = generate_retention_strategies(df)
    md_content = generate_executive_markdown_report(kpis, eval_res, insights, strategies)

    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=Attrition_Analysis_Report.md"}
    )


# -------------------------------------------------------------
# STATIC FILES & FRONTEND SERVING
# -------------------------------------------------------------
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    """Serve the primary HTML application interface."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>Application interface initializing...</h1>")
    return FileResponse(str(index_file))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
