# EMPLOYEES ATTRITION ANALYSIS
### *An Interactive HR Analytics and Machine Learning Decision Support System*
**MBA Business Analytics Capstone Project**  
**Enterprise Focus:** Quick-Commerce & High-Growth Technology Operations (*SnackRush Enterprise*)

---

## 📌 Executive Summary & Business Context

Unplanned employee turnover creates severe organizational friction, costing enterprises between **50% and 150% of an employee's annual salary** in direct recruitment, onboarding expenses, lost institutional knowledge, and operational delays. 

Traditional Human Resources teams operate reactively—conducting exit interviews only after resignation notices are tendered. This project builds an **End-to-End Decision Support System (DSS)** that bridges empirical workforce diagnostics, leakage-safe machine learning, transparent explainability, and strategic human capital planning.

---

## 🏛️ Application Architecture & Technology Stack

```
employees-attrition-analysis/
├── app.py                         # Streamlit multi-page application entry point
├── requirements.txt               # Locked production dependencies
├── README.md                      # Comprehensive academic & technical documentation
├── .gitignore                     # Repository exclusion configurations
├── config/
│   └── settings.py                # System parameters, color palettes, leakage exclusion lists
├── data/
│   └── attrition_analytics.db     # Persistent SQLite database (experiments, predictions, audit)
├── models/                        # Serialized Scikit-learn pipelines (.joblib)
├── styles/
│   └── custom.css                 # Custom enterprise CSS (warm cocoa, charcoal, copper palette)
├── src/
│   ├── data_loader.py             # Multi-sheet Excel & CSV caching data loader
│   ├── data_validation.py         # Schema mapping, validation rules, data quality profiling
│   ├── preprocessing.py           # Scikit-learn ColumnTransformer, train-test splitting
│   ├── feature_engineering.py     # HR domain ratios (OvertimeRatio, WorkloadBalanceIndex, etc.)
│   ├── attrition_analysis.py      # Multivariate cross-tabs, stayer-vs-leaver comparisons, insights
│   ├── attrition_calculator.py    # Standard workforce headcount & rate formulas
│   ├── model_training.py          # Stratified 5-Fold CV model training suite
│   ├── model_evaluation.py        # Held-out test evaluation, HR confusion matrix, threshold tuning
│   ├── prediction.py              # Single employee simulation & batch CSV inference
│   ├── explainability.py          # Tree feature importance, permutation importance, SHAP values
│   ├── retention_planner.py       # Evidence-based retention roadmaps & ROI simulator
│   ├── reporting.py               # Markdown and HTML executive report generator
│   └── database.py                # SQLite persistence interface
└── tests/
    ├── test_data_loader.py        # Data loading and fingerprinting unit tests
    ├── test_validation.py         # Schema profiling and quality check unit tests
    ├── test_leakage.py            # Data leakage and demographic exclusion tests
    ├── test_calculator.py         # Workforce formula mathematical tests
    ├── test_model_training.py     # Training, evaluation, and prediction tests
    └── test_edge_cases.py         # Edge cases, empty data, single-class tests
```

### Core Technologies
- **Frontend / Web App:** Streamlit with custom CSS (warm cocoa `#181513`, copper `#c86d51`, warm ivory `#f7f3eb`).
- **Data Analytics:** Pandas, NumPy, Plotly.
- **Machine Learning:** Scikit-learn (DummyClassifier, LogisticRegression, DecisionTreeClassifier, RandomForestClassifier, HistGradientBoostingClassifier).
- **Explainability:** Tree feature importance, test-set Permutation Importance, SHAP (SHapley Additive exPlanations).
- **Persistence:** SQLite for audit trails, experiment tracking, and prediction history.
- **Testing:** Pytest (23 automated test cases covering end-to-end functionality).

---

## 📊 Dataset Profile & Verification (*SnackRush Enterprise*)

The system operates natively on the verified **SnackRush Complete Dataset** (`SnackRush_Complete_Dataset.xlsx`, 2.65 MB):

| Sheet Name | Observations | Dimensions | Description |
| :--- | :--- | :--- | :--- |
| **Employee Master** | 2,500 | 70 columns | Full workforce master roster with demographic, compensation, satisfaction, and exit data |
| **Monthly History** | 26,115 | 16 columns | Longitudinal monthly observations across 12 operational months (Oct 2025 – Sep 2026) |
| **Satisfaction Survey**| 2,500 | 13 columns | Pre-exit climate survey ratings across 1-5 Likert scales and intent-to-leave scores |
| **Attrition Events** | 450 | 10 columns | Verified departure logs with exit dates, exit types, and exit reason categories |
| **KPI Summary** | 20 | 12 columns | Ground-truth department and city workforce rate benchmarks |
| **Data Dictionary** | 131 | 6 columns | Complete field definitions, scales, and intended analytical uses |
| **Quality Report** | 17 | 9 columns | Referential integrity passes across all cross-table relationships |

### Target Distribution
- **Active Personnel:** 2,050 employees (82.0%)
- **Exited Personnel:** 450 employees (18.0%)
- **Voluntary Exits:** 370 employees (14.8%)
- **Involuntary Exits:** 80 employees (3.2%)

---

## 🛡️ Data Leakage Prevention Protocol

Data leakage artificially inflates accuracy and renders models useless for real-world decision-making. We enforce an uncompromising data leakage prevention protocol:

1. **Cutoff Definition:** Prediction is defined as occurring during an active employee's regular review period prior to resignation.
2. **Outcome Synonyms Excluded:** `EmploymentStatus` ('Active' vs 'Exited') directly mirrors `Attrition` and is strictly excluded.
3. **Post-Exit Dates Excluded:** `ExitDate` is only populated upon departure; including it would constitute 100% artificial target leakage.
4. **Post-Exit Classifications Excluded:** `ExitType`, `AttritionCategory`, `ExitReasonCategory`, `TenureAtExitYears`, and `ExitInterviewCompleted` are captured during offboarding and are excluded from predictor features.
5. **Non-Predictive Keys Excluded:** `EmployeeID` is a non-predictive surrogate key.
6. **Collinear Variables Handled:** `AnnualSalaryINR` is an exact 12x replica of `MonthlySalaryINR` and is excluded.
7. **Protected Demographics:** `Gender`, `Age`, and `MaritalStatus` are excluded from operational prediction features to prevent proxy discrimination.
8. **Training-Only Preprocessing:** Imputation, standard scaling, and one-hot encoding are fitted strictly on training data folds.

---

## 🤖 Model Benchmark & Held-Out Performance Evaluation

Evaluated on a **stratified 20% held-out test partition (500 unseen employees: 410 Stayers, 90 Leavers)**:

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Primary Strategic Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Dummy (Baseline)** | 82.00% | 0.00% | 0.00% | 0.000 | 0.500 | 0.180 | Majority-class baseline; fails to detect any exits |
| **Logistic Regression** | 71.80% | 34.36% | **62.22%** | 0.443 | **0.733** | 0.445 | Broad-spectrum detection; captures 62% of all exits |
| **Decision Tree** | 59.20% | 25.85% | 67.78% | 0.374 | 0.683 | 0.362 | High false positives; low precision |
| **Random Forest (Selected)**| **80.20%** | **45.05%** | **45.56%** | **0.453** | **0.728** | **0.467** | **Optimal F1 & PR-AUC; best balance for intervention budgets** |
| **Gradient Boosting** | 82.60% | 52.46% | 35.56% | 0.424 | 0.726 | 0.436 | High precision; lower coverage of leavers |

### Contextual HR Confusion Matrix (Random Forest on 500 Test Employees)
- **True Negatives (Correctly identified stayers):** 360 employees
- **False Positives (Incorrectly flagged as leavers):** 50 employees (Retention check-in cost)
- **False Negatives (Missed departures):** 49 employees (Unplanned replacement cost)
- **True Positives (Correctly identified exits):** 41 employees (Actionable retention opportunities)

---

## 🧮 Workforce Attrition Rate Calculator Formulas

Conforming to international HR analytics standards:

$$\text{Average Headcount} = \frac{\text{Opening Headcount} + \text{Closing Headcount}}{2}$$

$$\text{Attrition Rate (\%)} = \left( \frac{\text{Total Exits During Reporting Period}}{\text{Average Headcount}} \right) \times 100$$

$$\text{Voluntary Attrition Rate (\%)} = \left( \frac{\text{Voluntary Resignations}}{\text{Average Headcount}} \right) \times 100$$

$$\text{Retention Rate (\%)} = 100\% - \text{Attrition Rate (\%)} \quad \text{or} \quad \left( \frac{\text{Closing Headcount} - \text{New Hires}}{\text{Opening Headcount}} \right) \times 100$$

---

## 💻 Installation & Quickstart Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Windows / macOS / Linux

### 1. Clone or Open Project Workspace
```powershell
cd "D:\Projects\Employee Attrtion Rate Analysis"
```

### 2. Install Production Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Run Automated Tests
```powershell
python -m pytest tests/ -v
```
*Expected: 23 passed.*

### 4. Launch Streamlit Web Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Deployment Instructions

### Option A: Streamlit Community Cloud
1. Push this repository to GitHub.
2. Log into [share.streamlit.io](https://share.streamlit.io).
3. Connect your repository, select branch `main`, and set the entry file to `app.py`.
4. Deploy. The platform will automatically install packages from `requirements.txt` and load `SnackRush_Complete_Dataset.xlsx`.

### Option B: Docker Container Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## ⚖️ Ethical AI & Governance Statement

1. **Advisory Decision Support:** Model predictions indicate aggregate probabilistic risk, not personal destiny.
2. **Prohibition of Adverse Employment Action:** Predictions must strictly never be utilized to terminate, demote, or discipline employees.
3. **Protected Classes:** Demographics (Gender, Age, Marital Status) are excluded from operational scoring to prevent historical bias propagation.
4. **Human-in-the-Loop:** All high-risk alerts are reviewed by qualified HR Business Partners for supportive, empathetic dialogue.

---
*Developed for MBA Business Analytics Capstone • SnackRush Enterprise Decision Support System*
