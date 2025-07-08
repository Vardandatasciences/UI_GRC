# Policy Module RBAC Implementation

## Overview

This document outlines the comprehensive Role-Based Access Control (RBAC) system implemented for the Policy module. The system provides fine-grained access control across all policy-related operations, ensuring users only see and access features they have permissions for.

## Backend Implementation

### 1. Permission Classes Fixed

Fixed missing imports in all policy route files:

**Files Updated:**
- `backend/grc/routes/policy.py`
- `backend/grc/routes/frameworks.py` 
- `backend/grc/routes/framework_version.py`
- `backend/grc/routes/policy_version.py`
- `backend/grc/routes/upload_framework.py`

**Permissions Added:**
- `PolicyExportPermission`
- `PolicyDashboardPermission` 
- `PolicyTailoringPermission`
- `PolicyVersioningPermission`
- `PolicyCreatePermission`

### 2. API Endpoint Protection

All policy-related API endpoints are now protected with appropriate RBAC permissions:

```python
@api_view(['GET'])
@permission_classes([PolicyViewPermission])
def get_policies(request):
    # Policy viewing endpoint

@api_view(['POST'])
@permission_classes([PolicyCreatePermission])
def create_policy(request):
    # Policy creation endpoint

@api_view(['PUT'])
@permission_classes([PolicyEditPermission])
def edit_policy(request, policy_id):
    # Policy editing endpoint

@api_view(['PUT'])
@permission_classes([PolicyApprovePermission])
def approve_policy(request, policy_id):
    # Policy approval endpoint
```

## Frontend Implementation

### 1. RBAC Utilities (`frontend/src/utils/policyRbacUtils.js`)

Comprehensive utility system providing:

**Core Features:**
- Permission caching with 5-minute expiry
- Parallel API calls for permissions and roles
- Comprehensive error handling
- User session validation

**Permission Checks:**
- `canViewPolicies()` - View policy data
- `canCreatePolicies()` - Create new policies
- `canEditPolicies()` - Modify existing policies
- `canDeletePolicies()` - Remove policies
- `canApprovePolicies()` - Approve policy changes
- `canViewFrameworks()` - Access framework data
- `canCreateFrameworks()` - Create new frameworks
- `canUploadFrameworks()` - Upload framework documents
- `canViewAnalytics()` - Access policy analytics
- `canViewKPIs()` - View KPI dashboards
- `canViewDashboard()` - Access policy dashboard
- `canExportData()` - Export policy data
- `canManageVersions()` - Handle policy versioning
- `canTailorPolicies()` - Customize policies
- `canManageApprovalWorkflow()` - Manage approval processes

**Access Control Features:**
- Route-based access control
- Component-level permissions
- Button/action visibility control
- Integrated popup system for access denied messages

### 2. Vue Mixin (`frontend/src/mixins/policyRbacMixin.js`)

**Composition API Integration:**
```javascript
// For script setup components
import { usePolicyRbac } from '@/mixins/policyRbacMixin'

export default {
  setup() {
    const {
      rbacLoading,
      canViewPolicies,
      canCreatePolicies,
      canEditPolicies,
      showAccessDenied,
      initializeRBAC
    } = usePolicyRbac()
    
    return {
      rbacLoading,
      canViewPolicies,
      canCreatePolicies,
      canEditPolicies,
      showAccessDenied
    }
  }
}
```

**Traditional Mixin:**
```javascript
// For options API components
import { policyRbacMixin } from '@/mixins/policyRbacMixin'

export default {
  mixins: [policyRbacMixin],
  // Component now has access to all RBAC properties and methods
}
```

### 3. Component Integration

**Components Updated:**
- `AllPolicies.vue` - Main policy listing with full RBAC integration
- `CreatePolicy.vue` - Policy creation with access control
- `PolicyApprover.vue` - Approval interface with permission checks

**Template Integration:**
```vue
<template>
  <div class="policy-container">
    <!-- RBAC Loading State -->
    <div v-if="rbacLoading" class="loading-overlay">
      <div class="loading-spinner">
        <i class="fas fa-shield-alt fa-spin"></i>
        <span>Checking access permissions...</span>
      </div>
    </div>

    <!-- Access Denied Screen -->
    <div v-else-if="!canViewPolicies && !rbacLoading" class="access-denied-container">
      <div class="access-denied-content">
        <i class="fas fa-shield-alt access-denied-icon"></i>
        <h2>Access Denied</h2>
        <p>You don't have permission to view policies. Please contact your administrator.</p>
        <div class="access-info">
          <strong>Your Role:</strong> {{ userRole }}
        </div>
        <div class="access-actions">
          <button @click="showAccessDenied('view')" class="btn btn-warning">
            <i class="fas fa-envelope"></i> Contact Admin
          </button>
          <button @click="$router.push('/')" class="btn btn-secondary">
            <i class="fas fa-home"></i> Go to Dashboard
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Your component content here -->
      <div v-if="canCreatePolicies">
        <button @click="createPolicy">Create Policy</button>
      </div>
    </template>
  </div>
</template>
```

## Access Control Matrix

| Operation | Required Permission | Description |
|-----------|-------------------|-------------|
| View Policies | `policy.view`, `policy.view_all`, `policy.list` | Access to view policy data |
| Create Policies | `policy.create` | Create new policies |
| Edit Policies | `policy.edit` | Modify existing policies |
| Delete Policies | `policy.delete` | Remove policies |
| Approve Policies | `policy.approve` | Approve policy changes |
| View Frameworks | `policy.view_framework`, `policy.view` | Access framework data |
| Create Frameworks | `policy.create_framework` | Create new frameworks |
| Upload Frameworks | `policy.upload_framework` | Upload framework documents |
| View Analytics | `policy.analytics` | Access policy analytics |
| View KPIs | `policy.kpi` | View KPI dashboards |
| View Dashboard | `policy.dashboard` | Access policy dashboard |
| Export Data | `policy.export` | Export policy data |
| Manage Versions | `policy.versioning` | Handle policy versioning |
| Tailor Policies | `policy.tailoring` | Customize policies |
| Approval Workflow | `policy.approval_workflow` | Manage approval processes |

## Popup Integration

The system integrates with the existing popup system (`@/modules/popup/`) to show user-friendly access denied messages:

**Features:**
- Role-based error messages
- Contact admin functionality
- Navigation assistance
- Consistent UI styling

**Usage:**
```javascript
PolicyRbacUtils.showPolicyAccessDenied('create'); // Shows create policy access denied
PolicyRbacUtils.showViewPolicyDenied(); // Specific view access denied
PolicyRbacUtils.showExportDenied(); // Export access denied
```

## Error Handling

**Backend:**
- Comprehensive logging for all permission checks
- Detailed error messages for debugging
- Secure error responses to frontend

**Frontend:**
- Graceful degradation when RBAC fails to load
- User-friendly error messages
- Automatic retry mechanisms
- Fallback to deny-all access when errors occur

## Security Features

1. **Server-side Validation**: All permissions validated on backend
2. **Token-based Authentication**: Uses JWT tokens for API calls
3. **Role-based Access**: Permissions tied to user roles
4. **Session Management**: Automatic session validation
5. **Cache Security**: Permissions cached securely with expiration
6. **XSS Protection**: All user data escaped in error messages

## Usage Examples

### Basic Permission Check
```javascript
// Check if user can create policies
if (PolicyRbacUtils.canCreatePolicies()) {
  // Show create button
  showCreateButton();
} else {
  // Hide create button or show access denied
  PolicyRbacUtils.showCreatePolicyDenied();
}
```

### Route Protection
```javascript
// Check if user can access a specific route
if (PolicyRbacUtils.canAccessRoute('CreatePolicy')) {
  router.push('/policy/create');
} else {
  PolicyRbacUtils.showPolicyAccessDenied('create');
}
```

### Component Integration
```javascript
// In component setup
const { canViewPolicies, rbacLoading } = usePolicyRbac();

// In template
<div v-if="!rbacLoading && canViewPolicies">
  <!-- Policy content -->
</div>
```

## Implementation Status

✅ **Completed:**
- Backend permission imports and decorators
- Frontend RBAC utility system
- Vue mixin and composable
- Component integration for main Policy components
- Access denied UI with popup integration
- Comprehensive error handling

🔄 **Remaining Components to Update:**
- `UploadFramework.vue`
- `PolicyDashboard.vue`
- `KPIDashboard.vue`
- `PerformancePage.vue`
- `FrameworkExplorer.vue`
- `FrameworkPolicies.vue`
- `StatusChangeRequests.vue`
- `TreePolicies.vue`
- `VV.vue` (Versioning)
- `TT.vue` (Tailoring)

## Next Steps

1. Apply RBAC to remaining Policy components
2. Test permission scenarios with different user roles
3. Implement permission-based menu filtering
4. Add audit logging for access attempts
5. Create admin interface for permission management

## Support

For issues or questions regarding the RBAC implementation, contact the development team or refer to the existing access utilities in `@/utils/accessUtils.js` for similar patterns. 