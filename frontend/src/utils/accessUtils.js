/**
 * Access Control Utilities
 * Utility functions for handling access control and permission errors
 */

import { PopupService } from '@/modules/popup/popupService';

// Session Management Utilities
export const SessionUtils = {
  /**
   * Set user session data
   * @param {Object} userData - User data from login response
   */
  setUserSession(userData) {
    console.log('[SESSION_UTILS] Setting user session:', userData);
    if (userData.user_id) {
      localStorage.setItem('user_id', userData.user_id.toString());
    }
    if (userData.email) {
      localStorage.setItem('user_email', userData.email);
    }
    if (userData.name) {
      localStorage.setItem('user_name', userData.name);
    }
    // Set a flag to indicate user is logged in
    localStorage.setItem('is_logged_in', 'true');
  },

  /**
   * Get user session data
   * @returns {Object} User session data
   */
  getUserSession() {
    return {
      user_id: localStorage.getItem('user_id'),
      email: localStorage.getItem('user_email'),
      name: localStorage.getItem('user_name'),
      is_logged_in: localStorage.getItem('is_logged_in') === 'true'
    };
  },

  /**
   * Clear user session
   */
  clearUserSession() {
    console.log('[SESSION_UTILS] Clearing user session');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_name');
    localStorage.removeItem('is_logged_in');
  },

  /**
   * Check if user is logged in
   * @returns {boolean} True if user is logged in
   */
  isLoggedIn() {
    return localStorage.getItem('is_logged_in') === 'true';
  },

  /**
   * Get user ID for API requests
   * @returns {string|null} User ID or null if not logged in
   */
  getUserId() {
    return localStorage.getItem('user_id');
  }
};

export const AccessUtils = {
  /**
   * Show access denied popup with default message
   * @param {string} feature - Feature name (e.g., 'Risk Management', 'Create Risk')
   * @param {string} customMessage - Custom message to display
   * @param {Function} onContactAdmin - Callback for contact admin action
   */
  showAccessDenied(feature = 'this feature', customMessage = null, onContactAdmin = null) {
    console.log('[ACCESS_UTILS] showAccessDenied called:', { feature, customMessage, hasCallback: !!onContactAdmin });
    
    const defaultMessage = `You don't have permission to access ${feature}. Please contact your administrator to activate this feature.`;
    const message = customMessage || defaultMessage;
    
    console.log('[ACCESS_UTILS] Calling PopupService.accessDenied with message:', message);
    
    try {
      PopupService.accessDenied(message, 'Access Denied', onContactAdmin || this.defaultContactAdmin);
      console.log('[ACCESS_UTILS] PopupService.accessDenied called successfully');
    } catch (error) {
      console.error('[ACCESS_UTILS] Error calling PopupService.accessDenied:', error);
    }
  },

  /**
   * Show access denied popup for specific risk operations
   * @param {string} operation - Operation type (e.g., 'create', 'edit', 'view', 'delete')
   * @param {Function} onContactAdmin - Callback for contact admin action
   */
  showRiskAccessDenied(operation = 'access', onContactAdmin = null) {
    console.log('[ACCESS_UTILS] showRiskAccessDenied called:', { operation, hasCallback: !!onContactAdmin });
    
    const operationText = {
      create: 'create new risks',
      edit: 'edit risks',
      view: 'view risks',
      delete: 'delete risks',
      approve: 'approve risks',
      assign: 'assign risks',
      analytics: 'view risk analytics',
      access: 'access the risk module'
    }[operation] || operation;

    const message = `You don't have permission to ${operationText}. Please contact your administrator to request access to this feature.`;
    
    console.log('[ACCESS_UTILS] Calling PopupService.accessDenied with risk message:', message);
    
    try {
      PopupService.accessDenied(message, 'Risk Access Denied', onContactAdmin || this.defaultContactAdmin);
      console.log('[ACCESS_UTILS] Risk access denied popup called successfully');
    } catch (error) {
      console.error('[ACCESS_UTILS] Error calling risk access denied popup:', error);
    }
  },

  /**
   * Show access denied popup for specific compliance operations (5 main features)
   * @param {string} operation - Operation type
   * @param {Function} onContactAdmin - Callback for contact admin action
   */
  showComplianceAccessDenied(operation = 'access', onContactAdmin = null) {
    console.log('[ACCESS_UTILS] showComplianceAccessDenied called:', { operation });
    
    // Map operations to main features and descriptions
    const operationFeatureMap = {
      // CreateCompliance operations
      create: { feature: 'CreateCompliance', text: 'create compliance items' },
      clone: { feature: 'CreateCompliance', text: 'clone compliance items' },
      
      // EditCompliance operations
      edit: { feature: 'EditCompliance', text: 'edit compliance items' },
      toggle: { feature: 'EditCompliance', text: 'toggle compliance status' },
      deactivate: { feature: 'EditCompliance', text: 'deactivate compliance items' },
      delete: { feature: 'EditCompliance', text: 'delete compliance items' },
      assign: { feature: 'EditCompliance', text: 'assign compliance items' },
      category: { feature: 'EditCompliance', text: 'manage compliance categories' },
      'business-unit': { feature: 'EditCompliance', text: 'manage compliance business units' },
      
      // ApproveCompliance operations
      approve: { feature: 'ApproveCompliance', text: 'approve compliance items' },
      review: { feature: 'ApproveCompliance', text: 'review compliance items' },
      
      // ViewAllCompliance operations
      view: { feature: 'ViewAllCompliance', text: 'view compliance items' },
      dashboard: { feature: 'ViewAllCompliance', text: 'access the compliance dashboard' },
      versioning: { feature: 'ViewAllCompliance', text: 'view compliance versioning' },
      audit: { feature: 'ViewAllCompliance', text: 'view compliance audit information' },
      framework: { feature: 'ViewAllCompliance', text: 'access compliance frameworks' },
      policy: { feature: 'ViewAllCompliance', text: 'access compliance policies' },
      subpolicy: { feature: 'ViewAllCompliance', text: 'access compliance subpolicies' },
      notification: { feature: 'ViewAllCompliance', text: 'view compliance notifications' },
      export: { feature: 'ViewAllCompliance', text: 'export compliance data' },
      access: { feature: 'ViewAllCompliance', text: 'access the compliance module' },
      
      // CompliancePerformanceAnalytics operations
      analytics: { feature: 'CompliancePerformanceAnalytics', text: 'view compliance analytics' },
      kpi: { feature: 'CompliancePerformanceAnalytics', text: 'view compliance KPIs' }
    };

    const operationInfo = operationFeatureMap[operation] || { feature: 'ViewAllCompliance', text: operation };
    
    const message = `You don't have permission to ${operationInfo.text}. Please contact your administrator to request the "${operationInfo.feature}" permission.`;
    
    PopupService.accessDenied(message, 'Compliance Access Denied', onContactAdmin || this.defaultContactAdmin);
  },

  /**
   * Show access denied popup for specific main compliance features
   * @param {string} feature - Main feature name (CreateCompliance, EditCompliance, etc.)
   * @param {Function} onContactAdmin - Callback for contact admin action
   */
  showComplianceFeatureDenied(feature, onContactAdmin = null) {
    console.log('[ACCESS_UTILS] showComplianceFeatureDenied called:', { feature });
    
    const featureMessages = {
      'CreateCompliance': 'create compliance items',
      'EditCompliance': 'edit compliance items',
      'ApproveCompliance': 'approve compliance items',
      'ViewAllCompliance': 'view compliance information',
      'CompliancePerformanceAnalytics': 'view compliance performance analytics'
    };
    
    const operationText = featureMessages[feature] || 'access this compliance feature';
    const message = `You don't have permission to ${operationText}. Please contact your administrator to request the "${feature}" permission.`;
    
    PopupService.accessDenied(message, 'Compliance Access Denied', onContactAdmin || this.defaultContactAdmin);
  },

  /**
   * Comprehensive compliance access control methods
   */
  
  // Compliance viewing methods
  showComplianceViewDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('view', onContactAdmin);
  },
  
  showComplianceDashboardDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('dashboard', onContactAdmin);
  },
  
  showComplianceVersioningDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('versioning', onContactAdmin);
  },
  
  // Compliance creation methods
  showComplianceCreateDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('create', onContactAdmin);
  },
  
  showComplianceCloneDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('clone', onContactAdmin);
  },
  
  // Compliance editing methods
  showComplianceEditDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('edit', onContactAdmin);
  },
  
  showComplianceToggleDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('toggle', onContactAdmin);
  },
  
  showComplianceDeactivateDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('deactivate', onContactAdmin);
  },
  
  // Compliance approval methods
  showComplianceApproveDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('approve', onContactAdmin);
  },
  
  showComplianceReviewDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('review', onContactAdmin);
  },
  
  // Compliance analytics methods
  showComplianceAnalyticsDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('analytics', onContactAdmin);
  },
  
  showComplianceKPIDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('kpi', onContactAdmin);
  },
  
  showCompliancePerformanceAnalyticsDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('analytics', onContactAdmin);
  },
  
  // 5 Main Compliance Features
  showCreateComplianceDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('create', onContactAdmin);
  },
  
  showEditComplianceDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('edit', onContactAdmin);
  },
  
  showApproveComplianceDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('approve', onContactAdmin);
  },
  
  showViewAllComplianceDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('view', onContactAdmin);
  },
  
  // Compliance export methods
  showComplianceExportDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('export', onContactAdmin);
  },
  
  // Compliance audit methods
  showComplianceAuditDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('audit', onContactAdmin);
  },
  
  // Compliance framework methods
  showComplianceFrameworkDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('framework', onContactAdmin);
  },
  
  showCompliancePolicyDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('policy', onContactAdmin);
  },
  
  showComplianceSubpolicyDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('subpolicy', onContactAdmin);
  },
  
  // Compliance category methods
  showComplianceCategoryDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('category', onContactAdmin);
  },
  
  showComplianceBusinessUnitDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('business-unit', onContactAdmin);
  },
  
  // Compliance notification methods
  showComplianceNotificationDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('notification', onContactAdmin);
  },
  
  // Compliance assignment methods
  showComplianceAssignDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('assign', onContactAdmin);
  },
  
  // Compliance deletion methods
  showComplianceDeleteDenied(onContactAdmin = null) {
    this.showComplianceAccessDenied('delete', onContactAdmin);
  },

  /**
   * Show access denied popup for specific incident operations
   * @param {string} operation - Operation type
   * @param {Function} onContactAdmin - Callback for contact admin action
   */
  showIncidentAccessDenied(operation = 'access', onContactAdmin = null) {
    console.log('[ACCESS_UTILS] showIncidentAccessDenied called:', { operation });
    
    const operationText = {
      create: 'create incidents',
      edit: 'edit incidents',
      view: 'view incidents',
      delete: 'delete incidents',
      assign: 'assign incidents',
      escalate: 'escalate incidents',
      analytics: 'view incident analytics',
      access: 'access the incident module'
    }[operation] || operation;

    const message = `You don't have permission to ${operationText}. Please contact your administrator to request access to this feature.`;
    
    PopupService.accessDenied(message, 'Incident Access Denied', onContactAdmin || this.defaultContactAdmin);
  },

  /**
   * Show access denied popup for specific audit operations (6 main audit permissions)
   * @param {string} operation - Operation type
   * @param {Function} onContactAdmin - Callback for contact admin action
   */
  showAuditAccessDenied(operation = 'access', onContactAdmin = null) {
    console.log('[ACCESS_UTILS] showAuditAccessDenied called:', { operation });
    
    // Map operations to main audit permissions and descriptions
    const operationFeatureMap = {
      // AssignAudit operations
      assign: { feature: 'AssignAudit', text: 'assign audits' },
      create: { feature: 'AssignAudit', text: 'create audit assignments' },
      'assign-audit': { feature: 'AssignAudit', text: 'assign audit tasks' },
      'create-audit': { feature: 'AssignAudit', text: 'create new audits' },
      
      // ConductAudit operations
      conduct: { feature: 'ConductAudit', text: 'conduct audits' },
      perform: { feature: 'ConductAudit', text: 'perform audit tasks' },
      'conduct-audit': { feature: 'ConductAudit', text: 'conduct audit activities' },
      'update-task': { feature: 'ConductAudit', text: 'update audit tasks' },
      'checklist': { feature: 'ConductAudit', text: 'manage audit checklists' },
      
      // ReviewAudit operations
      review: { feature: 'ReviewAudit', text: 'review audits' },
      approve: { feature: 'ReviewAudit', text: 'approve audit results' },
      'review-audit': { feature: 'ReviewAudit', text: 'review audit submissions' },
      'approve-audit': { feature: 'ReviewAudit', text: 'approve audit reports' },
      
      // ViewAuditReports operations
      'view-reports': { feature: 'ViewAuditReports', text: 'view audit reports' },
      'generate-reports': { feature: 'ViewAuditReports', text: 'generate audit reports' },
      'download-reports': { feature: 'ViewAuditReports', text: 'download audit reports' },
      reports: { feature: 'ViewAuditReports', text: 'access audit reports' },
      
      // AuditPerformanceAnalytics operations
      analytics: { feature: 'AuditPerformanceAnalytics', text: 'view audit analytics' },
      kpi: { feature: 'AuditPerformanceAnalytics', text: 'view audit KPIs' },
      metrics: { feature: 'AuditPerformanceAnalytics', text: 'view audit metrics' },
      performance: { feature: 'AuditPerformanceAnalytics', text: 'view audit performance data' },
      
      // ViewAllAudits operations
      view: { feature: 'ViewAllAudits', text: 'view audit information' },
      'view-all': { feature: 'ViewAllAudits', text: 'view all audits' },
      dashboard: { feature: 'ViewAllAudits', text: 'access the audit dashboard' },
      list: { feature: 'ViewAllAudits', text: 'list audit items' },
      search: { feature: 'ViewAllAudits', text: 'search audits' },
      access: { feature: 'ViewAllAudits', text: 'access the audit module' }
    };

    const operationInfo = operationFeatureMap[operation] || { feature: 'ViewAllAudits', text: operation };
    
    const message = `You don't have permission to ${operationInfo.text}. Please contact your administrator to request the "${operationInfo.feature}" permission.`;
    
    PopupService.accessDenied(message, 'Audit Access Denied', onContactAdmin || this.defaultContactAdmin);
  },

  /**
   * Show access denied popup for specific main audit features
   * @param {string} feature - Main audit feature name (AssignAudit, ConductAudit, etc.)
   * @param {Function} onContactAdmin - Callback for contact admin action
   */
  showAuditFeatureDenied(feature, onContactAdmin = null) {
    console.log('[ACCESS_UTILS] showAuditFeatureDenied called:', { feature });
    
    const featureMessages = {
      'AssignAudit': 'assign audits',
      'ConductAudit': 'conduct audits',
      'ReviewAudit': 'review audits',
      'ViewAuditReports': 'view audit reports',
      'AuditPerformanceAnalytics': 'view audit performance analytics',
      'ViewAllAudits': 'view audit information'
    };
    
    const operationText = featureMessages[feature] || 'access this audit feature';
    const message = `You don't have permission to ${operationText}. Please contact your administrator to request the "${feature}" permission.`;
    
    PopupService.accessDenied(message, 'Audit Access Denied', onContactAdmin || this.defaultContactAdmin);
  },

  /**
   * Comprehensive audit access control methods
   */
  
  // Main audit feature access methods
  showAuditViewDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('view', onContactAdmin);
  },
  
  showAuditDashboardDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('dashboard', onContactAdmin);
  },
  
  showAuditListDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('list', onContactAdmin);
  },
  
  // Audit assignment methods
  showAuditAssignDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('assign', onContactAdmin);
  },
  
  showAuditCreateDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('create', onContactAdmin);
  },
  
  showCreateAuditDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('create-audit', onContactAdmin);
  },
  
  // Audit conduct methods
  showAuditConductDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('conduct', onContactAdmin);
  },
  
  showAuditPerformDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('perform', onContactAdmin);
  },
  
  showAuditTaskUpdateDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('update-task', onContactAdmin);
  },
  
  showAuditChecklistDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('checklist', onContactAdmin);
  },
  
  // Audit review methods
  showAuditReviewDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('review', onContactAdmin);
  },
  
  showAuditApproveDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('approve', onContactAdmin);
  },
  
  // Audit reports methods
  showAuditReportsDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('reports', onContactAdmin);
  },
  
  showAuditViewReportsDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('view-reports', onContactAdmin);
  },
  
  showAuditGenerateReportsDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('generate-reports', onContactAdmin);
  },
  
  showAuditDownloadReportsDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('download-reports', onContactAdmin);
  },
  
  // Audit analytics methods
  showAuditAnalyticsDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('analytics', onContactAdmin);
  },
  
  showAuditKPIDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('kpi', onContactAdmin);
  },
  
  showAuditMetricsDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('metrics', onContactAdmin);
  },
  
  showAuditPerformanceAnalyticsDenied(onContactAdmin = null) {
    this.showAuditAccessDenied('performance', onContactAdmin);
  },
  
  // Main audit permission methods
  showAssignAuditDenied(onContactAdmin = null) {
    this.showAuditFeatureDenied('AssignAudit', onContactAdmin);
  },
  
  showConductAuditDenied(onContactAdmin = null) {
    this.showAuditFeatureDenied('ConductAudit', onContactAdmin);
  },
  
  showReviewAuditDenied(onContactAdmin = null) {
    this.showAuditFeatureDenied('ReviewAudit', onContactAdmin);
  },
  
  showViewAuditReportsDenied(onContactAdmin = null) {
    this.showAuditFeatureDenied('ViewAuditReports', onContactAdmin);
  },
  
  showAuditPerformanceAnalyticsPermissionDenied(onContactAdmin = null) {
    this.showAuditFeatureDenied('AuditPerformanceAnalytics', onContactAdmin);
  },
  
  showViewAllAuditsDenied(onContactAdmin = null) {
    this.showAuditFeatureDenied('ViewAllAudits', onContactAdmin);
  },

  /**
   * Default contact admin callback - can be customized per application
   */
  defaultContactAdmin() {
    console.log('[ACCESS_UTILS] defaultContactAdmin callback triggered');
    
    // You can customize this based on your application's admin contact method
    console.log('Contact admin action triggered');
    
    // Example: Open email client
    // window.location.href = 'mailto:admin@company.com?subject=Access Request&body=I need access to additional features in the GRC system.';
    
    // Example: Show additional instructions
    try {
      PopupService.info(
        'Please contact your system administrator via email or support ticket to request access to this feature.',
        'Contact Administrator'
      );
    } catch (error) {
      console.error('[ACCESS_UTILS] Error showing contact admin popup:', error);
    }
  },

  /**
   * Handle API error responses and show appropriate access denied popup
   * @param {Object} error - Error object from API response
   * @param {string} defaultFeature - Default feature name if not specified in error
   */
  handleApiError(error, defaultFeature = 'this feature') {
    console.log('[ACCESS_UTILS] handleApiError called:', { 
      error: error?.response?.status, 
      defaultFeature,
      errorResponse: error?.response?.data 
    });
    
    // Check if it's a 401/403 error (unauthorized/forbidden)
    if (error.response && [401, 403].includes(error.response.status)) {
      console.log('[ACCESS_UTILS] Detected 401/403 error, showing access denied popup');
      
      const errorMessage = error.response.data?.message || error.response.data?.detail;
      
      if (errorMessage) {
        console.log('[ACCESS_UTILS] Using custom error message:', errorMessage);
        this.showAccessDenied(defaultFeature, errorMessage);
      } else {
        console.log('[ACCESS_UTILS] Using default access denied message for:', defaultFeature);
        this.showAccessDenied(defaultFeature);
      }
      return true; // Indicates this was an access error
    }
    
    console.log('[ACCESS_UTILS] Not an access error, status:', error?.response?.status);
    return false; // Not an access error, should be handled elsewhere
  },

  /**
   * Handle API errors based on URL patterns
   * @param {Object} error - Error object from API response
   * @param {string} url - The API URL that failed
   */
  handleApiErrorByUrl(error, url) {
    console.log('[ACCESS_UTILS] handleApiErrorByUrl called:', { 
      status: error?.response?.status, 
      url,
      method: error?.config?.method?.toUpperCase()
    });

    if (!error.response || ![401, 403].includes(error.response.status)) {
      console.log('[ACCESS_UTILS] Not an access error, ignoring');
      return false;
    }

    const method = error?.config?.method?.toUpperCase() || 'GET';
    
    // Risk-related URLs
    if (url.includes('/api/risks/')) {
      console.log('[ACCESS_UTILS] Risk API access denied detected');
      
      if (method === 'POST') {
        this.showRiskAccessDenied('create');
      } else if (method === 'PUT' || method === 'PATCH') {
        this.showRiskAccessDenied('edit');
      } else if (method === 'DELETE') {
        this.showRiskAccessDenied('delete');
      } else {
        this.showRiskAccessDenied('view');
      }
      return true;
    }
    
    // Risk instances URLs
    if (url.includes('/api/risk-instances/')) {
      console.log('[ACCESS_UTILS] Risk instances API access denied detected');
      
      if (method === 'POST') {
        this.showRiskAccessDenied('create');
      } else if (method === 'PUT' || method === 'PATCH') {
        this.showRiskAccessDenied('edit');
      } else {
        this.showRiskAccessDenied('view');
      }
      return true;
    }
    
    // Risk analytics/metrics URLs
    if (url.includes('/api/risk/metrics') || url.includes('/api/risk/analytics')) {
      console.log('[ACCESS_UTILS] Risk analytics API access denied detected');
      this.showRiskAccessDenied('analytics');
      return true;
    }
    
    // Compliance URLs
    if (url.includes('/api/compliance/')) {
      console.log('[ACCESS_UTILS] Compliance API access denied detected');
      
      if (method === 'POST') {
        this.showComplianceAccessDenied('create');
      } else if (method === 'PUT' || method === 'PATCH') {
        this.showComplianceAccessDenied('edit');
      } else {
        this.showComplianceAccessDenied('view');
      }
      return true;
    }
    
    // Incident URLs
    if (url.includes('/api/incidents/')) {
      console.log('[ACCESS_UTILS] Incident API access denied detected');
      
      if (method === 'POST') {
        this.showIncidentAccessDenied('create');
      } else if (method === 'PUT' || method === 'PATCH') {
        this.showIncidentAccessDenied('edit');
      } else {
        this.showIncidentAccessDenied('view');
      }
      return true;
    }
    
    // Audit URLs
    if (url.includes('/api/audit/') || url.includes('/api/audits/')) {
      console.log('[ACCESS_UTILS] Audit API access denied detected');
      
      // Audit assignment URLs
      if (url.includes('/assign') || url.includes('/create')) {
        this.showAuditAccessDenied('assign');
        return true;
      }
      
      // Audit conduct URLs
      if (url.includes('/conduct') || url.includes('/tasks/') || url.includes('/checklist')) {
        this.showAuditAccessDenied('conduct');
        return true;
      }
      
      // Audit review URLs
      if (url.includes('/review') || url.includes('/approve')) {
        this.showAuditAccessDenied('review');
        return true;
      }
      
      // Audit reports URLs
      if (url.includes('/reports') || url.includes('/generate') || url.includes('/download')) {
        this.showAuditAccessDenied('view-reports');
        return true;
      }
      
      // Audit analytics URLs
      if (url.includes('/analytics') || url.includes('/kpi') || url.includes('/metrics')) {
        this.showAuditAccessDenied('analytics');
        return true;
      }
      
      // General audit operations based on HTTP method
      if (method === 'POST') {
        this.showAuditAccessDenied('create');
      } else if (method === 'PUT' || method === 'PATCH') {
        this.showAuditAccessDenied('conduct');
      } else {
        this.showAuditAccessDenied('view');
      }
      return true;
    }
    
    // Generic fallback
    console.log('[ACCESS_UTILS] Generic API access denied detected for URL:', url);
    this.showAccessDenied('this feature');
    return true;
  }
};

export default AccessUtils; 