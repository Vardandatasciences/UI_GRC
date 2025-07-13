<template>
  <div class="risk-view-container">
    <PopupModal />
    
    <div class="risk-view-header">
      <h2 class="risk-view-title"><i class="fas fa-exclamation-triangle risk-view-icon"></i> Audit Finding Details</h2>
      <button class="risk-view-back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i> Back to Audit Findings
      </button>
    </div>

    <div v-if="loading" class="risk-view-no-data">
      Loading audit finding details...
    </div>

    <div v-else-if="error" class="risk-view-no-data">
      {{ error }}
    </div>

    <div class="risk-view-details-card" v-else-if="auditFinding">
      <div class="risk-view-details-top">
        <div class="risk-view-id-section">
          <span class="risk-view-id-label">Audit Finding ID:</span>
          <span class="risk-view-id-value">{{ auditFinding.IncidentId }}</span>
        </div>
        <div class="risk-view-meta">
          <div class="risk-view-category">{{ auditFinding.RiskCategory || 'N/A' }}</div>
          <div class="risk-view-criticality" :class="getCriticalityClass(auditFinding.Criticality)">{{ auditFinding.Criticality || 'N/A' }}</div>
        </div>
      </div>

      <div class="risk-view-title-section">
        <h3>{{ auditFinding.IncidentTitle }}</h3>
        <div class="risk-view-compliance-section">
          <span class="risk-view-compliance-label">Compliance ID:</span>
          <span class="risk-view-compliance-value">{{ auditFinding.ComplianceId || 'N/A' }}</span>
        </div>
      </div>

      <div class="risk-view-content">
        <div class="risk-view-content-row">
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Description:</h4>
            <div class="risk-view-section-content">{{ auditFinding.Description || 'N/A' }}</div>
          </div>
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Business Impact:</h4>
            <div class="risk-view-section-content">{{ auditFinding.InitialImpactAssessment || 'N/A' }}</div>
          </div>
        </div>

        <div class="risk-view-content-row">
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Possible Damage:</h4>
            <div class="risk-view-section-content">{{ auditFinding.PossibleDamage || 'N/A' }}</div>
          </div>
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Status:</h4>
            <div class="risk-view-section-content">{{ auditFinding.Status || 'N/A' }}</div>
          </div>
        </div>

        <div class="risk-view-content-row">
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Systems/Assets Involved:</h4>
            <div class="risk-view-section-content">{{ auditFinding.SystemsAssetsInvolved || 'N/A' }}</div>
          </div>
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Geographic Location:</h4>
            <div class="risk-view-section-content">{{ auditFinding.GeographicLocation || 'N/A' }}</div>
          </div>
        </div>

        <div class="risk-view-content-row">
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Mitigation Plan:</h4>
            <div class="risk-view-section-content">{{ auditFinding.Mitigation || 'N/A' }}</div>
          </div>
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Comments:</h4>
            <div class="risk-view-section-content">{{ auditFinding.Comments || 'N/A' }}</div>
          </div>
        </div>

        <div class="risk-view-content-row">
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Created At:</h4>
            <div class="risk-view-section-content">{{ formatDate(auditFinding.Date) }}</div>
          </div>
          <div class="risk-view-content-column">
            <h4 class="risk-view-section-title">Time:</h4>
            <div class="risk-view-section-content">{{ auditFinding.Time || 'N/A' }}</div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="risk-view-actions" v-if="auditFinding.Status === 'Open'">
        <button @click="openSolveModal" class="risk-view-action-button risk-view-escalate">
          <i class="fas fa-arrow-up"></i> ESCALATE TO RISK
        </button>
        <button @click="openRejectModal" class="risk-view-action-button risk-view-reject">
          <i class="fas fa-times"></i> REJECT AUDIT FINDING
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import '../Risk/ViewRisk.css';
import { PopupService, PopupModal } from '@/modules/popup';

export default {
  name: 'AuditFindingDetails',
  components: {
    PopupModal
  },
  data() {
    return {
      auditFinding: null,
      loading: true,
      error: null,
    }
  },
  async created() {
    await this.fetchAuditFindingDetails();
  },
  methods: {
    async fetchAuditFindingDetails() {
      try {
        this.loading = true;
        this.error = null;
        const incidentId = this.$route.params.id;
        const response = await axios.get(`http://localhost:8000/api/audit-findings/incident/${incidentId}/`);
        
        if (response.data.success) {
          this.auditFinding = response.data.data;
        } else {
          throw new Error(response.data.message || 'Failed to fetch audit finding details');
        }
      } catch (error) {
        console.error('Failed to fetch audit finding details:', error);
        this.error = 'Failed to load audit finding details. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    getCriticalityClass(criticality) {
      if (!criticality) return '';
      criticality = criticality.toLowerCase();
      if (criticality === 'critical') return 'risk-view-priority-critical';
      if (criticality === 'high') return 'risk-view-priority-high';
      if (criticality === 'medium') return 'risk-view-priority-medium';
      if (criticality === 'low') return 'risk-view-priority-low';
      return '';
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const [year, month, day] = dateString.split('-');
      return `${month}/${day}/${year}`;
    },
    goBack() {
      this.$router.push('/incident/audit-findings');
    },
    openSolveModal() {
      PopupService.confirm(
        'This audit finding will be forwarded to the Risk module. Do you want to proceed?',
        'Forward to Risk',
        () => this.confirmSolve(),
        () => {}
      );
    },
    openRejectModal() {
      PopupService.confirm(
        'Are you sure you want to reject this audit finding?',
        'Reject Audit Finding',
        () => this.confirmReject(),
        () => {}
      );
    },
    async sendPushNotification(notificationData) {
      try {
        const response = await fetch('http://localhost:8000/api/push-notification/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(notificationData)
        });
        if (response.ok) {
          console.log('Push notification sent successfully');
        } else {
          console.error('Failed to send push notification');
        }
      } catch (error) {
        console.error('Error sending push notification:', error);
      }
    },
    confirmSolve() {
      axios.put(`http://localhost:8000/api/incidents/${this.auditFinding.IncidentId}/status/`, {
        status: 'Scheduled'
      })
      .then(() => {
        this.auditFinding.Status = 'Scheduled';
        PopupService.success(`Incident ${this.auditFinding.IncidentId} escalated to Risk successfully!`);
        // Send push notification for successful escalation
        this.sendPushNotification({
          title: 'Audit Finding Escalated to Risk',
          message: `Audit finding "${this.auditFinding.IncidentTitle || 'Untitled Finding'}" (ID: ${this.auditFinding.IncidentId}) has been successfully escalated to the Risk module.`,
          category: 'audit_finding',
          priority: 'high',
          user_id: 'default_user'
        });
        setTimeout(() => {
          this.$router.push('/incident/incident');
        }, 2000);
      })
      .catch(error => {
        console.error('Error updating audit finding status:', error);
        PopupService.error('Failed to escalate audit finding. Please try again.');
        this.sendPushNotification({
          title: 'Audit Finding Escalation Failed',
          message: `Failed to escalate audit finding "${this.auditFinding.IncidentTitle || 'Untitled Finding'}" (ID: ${this.auditFinding.IncidentId}) to Risk module.`,
          category: 'audit_finding',
          priority: 'high',
          user_id: 'default_user'
        });
      });
    },
    confirmReject() {
      axios.put(`http://localhost:8000/api/incidents/${this.auditFinding.IncidentId}/status/`, {
        status: 'Rejected'
      })
      .then(() => {
        this.auditFinding.Status = 'Rejected';
        PopupService.success(`Incident ${this.auditFinding.IncidentId} rejected successfully!`);
        this.sendPushNotification({
          title: 'Audit Finding Rejected',
          message: `Audit finding "${this.auditFinding.IncidentTitle || 'Untitled Finding'}" (ID: ${this.auditFinding.IncidentId}) has been rejected successfully.`,
          category: 'audit_finding',
          priority: 'medium',
          user_id: 'default_user'
        });
        setTimeout(() => {
          this.$router.push('/incident/incident');
        }, 2000);
      })
      .catch(error => {
        console.error('Error updating audit finding status:', error);
        PopupService.error('Failed to reject audit finding. Please try again.');
        this.sendPushNotification({
          title: 'Audit Finding Rejection Failed',
          message: `Failed to reject audit finding "${this.auditFinding.IncidentTitle || 'Untitled Finding'}" (ID: ${this.auditFinding.IncidentId}).`,
          category: 'audit_finding',
          priority: 'high',
          user_id: 'default_user'
        });
      });
    }
  }
}
</script>

<style scoped>
.risk-view-actions {
  display: flex;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--risk-gray-200);
}

.risk-view-action-button {
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.risk-view-escalate {
  background-color: var(--risk-primary);
  color: white;
}

.risk-view-escalate:hover {
  background-color: var(--risk-primary-dark);
}

.risk-view-reject {
  background-color: var(--risk-danger);
  color: white;
}

.risk-view-reject:hover {
  background-color: #d32f2f;
}
</style> 