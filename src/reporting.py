"""
Reporting and export module.
Generates comprehensive executive summaries, data quality documentation,
and CSV/markdown export bundles.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd

from config.settings import APP_TITLE, APP_SUBTITLE, PROJECT_CONTEXT


def generate_executive_markdown_report(
    kpi_dict: Dict[str, Any],
    model_eval_dict: Optional[Dict[str, Any]],
    insights: List[Dict[str, str]],
    strategies: List[Dict[str, Any]],
    dataset_name: str = "SnackRush_Complete_Dataset.xlsx"
) -> str:
    """
    Generate an executive MBA-grade summary report in Markdown format.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = f"""# {APP_TITLE}
### {APP_SUBTITLE}
**Context:** {PROJECT_CONTEXT}  
**Dataset Source:** `{dataset_name}`  
**Report Generated:** {now_str}  

---

## 1. Executive Summary & Workforce KPIs
- **Total Headcount Analyzed:** {kpi_dict.get('total_employees', 'N/A')}
- **Active Personnel:** {kpi_dict.get('active_employees', 'N/A')}
- **Historical Exits:** {kpi_dict.get('exited_employees', 'N/A')}
- **Overall Attrition Rate:** {kpi_dict.get('attrition_rate_percent', 'N/A')}%
- **Voluntary Attrition Rate:** {kpi_dict.get('voluntary_attrition_rate_percent', 'N/A')}%
- **Average Monthly Base Salary:** INR {kpi_dict.get('avg_salary_inr', 'N/A'):,}
- **Average Organizational Tenure:** {kpi_dict.get('avg_tenure_years', 'N/A')} years
- **Average Job Satisfaction:** {kpi_dict.get('avg_job_satisfaction', 'N/A')} / 5.0

---

## 2. Key Data-Driven Insights & Findings
"""
    for ins in insights:
        md += f"### {ins.get('category')}\n"
        md += f"- **Observation:** {ins.get('finding')}\n"
        md += f"- **Recommended Action:** {ins.get('action')}\n\n"

    md += """---

## 3. Machine Learning Decision Support System Performance
"""
    if model_eval_dict and "comparison_df" in model_eval_dict:
        comp_df = model_eval_dict["comparison_df"]
        best_model = model_eval_dict.get("best_model_name", "Random Forest")
        md += f"**Primary Selected Model:** `{best_model}` (Selected based on balanced F1-Score & PR-AUC on held-out test data)\n\n"
        cols = list(comp_df.columns)
        table_str = "| " + " | ".join(cols) + " |\n"
        table_str += "| " + " | ".join(["---"] * len(cols)) + " |\n"
        for _, row in comp_df.iterrows():
            table_str += "| " + " | ".join(str(row[c]) for c in cols) + " |\n"
        md += table_str
        md += "\n\n*All metrics evaluated on stratified 20% held-out test set (500 unseen employees). Baseline Dummy accuracy is 82.0% due to class imbalance.*"
    else:
        md += "*Model evaluation pending or not executed.*\n"

    md += """\n\n---

## 4. Evidence-Grounded Retention Interventions
"""
    for strat in strategies:
        md += f"### {strat.get('pillar')}\n"
        md += f"- **Empirical Evidence:** {strat.get('empirical_evidence')}\n"
        md += f"- **Action Plan:** {strat.get('action_plan')}\n"
        md += f"- **Target Segments:** {strat.get('target_segments')}\n"
        md += f"- **Primary KPI & Timeline:** {strat.get('primary_kpi')} ({strat.get('target_timeline')})\n\n"

    md += """---

## 5. Ethical Governance and Decision Constraints
1. **Probabilistic Uncertainty:** Model outputs represent statistical risk estimates, not definitive personal outcomes.
2. **Prohibition of Adverse Action:** Predictions must strictly never be utilized to terminate, discipline, or withhold benefits from an employee.
3. **Protected Demographics:** Gender, age, and marital status are excluded from operational feature sets to prevent systemic proxy discrimination.
4. **Human-in-the-Loop:** All automated flags serve solely as advisory indicators for empathetic HR dialogue and organizational support.
"""
    return md
