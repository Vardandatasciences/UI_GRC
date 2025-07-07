/**
 * Access Control Utilities
 * Utility functions for handling access control and permission errors
 */

import { PopupService } from '@/modules/popup/popupService';

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
   * Show access denied popup for specific compliance operations
   * @param {string} operation - Operation type
   * @param {Function} onContactAdmin - Callback for contact admin action
   */
  showComplianceAccessDenied(operation = 'access', onContactAdmin = null) {
    console.log('[ACCESS_UTILS] showComplianceAccessDenied called:', { operation });
    
    const operationText = {
      create: 'create compliance items',
      edit: 'edit compliance items',
      view: 'view compliance items',
      delete: 'delete compliance items',
      approve: 'approve compliance items',
      analytics: 'view compliance analytics',
      access: 'access the compliance module'
    }[operation] || operation;

    const message = `You don't have permission to ${operationText}. Please contact your administrator to request access to this feature.`;
    
    PopupService.accessDenied(message, 'Compliance Access Denied', onContactAdmin || this.defaultContactAdmin);
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
    
    // Generic fallback
    console.log('[ACCESS_UTILS] Generic API access denied detected for URL:', url);
    this.showAccessDenied('this feature');
    return true;
  }
};

export default AccessUtils; 