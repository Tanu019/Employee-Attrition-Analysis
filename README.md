# 🔍 Attrition Lens · SnackRush Enterprise
### *Explainable HR Analytics, Leakage-Free Predictive Machine Learning & ROI-Driven Retention Platform*

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-32%20Passed%20(100%25)-8DD3A8?logo=pytest&logoColor=111315)](tests/)
[![Theme](https://img.shields.io/badge/Theme-Midnight%20Graphite%20%26%20Electric%20Lime-B8F34A?logoColor=111315)](static/css/style.css)
[![Architecture](https://img.shields.io/badge/Architecture-FastAPI%20%2B%20Vanilla%20SPA-83BFFF)](static/)
[![Governance](https://img.shields.io/badge/Governance-GDPR%20%7C%20DPDP%202023%20Compliant-F0C66B)](static/index.html)

**Product:** Attrition Lens  
**Enterprise Benchmark:** SnackRush Enterprise Solutions (Fictional Quick-Commerce & Food Logistics Network)  
**Core Purpose:** Transform reactive human capital departures into proactive, evidence-based retention decisions with explainable machine learning and financial ROI simulation.

---

## 📑 Table of Contents
- [Executive Overview](#-executive-overview)
- [Key Business Metrics](#-key-business-metrics)
- [System Architecture](#-system-architecture)
- [Workspace Modules](#-workspace-modules)
- [Dataset Profile & Verification](#-dataset-profile--verification)
- [Data Leakage Prevention Protocol](#-data-leakage-prevention-protocol)
- [Machine Learning Benchmark & Performance](#-machine-learning-benchmark--performance)
- [Workforce Attrition Calculator Formulas](#-workforce-attrition-calculator-formulas)
- [Ethical AI, Privacy & Data Governance](#-ethical-ai-privacy--data-governance)
- [REST API Reference](#-rest-api-reference)
- [Installation & Quickstart](#-installation--quickstart)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Repository Structure](#-repository-structure)
- [License & Acknowledgments](#-license--acknowledgments)

---

## 📌 Executive Overview

Unplanned employee turnover creates severe organizational friction, costing enterprises between **50% and 150% of an employee's annual salary** in direct recruitment, onboarding expenses, lost institutional knowledge, and operational delays.

Traditional Human Resources teams operate reactively—conducting exit interviews only after resignation notices are tendered. **Attrition Lens** transforms HR into a proactive, strategic decision center by bridging:
1. **Empirical Workforce Diagnostics:** Macro and granular analysis across 2,500 active and exited employees.
2. **Leakage-Safe Machine Learning:** Stratified 5-fold cross-validated classifiers audited against majority-class baselines.
3. **Transparent Explainability:** Global permutation rankings and local feature risk factor attribution.
4. **Actionable Retention Planning:** Intervention cost-benefit modeling and an interactive SQLite Action Plan Tracker.

---

## 📈 Key Business Metrics

| Metric | Benchmark Value | Analytical Meaning |
| :--- | :---: | :--- |
| **Total Monitored Personnel** | **2,500** | Full workforce headcount across 11 business units |
| **Active Employees (Stayers)** | **2,050 (82.0%)** | Current retained personnel |
| **Departed Employees (Leavers)** | **450 (18.0%)** | Historical departures (370 Voluntary, 80 Involuntary) |
| **Baseline Attrition Rate** | **18.00%** | Standard workforce turnover rate over 12 reporting months |
| **Highest Risk Department** | **Delivery Operations (24.8%)** | Driven by overtime burdens and high burnout risk scores |
| **Lowest Risk Department** | **Legal & Compliance (9.2%)** | High tenure stability, balanced compensation & work-life balance |
| **Production Model** | **Random Forest Classifier** | **ROC-AUC: 0.728 • F1: 0.453 • Precision: 45.1%** |
| **Turnover Cost Baseline** | **₹6.50 Lakhs / Exit** | Estimated average replacement cost per frontline/knowledge worker |

---

## 🏛️ System Architecture

Attrition Lens is architected as a high-performance, lightweight, full-stack enterprise web application:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USER BROWSER / CLIENT                           │
│   Landing Page (/)   │   SPA Platform (/app)   │   Streamlit (:8501)   │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ JSON REST API / WebSockets
┌────────────────────────────────────▼───────────────────────────────────┐
│                     FASTAPI APPLICATION SERVER                         │
│                    (server.py · Uvicorn Engine)                        │
│                                                                        │
│   /api/dataset/overview    /api/attrition/insights    /api/models/*   │
│   /api/predict             /api/retention/plans       /api/reports/*  │
└─────────────┬──────────────────────┬──────────────────────┬────────────┘
              │                      │                      │
┌─────────────▼─────────┐ ┌──────────▼──────────┐ ┌─────────▼────────────┐
│   ML INFERENCE ENGINE │ │ DATA ACCESS & ETL   │ │ PERSISTENCE (SQLite) │
│ • Scikit-learn Pipeline│ │ • Excel / CSV Loader │ │ • attrition_analytics│
│ • ColumnTransformer   │ │ • Quality Profiler  │ │   .db                │
│ • Random Forest (.joblib│ │ • Feature Engineering│ │ • Action Plans DB   │
│ • Threshold Optimizer │ │ • Leakage Exclusion │ │ • Audit Log Entries  │
└───────────────────────┘ └─────────────────────┘ └──────────────────────┘
```

---

## 🎛️ Workspace Modules

The single-page application (`/app`) provides five core navigation modules in the sidebar:

### 1. Overview (`mod-overview`)
- **Executive Header:** Live dataset status, verified record count, and production model indicator.
- **KPI Ribbon:** Total Employee Records, Exited Staff Count, Historical Attrition Rate, and Held-out Model ROC-AUC.
- **Visual Analytics:** Workforce status distribution donut and cross-department attrition comparison bar chart.
- **Automated Insights:** Real-time data-driven narrative summarizing critical department risk concentrations.

### 2. Attrition Analysis (`mod-attrition`)
- **Multivariate Breakdown:** Demographic, satisfaction, compensation, and tenure distributions.
- **Interactive Global Filters:** Department, job role, job level, work location, and tenure filters dynamically recalculating visualizations.
- **Deep-Dive Tab:** Stayer vs. Leaver comparative distributions, satisfaction radar metrics, and overtime burden correlation.
- **Headcount Calculator Tab:** Interactive calculator implementing standard international workforce formulas.

### 3. Prediction & Model (`mod-predictor`)
- **Live Simulator:** Real-time risk probability calculation with confidence intervals and contributing risk drivers.
- **Batch CSV Inference:** Upload workforce CSV files for instant scoring and risk tier tagging.
- **Model Benchmark Tab:** Side-by-side comparison of Random Forest, Gradient Boosting, Logistic Regression, Decision Tree, and Dummy baseline.
- **ROC & Precision-Recall Curves:** Multi-model comparison across test thresholds with interactive threshold cost optimizer.
- **Explainability:** Global permutation feature importance displaying the primary drivers of voluntary exits.

### 4. Retention Strategy (`mod-retention`)
- **Targeted Action Roadmaps:** Evidence-based organizational interventions tailored to high-risk roles.
- **Financial ROI Simulator:** Sliders for target headcount, average replacement cost, and intervention success rate to project net cost savings.
- **Interactive Action Plan Tracker:** Create, edit, and update retention initiatives backed by persistent SQLite storage.

### 5. Data & Reports (`mod-upload`)
- **Data Quality Engine:** Automated multi-point referential integrity checks (completeness, ranges, uniqueness).
- **Searchable Data Dictionary:** Interactive 70-field documentation with data types, descriptions, and sample values.
- **Executive Report Generation:** Exportable audit summaries in downloadable HTML and Markdown formats.

---

## 📊 Dataset Profile & Verification

Operating natively on the verified **SnackRush Complete Benchmark Dataset** (`SnackRush_Complete_Dataset.xlsx`, 2,500 employee records, 70 features):

| Sheet / Table | Records | Dimensions | Analytical Focus |
| :--- | :---: | :---: | :--- |
| **Employee Master** | 2,500 | 70 columns | Full personnel master roster (demographics, job roles, satisfaction, salaries) |
| **Monthly History** | 26,115 | 16 columns | Longitudinal monthly observations across 12 calendar months |
| **Satisfaction Survey** | 2,500 | 13 columns | Pre-exit climate survey scores across 1–5 Likert scales and flight intent |
| **Attrition Events** | 450 | 10 columns | Verified exit logs with exit dates, exit types, and categorized root causes |
| **KPI Summary** | 20 | 12 columns | Ground-truth department and operational city benchmark rates |
| **Data Dictionary** | 131 | 6 columns | Complete field definitions, data scales, and intended modeling usage |
| **Quality Report** | 17 | 9 columns | Referential integrity passes across all relational foreign keys |

---

## 🛡️ Data Leakage Prevention Protocol

Data leakage artificially inflates accuracy during training and renders models unreliable when deployed into production. Attrition Lens enforces an uncompromising 8-step protocol:

1. **Strict Temporal Cutoff:** Inference represents an active employee during a regular review period prior to any resignation event.
2. **Outcome Synonym Exclusion:** `EmploymentStatus` directly mirrors the target `Attrition` and is strictly excluded from feature sets.
3. **Post-Exit Timestamps Excluded:** `ExitDate` is only created upon departure; including it would create 100% artificial target leakage.
4. **Post-Exit Classifications Excluded:** `ExitType`, `AttritionCategory`, `ExitReasonCategory`, `TenureAtExitYears`, and `ExitInterviewCompleted` are collected exclusively during offboarding and are omitted from features.
5. **Non-Predictive Surrogate Keys:** `EmployeeID` is dropped to prevent memorization of index identifiers.
6. **Collinear Redundancy Removal:** `AnnualSalaryINR` is an exact mathematical 12× duplicate of `MonthlySalaryINR` and is excluded.
7. **Protected Demographics Excluded:** `Gender`, `Age`, and `MaritalStatus` are excluded from operational prediction features to prevent proxy discrimination.
8. **Pipeline Encapsulation:** Imputation, standard scaling, and one-hot encoding are fitted strictly on training data folds via `sklearn.compose.ColumnTransformer`.

---

## 🤖 Machine Learning Benchmark & Performance

Evaluated on a **stratified 20% held-out test partition (500 unseen employees: 410 Stayers, 90 Leavers)**:

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Strategic Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Dummy (Majority Class)** | 82.00% | 0.00% | 0.00% | 0.000 | 0.500 | 0.180 | Zero departure coverage; baseline sanity check |
| **Logistic Regression** | 71.80% | 34.36% | **62.22%** | 0.443 | **0.733** | 0.445 | Broad-spectrum detection; captures 62% of all exits |
| **Decision Tree** | 59.20% | 25.85% | 67.78% | 0.374 | 0.683 | 0.362 | High false positives; low operational precision |
| **Random Forest (Production)** | **80.20%** | **45.05%** | **45.56%** | **0.453** | **0.728** | **0.467** | **Optimal F1 & PR-AUC; best balance for intervention budgets** |
| **Gradient Boosting** | 82.60% | 52.46% | 35.56% | 0.424 | 0.726 | 0.436 | High precision; lower recall coverage |

### Operational HR Confusion Matrix (Random Forest on 500 Test Staff)
- **True Negatives:** 360 employees correctly predicted as stayers (no unnecessary intervention cost).
- **False Positives:** 50 employees flagged as flight risks (low-cost retention check-ins).
- **False Negatives:** 49 unflagged departures (unplanned replacement cost).
- **True Positives:** 41 departures successfully anticipated (actionable retention opportunities).

---

## 🧮 Workforce Attrition Calculator Formulas

Attrition Lens adheres to standard international workforce measurement formulas:

$$\text{Average Headcount} = \frac{\text{Opening Headcount} + \text{Closing Headcount}}{2}$$

$$\text{Attrition Rate (\%)} = \left( \frac{\text{Total Exits During Period}}{\text{Average Headcount}} \right) \times 100$$

$$\text{Voluntary Attrition Rate (\%)} = \left( \frac{\text{Voluntary Departures}}{\text{Average Headcount}} \right) \times 100$$

$$\text{Retention Rate (\%)} = 100\% - \text{Attrition Rate (\%)} = \left( \frac{\text{Closing Headcount} - \text{New Hires}}{\text{Opening Headcount}} \right) \times 100$$

---

## ⚖️ Ethical AI, Privacy & Data Governance

Attrition Lens incorporates strict privacy-by-design standards:
- **Regulatory Alignment:** Compliant with **GDPR Article 22** (human oversight on automated decisions) and the **India Digital Personal Data Protection (DPDP) Act 2023** (purpose limitation).
- **PII Redaction:** Direct personal identifiers are never displayed; employee IDs are masked as `EMP-***142`.
- **Strictly Advisory Use:** The platform must **never** be used for termination, demotion, or punitive personnel actions.
- **Demographic Exclusion:** Protected attributes (Age, Gender, Marital Status) are excluded from ML feature spaces to guarantee zero algorithmic discrimination.

---

## 🔌 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Cinematic SnackRush Enterprise company landing page |
| `GET` | `/app` | Main single-page application interface |
| `GET` | `/api/dataset/overview` | Headcount stats, data dictionary, and validation check report |
| `POST` | `/api/dataset/filter` | Multivariate filter endpoint with updated KPI summaries and chart JSON |
| `GET` | `/api/attrition/insights` | Automated natural language insights based on current dataset metrics |
| `GET` | `/api/attrition/deepdive` | Stayer vs. Leaver comparative distributions and correlations |
| `GET` | `/api/department/intelligence` | Department-level scorecards and risk rankings across all 11 business units |
| `GET` | `/api/employees` | Paginated employee directory with ethical PII masking |
| `GET` | `/api/models/evaluation` | Held-out benchmark metrics, confusion matrix, and ROC/PR curve points |
| `GET` | `/api/models/explainability` | Global permutation feature importance and local SHAP breakdowns |
| `POST` | `/api/predict` | Single employee risk simulation with contributing factor analysis |
| `POST` | `/api/predict/batch` | Batch CSV inference returning risk scores and tier tags |
| `GET` | `/api/retention/plans` | Fetch active retention action plans from SQLite persistence |
| `POST` | `/api/retention/plans` | Create a new retention action plan |
| `PATCH` | `/api/retention/plans/{id}` | Update status or notes of an existing retention plan |
| `GET` | `/api/reports/executive` | Generate structured markdown executive summary |

---

## 💻 Installation & Quickstart

### Prerequisites
- Python 3.10 to 3.13
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Tanu019/Employee-Attrition-Analysis.git
cd Employee-Attrition-Analysis
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Primary FastAPI Platform
```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```
- **Enterprise Landing Page:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Attrition Lens Application:** [http://127.0.0.1:8000/app](http://127.0.0.1:8000/app)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 5. Run the Companion Streamlit Interface (Optional)
```bash
streamlit run app.py
```
Access at [http://localhost:8501](http://localhost:8501).

---

## 🧪 Testing & Quality Assurance

The codebase includes an automated test suite verifying data loaders, leakage prevention rules, formula mathematics, ML model pipelines, and API endpoints:

```bash
python -m pytest tests/ -v
```

**Results:**
```
============================== test session starts ==============================
collected 32 items

tests/test_api_new_modules.py .........                                  [ 28%]
tests/test_calculator.py ...                                             [ 37%]
tests/test_data_loader.py ....                                           [ 50%]
tests/test_edge_cases.py ....                                            [ 62%]
tests/test_leakage.py ....                                               [ 75%]
tests/test_model_training.py ....                                        [ 87%]
tests/test_validation.py ....                                            [100%]

======================= 32 passed, 7 warnings in 36.38s =======================
```

---

## 📁 Repository Structure

```
Employee-Attrition-Analysis/
├── server.py                      # Primary FastAPI enterprise server & REST API
├── app.py                         # Companion Streamlit application entry point
├── requirements.txt               # Locked Python dependencies
├── README.md                      # Comprehensive project documentation
├── config/
│   └── settings.py                # System settings, color palettes & leakage exclusion lists
├── data/
│   ├── SnackRush_Complete_Dataset.xlsx # 2,500 record benchmark dataset
│   └── attrition_analytics.db     # SQLite persistence for retention plans & audit logs
├── models/                        # Serialized Scikit-learn models & preprocessors (.joblib)
├── src/
│   ├── data_loader.py             # Multi-sheet Excel & CSV caching data loader
│   ├── data_validation.py         # Schema profiling, validation rules & quality checks
│   ├── preprocessing.py           # Leakage-safe ColumnTransformer & train-test splitters
│   ├── feature_engineering.py     # HR domain indicators (BurnoutRisk, OvertimeRatio)
│   ├── attrition_analysis.py      # Multivariate cross-tabs & stayer-vs-leaver diagnostics
│   ├── attrition_calculator.py    # Standard workforce formula engine
│   ├── model_training.py          # Stratified 5-Fold CV training pipeline
│   ├── model_evaluation.py        # Held-out benchmark metrics, confusion matrix & ROC/PR curves
│   ├── prediction.py              # Single employee simulation & batch CSV inference
│   ├── explainability.py          # Global permutation importance & local feature attribution
│   ├── retention_planner.py       # Evidence-based roadmaps & ROI financial simulator
│   ├── reporting.py               # Markdown and HTML executive report generator
│   └── database.py                # SQLite database management interface
├── static/
│   ├── landing.html               # Cinematic company introduction page
│   ├── index.html                 # Attrition Lens single-page application interface
│   ├── css/
│   │   ├── landing.css            # Cinematic landing styling & atmospheric lighting
│   │   └── style.css              # Dark cocoa & terracotta design system with light theme toggle
│   └── js/
│       └── app.js                 # Frontend SPA controller, Plotly charts & dynamic filters
└── tests/
    ├── test_api_new_modules.py    # Integration tests for all REST endpoints & sidebar
    ├── test_calculator.py         # Mathematical tests for workforce formulas
    ├── test_data_loader.py        # Data loading and fingerprinting unit tests
    ├── test_edge_cases.py         # Edge cases, empty data & single-class resilience
    ├── test_leakage.py            # Target leakage & demographic exclusion tests
    ├── test_model_training.py     # Training, evaluation & inference pipeline tests
    └── test_validation.py         # Schema profiling and quality check tests
```

---

## 📄 License & Acknowledgments

- **License:** MIT License. Free for academic, educational, and organizational research use.
- **Dataset Attribution:** SnackRush Enterprise Benchmark Dataset, synthesized for workforce turnover analytics and retention planning.
- **Designed for:** Human Resources Executives, People Operations Partners, and Workforce Analytics Leaders.
