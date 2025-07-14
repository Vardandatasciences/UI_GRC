<template>
  <div class="dashboard-container">
    <!-- Dashboard content - always show this -->
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Compliance Approver</h2>
      <div class="dashboard-actions">
        <!-- User dropdown for GRC Administrator -->
        <div v-if="isAdministrator" class="user-selection-dropdown">
          <label for="userSelect">Select User to View Tasks:</label>
          <select id="userSelect" v-model="selectedUserId" @change="onUserChange" class="form-control">
            <option value="">-- Select a User to View Their Tasks --</option>
            <option v-for="user in availableUsers" :key="user.UserId" :value="user.UserId">
              {{ user.UserName }} ({{ user.Role }}) - ID: {{ user.UserId }}
            </option>
          </select>
          <small v-if="!selectedUserId" class="user-help-text">
            Please select a user to view their "My Tasks" and "Reviewer Tasks"
          </small>
        </div>
        <button class="action-btn" @click="refreshData" :disabled="isLoading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
        </button>
        <button class="action-btn" @click="testPagination">
          <i class="fas fa-cog"></i>
        </button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
      </div>
    </div>
    
    <!-- Error message -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="refreshData" class="retry-btn">Retry</button>
    </div>
    
    <!-- Performance Summary Cards -->
    <div class="performance-summary">
      <div class="summary-card growth">
        <div class="summary-icon"><i class="fas fa-user-check"></i></div>
        <div class="summary-content">
          <div class="summary-label">Pending Approvals</div>
          <div class="summary-value">{{ pendingApprovalsCount }}</div>
        </div>
      </div>
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-check-circle"></i></div>
        <div class="summary-content">
          <div class="summary-label">Approved</div>
          <div class="summary-value">{{ approvedApprovalsCount }}</div>
        </div>
      </div>
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-times-circle"></i></div>
        <div class="summary-content">
          <div class="summary-label">Rejected</div>
          <div class="summary-value">{{ rejectedApprovalsCount }}</div>
        </div>
      </div>
    </div>

    <!-- Tabs for My Tasks and Reviewer Tasks -->
    <div class="tabs-container">
      <div class="tabs">
        <button 
          class="tab-button"
          :class="{ active: activeTab === 'myTasks' }"
          @click="switchTab('myTasks')"
        >
          My Tasks
          <span class="tab-count">{{ myTasksCount }}</span>
        </button>
        <button 
          class="tab-button"
          :class="{ active: activeTab === 'reviewerTasks' }"
          @click="switchTab('reviewerTasks')"
        >
          Reviewer Tasks
          <span class="tab-count">{{ reviewerTasksCount }}</span>
        </button>
      </div>
    </div>

    <!-- Render My Tasks or Reviewer Tasks based on activeTab -->
    <div v-if="activeTab === 'myTasks'">
      <div class="compliance-approval-container">
        <h2 class="compliance-approval-title">My Compliance Approval Tasks</h2>
        <CollapsibleTable
          v-if="myTasksPending.length"
          :sectionConfig="{ name: 'Pending', statusClass: 'pending', tasks: myTasksPendingPaged.map(mapApprovalToRow) }"
          :tableHeaders="approvalTableHeaders"
          :isExpanded="myTasksCollapsible.Pending"
          @toggle="() => myTasksCollapsible.Pending = !myTasksCollapsible.Pending"
          @taskClick="handleApprovalAction"
          :pagination="{
            currentPage: myTasksPagination.Pending.currentPage,
            totalPages: Math.ceil(myTasksPending.length / myTasksPagination.Pending.pageSize),
            pageSize: myTasksPagination.Pending.pageSize,
            totalCount: myTasksPending.length,
            pageSizeOptions: [10],
            onPageSizeChange: () => {},
            onPageChange: page => handleMyTasksPageChange('Pending', page)
          }"
        />
        <CollapsibleTable
          v-if="myTasksApproved.length"
          :sectionConfig="{ name: 'Approved', statusClass: 'approved', tasks: myTasksApprovedPaged.map(mapApprovalToRow) }"
          :tableHeaders="approvalTableHeaders"
          :isExpanded="myTasksCollapsible.Approved"
          @toggle="() => myTasksCollapsible.Approved = !myTasksCollapsible.Approved"
          @taskClick="handleApprovalAction"
          :pagination="{
            currentPage: myTasksPagination.Approved.currentPage,
            totalPages: Math.ceil(myTasksApproved.length / myTasksPagination.Approved.pageSize),
            pageSize: myTasksPagination.Approved.pageSize,
            totalCount: myTasksApproved.length,
            pageSizeOptions: [10],
            onPageSizeChange: () => {},
            onPageChange: page => handleMyTasksPageChange('Approved', page)
          }"
        />
        <CollapsibleTable
          v-if="myTasksRejected.length"
          :sectionConfig="{ name: 'Rejected', statusClass: 'rejected', tasks: myTasksRejectedPaged.map(mapApprovalToRow) }"
          :tableHeaders="approvalTableHeaders"
          :isExpanded="myTasksCollapsible.Rejected"
          @toggle="() => myTasksCollapsible.Rejected = !myTasksCollapsible.Rejected"
          @taskClick="handleApprovalAction"
          :pagination="{
            currentPage: myTasksPagination.Rejected.currentPage,
            totalPages: Math.ceil(myTasksRejected.length / myTasksPagination.Rejected.pageSize),
            pageSize: myTasksPagination.Rejected.pageSize,
            totalCount: myTasksRejected.length,
            pageSizeOptions: [10],
            onPageSizeChange: () => {},
            onPageChange: page => handleMyTasksPageChange('Rejected', page)
          }"
        />
        <div v-if="!myTasksPending.length && !myTasksApproved.length && !myTasksRejected.length" class="no-tasks-message">
          <div class="no-tasks-icon">
            <i class="fas fa-clipboard-check"></i>
          </div>
          <h4>No My Tasks</h4>
          <p>{{ selectedUserInfo && isAdministrator ? `${selectedUserInfo.UserName} doesn't have` : 'You don\'t have' }} any tasks at the moment.</p>
        </div>
      </div>
    </div>
    <div v-if="activeTab === 'reviewerTasks'">
      <div class="compliance-approval-container">
        <h2 class="compliance-approval-title">Reviewer Tasks</h2>
        <CollapsibleTable
          v-if="reviewerTasksPending.length"
          :sectionConfig="{ name: 'Pending', statusClass: 'pending', tasks: reviewerTasksPendingPaged.map(mapApprovalToRow) }"
          :tableHeaders="approvalTableHeaders"
          :isExpanded="reviewerTasksCollapsible.Pending"
          @toggle="() => reviewerTasksCollapsible.Pending = !reviewerTasksCollapsible.Pending"
          @taskClick="handleApprovalAction"
          :pagination="{
            currentPage: reviewerTasksPagination.Pending.currentPage,
            totalPages: Math.ceil(reviewerTasksPending.length / reviewerTasksPagination.Pending.pageSize),
            pageSize: reviewerTasksPagination.Pending.pageSize,
            totalCount: reviewerTasksPending.length,
            pageSizeOptions: [10],
            onPageSizeChange: () => {},
            onPageChange: page => handleReviewerTasksPageChange('Pending', page)
          }"
        />
        <CollapsibleTable
          v-if="reviewerTasksApproved.length"
          :sectionConfig="{ name: 'Approved', statusClass: 'approved', tasks: reviewerTasksApprovedPaged.map(mapApprovalToRow) }"
          :tableHeaders="approvalTableHeaders"
          :isExpanded="reviewerTasksCollapsible.Approved"
          @toggle="() => reviewerTasksCollapsible.Approved = !reviewerTasksCollapsible.Approved"
          @taskClick="handleApprovalAction"
          :pagination="{
            currentPage: reviewerTasksPagination.Approved.currentPage,
            totalPages: Math.ceil(reviewerTasksApproved.length / reviewerTasksPagination.Approved.pageSize),
            pageSize: reviewerTasksPagination.Approved.pageSize,
            totalCount: reviewerTasksApproved.length,
            pageSizeOptions: [10],
            onPageSizeChange: () => {},
            onPageChange: page => handleReviewerTasksPageChange('Approved', page)
          }"
        />
        <CollapsibleTable
          v-if="reviewerTasksRejected.length"
          :sectionConfig="{ name: 'Rejected', statusClass: 'rejected', tasks: reviewerTasksRejectedPaged.map(mapApprovalToRow) }"
          :tableHeaders="approvalTableHeaders"
          :isExpanded="reviewerTasksCollapsible.Rejected"
          @toggle="() => reviewerTasksCollapsible.Rejected = !reviewerTasksCollapsible.Rejected"
          @taskClick="handleApprovalAction"
          :pagination="{
            currentPage: reviewerTasksPagination.Rejected.currentPage,
            totalPages: Math.ceil(reviewerTasksRejected.length / reviewerTasksPagination.Rejected.pageSize),
            pageSize: reviewerTasksPagination.Rejected.pageSize,
            totalCount: reviewerTasksRejected.length,
            pageSizeOptions: [10],
            onPageSizeChange: () => {},
            onPageChange: page => handleReviewerTasksPageChange('Rejected', page)
          }"
        />
        <div v-if="!reviewerTasksPending.length && !reviewerTasksApproved.length && !reviewerTasksRejected.length" class="no-tasks-message">
          <div class="no-tasks-icon">
            <i class="fas fa-clipboard-check"></i>
          </div>
          <h4>No Reviewer Tasks</h4>
          <p>{{ selectedUserInfo && isAdministrator ? `${selectedUserInfo.UserName} doesn't have` : 'You don\'t have' }} any reviewer tasks at the moment.</p>
        </div>
      </div>
    </div>

    <!-- (Comment out or remove the old groupedApprovals rendering) -->
    <!--
    <div class="compliance-approval-container">
      ... (old groupedApprovals code) ...
    </div>
    -->
    
    <!-- Edit Modal for Rejected Compliance -->
    <div v-if="showEditComplianceModal && editingCompliance" class="edit-policy-modal">
      <div class="edit-policy-content">
        <h3>Edit & Resubmit Compliance: {{ editingCompliance.Identifier }}</h3>
        <button class="close-btn" @click="closeEditComplianceModal">Close</button>
        <!-- Compliance fields -->
        <div>
          <label>Description:</label>
          <input v-model="editingCompliance.ExtractedData.ComplianceItemDescription" />
        </div>
        <div>
          <label>Criticality:</label>
          <select v-model="editingCompliance.ExtractedData.Criticality">
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </div>
        <div>
          <label>Severity Rating:</label>
          <input v-model="editingCompliance.ExtractedData.Impact" />
        </div>
        <div>
          <label>Probability:</label>
          <input v-model="editingCompliance.ExtractedData.Probability" />
        </div>
        <div>
          <label>Mitigation:</label>
          <textarea v-model="mitigationString"></textarea>
          <div v-if="isMitigationObject">
            <small>Mitigation (JSON): {{ formatMitigation(editingCompliance.ExtractedData.mitigation) }}</small>
          </div>
        </div>
        <!-- Show rejection reason -->
        <div>
          <label>Rejection Reason:</label>
          <div class="rejection-reason">{{ rejectionReason }}</div>
        </div>
        <button class="resubmit-btn" @click="resubmitCompliance(editingCompliance)" :disabled="isLoading">Resubmit for Review</button>
      </div>
    </div>
    
    <!-- Compliance Details Modal -->
    <div v-if="showDetailsModal && selectedApproval" class="compliance-details-modal" @click="closeDetailsModal">
      <div class="compliance-details-modal-content" @click.stop>
        <!-- Header Section -->
        <div class="compliance-details-header">
          <button class="close-btn" @click="closeDetailsModal">
            <i class="fas fa-times"></i>
          </button>
          
          <h3>
            <span class="detail-type-indicator">Compliance</span>
            <span v-if="selectedApproval.ExtractedData?.RequestType === 'Change Status to Inactive' || selectedApproval.ExtractedData?.type === 'compliance_deactivation'">
              Deactivation Request: {{ selectedApproval.Identifier }}
            </span>
            <span v-else>
              Details: {{ selectedApproval.Identifier }}
            </span>
          </h3>
        </div>

        <!-- Main Content Area -->
        <div class="policy-details-content">
          <!-- Compliance Approval Section -->
          <div class="policy-approval-section">
            <h4>
              <span v-if="selectedApproval.ExtractedData?.RequestType === 'Change Status to Inactive' || selectedApproval.ExtractedData?.type === 'compliance_deactivation'">
                Compliance Deactivation Approval
              </span>
              <span v-else>
                Compliance Approval
              </span>
            </h4>
            
            <!-- Quick Action Button -->
            <div class="policy-actions">
              <button class="submit-btn" @click="submitReview()">
                <i class="fas fa-paper-plane"></i>
                <span>Submit Review</span>
              </button>
            </div>
            
            <!-- Approval Status Display -->
            <div v-if="approvalStatus" class="policy-approval-status">
              <div class="status-container">
                <div class="status-label">Current Status:</div>
                <div class="status-value" :class="{
                  'approved': approvalStatus.approved === true,
                  'rejected': approvalStatus.approved === false,
                  'pending': approvalStatus.approved === null
                }">
                  {{ approvalStatus.approved === true ? 'Approved' :
                     approvalStatus.approved === false ? 'Rejected' : 'Pending Review' }}
                </div>
              </div>
              
              <!-- Approval Date Display -->
              <div v-if="selectedApproval.ApprovedDate" class="approval-date">
                <div class="date-label">
                  <i class="fas fa-calendar-check"></i>
                  Approved on:
                </div>
                <div class="date-value">{{ formatDate(selectedApproval.ApprovedDate) }}</div>
              </div>
              
              <!-- Rejection Remarks -->
              <div v-if="approvalStatus.approved === false && approvalStatus.remarks" class="policy-rejection-remarks">
                <div class="remarks-label">
                  <i class="fas fa-exclamation-circle"></i>
                  Rejection Reason:
                </div>
                <div class="remarks-value">{{ approvalStatus.remarks }}</div>
              </div>
            </div>
          </div>
          
          <!-- Compliance Details Display -->
          <div v-if="selectedApproval.ExtractedData" class="compliance-details">
            <!-- Deactivation Request Details -->
            <div v-if="selectedApproval.ExtractedData?.RequestType === 'Change Status to Inactive' || selectedApproval.ExtractedData?.type === 'compliance_deactivation'" 
                 class="deactivation-request-details">
              
              <div class="compliance-detail-row">
                <strong>
                  <i class="fas fa-question-circle"></i>
                  Reason for Deactivation:
                </strong>
                <span>{{ selectedApproval.ExtractedData.reason || 'No reason provided' }}</span>
              </div>
              
              <div class="compliance-detail-row">
                <strong>
                  <i class="fas fa-info-circle"></i>
                  Current Status:
                </strong>
                <span class="status-badge current">{{ selectedApproval.ExtractedData.current_status }}</span>
              </div>
              
              <div class="compliance-detail-row">
                <strong>
                  <i class="fas fa-arrow-right"></i>
                  Requested Status:
                </strong>
                <span class="status-badge requested">{{ selectedApproval.ExtractedData.requested_status }}</span>
              </div>
              
              <div class="compliance-detail-row">
                <strong>
                  <i class="fas fa-sitemap"></i>
                  Cascade to Policies:
                </strong>
                <span class="cascade-indicator" :class="{ 'warning': selectedApproval.ExtractedData.cascade_to_policies === 'Yes' }">
                  {{ selectedApproval.ExtractedData.cascade_to_policies }}
                </span>
              </div>
              
              <div v-if="selectedApproval.ExtractedData.affected_policies_count > 0" class="compliance-detail-row">
                <strong>
                  <i class="fas fa-file-alt"></i>
                  Affected Policies:
                </strong>
                <span class="policy-count">{{ selectedApproval.ExtractedData.affected_policies_count }} policies</span>
              </div>
              
              <!-- Enhanced Warning Message -->
              <div class="warning-message">
                <i class="fas fa-exclamation-triangle"></i>
                <span>
                  <strong>Warning:</strong> Deactivating this compliance will make it inactive.
                  {{ selectedApproval.ExtractedData.cascade_to_policies === 'Yes' ? 
                     'All related policies will also be deactivated.' : 
                     'Related policies will not be affected.' }}
                </span>
              </div>
            </div>
            
            <!-- Regular Compliance Details -->
            <div v-else>
              <div class="compliance-detail-row">
                <strong>
                  <i class="fas fa-file-text"></i>
                  Description:
                </strong>
                <span>{{ selectedApproval.ExtractedData.ComplianceItemDescription }}</span>
              </div>
              
              <div class="compliance-detail-row">
                <strong>
                  <i class="fas fa-exclamation"></i>
                  Criticality:
                </strong>
                <span class="criticality-badge" :class="selectedApproval.ExtractedData.Criticality?.toLowerCase()">
                  {{ selectedApproval.ExtractedData.Criticality }}
                </span>
              </div>
              
              <div class="compliance-detail-row">
                <strong>
                  <i class="fas fa-chart-line"></i>
                  Severity Rating:
                </strong>
                <span class="severity-rating">{{ selectedApproval.ExtractedData.Impact }}</span>
              </div>
              
              <div class="compliance-detail-row">
                <strong>
                  <i class="fas fa-percentage"></i>
                  Probability:
                </strong>
                <span class="probability-value">{{ selectedApproval.ExtractedData.Probability }}</span>
              </div>
              
              <div class="compliance-detail-row">
                <strong>
                  <i class="fas fa-shield-alt"></i>
                  Mitigation:
                </strong>
                <span>{{ formatMitigation(selectedApproval.ExtractedData.mitigation) }}</span>
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="policy-actions">
              <button class="approve-btn" @click="approveCompliance()">
                <i class="fas fa-check"></i>
                <span>Approve</span>
              </button>
              <button class="reject-btn" @click="rejectCompliance()">
                <i class="fas fa-times"></i>
                <span>Reject</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Enhanced Rejection Modal -->
    <div v-if="showRejectModal" class="reject-modal">
      <div class="reject-modal-content">
        <h4>
          <i class="fas fa-times-circle"></i>
          Rejection Reason Required
        </h4>
        <p>Please provide a detailed reason for rejecting this compliance item. This information will be used to improve future submissions.</p>
        
        <textarea
          v-model="rejectionComment"
          class="rejection-comment"
          placeholder="Enter your detailed comments here...">
        </textarea>
        
        <div class="reject-modal-actions">
          <button class="cancel-btn" @click="cancelRejection">
            <i class="fas fa-arrow-left"></i>
            Cancel
          </button>
          <button class="confirm-btn" @click="confirmRejection">
            <i class="fas fa-check"></i>
            Confirm Rejection
          </button>
        </div>
      </div>
    </div>
    
    <!-- Add PopupModal component -->
    <PopupModal />
  </div>

  <!-- Rejected Compliances (Edit & Resubmit) Section -->
  <div class="rejected-approvals-section">
    <h3>Rejected Compliances (Edit & Resubmit)</h3>
    <div class="table-container">
      <table class="frameworks-table">
        <thead>
          <tr>
            <th>COMPLIANCE ID</th>
            <th>NAME / DESCRIPTION</th>
            <th>CRITICALITY</th>
            <th>CREATED BY</th>
            <th>CREATED DATE</th>
            <th>STATUS</th>
            <th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!rejectedCompliances.length">
            <td colspan="7" style="text-align:center; color:#888;">No rejected compliances to edit or resubmit.</td>
          </tr>
          <tr v-for="item in rejectedCompliances" :key="item.ApprovalId">
            <td>
              <a href="#" class="framework-id-link" @click.prevent="handleApprovalAction(item)">
                {{ item.Identifier }}
              </a>
            </td>
            <td>{{ item.ExtractedData?.ComplianceItemDescription || 'No Description' }}</td>
            <td>{{ item.ExtractedData?.Criticality || 'N/A' }}</td>
            <td>{{ item.ExtractedData?.CreatedByName || 'System' }}</td>
            <td>{{ formatDate(item.ExtractedData?.CreatedByDate) }}</td>
            <td>
              <span class="status-badge rejected">REJECTED</span>
              <div v-if="item.ExtractedData && item.ExtractedData.compliance_approval && item.ExtractedData.compliance_approval.remarks" class="rejection-reason">
                {{ item.ExtractedData.compliance_approval.remarks }}
              </div>
            </td>
            <td class="actions-cell">
              <button class="view-btn" @click="handleApprovalAction(item)"><i class="fas fa-eye"></i> VIEW</button>
              <button class="edit-btn" @click="openRejectedItem(item)"><i class="fas fa-edit"></i> Edit</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
 
<script>
import { complianceService } from '@/services/api';
import { PopupModal } from '../../modules/popup';
import PopupMixin from './mixins/PopupMixin';
import { CompliancePopups } from './utils/popupUtils';
import CollapsibleTable from '../CollapsibleTable.vue';
import AccessUtils from '@/utils/accessUtils';
import axios from 'axios';
 
export default {
  name: 'ComplianceApprover',
  components: {
    PopupModal,
    CollapsibleTable
  },
  mixins: [PopupMixin],
  data() {
    return {
      approvals: [],
      selectedApproval: null,
      showRejectModal: false,
      rejectionComment: '',
      showEditComplianceModal: false,
      editingCompliance: null,
      userId: 2, // Default user id
      isLoading: false,
      error: null,
      counts: {
        pending: 0,
        approved: 0,
        rejected: 0
      },
      refreshInterval: null,
      isLoadingRejected: false,
      isDeactivationRequest: false,
      collapsibleStates: {
        Pending: true,
        Approved: false,
        Rejected: false,
        'Recently Approved': false
      },
      // Add pagination state for each section
      pagination: {
        Pending: { currentPage: 1, pageSize: 10, totalCount: 0 },
        Approved: { currentPage: 1, pageSize: 10, totalCount: 0 },
        Rejected: { currentPage: 1, pageSize: 10, totalCount: 0 },
        'Recently Approved': { currentPage: 1, pageSize: 10, totalCount: 0 }
      },
      showDetailsModal: false, // New state for details modal
      activeTab: 'myTasks', // Default to 'myTasks'
      selectedUserId: '', // To hold the selected user ID
      availableUsers: [], // To store available users for dropdown
      myTasks: [],
      reviewerTasks: [],
      isAdministrator: false,
      selectedUserInfo: null,
      currentUserId: null,
      myTasksCollapsible: {
        Pending: true,
        Approved: false,
        Rejected: false,
      },
      reviewerTasksCollapsible: {
        Pending: true,
        Approved: false,
        Rejected: false,
      },
      myTasksPagination: {
        Pending: { currentPage: 1, pageSize: 10 },
        Approved: { currentPage: 1, pageSize: 10 },
        Rejected: { currentPage: 1, pageSize: 10 },
      },
      reviewerTasksPagination: {
        Pending: { currentPage: 1, pageSize: 10 },
        Approved: { currentPage: 1, pageSize: 10 },
        Rejected: { currentPage: 1, pageSize: 10 },
      },
      mitigationString: '',
    }
  },
  async mounted() {
    console.log('ComplianceApprover mounted');
    await this.refreshData();
    await this.initializeUser();
    
    // Set up auto-refresh every 30 seconds
    this.refreshInterval = setInterval(() => {
      this.refreshData();
    }, 30000);
    
    // Add escape key handler for modal
    document.addEventListener('keydown', this.handleKeydown);
  },
  beforeUnmount() {
    // Clear the refresh interval when component is destroyed
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
    
    // Remove escape key handler
    document.removeEventListener('keydown', this.handleKeydown);
  },
  watch: {
    // Watch for changes in data and update pagination counts
    complianceApprovals: {
      handler() {
        this.updatePaginationCounts();
      },
      deep: true
    },
    approvedComplianceItems: {
      handler() {
        this.updatePaginationCounts();
      },
      deep: true
    },
    editingCompliance: {
      handler(newVal) {
        if (newVal && newVal.ExtractedData && newVal.ExtractedData.mitigation) {
          if (typeof newVal.ExtractedData.mitigation === 'object') {
            this.mitigationString = JSON.stringify(newVal.ExtractedData.mitigation, null, 2);
          } else {
            this.mitigationString = newVal.ExtractedData.mitigation;
          }
        }
      },
      deep: true
    },
    mitigationString(newVal) {
      if (this.editingCompliance && this.editingCompliance.ExtractedData) {
        try {
          // Try to parse as JSON, fallback to string
          this.editingCompliance.ExtractedData.mitigation = JSON.parse(newVal);
        } catch {
          this.editingCompliance.ExtractedData.mitigation = newVal;
        }
      }
    },
  },
  methods: {
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
    async refreshData() {
      if (this.isLoading) return; // Prevent multiple simultaneous refreshes
      
      this.isLoading = true;
      this.error = null;
      console.log('Refreshing data...');
      
      try {
        // Fetch approvals with reviewer_id
        const approvalsResponse = await complianceService.getCompliancePolicyApprovals({
          reviewer_id: this.userId
        });
        console.log('Approvals response:', approvalsResponse);

        if (approvalsResponse.data.success) {
          // Debug the incoming data
          console.log('Raw approvals data:', approvalsResponse.data.data);
          
          // Check for deactivation requests specifically
          const deactivationRequests = (approvalsResponse.data.data || []).filter(approval => 
            approval.ExtractedData?.type === 'compliance_deactivation' || 
            approval.ExtractedData?.RequestType === 'Change Status to Inactive' ||
            (approval.Identifier && approval.Identifier.includes('COMP-DEACTIVATE'))
          );
          
          console.log(`Found ${deactivationRequests.length} deactivation requests in the response:`, deactivationRequests);
          
          // Ensure ExtractedData is properly formatted
          this.approvals = (approvalsResponse.data.data || []).map(approval => ({
            ...approval,
            ExtractedData: {
              ...approval.ExtractedData,
              type: approval.ExtractedData?.type || 'compliance',
              compliance_approval: approval.ExtractedData?.compliance_approval || {
                approved: null,
                remarks: ''
              }
            }
          }));
          
          this.counts = approvalsResponse.data.counts || {
            pending: 0,
            approved: 0,
            rejected: 0
          };
          
          // Log approved compliances specifically to debug
          const approvedItems = this.approvals.filter(a => a.ApprovedNot === true);
          console.log(`Found ${approvedItems.length} approved compliances:`, approvedItems);
          
          console.log('Updated approvals:', this.approvals);
          console.log('Updated counts:', this.counts);
        } else {
          throw new Error(approvalsResponse.data.message || 'Failed to fetch approvals');
        }
        
        // Load rejected compliances
        await this.loadRejectedCompliances();
        
        // Update pagination counts after loading data
        this.updatePaginationCounts();
        
      } catch (error) {
        // Check if it's an access control error
        if (error.response && [401, 403].includes(error.response.status)) {
          AccessUtils.showApproveComplianceDenied();
          return;
        }
        
        console.error('Error refreshing data:', error);
        this.error = error.response?.data?.message || error.message || 'Failed to load approvals';
      } finally {
        this.isLoading = false;
      }
    },
   
    openApprovalDetails(approval) {
      console.log('Opening approval details:', approval);
      this.selectedApproval = approval;
      this.showDetailsModal = true;
    },
   

   
    async submitReview() {
      // Use popup for confirmation instead of window.confirm
      this.showConfirmPopup(
        'Do you want to approve this compliance item?',
        'Compliance Review',
        () => this.processApproval(true),
        () => this.showRejectPopup()
      );
    },
   
    showRejectPopup() {
      // Use popup for getting rejection comments
      this.showCommentPopup(
        'Please provide a reason for rejecting this compliance:',
        'Reject Compliance',
        (comments) => this.processApproval(false, comments)
      );
    },
    
    async processApproval(isApproved, remarks = '') {
      try {
        if (!this.selectedApproval) {
          return;
        }
        
        this.isSubmitting = true;
        
        let approvalId = this.selectedApproval.ApprovalId;
        
        // Handle different approval types
        if (this.selectedApproval.ExtractedData?.type === 'compliance_deactivation' ||
            this.selectedApproval.ExtractedData?.RequestType === 'Change Status to Inactive') {
          
          // Deactivation approval/rejection
          if (isApproved) {
            await complianceService.approveComplianceDeactivation(
              approvalId,
              { user_id: this.userId }
            );
          } else {
            await complianceService.rejectComplianceDeactivation(
              approvalId,
              { 
                user_id: this.userId,
                remarks: remarks
              }
            );
          }
        } else {
          // Regular compliance approval
          
          // Extract data from selected approval
          let extractedData = this.selectedApproval.ExtractedData;
          
          // Update approval status in the extracted data
          if (!extractedData.compliance_approval) {
            extractedData.compliance_approval = {};
          }
          
          extractedData.compliance_approval.approved = isApproved;
          extractedData.compliance_approval.remarks = remarks;
          
          await complianceService.submitComplianceReview(
            approvalId,
            {
              ExtractedData: extractedData,
              ApprovedNot: isApproved
            }
          );
        }
        
        // Show success popup
        CompliancePopups.reviewSubmitted(isApproved);
        
        // Update local approval status
        this.approvalStatus = {
          approved: isApproved,
          remarks: remarks
        };
        
        // Refresh the list
        this.refreshData();
      } catch (error) {
        console.error('Error submitting review:', error);
        // Show error popup
        this.showErrorPopup(`Error submitting review: ${error.message || 'Unknown error'}`);
      } finally {
        this.isSubmitting = false;
      }
    },
   
    async approveCompliance() {
      if (!this.selectedApproval) return;
     
      try {
        this.isLoading = true;
        console.log("Starting approval process for compliance ID:", this.selectedApproval.ApprovalId);
       
        // Check if this is a deactivation request
        const isDeactivationRequest = 
          this.selectedApproval.ExtractedData?.type === 'compliance_deactivation' || 
          this.selectedApproval.ExtractedData?.RequestType === 'Change Status to Inactive' ||
          (this.selectedApproval.Identifier && this.selectedApproval.Identifier.includes('COMP-DEACTIVATE'));
        
        console.log(`This is ${isDeactivationRequest ? 'a' : 'not a'} deactivation request`);
        
        let response;
        
        if (isDeactivationRequest) {
          // This is a deactivation request
          console.log("Processing deactivation approval...");
          response = await complianceService.approveComplianceDeactivation(
            this.selectedApproval.ApprovalId,
            { user_id: this.userId }
          );
          
          // Update the local data to reflect the compliance was deactivated
          if (this.selectedApproval.ExtractedData) {
            this.selectedApproval.ExtractedData.current_status = 'Inactive';
            if (this.selectedApproval.ExtractedData.compliance_approval) {
              this.selectedApproval.ExtractedData.compliance_approval.approved = true;
            }
          }
        } else {
          // This is a regular compliance approval
          // Initialize compliance approval if doesn't exist
          if (!this.selectedApproval.ExtractedData.compliance_approval) {
            this.selectedApproval.ExtractedData.compliance_approval = {};
          }
          this.selectedApproval.ExtractedData.compliance_approval.approved = true;
          this.selectedApproval.ExtractedData.compliance_approval.remarks = '';
         
          // Update the overall approval status
          this.selectedApproval.ApprovedNot = true;
         
          // Update status in ExtractedData - IMPORTANT for update after approval
          this.selectedApproval.ExtractedData.Status = 'Approved';
          this.selectedApproval.ExtractedData.ActiveInactive = 'Active';
         
          console.log('Approving compliance with data:', JSON.stringify(this.selectedApproval.ExtractedData));
         
          // Create a payload with just what's needed to reduce chance of network issues
          const reviewPayload = {
            ExtractedData: this.selectedApproval.ExtractedData,
            ApprovedNot: true
          };
          
          try {
            // First try with the full data
            response = await complianceService.submitComplianceReview(
              this.selectedApproval.ApprovalId,
              reviewPayload
            );
          } catch (apiError) {
            console.error('API call failed:', apiError);
            
            // If there's a network error, try with a simplified payload
            if (apiError.message === 'Network Error' || apiError.code === 'ERR_NETWORK') {
              console.log('Retrying with simplified payload due to network error');
              
              // Create a minimal payload for the retry
              const minimalPayload = {
                approved: true,
                remarks: ''
              };
              
              response = await complianceService.submitComplianceReview(
                this.selectedApproval.ApprovalId, 
                minimalPayload
              );
            } else {
              // If it's not a network error, rethrow
              throw apiError;
            }
          }
        }
       
        console.log('Approval response:', response?.data);
       
        // Note: rejectedCompliances is now a computed property, so it updates automatically
        // when the underlying data changes
       
        // Replace alert with popup
        this.showSuccessPopup(
          isDeactivationRequest ? 
          'Compliance has been deactivated successfully!' : 
          'Compliance has been approved successfully!',
          isDeactivationRequest ? 'Deactivation Complete' : 'Approval Complete'
        );
          
        this.closeDetailsModal();
       
        // Force a refresh after a short delay to ensure backend has updated
        setTimeout(() => {
          this.refreshData();
        }, 1000);
      } catch (error) {
        console.error('Error approving compliance:', error);
        // Replace alert with popup
        this.showErrorPopup(
          'Error approving compliance: ' + (error.response?.data?.message || error.message || 'Network error - please check server connection'),
          'Approval Error'
        );
      } finally {
        this.isLoading = false;
      }
    },
   
    rejectCompliance() {
      // Check if this is a deactivation request
      const isDeactivationRequest = 
        this.selectedApproval?.ExtractedData?.type === 'compliance_deactivation' || 
        this.selectedApproval?.ExtractedData?.RequestType === 'Change Status to Inactive' ||
        (this.selectedApproval?.Identifier && this.selectedApproval?.Identifier.includes('COMP-DEACTIVATE'));
      
      // Store the request type in the component data to use in confirmation
      this.isDeactivationRequest = isDeactivationRequest;
      
      this.showRejectModal = true;
    },
   
    async confirmRejection() {
      if (!this.rejectionComment.trim()) {
        alert('Please provide a reason for rejection');
        return;
      }
     
      try {
        this.isLoading = true;
        console.log("Starting rejection process for compliance ID:", this.selectedApproval.ApprovalId);
        
        let response;
        
        // Check if this is a deactivation request based on stored value
        if (this.isDeactivationRequest) {
          // This is a deactivation request rejection
          console.log("Processing deactivation rejection...");
          response = await complianceService.rejectComplianceDeactivation(
            this.selectedApproval.ApprovalId,
            { 
              user_id: this.userId,
              remarks: this.rejectionComment
            }
          );
          
          // Update the local data to reflect the deactivation was rejected
          if (this.selectedApproval.ExtractedData) {
            // Ensure compliance status remains Active in the local data
            this.selectedApproval.ExtractedData.current_status = 'Active';
            if (!this.selectedApproval.ExtractedData.compliance_approval) {
              this.selectedApproval.ExtractedData.compliance_approval = {};
            }
            this.selectedApproval.ExtractedData.compliance_approval.approved = false;
            this.selectedApproval.ExtractedData.compliance_approval.remarks = this.rejectionComment;
          }
        } else {
          // This is a regular compliance rejection
          // Initialize compliance approval object if it doesn't exist
          if (!this.selectedApproval.ExtractedData.compliance_approval) {
            this.selectedApproval.ExtractedData.compliance_approval = {};
          }
          // Set the approval status to rejected and add remarks
          this.selectedApproval.ExtractedData.compliance_approval.approved = false;
          this.selectedApproval.ExtractedData.compliance_approval.remarks = this.rejectionComment;
          this.selectedApproval.ApprovedNot = false;
          // Update status in ExtractedData - IMPORTANT for update after rejection
          this.selectedApproval.ExtractedData.Status = 'Rejected';
          this.selectedApproval.ExtractedData.ActiveInactive = 'Inactive';
          // --- Ensure remarks are included in the payload sent to backend ---
          const payload = {
            ExtractedData: {
              ...this.selectedApproval.ExtractedData,
              compliance_approval: {
                ...this.selectedApproval.ExtractedData.compliance_approval,
                remarks: this.rejectionComment,
                approved: false
              }
            },
            ApprovedNot: false
          };
          // Submit the review with the updated data
          response = await complianceService.submitComplianceReview(
            this.selectedApproval.ApprovalId,
            payload
          );
        }
        
        console.log('Rejection response:', response.data);
        
        // Replace alert with popup
        this.showSuccessPopup(
          this.isDeactivationRequest ? 
          'Deactivation request has been rejected successfully!' : 
          'Compliance has been rejected successfully!',
          'Rejection Complete'
        );
          
        this.showRejectModal = false;
        this.rejectionComment = '';
        this.closeDetailsModal();
        
        // Force a refresh after a short delay to ensure backend has updated
        setTimeout(() => {
          this.refreshData();
        }, 1000);
      } catch (error) {
        console.error('Error rejecting compliance:', error);
        // Replace alert with popup
        this.showErrorPopup(
          'Error rejecting compliance: ' + (error.response?.data?.message || error.message),
          'Rejection Error'
        );
      } finally {
        this.isLoading = false;
      }
    },
   
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectionComment = '';
    },
   
    openRejectedItem(item) {
      console.log('Opening rejected item:', item);
      this.editingCompliance = JSON.parse(JSON.stringify(item));
      this.showEditComplianceModal = true;
      
      // Log details for debugging
      console.log('Opened rejected item in edit modal:', {
        ApprovalId: this.editingCompliance.ApprovalId,
        Identifier: this.editingCompliance.Identifier,
        ApprovedNot: this.editingCompliance.ApprovedNot,
        remarks: this.editingCompliance.ExtractedData?.compliance_approval?.remarks
      });
    },
   
    closeEditComplianceModal() {
      this.showEditComplianceModal = false;
      this.editingCompliance = null;
    },
   
    async resubmitCompliance(compliance) {
      try {
        // Reset approval status
        if (compliance.ExtractedData.compliance_approval) {
          compliance.ExtractedData.compliance_approval.approved = null;
          compliance.ExtractedData.compliance_approval.remarks = '';
          // Mark as being resubmitted to prevent showing in the rejected list
          compliance.ExtractedData.compliance_approval.inResubmission = true;
        } else {
          compliance.ExtractedData.compliance_approval = {
            approved: null,
            remarks: '',
            inResubmission: true
          };
        }
       
        this.isLoading = true;
        console.log("Resubmitting compliance with ID:", compliance.ApprovalId);
        console.log("Resubmitting with data:", JSON.stringify(compliance.ExtractedData));
        
        const response = await complianceService.resubmitComplianceApproval(
          compliance.ApprovalId,
          { ExtractedData: compliance.ExtractedData }
        );
       
        console.log("Resubmission response:", response);
        
        if (response.data && (response.data.ApprovalId || response.data.success)) {
          // Note: rejectedCompliances is now a computed property, so it updates automatically
          // when the underlying data changes
          
          this.showEditComplianceModal = false;
          this.editingCompliance = null;
          
          // Show success message after the UI updates
          this.showSuccessPopup('Compliance resubmitted for review successfully!', 'Resubmission Complete');
          
          // Show more details about what happened
          console.log(`Resubmitted compliance with ID ${compliance.ApprovalId}. New version: ${response.data.Version}`);
          
          // Wait a moment before refreshing to allow the backend to update
          setTimeout(() => {
            this.refreshData();
          }, 1000);
        } else {
          throw new Error('Failed to get confirmation from server');
        }
      } catch (error) {
        console.error('Error resubmitting compliance:', error);
        this.showErrorPopup('Error resubmitting compliance: ' + (error.response?.data?.message || error.message), 'Resubmission Error');
      } finally {
        this.isLoading = false;
      }
    },
   
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        // Handle different date formats
        let date;
        if (typeof dateString === 'string') {
          // Try different date formats
          if (dateString.includes('T')) {
            // ISO format
            date = new Date(dateString);
          } else if (dateString.includes('-')) {
            // YYYY-MM-DD format
            const parts = dateString.split(' ')[0].split('-');
            date = new Date(parts[0], parts[1] - 1, parts[2]);
          } else if (dateString.includes('/')) {
            // MM/DD/YYYY format
            const parts = dateString.split(' ')[0].split('/');
            date = new Date(parts[2], parts[0] - 1, parts[1]);
          } else {
            date = new Date(dateString);
          }
        } else {
          date = new Date(dateString);
        }
        
        // Format the date
        return date.toLocaleString();
      } catch (e) {
        console.error('Error formatting date:', e);
        return dateString; // Return the original string if parsing fails
      }
    },
    async checkForApprovedIdentifiers() {
      // Note: rejectedCompliances is now a computed property, so it updates automatically
      // when the underlying data changes. No need to manually filter.
      console.log('Rejected compliances computed automatically:', this.rejectedCompliances);
    },
    isCompliantIdentifierApproved(identifier) {
      // Check if any approval with this identifier exists and is approved
      return this.approvals.some(approval => 
        approval.Identifier === identifier && approval.ApprovedNot === true
      );
    },
    // Load rejected compliances
    async loadRejectedCompliances() {
      try {
        this.isLoadingRejected = true;
        // The rejectedCompliances computed property now handles this automatically
        // No need to manually populate the array since it's computed from myTasksRejected and reviewerTasksRejected
        console.log('Rejected compliances computed automatically:', this.rejectedCompliances);
      } catch (error) {
        console.error('Error loading rejected compliances:', error);
      } finally {
        this.isLoadingRejected = false;
        // Update pagination counts after loading rejected compliances
        this.updatePaginationCounts();
      }
    },
    mapApprovalToRow(approval) {
      return {
        ...approval,
        Identifier: approval.Identifier || (approval.ExtractedData && approval.ExtractedData.Identifier) || 'N/A',
        Description: approval.ExtractedData?.ComplianceItemDescription || approval.ExtractedData?.reason || 'No Description',
        Criticality: approval.ExtractedData?.Criticality || 'N/A',
        CreatedBy: approval.ExtractedData?.CreatedByName || 'System',
        Version: approval.ExtractedData?.ComplianceVersion || approval.ExtractedData?.version || '1.0',
        actions: approval // Pass the whole object for the action button
      };
    },
    mapRejectedToRow(compliance) {
      return {
        ...compliance,
        Identifier: compliance.Identifier || (compliance.ExtractedData && compliance.ExtractedData.Identifier) || 'N/A',
        Description: compliance.ExtractedData?.ComplianceItemDescription || 'No Description',
        Criticality: compliance.ExtractedData?.Criticality || 'N/A',
        CreatedBy: compliance.ExtractedData?.CreatedByName || 'System',
        Version: compliance.ExtractedData?.ComplianceVersion || compliance.ExtractedData?.version || '1.0',
        actions: compliance // Pass the whole object for the action button
      };
    },
    handleApprovalAction(approval) {
      this.selectedApproval = approval; // Set selectedApproval for the modal
      this.showDetailsModal = true; // Open the details modal
    },
    handleRejectedAction(compliance) {
      this.openRejectedItem(compliance);
    },
    toggleSection(section) {
      this.collapsibleStates = {
        ...this.collapsibleStates,
        [section]: !this.collapsibleStates[section]
      };
    },
    handlePaginationChange(section, newPagination) {
      console.log(`Pagination change for section "${section}":`, {
        old: this.pagination[section],
        new: newPagination
      });
      this.pagination[section] = newPagination;
      console.log(`Updated pagination for section "${section}":`, this.pagination[section]);
    },
    
    // Add pagination methods
    getPaginatedTasks(tasks, section) {
      const pagination = this.pagination[section];
      const startIndex = (pagination.currentPage - 1) * pagination.pageSize;
      const endIndex = startIndex + pagination.pageSize;
      return tasks.slice(startIndex, endIndex);
    },
    
    updatePaginationCounts() {
      // Update pagination counts for each section
      const pendingCount = this.complianceApprovals.length;
      const approvedCount = this.approvedComplianceItems.length;
      const rejectedCount = this.rejectedCompliances.length;
      
      // Ensure minimum count for testing pagination visibility
      this.pagination.Pending.totalCount = Math.max(pendingCount, 1);
      this.pagination.Approved.totalCount = Math.max(approvedCount, 1);
      this.pagination.Rejected.totalCount = Math.max(rejectedCount, 1);
      this.pagination['Recently Approved'].totalCount = Math.max(approvedCount, 1);
      
      console.log('Updated pagination counts:', {
        Pending: this.pagination.Pending.totalCount,
        Approved: this.pagination.Approved.totalCount,
        Rejected: this.pagination.Rejected.totalCount,
        'Recently Approved': this.pagination['Recently Approved'].totalCount
      });
      
      console.log('Current pagination state:', this.pagination);
    },
    
    resetPagination() {
      // Reset pagination to first page for all sections
      Object.keys(this.pagination).forEach(section => {
        this.pagination[section].currentPage = 1;
      });
    },
    
    // Test method to verify pagination is working
    testPagination() {
      console.log('Testing pagination...');
      console.log('Current pagination state:', this.pagination);
      console.log('Compliance approvals count:', this.complianceApprovals.length);
      console.log('Approved items count:', this.approvedComplianceItems.length);
      console.log('Rejected compliances count:', this.rejectedCompliances.length);
      
      // Force update pagination counts
      this.updatePaginationCounts();
    },
         closeDetailsModal() {
       this.showDetailsModal = false;
       this.selectedApproval = null;
     },
     
     handleKeydown(event) {
       if (event.key === 'Escape' && this.showDetailsModal) {
         this.closeDetailsModal();
       }
     },
     async initializeUser() {
      try {
        // Get current user role
        const response = await axios.get('http://localhost:8000/api/user-role/');
        if (response.data.success) {
          this.currentUserId = response.data.user_id;
          const userRole = response.data.role;
          this.isAdministrator = userRole === 'GRC Administrator';
          if (this.isAdministrator) {
            await this.fetchUsers();
            this.selectedUserId = null;
          } else {
            this.selectedUserId = this.currentUserId;
            await this.loadUserTasks();
          }
        }
      } catch (error) {
        console.error('Error initializing user:', error);
      }
    },
    async fetchUsers() {
      try {
        const response = await axios.get('http://localhost:8000/api/users-for-dropdown/');
        if (Array.isArray(response.data)) {
          this.availableUsers = response.data;
        } else if (response.data && response.data.success && Array.isArray(response.data.data)) {
          this.availableUsers = response.data.data;
        } else {
          this.availableUsers = response.data || [];
        }
      } catch (error) {
        console.error('Error fetching users:', error);
        this.availableUsers = [];
      }
    },
    async onUserChange() {
      if (this.selectedUserId) {
        this.selectedUserInfo = this.availableUsers.find(u => u.UserId == this.selectedUserId);
        await this.loadUserTasks();
      } else {
        this.selectedUserInfo = null;
        this.myTasks = [];
        this.reviewerTasks = [];
      }
    },
    switchTab(tab) {
      this.activeTab = tab;
    },
    async loadUserTasks() {
      const targetUserId = this.selectedUserId || this.currentUserId;
      if (this.isAdministrator && !this.selectedUserId) {
        this.myTasks = [];
        this.reviewerTasks = [];
        return;
      }
      await this.fetchMyTasks(targetUserId);
      await this.fetchReviewerTasks(targetUserId);
    },
    async fetchMyTasks(userId) {
      try {
        const response = await axios.get(`http://localhost:8000/api/compliance-approvals/user/${userId}/`);
        if (Array.isArray(response.data)) {
          this.myTasks = response.data;
        } else if (response.data && Array.isArray(response.data.data)) {
          this.myTasks = response.data.data;
        } else if (response.data && Array.isArray(response.data.results)) {
          this.myTasks = response.data.results;
        } else {
          this.myTasks = [];
        }
      } catch (error) {
        this.myTasks = [];
      }
    },
    async fetchReviewerTasks(userId) {
      try {
        const response = await axios.get(`http://localhost:8000/api/compliance-approvals/reviewer/${userId}/`);
        if (Array.isArray(response.data)) {
          this.reviewerTasks = response.data;
        } else if (response.data && Array.isArray(response.data.data)) {
          this.reviewerTasks = response.data.data;
        } else if (response.data && Array.isArray(response.data.results)) {
          this.reviewerTasks = response.data.results;
        } else {
          this.reviewerTasks = [];
        }
      } catch (error) {
        this.reviewerTasks = [];
      }
    },
    handleMyTasksPageChange(section, page) {
      this.myTasksPagination[section].currentPage = page;
    },
    handleReviewerTasksPageChange(section, page) {
      this.reviewerTasksPagination[section].currentPage = page;
    },
    formatMitigation(mitigation) {
      if (!mitigation) return '';
      if (typeof mitigation === 'string') return mitigation;
      if (typeof mitigation === 'object') {
        try {
          // If it's a simple object, join values; otherwise, pretty print
          if (Array.isArray(mitigation)) {
            return mitigation.join(', ');
          } else {
            // Join values if all are strings, else pretty print
            const values = Object.values(mitigation);
            if (values.every(v => typeof v === 'string')) {
              return values.join(', ');
            } else {
              return JSON.stringify(mitigation, null, 2);
            }
          }
        } catch (e) {
          return String(mitigation);
        }
      }
      return String(mitigation);
    },
  },
  computed: {
    pendingApprovalsCount() {
      return this.counts.pending || 0;
    },
    approvedApprovalsCount() {
      return this.counts.approved || 0;
    },
    rejectedApprovalsCount() {
      return this.counts.rejected || 0;
    },
    complianceApprovals() {
      console.log("Computing complianceApprovals from", this.approvals.length, "total approvals");
      
      // Debug all incoming approval data to verify deactivation requests
      console.log("All approvals:");
      this.approvals.forEach((approval, index) => {
        if (!approval) {
          console.log(`[${index}] Approval is null or undefined`);
          return;
        }
        
        console.log(`[${index}] ID: ${approval.ApprovalId}, Identifier: ${approval.Identifier}`);
        
        if (!approval.ExtractedData) {
          console.log(`    WARNING: ExtractedData is null or undefined`);
          return;
        }
        
        console.log(`    Type: ${approval.ExtractedData?.type}, RequestType: ${approval.ExtractedData?.RequestType}`);
        console.log(`    ApprovedNot: ${approval.ApprovedNot}`);
        
        // Check if this appears to be a deactivation request
        const isDeactivation = 
          approval.ExtractedData?.type === 'compliance_deactivation' || 
          approval.ExtractedData?.RequestType === 'Change Status to Inactive' ||
          (approval.Identifier && approval.Identifier.includes('COMP-DEACTIVATE'));
          
        console.log(`    Is deactivation request: ${isDeactivation}`);
        
        if (isDeactivation) {
          console.log(`    Deactivation request details:`, 
            JSON.stringify({
              reason: approval.ExtractedData?.reason,
              compliance_id: approval.ExtractedData?.compliance_id,
              current_status: approval.ExtractedData?.current_status,
              requested_status: approval.ExtractedData?.requested_status
            })
          );
        }
      });
      
      // Apply the filter with detailed logging
      const filtered = this.approvals.filter(approval => {
        // Skip null or undefined approvals
        if (!approval) {
          console.log(`Skipping null approval`);
          return false;
        }
        
        // Check if ExtractedData exists
        if (!approval.ExtractedData) {
          console.log(`Approval ${approval.ApprovalId || 'unknown'}: ExtractedData is missing`);
          return false;
        }
        
        // For each approval, check if it matches our criteria
        const isCompliance = 
          approval.ExtractedData?.type === 'compliance' ||
          approval.ExtractedData?.type === 'compliance_deactivation' ||
          (approval.Identifier && approval.Identifier.includes('COMP-DEACTIVATE'));
          
        const isPending = approval.ApprovedNot === null;
        
        // CRITICAL: Log the exact properties we're testing for
        if (approval.ExtractedData?.type === 'compliance_deactivation') {
          console.log(`Found deactivation by type: ${approval.Identifier}`);
        }
        
        if (approval.ExtractedData?.RequestType === 'Change Status to Inactive') {
          console.log(`Found deactivation by RequestType: ${approval.Identifier}`);
        }
        
        if (approval.Identifier && approval.Identifier.includes('COMP-DEACTIVATE')) {
          console.log(`Found deactivation by Identifier: ${approval.Identifier}`);
        }
        
        console.log(`Approval ${approval.ApprovalId}: isCompliance=${isCompliance}, isPending=${isPending}`);
        
        return isCompliance && isPending;
      });
      
      console.log(`Filtered to ${filtered.length} pending compliance approvals`);
      
      // If we have deactivation requests in the original data but none in the filtered list, log a warning
      const deactivationRequests = this.approvals.filter(approval => 
        approval?.ExtractedData?.type === 'compliance_deactivation' || 
        approval?.ExtractedData?.RequestType === 'Change Status to Inactive' ||
        (approval?.Identifier && approval?.Identifier.includes('COMP-DEACTIVATE'))
      );
      
      if (deactivationRequests.length > 0 && !filtered.some(item => 
        item?.ExtractedData?.type === 'compliance_deactivation' || 
        item?.ExtractedData?.RequestType === 'Change Status to Inactive' ||
        (item?.Identifier && item?.Identifier.includes('COMP-DEACTIVATE'))
      )) {
        console.warn('WARNING: Deactivation requests exist but none passed the filter!');
        
        // Try to find out why they were filtered out
        deactivationRequests.forEach(request => {
          console.log(`Deactivation request ${request.ApprovalId} with ApprovedNot=${request.ApprovedNot}`);
          
          // If it was filtered because it's already approved/rejected, add it anyway for debugging
          if (request.ApprovedNot !== null) {
            console.log(`This request was filtered because ApprovedNot=${request.ApprovedNot}`);
            // Uncomment this line to force inclusion of these items for debugging
            // filtered.push(request);
          }
        });
      }
      
      return filtered;
    },
    approvalStatus() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return null;
      return this.selectedApproval.ExtractedData.compliance_approval || { approved: null, remarks: '' };
    },
    approvedComplianceItems() {
      // Debug the approvals array
      console.log('Computing approvedComplianceItems from approvals:', this.approvals);
     
      // Filter approved items and include more details in the debug log
      const approved = this.approvals.filter(approval => {
        const isApproved = approval.ApprovedNot === true;
        const isCompliance = approval.ExtractedData?.type === 'compliance';
       
        if (isApproved) {
          console.log(`Approval ${approval.ApprovalId} is approved:`,
            {isCompliance, type: approval.ExtractedData?.type, ApprovedNot: approval.ApprovedNot});
        }
       
        return isApproved && isCompliance;
      });
     
      console.log(`Found ${approved.length} approved compliance items`);
      return approved;
    },
    groupedApprovals() {
      // Group approvals by status
      const groups = {
        Pending: [],
        Approved: [],
        Rejected: []
      };
      this.approvals.forEach(approval => {
        if (approval.ApprovedNot === null) {
          groups.Pending.push(approval);
        } else if (approval.ApprovedNot === true) {
          groups.Approved.push(approval);
        } else if (approval.ApprovedNot === false) {
          groups.Rejected.push(approval);
        }
      });
      return groups;
    },
    approvalTableHeaders() {
      return [
        { key: 'Identifier', label: 'Identifier' },
        { key: 'Description', label: 'Description' },
        { key: 'Criticality', label: 'Criticality' },
        { key: 'CreatedBy', label: 'Created By' },
        { key: 'Version', label: 'Version' },
        { key: 'actions', label: 'Actions' }
      ];
    },
    rejectedTableHeaders() {
      return [
        { key: 'Identifier', label: 'Identifier' },
        { key: 'Description', label: 'Description' },
        { key: 'Criticality', label: 'Criticality' },
        { key: 'CreatedBy', label: 'Created By' },
        { key: 'Version', label: 'Version' },
        { key: 'actions', label: 'Actions' }
      ];
    },
    myTasksCount() {
      return this.myTasks ? this.myTasks.length : 0;
    },
    reviewerTasksCount() {
      return this.reviewerTasks ? this.reviewerTasks.length : 0;
    },
    myTasksPending() {
      return this.myTasks.filter(t => t.ApprovedNot === null);
    },
    myTasksApproved() {
      return this.myTasks.filter(t => t.ApprovedNot === true);
    },
    myTasksRejected() {
      return this.myTasks.filter(t => t.ApprovedNot === false);
    },
    reviewerTasksPending() {
      return this.reviewerTasks.filter(t => t.ApprovedNot === null);
    },
    reviewerTasksApproved() {
      return this.reviewerTasks.filter(t => t.ApprovedNot === true);
    },
    reviewerTasksRejected() {
      return this.reviewerTasks.filter(t => t.ApprovedNot === false);
    },
    myTasksPendingPaged() {
      const { currentPage, pageSize } = this.myTasksPagination.Pending;
      const start = (currentPage - 1) * pageSize;
      return this.myTasksPending.slice(start, start + pageSize);
    },
    myTasksApprovedPaged() {
      const { currentPage, pageSize } = this.myTasksPagination.Approved;
      const start = (currentPage - 1) * pageSize;
      return this.myTasksApproved.slice(start, start + pageSize);
    },
    myTasksRejectedPaged() {
      const { currentPage, pageSize } = this.myTasksPagination.Rejected;
      const start = (currentPage - 1) * pageSize;
      return this.myTasksRejected.slice(start, start + pageSize);
    },
    reviewerTasksPendingPaged() {
      const { currentPage, pageSize } = this.reviewerTasksPagination.Pending;
      const start = (currentPage - 1) * pageSize;
      return this.reviewerTasksPending.slice(start, start + pageSize);
    },
    reviewerTasksApprovedPaged() {
      const { currentPage, pageSize } = this.reviewerTasksPagination.Approved;
      const start = (currentPage - 1) * pageSize;
      return this.reviewerTasksApproved.slice(start, start + pageSize);
    },
    reviewerTasksRejectedPaged() {
      const { currentPage, pageSize } = this.reviewerTasksPagination.Rejected;
      const start = (currentPage - 1) * pageSize;
      return this.reviewerTasksRejected.slice(start, start + pageSize);
    },
    rejectedCompliances() {
      // Combine all rejected items
      const allRejected = [...this.myTasksRejected, ...this.reviewerTasksRejected];
      const seen = new Set();
      return allRejected.filter(item => {
        // Normalize Identifier and ApprovalId
        const identifier = (item.Identifier || '').toString().trim().toLowerCase();
        const approvalId = (item.ApprovalId || '').toString().trim().toLowerCase();
        const key = `${identifier}__${approvalId}`;
        // Debug: log the key
        console.log('Rejected key:', key, item);
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
    },
    isMitigationObject() {
      return this.editingCompliance && this.editingCompliance.ExtractedData && typeof this.editingCompliance.ExtractedData.mitigation === 'object';
    },
    rejectionReason() {
      if (!this.editingCompliance || !this.editingCompliance.ExtractedData) return '';
      const ca = this.editingCompliance.ExtractedData.compliance_approval || {};
      return ca.remarks || ca.rejection_reason || ca.reason || '';
    },
  }
}
</script>
 
<style scoped>
.error-message {
  background-color: #fee;
  color: #c00;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
  border: 1px solid #fcc;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
 
.retry-btn {
  background: #c00;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
 
.loading-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}
 
.no-data-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  background: #f9f9f9;
  border-radius: 4px;
  margin: 1rem 0;
}
 
.no-data-state i {
  font-size: 2rem;
  color: #999;
  margin-bottom: 1rem;
}
 
.approval-details {
  margin: 0.5rem 0;
}
 
.description {
  margin: 0.5rem 0;
  color: #666;
}
 
.meta-info {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #666;
}
 
.criticality {
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  font-weight: 500;
}
 
.criticality.high {
  background: #fee;
  color: #c00;
}
 
.criticality.medium {
  background: #ffd;
  color: #960;
}
 
.criticality.low {
  background: #efe;
  color: #060;
}
 
.created-by {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
 
.version {
  color: #999;
}
 
.approval-status.approved {
  color: #28a745;
  font-weight: 500;
}
 
.approved-list {
  margin-top: 2rem;
  background-color: #f8fff8;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #d0e9d0;
}
 
.approved-list h3 {
  color: #28a745;
  border-bottom: 1px solid #d0e9d0;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}
 
.approved-list li {
  background-color: white;
  border: 1px solid #e0e0e0;
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 4px;
  position: relative;
}
 
.status-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  font-size: 0.8rem;
  font-weight: 500;
  margin-left: 0.5rem;
}
 
.status-badge.approved {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}
 
.approval-date {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #28a745;
}
 
.approval-date i {
  font-size: 0.9rem;
}
 
.rejection-reason {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #fff0f0;
  border-left: 3px solid #ff3333;
  border-radius: 0 4px 4px 0;
  color: #c00;
  font-size: 0.9rem;
}

.badge.rejected {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ffcdd2;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.rejected-approvals-list {
  margin-top: 2rem;
  background-color: #fff8f8;
  padding: 1.5rem;
  border-radius: 8px;
  border: 2px solid #e6d0d0;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.1);
}

.rejected-approvals-list h3 {
  color: #c00;
  border-bottom: 1px solid #e6d0d0;
  padding-bottom: 0.8rem;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.rejected-approvals-list li {
  background-color: white;
  border: 1px solid #e0e0e0;
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 4px;
  position: relative;
}

.rejected-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.rejected-item-details {
  padding-left: 0.5rem;
  border-left: 2px solid #f0f0f0;
}

.rejected-date {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #d32f2f;
}

.rejected-date i {
  font-size: 0.9rem;
}

.edit-rejected-btn {
  margin-top: 1rem;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.edit-rejected-btn:hover {
  background-color: #eeeeee;
  border-color: #ccc;
}

.edit-rejected-btn i {
  font-size: 0.9rem;
  color: #555;
}

.rejected-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e6d0d0;
  padding-bottom: 0.8rem;
  margin-bottom: 1.5rem;
}

.refresh-rejected-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: 1px solid #dc3545;
  background-color: #fff;
  color: #dc3545;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.refresh-rejected-btn:hover {
  background-color: #dc3545;
  color: white;
}

@import './ComplianceApprover.css';

/* Add styles for the deactivation badge */
.deactivation-badge {
  display: inline-block;
  background-color: #ffe0b2;
  color: #e65100;
  border: 1px solid #ffcc80;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  margin-left: 0.5rem;
}

/* Add styles for the warning message */
.warning-message {
  margin-top: 15px;
  padding: 10px 15px;
  background-color: #fff3e0;
  border-left: 4px solid #ff9800;
  border-radius: 0 4px 4px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.warning-message i {
  color: #ff9800;
  font-size: 1.2rem;
}

.deactivation-request-details {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fff8e1;
  border-radius: 4px;
}

.compliance-details-section {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  padding: 2rem;
  margin: 2rem auto;
  max-width: 900px;
  position: relative;
  animation: fadeIn 0.3s;
}
.back-btn {
  background: #f5f5f5;
  border: none;
  color: #333;
  font-size: 1rem;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: background 0.2s;
}
.back-btn:hover {
  background: #e0e0e0;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(30px);}
  to { opacity: 1; transform: translateY(0);}
}

.rejected-table-wrapper {
  overflow-x: auto;
}

.rejected-table {
  width: 100%;
  border-collapse: collapse;
}

.rejected-table th, .rejected-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.rejected-table th {
  background-color: #f8f9fa;
}

.badge-rejected {
  background-color: #ffdddd;
  color: #d32f2f;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.action-btn {
  margin-right: 10px;
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background-color: #e0e0e0;
}

.view-btn {
  background-color: #d3d3d3;
}

.edit-btn {
  background-color: #ffdddd;
}

.status-badge.rejected {
  background-color: #ffdddd;
  color: #d32f2f;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.actions-cell {
  display: flex;
  gap: 10px;
}
</style>