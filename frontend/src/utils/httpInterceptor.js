/**
 * HTTP Interceptor for Access Control
 * Automatically handles 401/403 errors and shows access denied popups
 */

import axios from 'axios';
import AccessUtils from './accessUtils';

// Flag to prevent duplicate popups for the same request
let showingPopup = false;

/**
 * Setup axios response interceptor to handle access denied errors
 */
export function setupHttpInterceptor() {
  console.log('[HTTP_INTERCEPTOR] Setting up HTTP interceptor for access control');

  // Response interceptor
  axios.interceptors.response.use(
    (response) => {
      // Reset flag on successful response
      showingPopup = false;
      return response;
    },
    (error) => {
      console.log('[HTTP_INTERCEPTOR] Response error intercepted:', {
        status: error?.response?.status,
        url: error?.config?.url,
        method: error?.config?.method?.toUpperCase(),
        showingPopup
      });

      // Only handle 401/403 errors
      if (error.response && [401, 403].includes(error.response.status)) {
        console.log('[HTTP_INTERCEPTOR] Access denied error detected');

        // Prevent duplicate popups
        if (!showingPopup) {
          showingPopup = true;
          console.log('[HTTP_INTERCEPTOR] Showing access denied popup');

          // Handle the error based on URL
          const handled = AccessUtils.handleApiErrorByUrl(error, error.config.url);
          
          if (handled) {
            console.log('[HTTP_INTERCEPTOR] Access denied popup handled by URL pattern');
          } else {
            console.log('[HTTP_INTERCEPTOR] Using fallback access denied popup');
            AccessUtils.showAccessDenied('this feature');
          }

          // Reset flag after a short delay to allow for new requests
          setTimeout(() => {
            showingPopup = false;
            console.log('[HTTP_INTERCEPTOR] Reset popup flag');
          }, 1000);
        } else {
          console.log('[HTTP_INTERCEPTOR] Popup already showing, skipping duplicate');
        }
      }

      // Always reject the promise so the calling code can handle it appropriately
      return Promise.reject(error);
    }
  );

  // Request interceptor (optional - for logging)
  axios.interceptors.request.use(
    (config) => {
      console.log('[HTTP_INTERCEPTOR] Request:', {
        method: config.method?.toUpperCase(),
        url: config.url
      });
      return config;
    },
    (error) => {
      console.error('[HTTP_INTERCEPTOR] Request error:', error);
      return Promise.reject(error);
    }
  );

  console.log('[HTTP_INTERCEPTOR] HTTP interceptor setup complete');
}

/**
 * Remove all interceptors (useful for cleanup)
 */
export function removeHttpInterceptor() {
  console.log('[HTTP_INTERCEPTOR] Removing HTTP interceptors');
  axios.interceptors.response.clear();
  axios.interceptors.request.clear();
}

export default {
  setupHttpInterceptor,
  removeHttpInterceptor
}; 