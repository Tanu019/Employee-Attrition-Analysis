"""
Automated unit and integration tests for new People Intelligence API modules:
- Dynamic Insights API (/api/analytics/insights)
- Department Intelligence API (/api/department-intelligence)
- Employee Explorer API (/api/employees)
- Retention Action Plans CRUD API (/api/retention/action-plans)
- Analytical Charts Breakdowns (/api/analytics/charts)
"""
import pytest
from fastapi.testclient import TestClient
from server import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_dynamic_insights_endpoint(client):
    """Verify dynamic insights returns 5 data-grounded observations."""
    response = client.get("/api/analytics/insights")
    assert response.status_code == 200
    data = response.json()
    assert "insights" in data
    assert len(data["insights"]) == 5
    for ins in data["insights"]:
        assert "title" in ins
        assert "observation" in ins
        assert "supporting_metric" in ins
        assert "relevant_segment" in ins
        assert "implication" in ins


def test_department_intelligence_endpoint(client):
    """Verify department intelligence returns headcount, exit rates, and risk scores."""
    response = client.get("/api/department-intelligence")
    assert response.status_code == 200
    data = response.json()
    assert "departments" in data
    assert len(data["departments"]) >= 10
    for dept in data["departments"]:
        assert dept["Headcount"] > 0
        assert 0 <= dept["Attrition_Rate_Pct"] <= 100
        assert dept["Risk_Level"] in ["High Risk", "Moderate Risk", "Low Risk", "Stable"]


def test_employee_explorer_pagination_and_masking(client):
    """Verify employee records are properly paginated and IDs masked."""
    response = client.get("/api/employees?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 2500
    assert data["page_size"] == 10
    assert len(data["employees"]) == 10
    for emp in data["employees"]:
        assert emp["MaskedID"].startswith("EMP-***")
        assert "RawID" not in emp or emp["MaskedID"] != emp.get("RawID")
        assert emp["JobLevel"] in [1, 2, 3, 4, 5]


def test_employee_explorer_department_filter(client):
    """Verify employee filtering by department."""
    response = client.get("/api/employees?department=Sales&page=1&page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 174
    for emp in data["employees"]:
        assert emp["Department"] == "Sales"


def test_action_plans_crud_lifecycle(client):
    """Verify retention action plan creation, retrieval, and deletion."""
    # 1. Create plan
    new_plan = {
        "department": "Delivery Operations",
        "observed_issue": "Late night shift fatigue",
        "action_plan": "Implement rotating 8-hour shift rest policy",
        "owner": "Director Operations",
        "target_date": "2026-12-15",
        "status": "In Progress"
    }
    create_res = client.post("/api/retention/action-plans", json=new_plan)
    assert create_res.status_code == 200
    plan_id = create_res.json()["plan_id"]
    assert plan_id is not None

    # 2. Retrieve plans
    get_res = client.get("/api/retention/action-plans")
    assert get_res.status_code == 200
    plans = get_res.json()["action_plans"]
    matching = [p for p in plans if p["plan_id"] == plan_id]
    assert len(matching) == 1
    assert matching[0]["department"] == "Delivery Operations"
    assert matching[0]["status"] == "In Progress"

    # 3. Delete plan
    del_res = client.delete(f"/api/retention/action-plans/{plan_id}")
    assert del_res.status_code == 200

    # 4. Confirm deleted
    get_res_after = client.get("/api/retention/action-plans")
    plans_after = get_res_after.json()["action_plans"]
    assert not any(p["plan_id"] == plan_id for p in plans_after)


def test_analytics_charts_breakdowns(client):
    """Verify charts endpoint provides monthly trend, salary band, and satisfaction breakdown."""
    response = client.get("/api/analytics/charts?department=All&job_role=All")
    assert response.status_code == 200
    data = response.json()
    assert "monthly_trend" in data
    assert len(data["monthly_trend"]) > 10
    assert "salary_breakdown" in data
    assert len(data["salary_breakdown"]) > 0
    assert "satisfaction_breakdown" in data
    assert len(data["satisfaction_breakdown"]) == 5
    assert "job_level_breakdown" in data
    assert len(data["job_level_breakdown"]) == 5


def test_dataset_upload_and_reset_lifecycle(client):
    """Verify custom dataset upload and reset to benchmark defaults."""
    # Test valid CSV upload
    csv_content = (
        "EmployeeID,Department,JobRole,JobLevel,MonthlySalaryINR,YearsAtCompany,JobSatisfaction,WorkLifeBalance,Overtime,Attrition\n"
        "EMP-9001,Delivery Operations,Delivery Coordinator,2,32000,1.5,2,1,Yes,Yes\n"
        "EMP-9002,Sales,Sales Executive,2,45000,3.0,4,3,No,No\n"
        "EMP-9003,Technology,Software Engineer,3,78000,4.5,4,4,No,No\n"
    )
    files = {"file": ("custom_test_upload.csv", csv_content.encode("utf-8"), "text/csv")}
    upload_res = client.post("/api/dataset/upload", files=files)
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    assert upload_data["status"] == "success"
    assert upload_data["rows"] == 3
    assert upload_data["columns"] == 10
    assert upload_data["target_col"] == "Attrition"

    # Verify overview reflects uploaded dataset
    ov_res = client.get("/api/dataset/overview")
    assert ov_res.status_code == 200
    assert ov_res.json()["dataset_name"] == "custom_test_upload.csv"

    # Reset back to default SnackRush dataset
    reset_res = client.post("/api/dataset/reset-default")
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "success"
    assert reset_res.json()["rows"] == 2500

    # Verify restored master dataset
    ov_restored = client.get("/api/dataset/overview")
    assert ov_restored.status_code == 200
    assert ov_restored.json()["dataset_name"] == "SnackRush_Complete_Dataset.xlsx"


def test_landing_page_and_app_routes(client):
    """Verify separate landing page and executive dashboard route separation."""
    # 1. Root route serves cinematic landing page
    res_root = client.get("/")
    assert res_root.status_code == 200
    root_text = res_root.text
    assert "SnackRush" in root_text
    assert "Enterprise Solutions" in root_text
    assert "PEOPLE · PERFORMANCE · POSSIBILITIES" in root_text
    assert "Every business runs on people." in root_text
    assert "Understand" in root_text
    assert "yours better." in root_text
    assert "Enter People Intelligence" in root_text

    # 2. /landing serves landing page
    res_landing = client.get("/landing")
    assert res_landing.status_code == 200
    assert "Every business runs on people." in res_landing.text

    # 3. /app and /dashboard serve full executive platform
    res_app = client.get("/app")
    assert res_app.status_code == 200
    assert "mod-overview" in res_app.text
    assert "mod-predictor" in res_app.text
    assert "mod-upload" in res_app.text

    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert "mod-overview" in res_dash.text


def test_attrition_lens_executive_dashboard(client):
    """Verify redesigned minimal Attrition Lens overview page on /app and /dashboard."""
    res = client.get("/app")
    assert res.status_code == 200
    html = res.text

    # 1. Identity & Company Introduction
    assert "Attrition Lens" in html
    assert "SnackRush Enterprise Solutions" in html
    assert "quick-commerce and food-delivery" in html
    assert "analyzes employee attrition and supports retention decisions" in html

    # 2. Four Responsive KPI Cards
    assert "kpi-headcount" in html
    assert "kpi-leavers" in html
    assert "kpi-rate" in html
    assert "kpi-model-eval-stat" in html

    # 3. Two Core Analytics Visualizations
    assert "Workforce Distribution" in html
    assert "chart-overall-dist" in html
    assert "kpi-stayers" in html
    assert "Department Attrition Comparison" in html
    assert "chart-dept-attrition" in html

    # 4. Calculated Insight from Active Dataset & Link
    assert "CALCULATED DATASET INSIGHT" in html
    assert "overview-insight-title" in html
    assert "overview-insight-body" in html
    assert "Explore Full Attrition Analysis" in html

    # 5. Verified Removals from Overview
    assert "EXECUTIVE COMMAND CENTER" not in html
    assert "hero-workforce-canvas" not in html
    assert "lens-top-dept-cards" not in html

    # 6. Advanced Filters relocated to Attrition Analysis
    assert 'id="filter-dept"' in html
    assert 'id="filter-role"' in html
    assert 'id="filter-level"' in html
    assert 'id="filter-location"' in html
    assert 'id="filter-tenure"' in html

    # 7. Enhanced Sidebar Branding & Dynamic Status Card
    assert "WORKSPACE" in html
    assert "SnackRush Enterprise" in html
    assert "sidebar-status-card" in html
    assert "sidebar-workspace-title" in html
    assert "sidebar-record-count" in html
    assert "sidebar-model-status" in html



