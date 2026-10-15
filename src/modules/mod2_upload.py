"""
Module 2: Data Upload & Validation.
Enables file uploads, structural inspection, data quality audit checks, and schema mapping.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any

from src.data_loader import load_workbook_data, compute_file_fingerprint
from src.data_validation import (
    perform_data_quality_checks,
    generate_data_dictionary,
    map_schema,
    identify_target_column
)


def render_module_upload(current_workbook: Dict[str, pd.DataFrame], current_fingerprint: str):
    """Render Module 2: Data Upload and Validation."""
    st.markdown("""
    <div class="content-card">
        <div class="card-title">📂 Data Upload, Inspection & Validation Engine</div>
        <div class="card-subtitle">
            Upload custom enterprise HR datasets (Excel or CSV) or audit the currently active SnackRush dataset.
            Every dataset undergoes automated structural validation, target discovery, and referential integrity auditing.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload control
    uploaded_file = st.file_uploader(
        "Upload Employee Dataset (.xlsx, .xls, .csv)",
        type=["xlsx", "xls", "csv"],
        help="Upload an employee roster or multi-sheet Excel file. Maximum file size: 50MB."
    )

    if uploaded_file is not None:
        try:
            file_bytes = uploaded_file.getvalue()
            new_workbook, new_fingerprint = load_workbook_data(uploaded_file)
            st.session_state["workbook"] = new_workbook
            st.session_state["fingerprint"] = new_fingerprint
            st.session_state["dataset_name"] = uploaded_file.name
            # Invalidate cached models if new dataset is loaded
            st.session_state["models_trained"] = False
            st.success(f"Successfully loaded '{uploaded_file.name}' (Fingerprint: {new_fingerprint})")
            st.rerun()
        except Exception as e:
            st.error(f"Error parsing uploaded file: {str(e)}")

    # Active dataset selection & sheet selector
    active_sheet = "Employee Master"
    sheet_names = list(current_workbook.keys())
    if len(sheet_names) > 1:
        col_sel, col_info = st.columns([2, 3])
        with col_sel:
            active_sheet = st.selectbox(
                "Select Workbook Sheet to Inspect:",
                sheet_names,
                index=sheet_names.index("Employee Master") if "Employee Master" in sheet_names else 0
            )
        with col_info:
            st.info(f"Active workbook contains **{len(sheet_names)} sheets**. Primary employee master sheet is used for predictive modeling.")

    df_active = current_workbook.get(active_sheet, next(iter(current_workbook.values())))

    # Run data quality checks on the active sheet
    quality_summary = perform_data_quality_checks(df_active)

    # Display KPI metric cards
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Total Observations</div>
            <div class="kpi-value">{quality_summary['total_rows']:,}</div>
            <div class="kpi-subtext">Active sheet rows</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Features / Columns</div>
            <div class="kpi-value">{quality_summary['total_cols']}</div>
            <div class="kpi-subtext">Recorded attributes</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Duplicate Records</div>
            <div class="kpi-value">{quality_summary['duplicate_rows']}</div>
            <div class="kpi-subtext">Identical rows detected</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Missing Values</div>
            <div class="kpi-value">{quality_summary['missing_pct']}%</div>
            <div class="kpi-subtext">{quality_summary['total_missing']:,} null cells</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Identified Target</div>
            <div class="kpi-value" style="font-size: 1.25rem; color: var(--accent-copper);">{quality_summary['target_col'] or 'None'}</div>
            <div class="kpi-subtext">Positive: {quality_summary['positive_label'] or 'N/A'} ({quality_summary['attrition_rate']}%)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🔍 Quality Audit Report", "📖 Data Dictionary", "📊 Schema Classification", "👀 Data Sample Preview"])

    with tabs[0]:
        st.markdown("#### Automated Quality & Integrity Checks")
        checks_df = quality_summary["checks_df"]
        
        # Color formatted results
        def highlight_status(val):
            if val == "PASS":
                return "color: #81c784; font-weight: bold;"
            elif val == "FAIL":
                return "color: #e57373; font-weight: bold;"
            elif val == "WARN":
                return "color: #ffb74d; font-weight: bold;"
            return "color: #aba398;"

        st.dataframe(checks_df.style.map(highlight_status, subset=["Result"]), use_container_width=True)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_report = checks_df.to_csv(index=False)
            st.download_button(
                "📥 Download Data Quality Audit Report (CSV)",
                data=csv_report,
                file_name=f"data_quality_report_{current_fingerprint}.csv",
                mime="text/csv"
            )
        with col_dl2:
            csv_cleaned = df_active.to_csv(index=False)
            st.download_button(
                "📥 Export Active Dataset (CSV)",
                data=csv_cleaned,
                file_name=f"active_dataset_{active_sheet.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )

    with tabs[1]:
        st.markdown("#### Dynamic Column Dictionary & Usage Guidelines")
        data_dict = generate_data_dictionary(df_active)
        search_term = st.text_input("Filter Dictionary by Column Name:", "")
        if search_term:
            data_dict = data_dict[data_dict["ColumnName"].str.contains(search_term, case=False)]
        st.dataframe(data_dict, use_container_width=True, height=400)

    with tabs[2]:
        st.markdown("#### Analytical Schema Categorization")
        schema_map = map_schema(df_active)
        for cat, cols in schema_map.items():
            if cols:
                badge_style = "badge-mod" if cat == "leakage_post_exit" else ("badge-neutral" if cat == "target" else "badge-low")
                st.markdown(f"**{cat.replace('_', ' ').title()}** ({len(cols)} columns):")
                st.write(", ".join([f"`{c}`" for c in cols]))

    with tabs[3]:
        st.markdown("#### First 15 Records")
        st.dataframe(df_active.head(15), use_container_width=True)
