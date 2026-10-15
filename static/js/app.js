/**
 * EMPLOYEES ATTRITION ANALYSIS - MODERN WEB APPLICATION CONTROLLER
 * Handles tab navigation, asynchronous API integration, Plotly chart rendering,
 * real-time predictions, workforce calculations, and report downloads.
 */

const THEME = {
  copper: '#d97757',
  copperHover: '#e68c6e',
  emerald: '#10b981',
  amber: '#f59e0b',
  crimson: '#ef4444',
  sapphire: '#6366f1',
  bgCard: '#201c18',
  bgSidebar: '#181512',
  borderCard: '#3d332a',
  textPrimary: '#faf6ee',
  textSecondary: '#ded6c8',
  textMuted: '#9c9183',
  fontFamily: "'Plus Jakarta Sans', sans-serif"
};

class AttritionApp {
  constructor() {
    this.currentView = 'mod-dashboard';
    this.filterOptions = { departments: [], roles: [] };
    this.cachedData = {};
    this.chartsRendered = false;
  }

  async init() {
    console.log("Initializing Attrition Analytics Web Application...");
    this.setupNavigation();
    if (window.lucide) {
      window.lucide.createIcons();
    }

    try {
      await this.loadInitialData();
      await this.applyDashboardFilters();
      this.loadDeepDiveData();
      this.loadModelEvaluationData();
      this.loadExplainabilityData();
      this.loadRetentionData();
      this.loadExperimentHistory();
      this.executeCalculator();
      this.calculateRoi();
    } catch (err) {
      console.error("Initialization error:", err);
    }
  }

  setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        const targetId = item.getAttribute('data-target');
        this.switchView(targetId);
      });
    });
  }

  switchView(viewId) {
    if (!viewId) return;
    this.currentView = viewId;

    // Update active nav state
    document.querySelectorAll('.nav-item').forEach(item => {
      if (item.getAttribute('data-target') === viewId) {
        item.classList.add('active');
        const titleEl = document.getElementById('top-header-title');
        if (titleEl) {
          titleEl.textContent = item.textContent.trim();
        }
      } else {
        item.classList.remove('active');
      }
    });

    // Update active section
    document.querySelectorAll('.view-section').forEach(sec => {
      if (sec.id === viewId) {
        sec.classList.add('active');
      } else {
        sec.classList.remove('active');
      }
    });

    // Trigger chart resize when switching to dashboard or deepdive
    setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
    }, 100);
  }

  async loadInitialData() {
    // 1. Overview and Data Dictionary
    const res = await fetch('/api/dataset/overview');
    if (res.ok) {
      const data = await res.json();
      this.cachedData.overview = data;
      this.renderDataDictionary(data.data_dictionary);
      this.populateFilterDropdowns(data.filter_options);
    }
  }

  populateFilterDropdowns(filterOptions) {
    const deptSelect = document.getElementById('filter-dept');
    const roleSelect = document.getElementById('filter-role');
    const calcDeptSelect = document.getElementById('calc-dept-select');

    if (deptSelect && filterOptions.departments) {
      deptSelect.innerHTML = filterOptions.departments
        .map(d => `<option value="${d}">${d === 'All' ? 'All Departments' : d}</option>`)
        .join('');
    }

    if (calcDeptSelect && filterOptions.departments) {
      calcDeptSelect.innerHTML = filterOptions.departments
        .map(d => `<option value="${d}">${d === 'All' ? 'Entire Organization (All Departments)' : d}</option>`)
        .join('');
    }

    if (roleSelect && filterOptions.roles) {
      roleSelect.innerHTML = filterOptions.roles
        .map(r => `<option value="${r}">${r === 'All' ? 'All Job Roles' : r}</option>`)
        .join('');
    }
  }

  renderDataDictionary(dictRecords) {
    const tbody = document.getElementById('data-dict-body');
    if (!tbody || !dictRecords) return;

    tbody.innerHTML = dictRecords.map(row => `
      <tr>
        <td><strong>${row.Column_Name}</strong></td>
        <td><code>${row.Data_Type}</code></td>
        <td>${row.Non_Null_Count.toLocaleString()}</td>
        <td>${row.Unique_Values.toLocaleString()}</td>
        <td style="max-width:240px; overflow:hidden; text-overflow:ellipsis;" title="${row.Sample_Values}">${row.Sample_Values}</td>
        <td><span class="badge badge-low">${row.Analytical_Category}</span></td>
      </tr>
    `).join('');
  }

  async applyDashboardFilters() {
    const dept = document.getElementById('filter-dept')?.value || 'All';
    const role = document.getElementById('filter-role')?.value || 'All';
    const tenure = document.getElementById('filter-tenure')?.value || 'All';

    // Fetch KPIs
    const kpiUrl = `/api/analytics/kpis?department=${encodeURIComponent(dept)}&job_role=${encodeURIComponent(role)}&tenure_band=${encodeURIComponent(tenure)}`;
    const kpiRes = await fetch(kpiUrl);
    if (kpiRes.ok) {
      const data = await kpiRes.json();
      this.renderKpiCards(data.kpis, data.filtered_count, data.total_count);
    }

    // Fetch Charts
    const chartUrl = `/api/analytics/charts?department=${encodeURIComponent(dept)}&job_role=${encodeURIComponent(role)}`;
    const chartRes = await fetch(chartUrl);
    if (chartRes.ok) {
      const chartData = await chartRes.json();
      this.renderDashboardCharts(chartData);
    }
  }

  resetDashboardFilters() {
    if (document.getElementById('filter-dept')) document.getElementById('filter-dept').value = 'All';
    if (document.getElementById('filter-role')) document.getElementById('filter-role').value = 'All';
    if (document.getElementById('filter-tenure')) document.getElementById('filter-tenure').value = 'All';
    this.applyDashboardFilters();
  }

  renderKpiCards(kpis, filteredCount, totalCount) {
    document.getElementById('kpi-headcount').textContent = kpis.Total_Employees.toLocaleString();
    document.getElementById('kpi-headcount-sub').textContent = filteredCount < totalCount ? `Filtered from ${totalCount}` : `Entire Workforce`;
    document.getElementById('kpi-leavers').textContent = kpis.Employees_Who_Left.toLocaleString();
    document.getElementById('kpi-rate').textContent = `${kpis.Overall_Attrition_Rate_Pct}%`;
    document.getElementById('kpi-stayers').textContent = kpis.Active_Employees.toLocaleString();
    
    if (kpis.Average_Salary) {
      document.getElementById('kpi-salary').textContent = `$${Math.round(kpis.Average_Salary).toLocaleString()}`;
    }
    if (kpis.Average_Tenure_Years) {
      document.getElementById('kpi-tenure').textContent = `${kpis.Average_Tenure_Years} Yrs`;
    }
    if (kpis.Model_Accuracy_Pct) {
      document.getElementById('kpi-model-acc').textContent = `${kpis.Model_Accuracy_Pct}%`;
    }
    if (kpis.Model_F1_Score) {
      document.getElementById('kpi-model-f1').textContent = `${kpis.Model_F1_Score}`;
    }
  }

  renderDashboardCharts(data) {
    const defaultLayout = {
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { color: THEME.textSecondary, family: THEME.fontFamily, size: 12 },
      margin: { l: 45, r: 25, t: 30, b: 45 },
      showlegend: false
    };

    // 1. Overall Distribution Donut
    if (data.overall_distribution && document.getElementById('chart-overall-dist')) {
      const labels = data.overall_distribution.map(d => d.label);
      const values = data.overall_distribution.map(d => d.value);
      const donutData = [{
        labels: labels,
        values: values,
        type: 'pie',
        hole: 0.58,
        marker: { colors: [THEME.emerald, THEME.crimson] },
        textinfo: 'label+percent',
        hoverinfo: 'label+value+percent'
      }];
      const donutLayout = {
        ...defaultLayout,
        showlegend: false,
        margin: { l: 20, r: 20, t: 20, b: 20 }
      };
      Plotly.newPlot('chart-overall-dist', donutData, donutLayout, { responsive: true, displayModeBar: false });
    }

    // 2. Department Breakdown
    if (data.department_breakdown && document.getElementById('chart-dept-attrition')) {
      const sorted = [...data.department_breakdown].sort((a, b) => b.Attrition_Rate_Pct - a.Attrition_Rate_Pct);
      const depts = sorted.map(d => d.Department);
      const rates = sorted.map(d => d.Attrition_Rate_Pct);
      const deptData = [{
        x: depts,
        y: rates,
        type: 'bar',
        marker: { color: THEME.copper },
        text: rates.map(r => `${r}%`),
        textposition: 'auto'
      }];
      const deptLayout = {
        ...defaultLayout,
        yaxis: { title: 'Attrition Rate (%)', gridcolor: THEME.borderCard },
        xaxis: { tickangle: -25 }
      };
      Plotly.newPlot('chart-dept-attrition', deptData, deptLayout, { responsive: true, displayModeBar: false });
    }

    // 3. Role Breakdown
    if (data.role_breakdown && document.getElementById('chart-role-attrition')) {
      const sorted = [...data.role_breakdown].sort((a, b) => a.Attrition_Rate_Pct - b.Attrition_Rate_Pct).slice(-8);
      const roles = sorted.map(d => d.JobRole);
      const rates = sorted.map(d => d.Attrition_Rate_Pct);
      const roleData = [{
        x: rates,
        y: roles,
        type: 'bar',
        orientation: 'h',
        marker: { color: THEME.crimson },
        text: rates.map(r => `${r}%`),
        textposition: 'auto'
      }];
      const roleLayout = {
        ...defaultLayout,
        margin: { l: 140, r: 25, t: 20, b: 40 },
        xaxis: { title: 'Attrition Rate (%)', gridcolor: THEME.borderCard }
      };
      Plotly.newPlot('chart-role-attrition', roleData, roleLayout, { responsive: true, displayModeBar: false });
    }

    // 4. Overtime Impact
    if (data.overtime_breakdown && document.getElementById('chart-overtime-attrition')) {
      const ots = data.overtime_breakdown.map(d => d.OverTime === 'Yes' ? 'Overtime (Yes)' : 'Standard Hours (No)');
      const rates = data.overtime_breakdown.map(d => d.AttritionRate);
      const otData = [{
        x: ots,
        y: rates,
        type: 'bar',
        marker: { color: [THEME.crimson, THEME.emerald] },
        text: rates.map(r => `${r}%`),
        textposition: 'auto'
      }];
      const otLayout = {
        ...defaultLayout,
        yaxis: { title: 'Attrition Rate (%)', gridcolor: THEME.borderCard }
      };
      Plotly.newPlot('chart-overtime-attrition', otData, otLayout, { responsive: true, displayModeBar: false });
    }

    // 5. Tenure Breakdown
    if (data.tenure_breakdown && document.getElementById('chart-tenure-attrition')) {
      const tenures = data.tenure_breakdown.map(d => d.TenureBand);
      const rates = data.tenure_breakdown.map(d => d.Attrition_Rate_Pct);
      const tenureData = [{
        x: tenures,
        y: rates,
        type: 'bar',
        marker: { color: THEME.copper },
        text: rates.map(r => `${r}%`),
        textposition: 'auto'
      }];
      const tenureLayout = {
        ...defaultLayout,
        yaxis: { title: 'Attrition Rate (%)', gridcolor: THEME.borderCard },
        xaxis: { title: 'Tenure Group' }
      };
      Plotly.newPlot('chart-tenure-attrition', tenureData, tenureLayout, { responsive: true, displayModeBar: false });
    }
  }

  async loadDeepDiveData() {
    const res = await fetch('/api/analytics/stayers-vs-leavers');
    if (!res.ok) return;
    const data = await res.json();

    // 1. Comparison Table
    const tbody = document.getElementById('comparison-stats-body');
    if (tbody && data.comparison_table) {
      tbody.innerHTML = data.comparison_table.map(row => `
        <tr>
          <td><strong>${row.Metric}</strong></td>
          <td style="color:var(--status-emerald); font-weight:600;">${row.Stayers_Mean}</td>
          <td style="color:var(--status-crimson); font-weight:600;">${row.Leavers_Mean}</td>
          <td>${row.Difference}</td>
          <td style="color:var(--text-muted); font-size:0.8rem;">${row.Interpretation || 'Observed divergence'}</td>
        </tr>
      `).join('');
    }

    // 2. Correlation Bars
    if (data.correlations && document.getElementById('chart-correlation-bars')) {
      const topCorrs = data.correlations.slice(0, 10);
      const vars = topCorrs.map(c => c.Feature);
      const vals = topCorrs.map(c => c.Correlation);
      const corrData = [{
        x: vals,
        y: vars,
        type: 'bar',
        orientation: 'h',
        marker: {
          color: vals.map(v => v >= 0 ? THEME.crimson : THEME.emerald)
        }
      }];
      const corrLayout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: THEME.textSecondary, family: THEME.fontFamily, size: 11 },
        margin: { l: 140, r: 25, t: 20, b: 40 },
        xaxis: { title: 'Correlation with Attrition', gridcolor: THEME.borderCard }
      };
      Plotly.newPlot('chart-correlation-bars', corrData, corrLayout, { responsive: true, displayModeBar: false });
    }

    // 3. Dynamic Insights
    const insightsList = document.getElementById('dynamic-insights-list');
    if (insightsList && data.insights) {
      insightsList.innerHTML = data.insights.map(ins => `
        <div style="background-color:var(--bg-sidebar); border-left:3px solid var(--accent-copper); padding:12px 16px; border-radius:0 6px 6px 0; font-size:0.86rem; color:var(--text-secondary);">
          ${ins}
        </div>
      `).join('');
    }
  }

  toggleCalcMode() {
    const mode = document.getElementById('calc-source-mode').value;
    const datasetInputs = document.getElementById('calc-dataset-inputs');
    const manualInputs = document.getElementById('calc-manual-inputs');

    if (mode === 'manual') {
      datasetInputs.style.display = 'none';
      manualInputs.style.display = 'block';
    } else {
      datasetInputs.style.display = 'block';
      manualInputs.style.display = 'none';
    }
  }

  async executeCalculator() {
    const mode = document.getElementById('calc-source-mode')?.value || 'dataset';
    let body = { calculation_mode: mode };

    if (mode === 'manual') {
      body.opening_headcount = parseFloat(document.getElementById('calc-in-opening').value);
      body.closing_headcount = parseFloat(document.getElementById('calc-in-closing').value);
      body.exits = parseInt(document.getElementById('calc-in-exits').value);
    } else {
      body.department = document.getElementById('calc-dept-select')?.value || 'All';
    }

    try {
      const res = await fetch('/api/calculator', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (res.ok) {
        const out = await res.json();
        document.getElementById('calc-res-rate').textContent = `${out.attrition_rate_pct}%`;
        document.getElementById('calc-res-source').textContent = out.source || '';
        document.getElementById('calc-res-opening').textContent = Math.round(out.opening_headcount).toLocaleString();
        document.getElementById('calc-res-closing').textContent = Math.round(out.closing_headcount).toLocaleString();
        document.getElementById('calc-res-avg').textContent = out.average_headcount.toLocaleString();
        document.getElementById('calc-res-exits').textContent = out.employees_left.toLocaleString();
      }
    } catch (e) {
      console.error('Calculator execution error:', e);
    }
  }

  async loadModelEvaluationData() {
    const res = await fetch('/api/models/evaluation');
    if (!res.ok) return;
    const data = await res.json();

    // Table
    const tbody = document.getElementById('models-comparison-body');
    if (tbody && data.comparison_table) {
      tbody.innerHTML = data.comparison_table.map(row => {
        const isBest = row.Model === 'Random Forest';
        const isBaseline = row.Model.includes('Dummy');
        return `
          <tr style="${isBest ? 'background:rgba(217,119,87,0.08); font-weight:600;' : ''}">
            <td>
              ${row.Model}
              ${isBest ? ' <span class="badge badge-low">Selected Model</span>' : ''}
              ${isBaseline ? ' <span class="badge badge-high">Naive Baseline</span>' : ''}
            </td>
            <td>${(row.Accuracy * 100).toFixed(1)}%</td>
            <td>${(row.Precision * 100).toFixed(1)}%</td>
            <td>${(row.Recall * 100).toFixed(1)}%</td>
            <td><strong>${row.F1_Score.toFixed(4)}</strong></td>
            <td>${isNaN(row.ROC_AUC) ? 'N/A' : row.ROC_AUC.toFixed(4)}</td>
            <td>${isNaN(row.PR_AUC) ? 'N/A' : row.PR_AUC.toFixed(4)}</td>
            <td>${isBest ? 'Optimal balance of Precision/Recall' : (isBaseline ? 'Exposes Accuracy Paradox' : 'Evaluated')}</td>
          </tr>
        `;
      }).join('');
    }

    // Confusion Matrix
    if (data.selected_model_confusion_matrix) {
      const cm = data.selected_model_confusion_matrix;
      document.getElementById('cm-tp').textContent = cm.true_positives.count;
      document.getElementById('cm-fn').textContent = cm.false_negatives.count;
      document.getElementById('cm-fp').textContent = cm.false_positives.count;
      document.getElementById('cm-tn').textContent = cm.true_negatives.count;
    }
  }

  async predictSingleEmployee() {
    const payload = {
      Department: document.getElementById('p-dept').value,
      JobRole: document.getElementById('p-role').value,
      JobLevel: parseInt(document.getElementById('p-level').value),
      MonthlyIncome: parseFloat(document.getElementById('p-salary').value),
      YearsAtCompany: parseFloat(document.getElementById('p-tenure').value),
      TotalWorkingYears: parseFloat(document.getElementById('p-total-exp').value),
      OverTime: document.getElementById('p-overtime').value,
      JobSatisfaction: parseInt(document.getElementById('p-job-sat').value),
      WorkLifeBalance: parseInt(document.getElementById('p-wlb').value),
      DistanceFromHomeKM: parseFloat(document.getElementById('p-distance').value),
      YearsInCurrentRole: parseFloat(document.getElementById('p-role-tenure').value),
      YearsSinceLastPromotion: parseFloat(document.getElementById('p-promo-years').value)
    };

    try {
      const res = await fetch('/api/predict/single', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const out = await res.json();
        this.renderPredictionResult(out);
      }
    } catch (err) {
      console.error('Prediction failed:', err);
    }
  }

  renderPredictionResult(res) {
    const panel = document.getElementById('prediction-result-panel');
    panel.style.display = 'flex';

    const probValueEl = document.getElementById('pred-prob-value');
    const badgeEl = document.getElementById('pred-risk-badge');
    const pct = (res.attrition_probability * 100).toFixed(1);

    probValueEl.textContent = `${pct}%`;

    badgeEl.textContent = res.risk_band;
    if (res.risk_band === 'High Risk') {
      badgeEl.className = 'badge badge-high';
      probValueEl.style.color = THEME.crimson;
    } else if (res.risk_band === 'Moderate Risk') {
      badgeEl.className = 'badge badge-mod';
      probValueEl.style.color = THEME.amber;
    } else {
      badgeEl.className = 'badge badge-low';
      probValueEl.style.color = THEME.emerald;
    }

    // Factors list
    const factorsList = document.getElementById('pred-factors-list');
    factorsList.innerHTML = (res.top_risk_drivers || []).map(f => `<li>${f}</li>`).join('');

    // Actions list
    const actionsList = document.getElementById('pred-actions-list');
    actionsList.innerHTML = (res.suggested_interventions || []).map(a => `<li>${a}</li>`).join('');

    // Scroll smoothly to result
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  resetPredictionForm() {
    document.getElementById('single-pred-form').reset();
    document.getElementById('prediction-result-panel').style.display = 'none';
  }

  async loadExplainabilityData() {
    const res = await fetch('/api/explainability');
    if (!res.ok) return;
    const data = await res.json();

    if (data.permutation_importance && document.getElementById('chart-permutation-importance')) {
      const topFeats = data.permutation_importance.slice(0, 10).reverse();
      const names = topFeats.map(f => f.Feature);
      const imps = topFeats.map(f => f.Importance_Mean);

      const pData = [{
        x: imps,
        y: names,
        type: 'bar',
        orientation: 'h',
        marker: { color: THEME.copper },
        text: imps.map(v => v.toFixed(4)),
        textposition: 'auto'
      }];
      const pLayout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: THEME.textSecondary, family: THEME.fontFamily, size: 12 },
        margin: { l: 180, r: 25, t: 20, b: 40 },
        xaxis: { title: 'Mean Drop in Test ROC-AUC', gridcolor: THEME.borderCard }
      };
      Plotly.newPlot('chart-permutation-importance', pData, pLayout, { responsive: true, displayModeBar: false });
    }
  }

  async loadRetentionData() {
    const res = await fetch('/api/retention/strategies');
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.getElementById('retention-strategies-body');
    if (tbody && data.strategies) {
      tbody.innerHTML = data.strategies.map(s => `
        <tr>
          <td><strong>${s.Observed_Issue}</strong></td>
          <td style="font-size:0.8rem; color:var(--text-muted);">${s.Dataset_Evidence}</td>
          <td><span class="badge badge-mod">${s.Target_Segment}</span></td>
          <td style="font-size:0.82rem;">${s.Suggested_Action}</td>
          <td><code>${s.Progress_KPI}</code></td>
        </tr>
      `).join('');
    }
  }

  async calculateRoi() {
    const cohort = parseInt(document.getElementById('roi-cohort-size').value) || 150;
    const salary = parseFloat(document.getElementById('roi-avg-salary').value) || 65000;
    const mult = parseFloat(document.getElementById('roi-cost-multiplier').value) || 1.5;
    const rate = parseFloat(document.getElementById('roi-success-rate').value) || 0.35;

    const payload = {
      high_risk_count: cohort,
      avg_annual_salary: salary,
      turnover_cost_pct: mult,
      intervention_success_rate: rate,
      intervention_cost_per_emp: 1800.0
    };

    try {
      const res = await fetch('/api/retention/roi-simulator', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const out = await res.json();
        document.getElementById('roi-gross-cost').textContent = `$${(out.gross_turnover_exposure_cost / 1e6).toFixed(2)}M`;
        document.getElementById('roi-net-savings').textContent = `$${(out.net_savings / 1e6).toFixed(2)}M`;
        document.getElementById('roi-retained-count').textContent = `${out.projected_retained_employees} Employees`;
        document.getElementById('roi-unit-cost').textContent = `$${Math.round(out.turnover_cost_per_employee).toLocaleString()}`;
        document.getElementById('roi-program-cost').textContent = `$${Math.round(out.total_intervention_cost).toLocaleString()} ($1,800 / emp)`;
        document.getElementById('roi-ratio').textContent = `${Math.round(out.roi_percentage)}%`;
      }
    } catch (e) {
      console.error('ROI simulation error:', e);
    }
  }

  async loadExperimentHistory() {
    const res = await fetch('/api/experiments');
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.getElementById('experiments-body');
    if (tbody && data.experiments) {
      if (data.experiments.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No prior experiments logged in SQLite.</td></tr>`;
        return;
      }
      tbody.innerHTML = data.experiments.map(e => `
        <tr>
          <td><code>${e.experiment_id.substring(0, 8)}...</code></td>
          <td>${e.timestamp}</td>
          <td><strong>${e.model_type}</strong></td>
          <td>${(e.cv_accuracy * 100).toFixed(1)}%</td>
          <td>${e.cv_f1.toFixed(3)}</td>
          <td>${e.cv_roc_auc.toFixed(3)}</td>
          <td>${e.test_f1 ? e.test_f1.toFixed(3) : 'N/A'}</td>
          <td><span class="badge badge-low">${e.status}</span></td>
        </tr>
      `).join('');
    }
  }

  downloadReport(format) {
    if (format === 'html') {
      window.location.href = '/api/reports/download-html';
    } else {
      window.location.href = '/api/reports/download-markdown';
    }
  }
}

// Global App Instance
const app = new AttritionApp();
document.addEventListener('DOMContentLoaded', () => {
  app.init();
});
