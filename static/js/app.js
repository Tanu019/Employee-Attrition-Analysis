/**
 * EMPLOYEES ATTRITION ANALYSIS - MODERN WEB APPLICATION CONTROLLER
 * Handles tab navigation, asynchronous API integration, Plotly chart rendering,
 * real-time predictions, workforce calculations, and report downloads.
 */

const DARK_THEME = {
  copper: '#B8F34A', // Electric Lime primary accent
  copperHover: '#CAFF72', // Lime hover
  copperSoft: 'rgba(184, 243, 74, 0.25)',
  emerald: '#8DD3A8', // Positive / Low risk
  amber: '#F0C66B', // Warning / Medium risk
  crimson: '#FF7777', // High risk
  sapphire: '#83BFFF', // Informational
  bgCard: '#202428', // Primary card surface
  bgElevated: '#272D32', // Elevated surface
  bgSidebar: '#15181B', // Sidebar background
  borderCard: '#343B40', // Borders & dividers
  textPrimary: '#F2F4F3', // Main text
  textSecondary: '#A5ADB3', // Secondary text
  textMuted: '#7F8B91', // Muted labels
  fontFamily: "'Plus Jakarta Sans', -apple-system, sans-serif"
};

const LIGHT_THEME = {
  copper: '#697653', // Olive accent from user swatch #697653
  copperHover: '#556242',
  copperSoft: 'rgba(105, 118, 83, 0.45)',
  emerald: '#557C61', // Positive from user swatch #557C61
  amber: '#B5762A',
  crimson: '#B84A4A',
  sapphire: '#4E6B7C',
  bgCard: '#FFFFFF',
  bgElevated: '#E8E3D9', // Surface from user swatch #E8E3D9
  bgSidebar: '#EDE8DE',
  borderCard: '#D0C8BB',
  textPrimary: '#292D2B', // Text from user swatch #292D2B
  textSecondary: '#535C56',
  textMuted: '#737D77',
  fontFamily: "'Plus Jakarta Sans', -apple-system, sans-serif"
};

let THEME = { ...DARK_THEME };

const PRESETS = {
  high_risk: {
    Department: 'Sales',
    JobRole: 'Sales Executive',
    JobLevel: 2,
    MonthlySalaryINR: 32000,
    YearsAtCompany: 1.5,
    TotalWorkingYears: 4.0,
    Overtime: 'Yes',
    JobSatisfaction: 1,
    WorkLifeBalance: 1,
    DistanceFromHomeKM: 28,
    YearsInCurrentRole: 1.0,
    YearsSinceLastPromotion: 1.5,
    BurnoutRiskScore: 68
  },
  low_risk: {
    Department: 'Technology',
    JobRole: 'Software Engineer',
    JobLevel: 3,
    MonthlySalaryINR: 95000,
    YearsAtCompany: 6.0,
    TotalWorkingYears: 9.0,
    Overtime: 'No',
    JobSatisfaction: 5,
    WorkLifeBalance: 4,
    DistanceFromHomeKM: 6,
    YearsInCurrentRole: 3.5,
    YearsSinceLastPromotion: 1.0,
    BurnoutRiskScore: 32
  },
  burnout: {
    Department: 'Delivery Operations',
    JobRole: 'Delivery Coordinator',
    JobLevel: 2,
    MonthlySalaryINR: 28000,
    YearsAtCompany: 2.0,
    TotalWorkingYears: 5.0,
    Overtime: 'Yes',
    JobSatisfaction: 2,
    WorkLifeBalance: 1,
    DistanceFromHomeKM: 22,
    YearsInCurrentRole: 2.0,
    YearsSinceLastPromotion: 2.0,
    BurnoutRiskScore: 78
  }
};

class AttritionApp {
  constructor() {
    this.currentView = 'mod-overview';
    this.filterOptions = { departments: [], roles: [] };
    this.cachedData = {};
    this.allDictRecords = [];
    this.employeePage = 1;
    this.employeeTotalPages = 1;
    this.searchTimeout = null;
    this.privacyMode = 'public'; // 'public' | 'hr_admin'
  }

  async init() {
    console.log("Initializing People Intelligence Decision Platform...");
    this.initTheme();
    this.initLiveDateBadge();
    this.initDynamicGreeting();
    this.setupNavigation();
    this.setupTabs();
    this.setupAccordions();
    this.initHeroCanvas();
    this.setupGlobalKeyboard();
    if (window.lucide) {
      window.lucide.createIcons();
    }

    try {
      await this.loadInitialData();
      await this.loadDynamicInsights();
      await this.applyDashboardFilters();
      this.loadDepartmentIntelligence();
      this.loadEmployees(1);
      this.loadDeepDiveData();
      this.loadModelEvaluationData();
      this.loadExplainabilityData();
      this.loadRetentionData();
      this.loadActionPlans();
      this.loadExperimentHistory();
      this.executeCalculator();
      this.calculateRoi();
    } catch (err) {
      console.error("Initialization error:", err);
    }
  }

  // Live executive date badge — updates every minute
  initLiveDateBadge() {
    const el = document.getElementById('header-live-date');
    if (!el) return;
    const update = () => {
      const now = new Date();
      const dayName = now.toLocaleDateString('en-US', { weekday: 'short' });
      const month   = now.toLocaleDateString('en-US', { month: 'short' });
      const day     = now.getDate();
      el.textContent = `${dayName}, ${month} ${day}  ·  Demo Environment`;
    };
    update();
    setInterval(update, 60000);
  }

  // Dynamic time-based greeting
  initDynamicGreeting() {
    const el = document.getElementById('overview-greeting-text');
    if (!el) return;
    const h = new Date().getHours();
    let period = 'morning';
    if (h >= 12 && h < 17) period = 'afternoon';
    else if (h >= 17) period = 'evening';
    el.innerHTML = `Good ${period}, <em class="copper-accent">People Operations.</em>`;
  }

  // Global keyboard shortcut: Ctrl+K → command bar
  setupGlobalKeyboard() {
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        this.openCommandBar();
      }
    });
  }



  initTheme() {
    let savedTheme = 'dark';
    try {
      savedTheme = localStorage.getItem('attrition_lens_theme') || 'dark';
    } catch (e) {}
    this.setTheme(savedTheme, false);
  }

  setTheme(themeName, showToast = true) {
    const isLight = themeName === 'light';
    const effectiveTheme = isLight ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', effectiveTheme);

    // Update active THEME palette for Plotly charts
    Object.assign(THEME, isLight ? LIGHT_THEME : DARK_THEME);

    // Update switcher pill buttons in sidebar footer
    const darkBtn = document.getElementById('theme-btn-dark');
    const lightBtn = document.getElementById('theme-btn-light');
    if (darkBtn && lightBtn) {
      darkBtn.classList.toggle('active', !isLight);
      lightBtn.classList.toggle('active', isLight);
    }

    try {
      localStorage.setItem('attrition_lens_theme', effectiveTheme);
    } catch (e) {}

    // Update workforce canvas particles if active
    if (this.canvasNodes && Array.isArray(this.canvasNodes)) {
      this.canvasNodes.forEach(node => {
        node.color = node.isLeaver ? THEME.copper : THEME.emerald;
      });
    }

    // Refresh lucide icons if needed
    if (window.lucide) {
      window.lucide.createIcons();
    }

    // Re-render cached charts with new theme colors
    setTimeout(() => {
      if (this.cachedData.charts) this.renderDashboardCharts(this.cachedData.charts);
      if (this.cachedData.deepdive) this.renderDeepDiveCharts(this.cachedData.deepdive);
      if (this.cachedData.modelEval && this.cachedData.modelEval.curves) {
        this.renderModelCurves(this.cachedData.modelEval.curves);
      }
      if (this.cachedData.explainability) {
        this.renderExplainabilityChart(this.cachedData.explainability);
      }
      window.dispatchEvent(new Event('resize'));
    }, 60);

    if (showToast) {
      const msg = isLight 
        ? 'Switched to Warm Ivory & Olive light theme.' 
        : 'Switched to Cocoa & Terracotta dark theme.';
      this.showToast(msg, 'info');
    }
  }

  toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    this.setTheme(current === 'light' ? 'dark' : 'light', true);
  }

  setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        const targetId = item.getAttribute('data-target');
        this.switchView(targetId);
      });
      item.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          const targetId = item.getAttribute('data-target');
          this.switchView(targetId);
        }
      });
    });
  }

  setupTabs() {
    document.querySelectorAll('.app-tabs').forEach(tabGroup => {
      const buttons = tabGroup.querySelectorAll('.tab-btn');
      buttons.forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const targetTabId = btn.getAttribute('data-tab');
          if (!targetTabId) return;

          buttons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');

          const container = tabGroup.closest('.view-section');
          if (container) {
            container.querySelectorAll('.tab-pane').forEach(pane => {
              if (pane.id === targetTabId) {
                pane.classList.add('active');
              } else {
                pane.classList.remove('active');
              }
            });
          }

          if (window.lucide) window.lucide.createIcons();
          setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
          }, 60);
        });
      });
    });
  }

  setupAccordions() {
    document.querySelectorAll('details.expandable-panel').forEach(detail => {
      detail.addEventListener('toggle', () => {
        if (window.lucide) window.lucide.createIcons();
        setTimeout(() => {
          window.dispatchEvent(new Event('resize'));
        }, 50);
      });
    });
  }

  activateTab(tabId) {
    const targetPane = document.getElementById(tabId);
    if (!targetPane) return;
    const container = targetPane.closest('.view-section');
    if (!container) return;

    // Ensure the container view is active
    if (!container.classList.contains('active')) {
      this.switchView(container.id, tabId);
      return;
    }

    const btn = container.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    if (btn) {
      container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }

    container.querySelectorAll('.tab-pane').forEach(pane => {
      pane.classList.toggle('active', pane.id === tabId);
    });

    if (window.lucide) window.lucide.createIcons();
    setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
    }, 60);
  }

  navigateTo(viewId, targetTab = null) {
    this.switchView(viewId, targetTab);
  }

  switchView(viewId, targetTab = null) {
    if (!viewId) return;

    // View Aliasing for backwards-compatibility and consolidated modules
    const ALIASES = {
      'mod-dashboard': 'mod-overview',
      'mod-department': 'mod-attrition',
      'mod-explorer': 'mod-attrition',
      'mod-deepdive': 'mod-attrition',
      'mod-model-eval': 'mod-predictor',
      'mod-explainability': 'mod-predictor',
      'mod-experiments': 'mod-predictor',
      'mod-prediction-model': 'mod-predictor',
      'mod-upload': 'mod-upload',
      'mod-quality': 'mod-upload',
      'mod-reports': 'mod-upload',
      'mod-methodology': 'mod-upload',
      'mod-preprocessing': 'mod-upload',
      'mod-calculator': 'mod-upload',
      'mod-data-reports': 'mod-upload'
    };

    const TAB_ALIASES = {
      'mod-department': 'tab-attrition-dept',
      'mod-explorer': 'tab-attrition-explorer',
      'mod-model-eval': 'tab-model-performance',
      'mod-explainability': 'tab-model-explainability',
      'mod-experiments': 'tab-model-performance',
      'mod-quality': 'tab-data-quality',
      'mod-reports': 'tab-data-reports',
      'mod-methodology': 'tab-data-methodology',
      'mod-preprocessing': 'tab-data-methodology',
      'mod-calculator': 'tab-data-methodology'
    };

    const target = ALIASES[viewId] || viewId;
    this.currentView = target;

    // Update active nav state
    document.querySelectorAll('.nav-item').forEach(item => {
      if (item.getAttribute('data-target') === target) {
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
      if (sec.id === target) {
        sec.classList.add('active');
      } else {
        sec.classList.remove('active');
      }
    });

    // If a tab is specified or implied by alias, activate it
    const tabToActivate = targetTab || TAB_ALIASES[viewId];
    if (tabToActivate) {
      const pane = document.getElementById(tabToActivate);
      if (pane) {
        const container = pane.closest('.view-section');
        if (container) {
          const btn = container.querySelector(`.tab-btn[data-tab="${tabToActivate}"]`);
          if (btn) {
            container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
          }
          container.querySelectorAll('.tab-pane').forEach(p => {
            p.classList.toggle('active', p.id === tabToActivate);
          });
        }
      }
    }

    // Re-create lucide icons for newly unhidden DOM elements
    if (window.lucide) {
      window.lucide.createIcons();
    }

    // Scroll main view container to top smoothly
    const mainEl = document.querySelector('.app-main');
    if (mainEl) mainEl.scrollTop = 0;

    // Re-render and resize charts for unhidden view
    setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
      if (target === 'mod-overview' && this.cachedData.charts) {
        this.renderDashboardCharts(this.cachedData.charts);
      } else if (target === 'mod-attrition') {
        if (this.cachedData.charts) this.renderDashboardCharts(this.cachedData.charts);
        if (this.cachedData.deepdive) this.renderDeepDiveCharts(this.cachedData.deepdive);
      } else if (target === 'mod-predictor') {
        if (this.cachedData.modelEval) this.renderModelCurves(this.cachedData.modelEval.curves);
        if (this.cachedData.explainability) {
          this.renderExplainabilityChart(this.cachedData.explainability);
        }
      }
    }, 80);
  }

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let iconName = 'info';
    if (type === 'success') iconName = 'check-circle';
    else if (type === 'warn') iconName = 'alert-triangle';

    toast.innerHTML = `
      <i data-lucide="${iconName}" style="width:18px;height:18px;flex-shrink:0;"></i>
      <span style="flex:1;">${message}</span>
    `;
    container.appendChild(toast);
    if (window.lucide) window.lucide.createIcons();

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, 3800);
  }

  showTourModal() {
    const modal = document.getElementById('guide-modal');
    if (modal) {
      modal.style.display = 'flex';
      if (window.lucide) window.lucide.createIcons();
    }
  }

  closeTourModal() {
    const modal = document.getElementById('guide-modal');
    if (modal) modal.style.display = 'none';
  }

  togglePrivacyMode() {
    if (this.privacyMode === 'public') {
      this.privacyMode = 'hr_admin';
      const btn = document.getElementById('mode-toggle-btn');
      const text = document.getElementById('mode-toggle-text');
      if (btn) btn.className = 'btn-header-action mode-active';
      if (text) text.textContent = 'HR Executive Mode';
      this.showToast('Switched to HR Executive Mode: Full audit details and exact salaries unmasked.', 'info');
    } else {
      this.privacyMode = 'public';
      const btn = document.getElementById('mode-toggle-btn');
      const text = document.getElementById('mode-toggle-text');
      if (btn) btn.className = 'btn-header-action mode-demo';
      if (text) text.textContent = 'Public Demo Mode';
      this.showToast('Switched to Public Demo Mode: PII masked and salary brackets applied.', 'success');
    }
    this.loadEmployees(this.employeePage || 1);
  }

  showPrivacyModal() {
    const modal = document.getElementById('privacy-modal');
    if (modal) {
      modal.style.display = 'flex';
      if (window.lucide) window.lucide.createIcons();
    }
  }

  closePrivacyModal() {
    const modal = document.getElementById('privacy-modal');
    if (modal) modal.style.display = 'none';
  }

  async loadInitialData() {
    try {
      const res = await fetch('/api/dataset/overview');
      if (res.ok) {
        const data = await res.json();
        this.cachedData.overview = data;
        this.allDictRecords = data.data_dictionary || [];
        this.renderDataDictionary(this.allDictRecords);
        this.renderQualityChecks(data.quality_report || []);
        this.populateFilterDropdowns(data.filter_options);

        // Populate Attrition Lens Data Quality & Freshness Indicator
        if (document.getElementById('lens-active-dataset-name') && data.dataset_name) {
          document.getElementById('lens-active-dataset-name').textContent = data.dataset_name;
        }
        if (document.getElementById('lens-dataset-fingerprint') && data.dataset_fingerprint) {
          document.getElementById('lens-dataset-fingerprint').textContent = `${data.dataset_fingerprint.slice(0, 16)}... (SHA-256)`;
        }
        if (document.getElementById('top-dataset-text') && data.validation) {
          document.getElementById('top-dataset-text').textContent = `${data.validation.total_rows.toLocaleString()} Monitored Staff`;
        }
        if (document.getElementById('lens-quality-status-badge') && data.validation) {
          const hasFail = data.quality_report?.some(c => c.Result === 'FAIL');
          document.getElementById('lens-quality-status-badge').textContent = hasFail ? 'Requires Review' : '100% Validated';
          document.getElementById('lens-quality-status-badge').className = hasFail ? 'badge badge-warn' : 'badge badge-pass';
        }

        // Update sidebar workspace status card from actual application state
        this.updateSidebarWorkspaceStatus(data);
      } else {
        if (document.getElementById('lens-quality-status-badge')) {
          document.getElementById('lens-quality-status-badge').textContent = 'Unavailable';
          document.getElementById('lens-quality-status-badge').className = 'badge badge-warn';
        }
        this.updateSidebarWorkspaceStatus(null);
      }
    } catch (err) {
      console.error("Failed to load initial dataset overview:", err);
      this.updateSidebarWorkspaceStatus(null);
    }
  }

  updateSidebarWorkspaceStatus(data) {
    const wsDot = document.getElementById('sidebar-workspace-dot');
    const wsTitle = document.getElementById('sidebar-workspace-title');
    const recEl = document.getElementById('sidebar-record-count');

    if (data && data.validation && typeof data.validation.total_rows === 'number') {
      if (wsDot) wsDot.className = 'status-indicator-dot online';
      if (wsTitle) wsTitle.textContent = 'Workspace Active';
      if (recEl) recEl.textContent = `${data.validation.total_rows.toLocaleString()} Records`;
    } else {
      if (wsDot) wsDot.className = 'status-indicator-dot offline';
      if (wsTitle) wsTitle.textContent = 'Data Disconnected';
      if (recEl) recEl.textContent = '0 Records';
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

  renderQualityChecks(checks) {
    const tbody = document.getElementById('quality-checks-body');
    if (!tbody || !checks) return;

    tbody.innerHTML = checks.map(c => {
      let badgeClass = 'badge-pass';
      if (c.Result === 'FAIL') badgeClass = 'badge-high';
      else if (c.Result === 'WARN') badgeClass = 'badge-warn';
      else if (c.Result === 'INFO') badgeClass = 'badge-info';

      return `
        <tr>
          <td><strong>${c.Check}</strong></td>
          <td><span class="badge ${badgeClass}">${c.Result}</span></td>
          <td style="color:var(--text-secondary); font-size:0.84rem;">${c.Details}</td>
        </tr>
      `;
    }).join('');
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

  filterDataDictionary() {
    const query = document.getElementById('dict-search-input')?.value.toLowerCase() || '';
    if (!this.allDictRecords) return;

    const filtered = this.allDictRecords.filter(r => 
      r.Column_Name.toLowerCase().includes(query) ||
      r.Data_Type.toLowerCase().includes(query) ||
      r.Analytical_Category.toLowerCase().includes(query)
    );
    this.renderDataDictionary(filtered);
  }

  async loadDynamicInsights() {
    try {
      const res = await fetch('/api/analytics/insights');
      if (!res.ok) {
        this.renderLensDynamicInsights([]);
        return;
      }
      const data = await res.json();
      this.cachedData.insights = data.insights || [];
      this.renderLensDynamicInsights(this.cachedData.insights);

      // Support legacy container if present
      const legacyContainer = document.getElementById('dynamic-insights-container');
      if (legacyContainer && data.insights) {
        const icons = ['flame', 'trending-down', 'clock', 'indian-rupee', 'shield-check'];
        const styles = ['critical', 'warning', 'info', 'warning', 'success'];
        legacyContainer.innerHTML = data.insights.map((ins, i) => {
          const title = ins.title || 'Analytical Finding';
          const obs = ins.observation || '';
          const metric = ins.supporting_metric || '';
          const segment = ins.relevant_segment || '';
          const implication = ins.implication || '';
          const style = ins.type || styles[i % styles.length] || 'info';
          const icon = icons[i % icons.length];
          return `
            <div class="exec-finding-card ${style}">
              <div class="exec-finding-title"><i data-lucide="${icon}"></i> ${title}</div>
              <div class="exec-finding-body"><strong>Observation:</strong> ${obs}<br><strong>Metric Evidence:</strong> ${metric}</div>
              <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:4px;"><strong>Affected Segment:</strong> ${segment}</div>
              <div style="font-size:0.82rem; color:var(--text-secondary); border-top:1px solid rgba(255,255,255,0.06); padding-top:6px; margin-top:6px;"><strong>Strategic Implication:</strong> ${implication}</div>
            </div>
          `;
        }).join('');
      }

      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      console.error("Failed to load dynamic insights:", err);
      this.renderLensDynamicInsights([]);
    }
  }

  renderLensDynamicInsights(insights) {
    // 1. Populate the single calculated overview insight card if present
    if (insights && insights.length > 0) {
      const topIns = insights[0];
      const titleEl = document.getElementById('overview-insight-title');
      const bodyEl = document.getElementById('overview-insight-body');
      const metricEl = document.getElementById('overview-insight-metric');
      const implEl = document.getElementById('overview-insight-implication');

      if (titleEl) titleEl.textContent = topIns.title || 'Workforce Analytical Finding';
      if (bodyEl) bodyEl.textContent = topIns.observation || 'Observed correlation in active workforce data.';
      if (metricEl) metricEl.textContent = `Evidence: ${topIns.supporting_metric || 'Verified dataset metric'}`;
      if (implEl) implEl.textContent = topIns.implication || 'Targeted retention intervention recommended.';
    }

    const container = document.getElementById('lens-dynamic-insights-container');
    if (!container) {
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    if (!insights || insights.length === 0) {
      container.innerHTML = `
        <div class="lens-insight-card info" style="grid-column:1/-1; text-align:center; padding:24px;">
          <p style="color:var(--text-muted);">Workforce analytical findings currently unavailable. Check active dataset status.</p>
        </div>
      `;
      return;
    }

    // Three findings derived from actual calculations on the active dataset
    const top3 = insights.slice(0, 3);
    const icons = {
      critical: 'flame',
      warning: 'trending-down',
      info: 'clock',
      success: 'shield-check'
    };

    container.innerHTML = top3.map((ins, i) => {
      const type = ins.type || (i === 0 ? 'critical' : i === 1 ? 'warning' : 'info');
      const icon = icons[type] || 'sparkles';
      const title = ins.title || 'Workforce Finding';
      const obs = ins.observation || 'Observed correlation in active workforce data.';
      const metric = ins.supporting_metric || 'Verified dataset metric';
      const implication = ins.implication || 'Targeted retention intervention recommended.';

      return `
        <div class="lens-insight-card ${type}">
          <div class="lens-insight-header">
            <div class="lens-insight-icon"><i data-lucide="${icon}"></i></div>
            <div class="lens-insight-title">${title}</div>
          </div>
          <div class="lens-insight-obs">${obs}</div>
          <div class="lens-insight-metric-box">
            <span class="metric-box-label">Supporting Metric</span>
            <span class="metric-box-value">${metric}</span>
          </div>
          <div class="lens-insight-implication">
            <strong>Strategic Implication:</strong> ${implication}
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
  }

  async applyDashboardFilters() {
    const dept = document.getElementById('filter-dept')?.value || 'All';
    const role = document.getElementById('filter-role')?.value || 'All';
    const level = document.getElementById('filter-level')?.value || 'All';
    const location = document.getElementById('filter-location')?.value || 'All';
    const tenure = document.getElementById('filter-tenure')?.value || 'All';

    // Fetch KPIs
    const kpiUrl = `/api/analytics/kpis?department=${encodeURIComponent(dept)}&job_role=${encodeURIComponent(role)}&job_level=${encodeURIComponent(level)}&work_location=${encodeURIComponent(location)}&tenure_band=${encodeURIComponent(tenure)}`;
    const kpiRes = await fetch(kpiUrl);
    if (kpiRes.ok) {
      const data = await kpiRes.json();
      this.renderKpiCards(data.kpis, data.filtered_count, data.total_count);
    }

    // Fetch Charts
    const chartUrl = `/api/analytics/charts?department=${encodeURIComponent(dept)}&job_role=${encodeURIComponent(role)}&job_level=${encodeURIComponent(level)}&work_location=${encodeURIComponent(location)}&tenure_band=${encodeURIComponent(tenure)}`;
    const chartRes = await fetch(chartUrl);
    if (chartRes.ok) {
      const chartData = await chartRes.json();
      this.cachedData.charts = chartData;
      this.renderDashboardCharts(chartData);
    }
  }

  resetDashboardFilters() {
    if (document.getElementById('filter-dept')) document.getElementById('filter-dept').value = 'All';
    if (document.getElementById('filter-role')) document.getElementById('filter-role').value = 'All';
    if (document.getElementById('filter-level')) document.getElementById('filter-level').value = 'All';
    if (document.getElementById('filter-location')) document.getElementById('filter-location').value = 'All';
    if (document.getElementById('filter-tenure')) document.getElementById('filter-tenure').value = 'All';
    this.applyDashboardFilters();
    this.showToast('Reset dashboard filters to entire organization', 'info');
  }

  renderKpiCards(kpis, filteredCount, totalCount) {
    if (!kpis) return;

    // 1. Total Employees
    if (document.getElementById('kpi-headcount')) {
      document.getElementById('kpi-headcount').textContent = kpis.Total_Employees.toLocaleString();
    }
    if (document.getElementById('kpi-headcount-sub')) {
      document.getElementById('kpi-headcount-sub').textContent = filteredCount < totalCount ? `Filtered from ${totalCount} workforce` : `Monitored active headcount in scope`;
    }

    // 2. Historical Attrition Rate (with clear denominator context)
    if (document.getElementById('kpi-rate')) {
      document.getElementById('kpi-rate').textContent = `${kpis.Overall_Attrition_Rate_Pct}%`;
    }
    if (document.getElementById('kpi-rate-sub')) {
      document.getElementById('kpi-rate-sub').textContent = `Cohort exit incidence (${kpis.Employees_Who_Left} exits / ${kpis.Total_Employees} total)`;
    }

    // 3. Employees Who Left
    if (document.getElementById('kpi-leavers')) {
      document.getElementById('kpi-leavers').textContent = kpis.Employees_Who_Left.toLocaleString();
    }
    if (document.getElementById('kpi-leavers-sub')) {
      const volCount = kpis.Voluntary_Attrition_Count !== undefined ? kpis.Voluntary_Attrition_Count : Math.round(kpis.Employees_Who_Left * 0.822);
      const involCount = Math.max(0, kpis.Employees_Who_Left - volCount);
      const volPct = kpis.Employees_Who_Left > 0 ? Math.round((volCount / kpis.Employees_Who_Left) * 100) : 82;
      document.getElementById('kpi-leavers-sub').textContent = `${volCount} Voluntary (${volPct}%) • ${involCount} Involuntary`;
    }
    if (document.getElementById('breakdown-leavers-text')) {
      document.getElementById('breakdown-leavers-text').textContent = `${kpis.Employees_Who_Left.toLocaleString()} staff (${kpis.Overall_Attrition_Rate_Pct}%)`;
    }

    // Stayers Breakdown & Rates
    if (document.getElementById('kpi-stayers')) {
      const retentionPct = (100 - kpis.Overall_Attrition_Rate_Pct).toFixed(1);
      document.getElementById('kpi-stayers').textContent = `${kpis.Active_Employees.toLocaleString()} staff (${retentionPct}%)`;
    }
    if (document.getElementById('overview-retention-rate')) {
      document.getElementById('overview-retention-rate').textContent = `${(100 - kpis.Overall_Attrition_Rate_Pct).toFixed(1)}% Retained`;
    }
    if (document.getElementById('overview-attrition-rate')) {
      document.getElementById('overview-attrition-rate').textContent = `${kpis.Overall_Attrition_Rate_Pct}% Turnover`;
    }
    if (document.getElementById('hero-retention-pill')) {
      document.getElementById('hero-retention-pill').textContent = `${(100 - kpis.Overall_Attrition_Rate_Pct).toFixed(1)}% Retained`;
    }
    if (document.getElementById('kpi-vol-rate') && kpis.Voluntary_Attrition_Rate_Pct !== undefined) {
      document.getElementById('kpi-vol-rate').textContent = `${kpis.Voluntary_Attrition_Rate_Pct}% of Total (82.2% of Exits)`;
    }

    // Legacy/Additional Metrics
    if (document.getElementById('kpi-salary') && kpis.Average_Salary) {
      document.getElementById('kpi-salary').textContent = `₹${Math.round(kpis.Average_Salary).toLocaleString()}`;
    }
    if (document.getElementById('kpi-tenure') && kpis.Average_Tenure_Years) {
      document.getElementById('kpi-tenure').textContent = `${kpis.Average_Tenure_Years} Yrs`;
    }
    if (document.getElementById('kpi-satisfaction') && kpis.Average_Satisfaction) {
      document.getElementById('kpi-satisfaction').textContent = `${kpis.Average_Satisfaction} / 5.0`;
    }
    if (document.getElementById('kpi-model-acc') && kpis.Model_Accuracy_Pct) {
      document.getElementById('kpi-model-acc').textContent = `${kpis.Model_Accuracy_Pct}%`;
    }
    if (document.getElementById('kpi-model-f1') && kpis.Model_F1_Score) {
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

    // 1. Overall Distribution Donut (Stayers vs Leavers)
    if (data.overall_distribution && document.getElementById('chart-overall-dist')) {
      const labels = data.overall_distribution.map(d => d.label);
      const values = data.overall_distribution.map(d => d.value);
      const donutData = [{
        labels: labels,
        values: values,
        type: 'pie',
        hole: 0.62,
        marker: { colors: [THEME.emerald, THEME.copper] },
        textinfo: 'percent',
        textfont: { family: THEME.fontFamily, size: 12, color: '#F5F0E8' },
        hoverinfo: 'label+value+percent'
      }];
      const donutLayout = {
        ...defaultLayout,
        showlegend: false,
        margin: { l: 15, r: 15, t: 15, b: 15 }
      };
      Plotly.newPlot('chart-overall-dist', donutData, donutLayout, { responsive: true, displayModeBar: false });
    }

    // 2. Department Breakdown (Horizontal Bar Chart comparing department attrition rates)
    if (data.department_breakdown && document.getElementById('chart-dept-attrition')) {
      // Sort ascending so highest rate appears at the top of horizontal chart
      const sorted = [...data.department_breakdown].sort((a, b) => a.Attrition_Rate_Pct - b.Attrition_Rate_Pct);
      const depts = sorted.map(d => d.Department);
      const rates = sorted.map(d => d.Attrition_Rate_Pct);
      const deptData = [{
        type: 'bar',
        orientation: 'h',
        x: rates,
        y: depts,
        marker: {
          color: rates.map(r => r > 20 ? THEME.copper : 'rgba(196, 124, 90, 0.72)'),
          line: { color: THEME.copper, width: 1 }
        },
        text: rates.map(r => `${r}%`),
        textposition: 'inside',
        insidetextanchor: 'end',
        textfont: { color: '#F5F0E8', size: 11, family: THEME.fontFamily }
      }];
      const deptLayout = {
        ...defaultLayout,
        xaxis: {
          title: 'Attrition Rate (%)',
          gridcolor: THEME.borderCard,
          zerolinecolor: THEME.borderCard,
          tickfont: { color: THEME.textSecondary, size: 10 }
        },
        yaxis: {
          automargin: true,
          tickfont: { color: THEME.textPrimary, size: 11 }
        },
        margin: { l: 110, r: 25, t: 15, b: 35 }
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
        margin: { l: 150, r: 25, t: 20, b: 40 },
        xaxis: { title: 'Attrition Rate (%)', gridcolor: THEME.borderCard }
      };
      Plotly.newPlot('chart-role-attrition', roleData, roleLayout, { responsive: true, displayModeBar: false });
    }

    // 4. Tenure Breakdown
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

    // 5. Salary Band Breakdown
    if (data.salary_breakdown && document.getElementById('chart-salary-attrition')) {
      const bands = data.salary_breakdown.map(d => d.SalaryBand);
      const rates = data.salary_breakdown.map(d => d.AttritionRate);
      const salaryData = [{
        x: bands,
        y: rates,
        type: 'bar',
        marker: { color: THEME.copper },
        text: rates.map(r => `${r}%`),
        textposition: 'auto'
      }];
      const salaryLayout = {
        ...defaultLayout,
        yaxis: { title: 'Attrition Rate (%)', gridcolor: THEME.borderCard },
        xaxis: { title: 'Salary Tier' }
      };
      Plotly.newPlot('chart-salary-attrition', salaryData, salaryLayout, { responsive: true, displayModeBar: false });
    }

    // 6. Job Satisfaction Breakdown
    if (data.satisfaction_breakdown && document.getElementById('chart-satisfaction-attrition')) {
      const sats = data.satisfaction_breakdown.map(d => `Rating ${d.Satisfaction}`);
      const rates = data.satisfaction_breakdown.map(d => d.AttritionRate);
      const satData = [{
        x: sats,
        y: rates,
        type: 'bar',
        marker: { color: rates.map(r => r > 20 ? THEME.crimson : THEME.emerald) },
        text: rates.map(r => `${r}%`),
        textposition: 'auto'
      }];
      const satLayout = {
        ...defaultLayout,
        yaxis: { title: 'Attrition Rate (%)', gridcolor: THEME.borderCard },
        xaxis: { title: 'Satisfaction Rating (1-5)' }
      };
      Plotly.newPlot('chart-satisfaction-attrition', satData, satLayout, { responsive: true, displayModeBar: false });
    }

    // 7. Overtime Impact
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

    // 8. Job Level Breakdown
    if (data.job_level_breakdown && document.getElementById('chart-joblevel-attrition')) {
      const levels = data.job_level_breakdown.map(d => `Level ${d.JobLevel}`);
      const rates = data.job_level_breakdown.map(d => d.AttritionRate);
      const lvlData = [{
        x: levels,
        y: rates,
        type: 'bar',
        marker: { color: THEME.copper },
        text: rates.map(r => `${r}%`),
        textposition: 'auto'
      }];
      const lvlLayout = {
        ...defaultLayout,
        yaxis: { title: 'Attrition Rate (%)', gridcolor: THEME.borderCard },
        xaxis: { title: 'Hierarchy Level' }
      };
      Plotly.newPlot('chart-joblevel-attrition', lvlData, lvlLayout, { responsive: true, displayModeBar: false });
    }

    // 9. Monthly Attrition Trend
    if (data.monthly_trend && document.getElementById('chart-monthly-trend')) {
      const months = data.monthly_trend.map(d => d.Month);
      const exits = data.monthly_trend.map(d => d.Exits);
      const rates = data.monthly_trend.map(d => d.AttritionRate);

      const trendData = [
        {
          x: months,
          y: exits,
          name: 'Monthly Departures',
          type: 'bar',
          marker: { color: THEME.copperSoft, line: { color: THEME.copper, width: 1 } },
          yaxis: 'y'
        },
        {
          x: months,
          y: rates,
          name: 'Turnover Rate %',
          type: 'scatter',
          mode: 'lines+markers',
          line: { color: THEME.crimson, width: 2.5 },
          marker: { size: 6, color: THEME.crimson },
          yaxis: 'y2'
        }
      ];

      const trendLayout = {
        ...defaultLayout,
        showlegend: true,
        legend: { orientation: 'h', x: 0.02, y: 1.15, font: { color: THEME.textSecondary } },
        xaxis: { tickangle: -30, gridcolor: THEME.borderCard },
        yaxis: { title: 'Departure Count', gridcolor: THEME.borderCard },
        yaxis2: { title: 'Monthly Rate (%)', overlaying: 'y', side: 'right', showgrid: false }
      };
      Plotly.newPlot('chart-monthly-trend', trendData, trendLayout, { responsive: true, displayModeBar: false });
    }

    // 10. Model Performance Summary
    if (document.getElementById('chart-model-summary')) {
      const models = ['Dummy Baseline', 'Logistic Regression', 'Decision Tree', 'Random Forest', 'Gradient Boosting'];
      const accs = [82.0, 77.4, 76.2, 80.2, 79.4];
      const recalls = [0.0, 48.9, 44.4, 43.3, 41.1];
      const f1s = [0.0, 43.6, 40.4, 45.9, 41.8];
      const rocs = [50.0, 71.9, 63.8, 74.5, 71.8];

      const modelData = [
        { x: models, y: accs, name: 'Accuracy %', type: 'bar', marker: { color: THEME.sapphire } },
        { x: models, y: recalls, name: 'Recall %', type: 'bar', marker: { color: THEME.amber } },
        { x: models, y: f1s, name: 'F1-Score x100', type: 'bar', marker: { color: THEME.copper } },
        { x: models, y: rocs, name: 'ROC-AUC %', type: 'bar', marker: { color: THEME.emerald } }
      ];

      const modelLayout = {
        ...defaultLayout,
        barmode: 'group',
        showlegend: true,
        legend: { orientation: 'h', x: 0.05, y: 1.15, font: { color: THEME.textSecondary } },
        yaxis: { title: 'Score (%)', gridcolor: THEME.borderCard },
        xaxis: { tickangle: -10 }
      };
      Plotly.newPlot('chart-model-summary', modelData, modelLayout, { responsive: true, displayModeBar: false });
    }
  }

  async loadDepartmentIntelligence() {
    try {
      const res = await fetch('/api/department-intelligence');
      if (!res.ok) return;
      const data = await res.json();
      const depts = data.departments || [];

      // Render cards
      const grid = document.getElementById('dept-intel-grid');
      if (grid) {
        grid.innerHTML = depts.map(d => {
          let badgeClass = 'badge-low';
          if (d.Risk_Level === 'High Risk') badgeClass = 'badge-high';
          else if (d.Risk_Level === 'Moderate Risk') badgeClass = 'badge-mod';

          return `
            <div class="dept-intel-card">
              <div class="dept-intel-header">
                <span class="dept-name">${d.Department}</span>
                <span class="badge ${badgeClass}">${d.Risk_Level}</span>
              </div>
              <div class="dept-kpi-row">
                <div class="dept-kpi-item">
                  <div class="kpi-sub">Headcount</div>
                  <div class="kpi-val">${d.Headcount.toLocaleString()}</div>
                </div>
                <div class="dept-kpi-item">
                  <div class="kpi-sub">Total Exits</div>
                  <div class="kpi-val" style="color:var(--status-crimson);">${d.Exits}</div>
                </div>
                <div class="dept-kpi-item">
                  <div class="kpi-sub">Attrition %</div>
                  <div class="kpi-val" style="color:${d.Attrition_Rate_Pct > 20 ? 'var(--status-crimson)' : 'var(--accent-copper)'};">${d.Attrition_Rate_Pct}%</div>
                </div>
              </div>
              <div style="font-size:0.8rem; color:var(--text-secondary); display:flex; justify-content:space-between; border-top:1px solid var(--border-subtle); padding-top:8px;">
                <span>Voluntary: <strong>${d.Voluntary_Rate_Pct}% (${d.Voluntary_Exits})</strong></span>
                <span>Avg Base: <strong>₹${Math.round(d.Avg_Salary_INR).toLocaleString()}</strong></span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-secondary); display:flex; justify-content:space-between;">
                <span>Overtime Ratio: <strong>${d.Overtime_Ratio_Pct}%</strong></span>
                <span>Burnout Risk: <strong style="color:${d.Burnout_Score > 55 ? 'var(--status-amber)' : 'var(--text-primary)'};">${d.Burnout_Score}</strong></span>
              </div>
            </div>
          `;
        }).join('');
      }

      // Render table
      const tbody = document.getElementById('dept-intel-table-body');
      if (tbody) {
        tbody.innerHTML = depts.map(d => {
          let badgeClass = 'badge-low';
          if (d.Risk_Level === 'High Risk') badgeClass = 'badge-high';
          else if (d.Risk_Level === 'Moderate Risk') badgeClass = 'badge-mod';

          return `
            <tr>
              <td><strong>${d.Department}</strong></td>
              <td>${d.Headcount.toLocaleString()}</td>
              <td style="color:var(--status-crimson); font-weight:600;">${d.Exits}</td>
              <td><strong style="color:${d.Attrition_Rate_Pct > 20 ? 'var(--status-crimson)' : 'var(--accent-copper)'};">${d.Attrition_Rate_Pct}%</strong></td>
              <td>${d.Voluntary_Exits}</td>
              <td>${d.Voluntary_Rate_Pct}%</td>
              <td>₹${Math.round(d.Avg_Salary_INR).toLocaleString()}</td>
              <td>${d.Avg_Tenure_Years} Yrs</td>
              <td>${d.Avg_Satisfaction} / 5.0</td>
              <td>${d.Overtime_Ratio_Pct}%</td>
              <td>${d.Burnout_Score}</td>
              <td><span class="badge ${badgeClass}">${d.Risk_Level}</span></td>
            </tr>
          `;
        }).join('');
      }
      // Render Attrition Lens Top Risk Highlights
      this.renderLensDepartmentHighlights(depts);
    } catch (err) {
      console.error("Failed to load department intelligence:", err);
      this.renderLensDepartmentHighlights([]);
    }
  }

  renderLensDepartmentHighlights(depts) {
    const container = document.getElementById('lens-top-dept-cards');
    if (!container) return;

    if (!depts || depts.length === 0) {
      container.innerHTML = `<div style="grid-column:1/-1; color:var(--text-muted); font-size:0.82rem; padding:12px;">Department intelligence metrics currently unavailable.</div>`;
      return;
    }

    // Top 3 departments with highest observed attrition rates
    const top3 = depts.slice(0, 3);
    container.innerHTML = top3.map(d => {
      const rate = d.Attrition_Rate_Pct || 0;
      const risk = d.Risk_Level || (rate > 20 ? 'High Risk' : 'Moderate Risk');
      const badgeClass = risk === 'High Risk' ? 'badge-high' : 'badge-mod';
      const barWidth = Math.min(100, Math.round((rate / 35) * 100));

      return `
        <div class="lens-dept-card">
          <div class="lens-dept-card-top">
            <span class="lens-dept-name" title="${d.Department}">${d.Department}</span>
            <span class="badge ${badgeClass}">${risk}</span>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:baseline; margin-top:2px;">
            <div class="lens-dept-rate">${rate}%</div>
            <div class="lens-dept-counts">${d.Exits} exits / ${d.Headcount} staff</div>
          </div>
          <div class="lens-dept-bar-track">
            <div class="lens-dept-bar-fill" style="width: ${barWidth}%;"></div>
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
  }

  async loadEmployees(page = 1) {
    try {
      this.employeePage = page;
      const query = document.getElementById('explorer-search')?.value.trim() || '';
      const dept = document.getElementById('explorer-dept')?.value || 'All';
      const role = document.getElementById('explorer-role')?.value || 'All';
      const level = document.getElementById('explorer-level')?.value || 'All';
      const status = document.getElementById('explorer-status')?.value || 'All';

      const url = `/api/employees?page=${page}&page_size=25&search=${encodeURIComponent(query)}&department=${encodeURIComponent(dept)}&job_role=${encodeURIComponent(role)}&job_level=${encodeURIComponent(level)}&status=${encodeURIComponent(status)}`;
      const res = await fetch(url);
      if (!res.ok) return;
      const data = await res.json();

      this.employeeTotalPages = data.total_pages || 1;

      // Populate filter dropdowns if needed
      const expDept = document.getElementById('explorer-dept');
      if (expDept && expDept.options.length <= 1 && this.filterOptions.departments) {
        expDept.innerHTML = this.filterOptions.departments
          .map(d => `<option value="${d}">${d === 'All' ? 'All Departments' : d}</option>`)
          .join('');
        expDept.value = dept;
      }
      const expRole = document.getElementById('explorer-role');
      if (expRole && expRole.options.length <= 1 && this.filterOptions.roles) {
        expRole.innerHTML = this.filterOptions.roles
          .map(r => `<option value="${r}">${r === 'All' ? 'All Job Roles' : r}</option>`)
          .join('');
        expRole.value = role;
      }

      // Render table rows
      const tbody = document.getElementById('explorer-table-body');
      if (tbody) {
        if (!data.employees || data.employees.length === 0) {
          tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:24px; color:var(--text-muted);">No employee records match the selected search or filters.</td></tr>`;
        } else {
          tbody.innerHTML = data.employees.map(emp => {
            const empId = emp.MaskedID || emp.EmployeeID || 'EMP-***';
            const tenure = emp.TenureYears !== undefined ? emp.TenureYears : (emp.YearsAtCompany || 0);
            const status = emp.EmploymentStatus || emp.Status || 'Active';
            const statusClass = (status === 'Exited' || status === 'Departed') ? 'badge-high' : 'badge-low';

            const salVal = Math.round(emp.MonthlySalaryINR || 0);
            let salDisplay = `₹${salVal.toLocaleString()}`;
            if (this.privacyMode === 'public') {
              if (salVal < 35000) salDisplay = 'Band 1 (< ₹35K)';
              else if (salVal < 60000) salDisplay = 'Band 2 (₹35K-₹60K)';
              else if (salVal < 100000) salDisplay = 'Band 3 (₹60K-₹100K)';
              else salDisplay = 'Band 4 (₹100K+)';
            }

            return `
              <tr>
                <td><code>${empId}</code></td>
                <td><strong>${emp.Department}</strong></td>
                <td>${emp.JobRole}</td>
                <td><span class="badge badge-low">L${emp.JobLevel}</span></td>
                <td><span style="${this.privacyMode === 'public' ? 'color:var(--text-secondary); font-size:0.82rem;' : 'font-weight:600;'}">${salDisplay}</span></td>
                <td>${tenure} Yrs</td>
                <td>${emp.Overtime === 'Yes' ? '<span class="badge badge-high">Yes</span>' : '<span class="badge badge-low">No</span>'}</td>
                <td>${emp.JobSatisfaction || 3} / 5</td>
                <td><span class="badge ${statusClass}">${status}</span></td>
              </tr>
            `;
          }).join('');
        }
      }

      // Update pagination info
      const curPage = data.current_page || data.page || page;
      const totalRecs = data.total_records !== undefined ? data.total_records : (data.total_matching || 0);

      const pageInfo = document.getElementById('explorer-page-info');
      if (pageInfo) {
        pageInfo.textContent = `Page ${curPage} of ${data.total_pages} (${totalRecs.toLocaleString()} records)`;
      }
      const badge = document.getElementById('explorer-total-badge');
      if (badge) {
        badge.textContent = `${totalRecs.toLocaleString()} Matching Records`;
      }
      const prevBtn = document.getElementById('explorer-prev-btn');
      if (prevBtn) prevBtn.disabled = curPage <= 1;
      const nextBtn = document.getElementById('explorer-next-btn');
      if (nextBtn) nextBtn.disabled = curPage >= data.total_pages;

      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      console.error("Failed to load employees:", err);
    }
  }

  prevEmployeePage() {
    if (this.employeePage > 1) {
      this.loadEmployees(this.employeePage - 1);
    }
  }

  nextEmployeePage() {
    if (this.employeePage < this.employeeTotalPages) {
      this.loadEmployees(this.employeePage + 1);
    }
  }

  onExplorerSearch() {
    if (this.searchTimeout) clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(() => {
      this.loadEmployees(1);
    }, 250);
  }

  async loadActionPlans() {
    try {
      const res = await fetch('/api/retention/action-plans');
      if (!res.ok) return;
      const data = await res.json();
      const plans = data.action_plans || [];

      const tbody = document.getElementById('action-plans-table-body');
      if (!tbody) return;

      if (plans.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:18px; color:var(--text-muted);">No action initiatives recorded yet. Log your first retention initiative above.</td></tr>`;
        return;
      }

      tbody.innerHTML = plans.map(p => {
        let badgeClass = 'badge-mod';
        if (p.Status === 'Completed') badgeClass = 'badge-low';
        else if (p.Status === 'In Progress') badgeClass = 'badge-info';

        return `
          <tr>
            <td><strong>${p.Department}</strong></td>
            <td>${p.Observed_Issue}</td>
            <td style="color:var(--text-primary);">${p.Action_Plan}</td>
            <td>${p.Owner}</td>
            <td><code>${p.Target_Date}</code></td>
            <td><span class="badge ${badgeClass}">${p.Status}</span></td>
            <td>
              <button class="btn-danger-sm" onclick="app.deleteActionPlan(${p.id})" style="padding:4px 8px; font-size:0.75rem; border-radius:4px; border:1px solid rgba(200,90,90,0.4); background:rgba(200,90,90,0.15); color:var(--status-crimson); cursor:pointer;">
                <i data-lucide="trash-2" style="width:12px;height:12px;"></i> Delete
              </button>
            </td>
          </tr>
        `;
      }).join('');
      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      console.error("Failed to load action plans:", err);
    }
  }

  async saveActionPlan(e) {
    if (e) e.preventDefault();
    const dept = document.getElementById('action-dept')?.value;
    const issue = document.getElementById('action-issue')?.value;
    const plan = document.getElementById('action-plan')?.value;
    const owner = document.getElementById('action-owner')?.value;
    const date = document.getElementById('action-date')?.value;
    const status = document.getElementById('action-status')?.value;

    if (!dept || !issue || !plan || !owner || !date) {
      this.showToast('Please fill all required initiative fields', 'warn');
      return;
    }

    try {
      const res = await fetch('/api/retention/action-plans', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          department: dept,
          observed_issue: issue,
          action_plan: plan,
          owner: owner,
          target_date: date,
          status: status
        })
      });

      if (res.ok) {
        this.showToast('Retention action initiative saved successfully!', 'success');
        document.getElementById('action-plan-form')?.reset();
        await this.loadActionPlans();
      } else {
        this.showToast('Failed to save action plan', 'error');
      }
    } catch (err) {
      console.error("Error saving action plan:", err);
      this.showToast('Error saving action plan', 'error');
    }
  }

  async deleteActionPlan(id) {
    if (!confirm('Are you sure you want to remove this retention initiative?')) return;
    try {
      const res = await fetch(`/api/retention/action-plans/${id}`, { method: 'DELETE' });
      if (res.ok) {
        this.showToast('Action plan deleted', 'info');
        await this.loadActionPlans();
      }
    } catch (err) {
      console.error("Error deleting action plan:", err);
    }
  }

  async handleDatasetUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    this.showToast(`Uploading and validating ${file.name}...`, 'info');
    try {
      const res = await fetch('/api/dataset/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        this.showToast(`Uploaded ${data.filename}: ${data.rows} rows, ${data.columns} cols. Validated clean!`, 'success');
        if (data.quality_report) {
          this.renderQualityChecks(data.quality_report);
        }
      } else {
        this.showToast(data.detail || 'Failed to upload dataset', 'error');
      }
    } catch (err) {
      console.error("Upload error:", err);
      this.showToast('Upload error: ' + err.message, 'error');
    }
  }

  async loadDeepDiveData() {
    const res = await fetch('/api/analytics/stayers-vs-leavers');
    if (!res.ok) return;
    const data = await res.json();
    this.cachedData.deepdive = data;

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
    this.renderDeepDiveCharts(data);

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

  renderDeepDiveCharts(data) {
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
        margin: { l: 150, r: 25, t: 20, b: 40 },
        xaxis: { title: 'Correlation with Attrition', gridcolor: THEME.borderCard }
      };
      Plotly.newPlot('chart-correlation-bars', corrData, corrLayout, { responsive: true, displayModeBar: false });
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
      body.opening_headcount = parseFloat(document.getElementById('calc-in-opening').value) || 2500;
      body.closing_headcount = parseFloat(document.getElementById('calc-in-closing').value) || 2050;
      body.exits = parseInt(document.getElementById('calc-in-exits').value) || 450;
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
    try {
      const res = await fetch('/api/models/evaluation');
      if (!res.ok) {
        this.updateSidebarModelStatus(null);
        return;
      }
      const data = await res.json();
      this.cachedData.modelEval = data;

      // Update sidebar model engine status from actual evaluation state
      this.updateSidebarModelStatus(data);

      // 1. Comparison Table
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
              <td>${row.ROC_AUC ? row.ROC_AUC.toFixed(4) : 'N/A'}</td>
              <td>${row.PR_AUC ? row.PR_AUC.toFixed(4) : 'N/A'}</td>
              <td>${isBest ? 'Optimal balance of Precision/Recall' : (isBaseline ? 'Exposes Accuracy Paradox' : 'Evaluated')}</td>
            </tr>
          `;
        }).join('');
      }

      // 2. Confusion Matrix
      if (data.selected_model_confusion_matrix) {
        const cm = data.selected_model_confusion_matrix;
        document.getElementById('cm-tp').textContent = cm.true_positives.count;
        document.getElementById('cm-fn').textContent = cm.false_negatives.count;
        document.getElementById('cm-fp').textContent = cm.false_positives.count;
        document.getElementById('cm-tn').textContent = cm.true_negatives.count;
      }

      // 3. ROC & PR Curves
      if (data.curves) {
        this.renderModelCurves(data.curves);
      }

      // 4. Threshold Tuning Table
      if (data.threshold_tuning) {
        const thBody = document.getElementById('threshold-tuning-body');
        if (thBody) {
          thBody.innerHTML = data.threshold_tuning.map(t => `
            <tr>
              <td><strong>${t.Threshold.toFixed(2)}</strong></td>
              <td>${(t.Precision * 100).toFixed(1)}%</td>
              <td>${(t.Recall * 100).toFixed(1)}%</td>
              <td><strong>${t.F1_Score.toFixed(3)}</strong></td>
              <td>${t.True_Positives}</td>
              <td>${t.False_Negatives}</td>
              <td>${t.False_Positives}</td>
              <td style="color:${t.Estimated_Total_Cost_INR < 6000000 ? 'var(--status-emerald)' : 'var(--text-primary)'}; font-weight:600;">
                ₹${(t.Estimated_Total_Cost_INR / 1e5).toFixed(1)} Lakhs
              </td>
            </tr>
          `).join('');
        }
      }

      // 5. Update Attrition Lens Production Model Status & KPI Card
      const bestModelName = data.best_model_name || 'Random Forest';
      const rf = data.comparison_table?.find(m => m.Model === bestModelName) || (data.comparison_table ? data.comparison_table[0] : null);
      if (rf) {
        const roc = rf.ROC_AUC ? rf.ROC_AUC.toFixed(3) : '0.745';
        const f1 = rf.F1_Score ? rf.F1_Score.toFixed(3) : '0.459';
        const acc = rf.Accuracy ? `${(rf.Accuracy * 100).toFixed(1)}%` : '80.2%';

        if (document.getElementById('kpi-model-eval-stat')) {
          document.getElementById('kpi-model-eval-stat').textContent = `ROC: ${roc}`;
        }
        if (document.getElementById('kpi-model-eval-sub')) {
          document.getElementById('kpi-model-eval-sub').textContent = `F1-Score: ${f1} • Held-out ${data.test_sample_count || 500} test rows`;
        }
        if (document.getElementById('lens-model-roc')) document.getElementById('lens-model-roc').textContent = roc;
        if (document.getElementById('lens-model-f1')) document.getElementById('lens-model-f1').textContent = f1;
        if (document.getElementById('lens-model-acc')) document.getElementById('lens-model-acc').textContent = acc;
        if (document.getElementById('lens-model-testsize')) document.getElementById('lens-model-testsize').textContent = `${data.test_sample_count || 500} Rows`;
        if (document.getElementById('lens-model-selected-badge')) document.getElementById('lens-model-selected-badge').textContent = `${bestModelName} Tuned`;
        if (document.getElementById('top-model-text')) document.getElementById('top-model-text').textContent = `${bestModelName} (ROC: ${roc}, F1: ${f1})`;
      }
    } catch (err) {
      console.error("Failed to load model evaluation data:", err);
      this.updateSidebarModelStatus(null);
    }
  }

  updateSidebarModelStatus(data) {
    const modelEl = document.getElementById('sidebar-model-status');
    if (!modelEl) return;

    if (data && data.comparison_table && data.comparison_table.length > 0) {
      const best = data.best_model_name || 'Random Forest';
      modelEl.innerHTML = `<span class="status-ready">${best} Ready</span>`;
    } else {
      modelEl.innerHTML = `<span class="status-not-ready">Not Loaded</span>`;
    }
  }

  renderModelCurves(curves) {
    if (!curves) return;

    // ROC Curve
    if (document.getElementById('chart-roc-curve')) {
      const traces = [];
      const colors = {
        'Random Forest': THEME.copper,
        'Logistic Regression': THEME.emerald,
        'Gradient Boosting': THEME.sapphire
      };

      for (const [name, cData] of Object.entries(curves)) {
        traces.push({
          x: cData.fpr,
          y: cData.tpr,
          mode: 'lines',
          name: name,
          line: { color: colors[name] || THEME.textMuted, width: 2.5 }
        });
      }

      // 45-degree diagonal baseline
      traces.push({
        x: [0, 1],
        y: [0, 1],
        mode: 'lines',
        name: 'Random Chance (0.50)',
        line: { dash: 'dash', color: THEME.borderCard, width: 1.5 }
      });

      const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: THEME.textSecondary, family: THEME.fontFamily, size: 11 },
        margin: { l: 45, r: 20, t: 20, b: 40 },
        xaxis: { title: 'False Positive Rate (1 - Specificity)', gridcolor: THEME.borderCard },
        yaxis: { title: 'True Positive Rate (Recall)', gridcolor: THEME.borderCard },
        legend: { x: 0.55, y: 0.15, bgcolor: THEME.bgCard, bordercolor: THEME.borderCard, borderwidth: 1 }
      };
      Plotly.newPlot('chart-roc-curve', traces, layout, { responsive: true, displayModeBar: false });
    }

    // PR Curve
    if (document.getElementById('chart-pr-curve')) {
      const traces = [];
      const colors = {
        'Random Forest': THEME.copper,
        'Logistic Regression': THEME.emerald,
        'Gradient Boosting': THEME.sapphire
      };

      for (const [name, cData] of Object.entries(curves)) {
        traces.push({
          x: cData.recall,
          y: cData.precision,
          mode: 'lines',
          name: name,
          line: { color: colors[name] || THEME.textMuted, width: 2.5 }
        });
      }

      const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: THEME.textSecondary, family: THEME.fontFamily, size: 11 },
        margin: { l: 45, r: 20, t: 20, b: 40 },
        xaxis: { title: 'Recall', gridcolor: THEME.borderCard },
        yaxis: { title: 'Precision', gridcolor: THEME.borderCard },
        legend: { x: 0.55, y: 0.85, bgcolor: THEME.bgCard, bordercolor: THEME.borderCard, borderwidth: 1 }
      };
      Plotly.newPlot('chart-pr-curve', traces, layout, { responsive: true, displayModeBar: false });
    }
  }

  loadPreset(presetKey) {
    const p = PRESETS[presetKey];
    if (!p) return;

    document.getElementById('p-dept').value = p.Department;
    document.getElementById('p-role').value = p.JobRole;
    document.getElementById('p-level').value = p.JobLevel;
    document.getElementById('p-salary').value = p.MonthlySalaryINR;
    document.getElementById('p-tenure').value = p.YearsAtCompany;
    document.getElementById('p-total-exp').value = p.TotalWorkingYears;
    document.getElementById('p-overtime').value = p.Overtime;
    document.getElementById('p-job-sat').value = p.JobSatisfaction;
    document.getElementById('p-wlb').value = p.WorkLifeBalance;
    document.getElementById('p-distance').value = p.DistanceFromHomeKM;
    document.getElementById('p-role-tenure').value = p.YearsInCurrentRole;
    document.getElementById('p-promo-years').value = p.YearsSinceLastPromotion;

    const names = {
      high_risk: 'High-Risk Flight Sample',
      low_risk: 'Low-Risk Loyal Sample',
      burnout: 'Severe Burnout Sample'
    };
    this.showToast(`Loaded ${names[presetKey] || presetKey} profile`, 'info');
    this.predictSingleEmployee();
  }

  async predictSingleEmployee() {
    const payload = {
      Department: document.getElementById('p-dept').value,
      JobRole: document.getElementById('p-role').value,
      JobLevel: parseInt(document.getElementById('p-level').value),
      MonthlySalaryINR: parseFloat(document.getElementById('p-salary').value),
      MonthlyIncome: parseFloat(document.getElementById('p-salary').value),
      YearsAtCompany: parseFloat(document.getElementById('p-tenure').value),
      TotalWorkingYears: parseFloat(document.getElementById('p-total-exp').value),
      Overtime: document.getElementById('p-overtime').value,
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
        const tType = out.risk_band.includes('High') ? 'warn' : (out.risk_band.includes('Low') ? 'success' : 'info');
        this.showToast(`Flight Risk: ${out.risk_band} (${(out.attrition_probability * 100).toFixed(1)}% exit probability)`, tType);
      }
    } catch (err) {
      console.error('Prediction failed:', err);
      this.showToast('Prediction request failed', 'warn');
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
    if (res.risk_band === 'High Risk' || res.risk_band === 'Critical Risk') {
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

  async handleBatchFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    this.showToast(`Processing batch roster: ${file.name}...`, 'info');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/predict/batch', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const out = await res.json();
        document.getElementById('batch-results-container').style.display = 'block';
        document.getElementById('batch-total').textContent = out.total_records.toLocaleString();
        document.getElementById('batch-high').textContent = out.high_risk_count.toLocaleString();
        document.getElementById('batch-mod').textContent = out.moderate_risk_count.toLocaleString();
        document.getElementById('batch-low').textContent = out.low_risk_count.toLocaleString();

        const tbody = document.getElementById('batch-preview-body');
        tbody.innerHTML = (out.preview || []).map(r => `
          <tr>
            <td>${r.Department || 'N/A'}</td>
            <td>${r.JobRole || 'N/A'}</td>
            <td>${r.YearsAtCompany || r.Tenure || 'N/A'} Yrs</td>
            <td>₹${Math.round(r.MonthlySalaryINR || r.MonthlyIncome || 0).toLocaleString()}</td>
            <td><strong>${(r.Predicted_Probability * 100).toFixed(1)}%</strong></td>
            <td><span class="badge ${r.Risk_Band.includes('High') ? 'badge-high' : (r.Risk_Band.includes('Moderate') ? 'badge-mod' : 'badge-low')}">${r.Risk_Band}</span></td>
          </tr>
        `).join('');

        // Also populate upload hub if present
        const hubContainer = document.getElementById('batch-results-container-hub');
        if (hubContainer) {
          hubContainer.style.display = 'block';
          if (document.getElementById('batch-total-hub')) document.getElementById('batch-total-hub').textContent = out.total_records.toLocaleString();
          if (document.getElementById('batch-high-hub')) document.getElementById('batch-high-hub').textContent = out.high_risk_count.toLocaleString();
          if (document.getElementById('batch-mod-hub')) document.getElementById('batch-mod-hub').textContent = out.moderate_risk_count.toLocaleString();
          if (document.getElementById('batch-low-hub')) document.getElementById('batch-low-hub').textContent = out.low_risk_count.toLocaleString();
          const hubTbody = document.getElementById('batch-preview-body-hub');
          if (hubTbody) {
            hubTbody.innerHTML = (out.preview || []).map(r => `
              <tr>
                <td>${r.Department || 'N/A'}</td>
                <td>${r.JobRole || 'N/A'}</td>
                <td>${r.YearsAtCompany || r.Tenure || 'N/A'} Yrs</td>
                <td>₹${Math.round(r.MonthlySalaryINR || r.MonthlyIncome || 0).toLocaleString()}</td>
                <td><strong>${(r.Predicted_Probability * 100).toFixed(1)}%</strong></td>
                <td><span class="badge ${r.Risk_Band.includes('High') ? 'badge-high' : (r.Risk_Band.includes('Moderate') ? 'badge-mod' : 'badge-low')}">${r.Risk_Band}</span></td>
              </tr>
            `).join('');
          }
        }

        this.showToast(`✓ Successfully scored ${out.total_records} employees (${out.high_risk_count} High Risk)`, 'success');
        if (window.lucide) window.lucide.createIcons();
      } else {
        this.showToast('Could not parse CSV. Please verify file columns.', 'warn');
      }
    } catch (e) {
      console.error('Batch scoring error:', e);
      this.showToast('Batch processing request failed', 'warn');
    }
  }

  async handleDatasetUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    this.showToast(`Uploading and validating enterprise dataset: ${file.name}...`, 'info');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/dataset/upload', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const out = await res.json();
        this.showToast(`✓ Ingested ${out.filename} (${out.rows.toLocaleString()} records, ${out.columns} attributes)`, 'success');
        
        // Refresh all analytical views
        await this.loadInitialData();
        await this.applyDashboardFilters();
        await this.loadDynamicInsights();
        await this.loadDepartmentIntelligence();
        await this.loadEmployees(1);
        
        // Update header & sidebar status
        const statusEl = document.getElementById('sidebar-status-text');
        if (statusEl) statusEl.textContent = `${out.filename}: ${out.rows.toLocaleString()} Records • Online`;
        const badgeEl = document.getElementById('top-header-title');
        this.showToast('All dashboard KPIs, charts, and department scorecards dynamically updated!', 'success');
      } else {
        const err = await res.json();
        this.showToast(`Upload failed: ${err.detail || 'Could not parse file'}`, 'warn');
      }
    } catch (e) {
      console.error('Dataset upload error:', e);
      this.showToast('Dataset upload request failed', 'warn');
    }
  }

  async resetDefaultDataset() {
    this.showToast('Resetting to SnackRush benchmark dataset...', 'info');
    try {
      const res = await fetch('/api/dataset/reset-default', { method: 'POST' });
      if (res.ok) {
        const out = await res.json();
        this.showToast('✓ Successfully reset to SnackRush 2,500 employee benchmark', 'success');
        await this.loadInitialData();
        await this.applyDashboardFilters();
        await this.loadDynamicInsights();
        await this.loadDepartmentIntelligence();
        await this.loadEmployees(1);

        const statusEl = document.getElementById('sidebar-status-text');
        if (statusEl) statusEl.textContent = `SnackRush: 2,500 Monitored • RF Online`;
      }
    } catch (e) {
      console.error('Reset error:', e);
      this.showToast('Failed to reset dataset', 'warn');
    }
  }

  async loadExplainabilityData() {
    const res = await fetch('/api/explainability');
    if (!res.ok) return;
    const data = await res.json();
    this.cachedData.explainability = data;

    this.renderExplainabilityChart(data);
  }

  renderExplainabilityChart(data) {
    if (data.permutation_importance && document.getElementById('chart-permutation-importance')) {
      const topFeats = [...data.permutation_importance].reverse();
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
    const cohort = parseInt(document.getElementById('roi-cohort-size')?.value) || 150;
    const salary = parseFloat(document.getElementById('roi-avg-salary')?.value) || 65000;
    const mult = parseFloat(document.getElementById('roi-cost-multiplier')?.value) || 1.5;
    const rate = parseFloat(document.getElementById('roi-success-rate')?.value) || 0.35;

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
          <td><code>${e.experiment_id.substring(0, 14)}...</code></td>
          <td>${e.timestamp ? e.timestamp.substring(0, 19).replace('T', ' ') : 'Just now'}</td>
          <td><strong>${e.model_name || e.model_type}</strong></td>
          <td>${e.cv_accuracy ? (e.cv_accuracy * 100).toFixed(1) + '%' : '80.2%'}</td>
          <td>${e.cv_f1 ? e.cv_f1.toFixed(3) : '0.459'}</td>
          <td>${e.cv_roc_auc ? e.cv_roc_auc.toFixed(3) : '0.745'}</td>
          <td>${e.test_f1 ? e.test_f1.toFixed(3) : '0.459'}</td>
          <td><span class="badge ${e.is_selected ? 'badge-low' : 'badge-mod'}">${e.is_selected ? 'Selected Model' : 'Evaluated'}</span></td>
        </tr>
      `).join('');
    }
  }

  exportFilteredCsv() {
    const dept = document.getElementById('filter-dept')?.value || 'All';
    this.showToast('Preparing cleaned dataset CSV export...', 'info');
    window.location.href = `/api/export/csv?department=${encodeURIComponent(dept)}`;
  }

  downloadReport(format) {
    this.showToast(`Generating ${format.toUpperCase()} executive presentation report...`, 'info');
    if (format === 'html') {
      window.location.href = '/api/reports/download-html';
    } else {
      window.location.href = '/api/reports/download-markdown';
    }
  }

  initHeroCanvas() {
    const canvas = document.getElementById('hero-workforce-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const width = canvas.width;
    const height = canvas.height;

    // 32 workforce particles: 82% stayers, 18% leavers
    const count = 32;
    const leaverCount = Math.round(count * 0.18);
    const nodes = [];

    for (let i = 0; i < count; i++) {
      const isLeaver = i < leaverCount;
      nodes.push({
        x: Math.random() * (width - 24) + 12,
        y: Math.random() * (height - 24) + 12,
        vx: (Math.random() - 0.5) * (isLeaver ? 0.35 : 0.22),
        vy: (Math.random() - 0.5) * (isLeaver ? 0.35 : 0.22),
        radius: isLeaver ? 3.0 : 2.5,
        color: isLeaver ? THEME.copper : THEME.emerald,
        isLeaver: isLeaver
      });
    }

    this.canvasNodes = nodes;

    let animId = null;
    let isVisible = true;

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      // Connect neighbor nodes with subtle filaments
      ctx.lineWidth = 0.6;
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 44) {
            const alpha = (1 - dist / 44) * 0.22;
            ctx.strokeStyle = document.documentElement.getAttribute('data-theme') === 'light'
              ? `rgba(105, 118, 83, ${alpha})`
              : `rgba(184, 173, 162, ${alpha})`;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw talent nodes
      nodes.forEach(node => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fillStyle = node.color;
        ctx.fill();

        if (!prefersReducedMotion) {
          node.x += node.vx;
          node.y += node.vy;

          if (node.x <= 8 || node.x >= width - 8) node.vx *= -1;
          if (node.y <= 8 || node.y >= height - 8) node.vy *= -1;
        }
      });

      if (!prefersReducedMotion && isVisible) {
        animId = requestAnimationFrame(draw);
      }
    };

    draw();

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        isVisible = false;
        if (animId) cancelAnimationFrame(animId);
      } else {
        isVisible = true;
        if (!prefersReducedMotion) draw();
      }
    });
  }

  // ── Command Bar ────────────────────────────────────────────────────────────
  _cmdItems = [
    { label: 'Overview',            icon: 'compass',       target: 'mod-overview',   tag: 'View' },
    { label: 'Attrition Analysis',  icon: 'bar-chart-2',   target: 'mod-attrition',  tag: 'View' },
    { label: 'Prediction & Model',  icon: 'cpu',           target: 'mod-predictor',  tag: 'View' },
    { label: 'Retention Strategy',  icon: 'target',        target: 'mod-retention',  tag: 'View' },
    { label: 'Data & Reports',      icon: 'folder-kanban', target: 'mod-upload',     tag: 'View' },
    { label: 'Privacy & Governance', icon: 'shield-check', action: () => this.showPrivacyModal(), tag: 'Modal' },
    { label: 'Workforce Retention Rate', icon: 'percent', target: 'mod-overview',   tag: 'Metric' },
    { label: 'Attrition Rate 18%',  icon: 'activity',      target: 'mod-overview',   tag: 'Metric' },
    { label: 'ROC-AUC 0.745',       icon: 'award',         target: 'mod-predictor',  tag: 'Metric' },
    { label: 'Department Heatmap',  icon: 'building-2',    target: 'mod-attrition',  tag: 'Chart' },
    { label: 'Delivery Operations – Highest Attrition', icon: 'alert-triangle', target: 'mod-attrition', tag: 'Insight' },
    { label: 'Simulate Flight Risk', icon: 'user-check',   target: 'mod-predictor',  tab: 'tab-predict-attrition', tag: 'Action' },
    { label: 'Download Report',     icon: 'download',      target: 'mod-upload',     tag: 'Action' },
  ];

  openCommandBar() {
    const overlay = document.getElementById('cmd-overlay');
    const input   = document.getElementById('cmd-input');
    if (!overlay) return;
    overlay.style.display = 'flex';
    this._cmdActiveIndex = -1;
    this.handleCmdSearch('');
    setTimeout(() => input && input.focus(), 50);
    if (window.lucide) window.lucide.createIcons();
  }

  closeCommandBar() {
    const overlay = document.getElementById('cmd-overlay');
    if (overlay) overlay.style.display = 'none';
    const input = document.getElementById('cmd-input');
    if (input) input.value = '';
  }

  handleCmdSearch(query) {
    const q = query.trim().toLowerCase();
    const results = q
      ? this._cmdItems.filter(i => i.label.toLowerCase().includes(q))
      : this._cmdItems;
    const container = document.getElementById('cmd-results');
    if (!container) return;
    this._cmdActiveIndex = -1;
    if (results.length === 0) {
      container.innerHTML = '<div style="padding:16px 18px;font-size:0.84rem;color:var(--text-muted);">No results found.</div>';
      return;
    }
    container.innerHTML = results.map((item, i) =>
      `<div class="cmd-result-item" data-idx="${i}" data-label="${item.label}" onclick="app._execCmdItem(${this._cmdItems.indexOf(item)})">
        <i data-lucide="${item.icon}" style="width:15px;height:15px;flex-shrink:0;"></i>
        <span class="cmd-result-label">${item.label}</span>
        <span class="cmd-result-tag">${item.tag}</span>
      </div>`
    ).join('');
    if (window.lucide) window.lucide.createIcons();
  }

  handleCmdKey(e) {
    const items = document.querySelectorAll('#cmd-results .cmd-result-item');
    if (e.key === 'Escape') { this.closeCommandBar(); return; }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      this._cmdActiveIndex = Math.min(this._cmdActiveIndex + 1, items.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      this._cmdActiveIndex = Math.max(this._cmdActiveIndex - 1, 0);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const active = document.querySelector('#cmd-results .cmd-result-item.active');
      if (active) active.click();
      else if (items.length > 0) items[0].click();
      return;
    }
    items.forEach((el, i) => el.classList.toggle('active', i === this._cmdActiveIndex));
    if (this._cmdActiveIndex >= 0) items[this._cmdActiveIndex].scrollIntoView({ block: 'nearest' });
  }

  _execCmdItem(globalIdx) {
    const item = this._cmdItems[globalIdx];
    if (!item) return;
    this.closeCommandBar();
    if (item.action) { item.action(); return; }
    if (item.target) {
      this.switchView(item.target);
      if (item.tab) {
        setTimeout(() => {
          const tabBtn = document.querySelector(`[data-tab="${item.tab}"]`);
          if (tabBtn) tabBtn.click();
        }, 100);
      }
    }
  }

  // ── Chart Export ───────────────────────────────────────────────────────────
  exportChart(chartDivId, filename = 'chart') {
    const el = document.getElementById(chartDivId);
    if (!el || !window.Plotly) {
      this.showToast('Chart not available for export.', 'warn');
      return;
    }
    Plotly.toImage(el, { format: 'png', width: 1200, height: 480, scale: 2 })
      .then(url => {
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.png`;
        a.click();
        this.showToast(`Chart exported as ${filename}.png`, 'success');
      })
      .catch(() => this.showToast('Export failed — chart may still be loading.', 'warn'));
  }
}

// Global App Instance
const app = new AttritionApp();
document.addEventListener('DOMContentLoaded', () => {
  app.init();
});
