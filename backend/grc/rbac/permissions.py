"""
Simple RBAC Permission Classes for GRC Incident Module

This module provides simple permission classes for checking incident permissions
using the single RBAC table.
"""

from rest_framework.permissions import BasePermission
import logging
from .utils import RBACUtils

logger = logging.getLogger(__name__)

# =====================================================
# PERMISSION CONSTANTS FOR DECORATORS
# =====================================================

# Risk Module Permission Constants
RISK_VIEW = 'view_all_risk'
RISK_CREATE = 'create_risk'
RISK_UPDATE = 'edit_risk'
RISK_DELETE = 'edit_risk'  # Delete uses edit permission
RISK_ASSIGN = 'assign_risk'
RISK_APPROVE = 'approve_risk'
RISK_REVIEW = 'evaluate_assigned_risk'
RISK_ANALYTICS = 'risk_performance_analytics'

# Incident Module Permission Constants
INCIDENT_VIEW = 'view_all_incident'
INCIDENT_CREATE = 'create_incident'
INCIDENT_UPDATE = 'edit_incident'
INCIDENT_DELETE = 'edit_incident'  # Delete uses edit permission

# Compliance Module Permission Constants
COMPLIANCE_VIEW = 'view_all_compliance'

# User Module Permission Constants
# Note: USER_VIEW permission doesn't exist as a specific field in RBAC model
# We'll use view_all_risk as a proxy for now, or this permission check should be updated
USER_VIEW = 'view_all_risk'  # Temporary mapping - consider adding 'view_users' field to RBAC model

# System Permission Constants
# Note: SYSTEM_ADMIN permission doesn't exist as a specific field in RBAC model
# System admin is determined by role = 'GRC Administrator' rather than a boolean field
SYSTEM_ADMIN = 'role'  # This will be checked differently - by role = 'GRC Administrator'

# Policy Module Permission Constants (for consistency)
POLICY_VIEW = 'view_all_policy'
POLICY_CREATE = 'create_policy'
POLICY_UPDATE = 'edit_policy'
POLICY_DELETE = 'edit_policy'  # Delete uses edit permission
POLICY_APPROVE = 'approve_policy'
POLICY_ANALYTICS = 'policy_performance_analytics'

# Audit Module Permission Constants (for consistency)
AUDIT_VIEW = 'view_audit_reports'
AUDIT_CONDUCT = 'conduct_audit'
AUDIT_REVIEW = 'review_audit'
AUDIT_ASSIGN = 'assign_audit'
AUDIT_ANALYTICS = 'audit_performance_analytics'
AUDIT_VIEW_ALL = 'view_all_audits'

class BaseIncidentPermission(BasePermission):
    """Base permission class for incident module"""
    
    def has_permission(self, request, view):
        """Check if user has basic authentication"""
        # Always allow if user is authenticated - specific permissions checked in subclasses
        return True
    
    def check_incident_permission(self, request, permission_type):
        """Helper method to check specific incident permission"""
        print(f"[DEBUG PERMISSION] check_incident_permission called with permission_type: {permission_type}")
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            print(f"[DEBUG PERMISSION] Extracted user_id: {user_id}")
            if not user_id:
                logger.warning(f"[RBAC PERM] No user_id found for {permission_type} permission check")
                print(f"[DEBUG PERMISSION] No user_id found, returning False")
                return False
        
            has_permission = RBACUtils.has_incident_permission(user_id, permission_type)
            print(f"[DEBUG PERMISSION] RBACUtils.has_incident_permission returned: {has_permission}")
            
            # Debug log the permission check
            RBACUtils.debug_permission_check(user_id, f"INCIDENT_{permission_type.upper()}", 'incident')
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC PERM] Error checking {permission_type} permission: {e}")
            print(f"[DEBUG PERMISSION] Exception occurred: {e}")
            return False
        
class IncidentViewPermission(BaseIncidentPermission):
    """Permission to view incidents"""
    
    def has_permission(self, request, view):
        print(f"[DEBUG PERMISSION] IncidentViewPermission.has_permission() called")
        print(f"[DEBUG PERMISSION] Request: {request}")
        print(f"[DEBUG PERMISSION] View: {view}")
        print(f"[DEBUG PERMISSION] Request user: {request.user}")
        
        result = self.check_incident_permission(request, 'view')
        print(f"[DEBUG PERMISSION] Permission check result: {result}")
        return result

class IncidentCreatePermission(BaseIncidentPermission):
    """Permission to create incidents"""
    
    def has_permission(self, request, view):
        return self.check_incident_permission(request, 'create')

class IncidentEditPermission(BaseIncidentPermission):
    """Permission to edit incidents"""
    
    def has_permission(self, request, view):
        return self.check_incident_permission(request, 'edit')

class IncidentAssignPermission(BaseIncidentPermission):
    """Permission to assign incidents"""
    
    def has_permission(self, request, view):
        return self.check_incident_permission(request, 'assign')

class IncidentEvaluatePermission(BaseIncidentPermission):
    """Permission to evaluate incidents (approve/reject)"""
    
    def has_permission(self, request, view):
        # Use evaluate permission for evaluation
        return self.check_incident_permission(request, 'evaluate')

class IncidentEscalatePermission(BaseIncidentPermission):
    """Permission to escalate incidents to risk"""
    
    def has_permission(self, request, view):
        # Use escalate permission for escalation
        return self.check_incident_permission(request, 'escalate')

class IncidentAnalyticsPermission(BaseIncidentPermission):
    """Permission to view incident analytics"""
    
    def has_permission(self, request, view):
        # Use analytics permission for analytics
        return self.check_incident_permission(request, 'analytics')

# Audit permissions for incident-related audit views
class AuditViewPermission(BaseIncidentPermission):
    """Permission to view audit findings"""
    
    def has_permission(self, request, view):
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                return False
            
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            if not rbac_record:
                return False
            
            # Check if user has audit view permission - use correct field name
            has_permission = rbac_record.view_audit_reports
            logger.info(f"[RBAC] User {user_id} audit.view = {'ALLOWED' if has_permission else 'DENIED'}")
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC PERM] Error checking audit view permission: {e}")
            return False

class AuditConductPermission(BaseIncidentPermission):
    """Permission to conduct audits"""
    
    def has_permission(self, request, view):
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                return False
            
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            if not rbac_record:
                return False
            
            # Check if user has audit conduct permission - use correct field name
            has_permission = rbac_record.conduct_audit
            logger.info(f"[RBAC] User {user_id} audit.conduct = {'ALLOWED' if has_permission else 'DENIED'}")
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC PERM] Error checking audit conduct permission: {e}")
            return False
        
class AuditReviewPermission(BaseIncidentPermission):
    """Permission to review audits"""
    
    def has_permission(self, request, view):
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                return False
        
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            if not rbac_record:
                return False
            
            # Check if user has audit review permission - use correct field name
            has_permission = rbac_record.review_audit
            logger.info(f"[RBAC] User {user_id} audit.review = {'ALLOWED' if has_permission else 'DENIED'}")
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC PERM] Error checking audit review permission: {e}")
            return False

class AuditAssignPermission(BaseIncidentPermission):
    """Permission to assign audits"""
    
    def has_permission(self, request, view):
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                return False
            
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            if not rbac_record:
                return False
            
            # Check if user has audit assign permission - use correct field name
            has_permission = rbac_record.assign_audit
            logger.info(f"[RBAC] User {user_id} audit.assign = {'ALLOWED' if has_permission else 'DENIED'}")
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC PERM] Error checking audit assign permission: {e}")
            return False
        
class AuditAnalyticsPermission(BaseIncidentPermission):
    """Permission to view audit analytics"""
    
    def has_permission(self, request, view):
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                return False
        
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            if not rbac_record:
                return False
            
            # Check if user has audit analytics permission - use correct field name
            has_permission = rbac_record.audit_performance_analytics
            logger.info(f"[RBAC] User {user_id} audit.analytics = {'ALLOWED' if has_permission else 'DENIED'}")
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC PERM] Error checking audit analytics permission: {e}")
            return False

class AuditViewAllPermission(BaseIncidentPermission):
    """Permission to view all audits"""
    
    def has_permission(self, request, view):
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                return False
        
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            if not rbac_record:
                return False
            
            # Check if user has view all audits permission - use correct field name
            has_permission = rbac_record.view_all_audits
            logger.info(f"[RBAC] User {user_id} audit.view_all = {'ALLOWED' if has_permission else 'DENIED'}")
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC PERM] Error checking audit view all permission: {e}")
            return False

class BaseAuditPermission(BasePermission):
    """Base permission class for audit module"""
    
    def has_permission(self, request, view):
        """Check if user has basic authentication"""
        # Always allow if user is authenticated - specific permissions checked in subclasses
        return True
    
    def check_audit_permission(self, request, permission_type):
        """Helper method to check specific audit permission"""
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                logger.warning(f"[RBAC AUDIT] No user_id found for {permission_type} permission check")
                return False
        
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            if not rbac_record:
                logger.warning(f"[RBAC AUDIT] No RBAC record found for user {user_id}")
                return False
            
            # Map permission types to correct model fields
            permission_field_map = {
                'view_reports': 'view_audit_reports',
                'conduct': 'conduct_audit',
                'review': 'review_audit',
                'assign': 'assign_audit',
                'analytics': 'audit_performance_analytics',
                'view_all': 'view_all_audits'
            }
            
            permission_field = permission_field_map.get(permission_type)
            if not permission_field:
                logger.error(f"[RBAC AUDIT] Invalid permission type: {permission_type}")
                return False
            
            has_permission = getattr(rbac_record, permission_field, False)
            
            # Debug log the permission check
            logger.info(f"[RBAC AUDIT] User {user_id} audit.{permission_type} = {'ALLOWED' if has_permission else 'DENIED'}")
            logger.info(f"[RBAC AUDIT] User Details - Role: {rbac_record.role}, Field Checked: {permission_field}")
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC AUDIT] Error checking {permission_type} permission: {e}")
            return False

# =====================================================
# POLICY MODULE PERMISSIONS - ENHANCED
# =====================================================

class BasePolicyPermission(BasePermission):
    """Base permission class for policy module"""
    
    def has_permission(self, request, view):
        """Check if user has basic authentication"""
        # Always allow if user is authenticated - specific permissions checked in subclasses
        return True
    
    def check_policy_permission(self, request, permission_type):
        """Helper method to check specific policy permission"""
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                logger.warning(f"[RBAC POLICY] No user_id found for {permission_type} permission check")
                return False
        
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            if not rbac_record:
                logger.warning(f"[RBAC POLICY] No RBAC record found for user {user_id}")
                return False
            
            # Map permission types to correct model fields
            permission_field_map = {
                'view': 'view_all_policy',
                'create': 'create_policy',
                'edit': 'edit_policy',
                'approve': 'approve_policy',
                'create_framework': 'create_framework',
                'approve_framework': 'approve_framework',
                'analytics': 'policy_performance_analytics'
            }
            
            permission_field = permission_field_map.get(permission_type)
            if not permission_field:
                logger.error(f"[RBAC POLICY] Invalid permission type: {permission_type}")
                return False
            
            has_permission = getattr(rbac_record, permission_field, False)
            
            # Debug log the permission check
            logger.info(f"[RBAC POLICY] User {user_id} policy.{permission_type} = {'ALLOWED' if has_permission else 'DENIED'}")
            logger.info(f"[RBAC POLICY] User Details - Role: {rbac_record.role}, Field Checked: {permission_field}")
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC POLICY] Error checking {permission_type} permission: {e}")
            return False

class PolicyViewPermission(BasePolicyPermission):
    """Permission to view policies"""
    
    def has_permission(self, request, view):
        result = self.check_policy_permission(request, 'view')
        logger.info(f"[RBAC POLICY] PolicyViewPermission check result: {result}")
        return result

class PolicyListPermission(BasePolicyPermission):
    """Permission to list/browse policies"""
    
    def has_permission(self, request, view):
        result = self.check_policy_permission(request, 'view')
        logger.info(f"[RBAC POLICY] PolicyListPermission check result: {result}")
        return result

class PolicyCreatePermission(BasePolicyPermission):
    """Permission to create policies"""
    
    def has_permission(self, request, view):
        result = self.check_policy_permission(request, 'create')
        logger.info(f"[RBAC POLICY] PolicyCreatePermission check result: {result}")
        return result

class PolicyEditPermission(BasePolicyPermission):
    """Permission to edit policies"""
    
    def has_permission(self, request, view):
        result = self.check_policy_permission(request, 'edit')
        logger.info(f"[RBAC POLICY] PolicyEditPermission check result: {result}")
        return result

class PolicyApprovePermission(BasePolicyPermission):
    """Permission to approve policies"""
    
    def has_permission(self, request, view):
        result = self.check_policy_permission(request, 'approve')
        logger.info(f"[RBAC POLICY] PolicyApprovePermission check result: {result}")
        return result

class PolicyDeletePermission(BasePolicyPermission):
    """Permission to delete policies - uses edit permission"""
    
    def has_permission(self, request, view):
        result = self.check_policy_permission(request, 'edit')
        logger.info(f"[RBAC POLICY] PolicyDeletePermission check result: {result}")
        return result

class PolicyAssignPermission(BasePolicyPermission):
    """Permission to assign policies - uses edit permission"""
    
    def has_permission(self, request, view):
        result = self.check_policy_permission(request, 'edit')
        logger.info(f"[RBAC POLICY] PolicyAssignPermission check result: {result}")
        return result

class PolicyExportPermission(BasePolicyPermission):
    """Permission to export policies"""
    
    def has_permission(self, request, view):
        # Export typically requires view permission
        result = self.check_policy_permission(request, 'view')
        logger.info(f"[RBAC POLICY] PolicyExportPermission check result: {result}")
        return result

class PolicyAnalyticsPermission(BasePolicyPermission):
    """Permission to view policy analytics and KPIs"""
    
    def has_permission(self, request, view):
        result = self.check_policy_permission(request, 'analytics')
        logger.info(f"[RBAC POLICY] PolicyAnalyticsPermission check result: {result}")
        return result

class PolicyKPIPermission(BasePolicyPermission):
    """Permission to view policy KPIs - specifically for Performance KPIs page"""
    
    def has_permission(self, request, view):
        try:
            # Enhanced debugging for session issues
            logger.info(f"[RBAC POLICY KPI] ===== DEBUGGING SESSION ISSUE =====")
            logger.info(f"[RBAC POLICY KPI] Request path: {request.path}")
            logger.info(f"[RBAC POLICY KPI] Request method: {request.method}")
            logger.info(f"[RBAC POLICY KPI] Request META keys: {list(request.META.keys())[:10]}...")  # Show first 10 keys
            
            # Check for session middleware
            middleware_classes = getattr(request, '_get_response', None)
            logger.info(f"[RBAC POLICY KPI] Middleware available: {middleware_classes is not None}")
            
            # Check session status
            if hasattr(request, 'session'):
                logger.info(f"[RBAC POLICY KPI] Session exists: YES")
                logger.info(f"[RBAC POLICY KPI] Session modified: {request.session.modified}")
                logger.info(f"[RBAC POLICY KPI] Session accessed: {request.session.accessed}")
                logger.info(f"[RBAC POLICY KPI] Session empty: {request.session.is_empty()}")
            else:
                logger.error(f"[RBAC POLICY KPI] Session exists: NO - Session middleware not loaded!")
            
            # Try to get user_id
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                logger.warning(f"[RBAC POLICY KPI] No user_id found for KPI permission check")
                logger.info(f"[RBAC POLICY KPI] === TROUBLESHOOTING SUGGESTIONS ===")
                logger.info(f"[RBAC POLICY KPI] 1. Check if session cookie 'grc_sessionid' is set in browser")
                logger.info(f"[RBAC POLICY KPI] 2. Run: python test_rbac_sessions.py to create test sessions")
                logger.info(f"[RBAC POLICY KPI] 3. Verify Django session middleware is enabled")
                logger.info(f"[RBAC POLICY KPI] 4. Check if user is properly authenticated")
                logger.info(f"[RBAC POLICY KPI] =======================================")
                return False
        
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            if not rbac_record:
                logger.warning(f"[RBAC POLICY KPI] No RBAC record found for user {user_id}")
                logger.info(f"[RBAC POLICY KPI] Run: mysql -u root -p grc < test_rbac_data.sql")
                return False
            
            # For KPIs, user needs policy view permission - use correct field name
            has_permission = rbac_record.view_all_policy
            
            # Detailed debug logging for KPI access
            logger.info(f"[RBAC POLICY KPI] ==================== KPI ACCESS CHECK ====================")
            logger.info(f"[RBAC POLICY KPI] User ID: {user_id}")
            logger.info(f"[RBAC POLICY KPI] User Role: {rbac_record.role}")
            logger.info(f"[RBAC POLICY KPI] User Username: {rbac_record.username}")
            logger.info(f"[RBAC POLICY KPI] Policy View Permission: {rbac_record.view_all_policy}")
            logger.info(f"[RBAC POLICY KPI] Policy Analytics Permission: {rbac_record.policy_performance_analytics}")
            logger.info(f"[RBAC POLICY KPI] Is Active: {rbac_record.is_active}")
            logger.info(f"[RBAC POLICY KPI] FINAL RESULT: {'ALLOWED' if has_permission else 'DENIED'}")
            logger.info(f"[RBAC POLICY KPI] ===============================================================")
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC POLICY KPI] Error checking KPI permission: {e}")
            import traceback
            logger.error(f"[RBAC POLICY KPI] Traceback: {traceback.format_exc()}")
            return False

class PolicyDashboardPermission(BasePolicyPermission):
    """Permission to view policy dashboard"""
    
    def has_permission(self, request, view):
        result = self.check_policy_permission(request, 'view')
        logger.info(f"[RBAC POLICY] PolicyDashboardPermission check result: {result}")
        return result

class PolicyFrameworkPermission(BasePolicyPermission):
    """Permission to manage frameworks"""
    
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            result = self.check_policy_permission(request, 'view')
        elif request.method in ['POST']:
            result = self.check_policy_permission(request, 'create_framework')
        elif request.method in ['PUT', 'PATCH']:
            result = self.check_policy_permission(request, 'edit')
        elif request.method in ['DELETE']:
            result = self.check_policy_permission(request, 'edit')
        else:
            result = False
        
        logger.info(f"[RBAC POLICY] PolicyFrameworkPermission ({request.method}) check result: {result}")
        return result

class PolicyTailoringPermission(BasePolicyPermission):
    """Permission to create tailored policies/frameworks"""
    
    def has_permission(self, request, view):
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                logger.warning("[RBAC POLICY] No user_id found for tailoring permission check")
                return False
            
            # Get RBAC record
            from ..models import RBAC
            rbac_record = RBAC.objects.filter(user_id=user_id, is_active='Y').first()
            if not rbac_record:
                logger.warning(f"[RBAC POLICY] No RBAC record found for user {user_id}")
                return False
            
            # Allow if user has create_framework permission OR is a Compliance Manager
            has_permission = rbac_record.create_framework or rbac_record.role == 'Compliance Manager'
            
            logger.info(f"[RBAC POLICY] PolicyTailoringPermission check result: {has_permission}")
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC POLICY] Error checking tailoring permission: {e}")
            return False

class PolicyVersioningPermission(BasePolicyPermission):
    """Permission to manage policy versions"""
    
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            result = self.check_policy_permission(request, 'view')
        else:
            result = self.check_policy_permission(request, 'edit')
        
        logger.info(f"[RBAC POLICY] PolicyVersioningPermission ({request.method}) check result: {result}")
        return result

class PolicyApprovalWorkflowPermission(BasePolicyPermission):
    """Permission to participate in policy approval workflow"""
    
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            result = self.check_policy_permission(request, 'view')
        else:
            result = self.check_policy_permission(request, 'approve')
        
        logger.info(f"[RBAC POLICY] PolicyApprovalWorkflowPermission ({request.method}) check result: {result}")
        return result 

# =====================================================
# RISK MODULE PERMISSIONS
# =====================================================

class BaseRiskPermission(BasePermission):
    """Base permission class for risk module"""
    
    def has_permission(self, request, view):
        """Check if user has basic authentication"""
        return True
    
    def check_risk_permission(self, request, permission_type):
        """Helper method to check specific risk permission"""
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                logger.warning(f"[RBAC RISK] No user_id found for {permission_type} permission check")
                return False
        
            has_permission = RBACUtils.has_risk_permission(user_id, permission_type)
            
            # Debug log the permission check
            RBACUtils.debug_permission_check(user_id, f"RISK_{permission_type.upper()}", 'risk')
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC RISK] Error checking {permission_type} permission: {e}")
            return False

class RiskViewPermission(BaseRiskPermission):
    """Permission to view risks"""
    
    def has_permission(self, request, view):
        return self.check_risk_permission(request, 'view')

class RiskCreatePermission(BaseRiskPermission):
    """Permission to create risks"""
    
    def has_permission(self, request, view):
        return self.check_risk_permission(request, 'create')

class RiskEditPermission(BaseRiskPermission):
    """Permission to edit risks"""
    
    def has_permission(self, request, view):
        return self.check_risk_permission(request, 'edit')

class RiskApprovePermission(BaseRiskPermission):
    """Permission to approve risks"""
    
    def has_permission(self, request, view):
        return self.check_risk_permission(request, 'approve')

class RiskAssignPermission(BaseRiskPermission):
    """Permission to assign risks"""
    
    def has_permission(self, request, view):
        return self.check_risk_permission(request, 'assign')

class RiskEvaluatePermission(BaseRiskPermission):
    """Permission to evaluate assigned risks"""
    
    def has_permission(self, request, view):
        return self.check_risk_permission(request, 'evaluate')

class RiskAnalyticsPermission(BaseRiskPermission):
    """Permission to view risk analytics"""
    
    def has_permission(self, request, view):
        return self.check_risk_permission(request, 'analytics')



# =====================================================
# COMPLIANCE MODULE PERMISSIONS
# =====================================================

class BaseCompliancePermission(BasePermission):
    """Base permission class for compliance module"""
    
    def has_permission(self, request, view):
        """Check if user has basic authentication"""
        return True
    
    def check_compliance_permission(self, request, permission_type):
        """Helper method to check specific compliance permission"""
        try:
            user_id = RBACUtils.get_user_id_from_request(request)
            if not user_id:
                logger.warning(f"[RBAC COMPLIANCE] No user_id found for {permission_type} permission check")
                return False
        
            has_permission = RBACUtils.has_compliance_permission(user_id, permission_type)
            
            # Debug log the permission check
            RBACUtils.debug_permission_check(user_id, f"COMPLIANCE_{permission_type.upper()}", 'compliance')
            
            return has_permission
            
        except Exception as e:
            logger.error(f"[RBAC COMPLIANCE] Error checking {permission_type} permission: {e}")
            return False

# =====================================================
# 5 MAIN COMPLIANCE FEATURE PERMISSION CLASSES
# =====================================================

class CreateCompliancePermission(BaseCompliancePermission):
    """Permission for CreateCompliance feature - creating new compliance items"""
    
    def has_permission(self, request, view):
        return self.check_compliance_permission(request, 'CreateCompliance')

class EditCompliancePermission(BaseCompliancePermission):
    """Permission for EditCompliance feature - editing existing compliance items"""
    
    def has_permission(self, request, view):
        return self.check_compliance_permission(request, 'EditCompliance')

class ApproveCompliancePermission(BaseCompliancePermission):
    """Permission for ApproveCompliance feature - approving compliance items"""
    
    def has_permission(self, request, view):
        return self.check_compliance_permission(request, 'ApproveCompliance')

class ViewAllCompliancePermission(BaseCompliancePermission):
    """Permission for ViewAllCompliance feature - viewing compliance data"""
    
    def has_permission(self, request, view):
        return self.check_compliance_permission(request, 'ViewAllCompliance')

class CompliancePerformanceAnalyticsPermission(BaseCompliancePermission):
    """Permission for CompliancePerformanceAnalytics feature - analytics and reporting"""
    
    def has_permission(self, request, view):
        return self.check_compliance_permission(request, 'CompliancePerformanceAnalytics')

# =====================================================
# LEGACY PERMISSION CLASS ALIASES (for backward compatibility)
# =====================================================

# Main feature aliases
ComplianceViewPermission = ViewAllCompliancePermission
ComplianceCreatePermission = CreateCompliancePermission
ComplianceEditPermission = EditCompliancePermission
ComplianceApprovePermission = ApproveCompliancePermission
ComplianceAnalyticsPermission = CompliancePerformanceAnalyticsPermission

# =====================================================
# OPERATION-SPECIFIC PERMISSION ALIASES 
# (mapped to the 5 main features)
# =====================================================

# EditCompliance operations
class ComplianceAssignPermission(EditCompliancePermission):
    """Permission to assign compliance items (uses EditCompliance)"""
    pass

class ComplianceDeletePermission(EditCompliancePermission):
    """Permission to delete compliance items (uses EditCompliance)"""
    pass

class ComplianceTogglePermission(EditCompliancePermission):
    """Permission to toggle compliance status (uses EditCompliance)"""
    pass

class ComplianceDeactivatePermission(EditCompliancePermission):
    """Permission to deactivate compliance items (uses EditCompliance)"""
    pass

class ComplianceCategoryPermission(EditCompliancePermission):
    """Permission to manage compliance categories (uses EditCompliance)"""
    pass

class ComplianceBusinessUnitPermission(EditCompliancePermission):
    """Permission to manage compliance business units (uses EditCompliance)"""
    pass

# ViewAllCompliance operations
class ComplianceExportPermission(ViewAllCompliancePermission):
    """Permission to export compliance data (uses ViewAllCompliance)"""
    pass

class ComplianceDashboardPermission(ViewAllCompliancePermission):
    """Permission to view compliance dashboard (uses ViewAllCompliance)"""
    pass

class ComplianceVersioningPermission(ViewAllCompliancePermission):
    """Permission to view compliance versioning (uses ViewAllCompliance)"""
    pass

class ComplianceFrameworkPermission(ViewAllCompliancePermission):
    """Permission to access compliance frameworks (uses ViewAllCompliance)"""
    pass

class ComplianceNotificationPermission(ViewAllCompliancePermission):
    """Permission to view compliance notifications (uses ViewAllCompliance)"""
    pass

class ComplianceAuditPermission(ViewAllCompliancePermission):
    """Permission to view compliance audit information (uses ViewAllCompliance)"""
    pass

# ApproveCompliance operations
class ComplianceReviewPermission(ApproveCompliancePermission):
    """Permission to review compliance items (uses ApproveCompliance)"""
    pass

# CreateCompliance operations
class ComplianceClonePermission(CreateCompliancePermission):
    """Permission to clone compliance items (uses CreateCompliance)"""
    pass

# CompliancePerformanceAnalytics operations
class ComplianceKPIPermission(CompliancePerformanceAnalyticsPermission):
    """Permission to view compliance KPIs (uses CompliancePerformanceAnalytics)"""
    pass 