<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Framework Approver</h2>
      <div class="dashboard-controls">
        <!-- User Selection Dropdown for GRC Administrators -->
        <div v-if="isGRCAdministrator && userInitialized" class="user-selection-container">
          <label for="userSelect" class="user-select-label">Select User:</label>
          <select 
            id="userSelect" 
            v-model="selectedUserId" 
            @change="onUserSelectionChange" 
            class="user-select-dropdown"
          >
            <option value="">-- Select a User --</option>
            <option 
              v-for="user in availableUsers" 
              :key="user.UserId" 
              :value="user.UserId"
            >
              {{ user.UserName }} ({{ user.Role }})
            </option>
          </select>
        </div>
        
      <div class="dashboard-actions">
        <button class="action-btn" @click="refreshData"><i class="fas fa-sync-alt"></i></button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
        </div>
          </div>
        </div>
        
    <!-- Performance Summary Cards for Framework Approver -->
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

    <!-- Collapsible Table with Framework Details -->
    <div class="frameworks-table-container">
      <!-- Show message when GRC Administrator hasn't selected a user -->
      <div v-if="isGRCAdministrator && !selectedUserId && userInitialized" class="no-user-selected-message">
        <div class="info-card">
          <i class="fas fa-info-circle"></i>
          <h3>Select a User</h3>
          <p>Please select a user from the dropdown above to view their framework tasks and reviewer assignments.</p>
        </div>
      </div>
      
      <!-- Show loading message while initializing -->
      <div v-else-if="!userInitialized" class="loading-message">
        <div class="info-card">
          <i class="fas fa-spinner fa-spin"></i>
          <h3>Loading...</h3>
          <p>Initializing user permissions and loading framework data...</p>
        </div>
      </div>
      
      <!-- Show framework sections when ready -->
      <template v-else>
        <!-- Tab Navigation -->
        <div class="tab-navigation">
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'myTasks' }"
            @click="activeTab = 'myTasks'"
          >
            <i class="fas fa-user"></i>
            My Tasks ({{ myTasksCount }})
          </button>
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'reviewerTasks' }"
            @click="activeTab = 'reviewerTasks'"
          >
            <i class="fas fa-clipboard-check"></i>
            Reviewer Tasks ({{ reviewerTasksCount }})
          </button>
        </div>

        <!-- Tab Content -->
        <div class="tab-content">
          <!-- My Tasks Tab -->
          <div v-if="activeTab === 'myTasks'" class="tab-panel">
      <CollapsibleTable
              v-for="section in myTasksSections"
        :key="section.name"
        :section-config="section"
        :table-headers="tableHeaders"
        :is-expanded="expandedSections[section.name]"
        @toggle="toggleSection(section.name)"
        @task-click="openApprovalDetails"
      />
          </div>

          <!-- Reviewer Tasks Tab -->
          <div v-if="activeTab === 'reviewerTasks'" class="tab-panel">
            <CollapsibleTable
              v-for="section in reviewerTasksSections"
              :key="section.name"
              :section-config="section"
              :table-headers="tableHeaders"
              :is-expanded="expandedSections[section.name]"
              @toggle="toggleSection(section.name)"
              @task-click="openApprovalDetails"
            />
          </div>
        </div>
      </template>
            </div>

    <!-- Framework Details Modal -->
    <div v-if="showFrameworkDetails && selectedApproval" class="framework-details-modal">
      <div class="framework-details-content">
        <h3>
          <span class="detail-type-indicator">Framework</span> 
          Details: {{ getFrameworkId(selectedApproval) }}
          <span class="version-pill">Version: {{ selectedApproval.version || 'u1' }}</span>
        </h3>
        
        <button class="close-btn" @click="closeApprovalDetails">Close</button>
        
        <!-- Framework Approval Section -->
        <div class="framework-approval-section">
          <h4>Framework Approval</h4>
          
          <!-- Framework status indicator -->
          <div class="framework-status-indicator">
            <span class="status-label">Status:</span>
            <span class="status-value" :class="{
              'status-approved': selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved',
              'status-rejected': selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected',
              'status-pending': selectedApproval.ApprovedNot === null && selectedApproval.ExtractedData?.Status !== 'Approved' && selectedApproval.ExtractedData?.Status !== 'Rejected'
            }">
              {{ selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved' ? 'Approved' : 
                 selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected' ? 'Rejected' : 
                 'Under Review' }}
            </span>
            <span v-if="selectedApproval.ApprovedDate" class="approval-date">
              (Approved on: {{ formatDate(selectedApproval.ApprovedDate) }})
            </span>
            </div>

          <div class="framework-actions">
            <button class="approve-btn" @click="approveFramework()" v-if="isReviewer && selectedApproval.ApprovedNot === null">
              <i class="fas fa-check"></i> Approve
            </button>
            <button class="reject-btn" @click="rejectFramework()" v-if="isReviewer && selectedApproval.ApprovedNot === null">
              <i class="fas fa-times"></i> Reject
            </button>
            <button class="submit-btn" @click="submitReview()" v-if="isReviewer && selectedApproval.ApprovedNot !== null">
              <i class="fas fa-paper-plane"></i> Submit Review
            </button>
        </div>
            </div>

        <!-- Display framework details -->
        <div v-if="selectedApproval.ExtractedData">
          <div v-for="(value, key) in selectedApproval.ExtractedData" :key="key" class="framework-detail-row">
            <template v-if="key !== 'policies' && key !== 'framework_approval' && key !== 'type' && key !== 'totalPolicies' && key !== 'totalSubpolicies'">
              <strong>{{ formatFieldName(key) }}:</strong> <span>{{ value }}</span>
            </template>
          </div>
            </div>

        <!-- Display policies from ExtractedData (for frameworks from tailoring) -->
        <div v-if="selectedApproval && selectedApproval.ExtractedData && selectedApproval.ExtractedData.policies" class="policies-section">
          <h4>Framework Policies ({{ selectedApproval.ExtractedData.policies.length }})</h4>
          
          <!-- Debug information -->
          <div v-if="selectedApproval.ExtractedData.policies.length === 0" class="no-policies-message">
            <p>No policies found in this framework.</p>
            </div>

          <div v-for="policy in selectedApproval.ExtractedData.policies" :key="policy.PolicyId" class="policy-item">
                  <div class="policy-header">
              <h5 class="policy-name">{{ policy.PolicyName || 'Unnamed Policy' }}</h5>
              <div class="policy-header-actions">
                <span class="policy-status" :class="{
                  'status-approved': policy.Status === 'Approved',
                  'status-rejected': policy.Status === 'Rejected',
                  'status-pending': policy.Status === 'Under Review' || !policy.Status
                }">{{ policy.Status || 'Under Review' }}</span>
                
                <!-- Policy Actions -->
                <div v-if="isReviewer && selectedApproval.ApprovedNot === null" class="policy-actions">
                  <button 
                    class="approve-policy-btn" 
                    @click="approvePolicy(policy)"
                    :disabled="!canApprovePolicy(policy)"
                    :title="!canApprovePolicy(policy) ? 'All subpolicies must be approved first' : 'Approve Policy'"
                  >
                    <i class="fas fa-check"></i>
                  </button>
                  <button 
                    class="reject-policy-btn" 
                    @click="rejectPolicy(policy)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
                  </div>
                  
                  <div class="policy-details">
              <div class="policy-detail-item" v-if="policy.PolicyDescription">
                <strong>Description:</strong> {{ policy.PolicyDescription }}
                  </div>
              <div class="policy-detail-item" v-if="policy.Objective">
                <strong>Objective:</strong> {{ policy.Objective }}
                </div>
              <div class="policy-detail-item" v-if="policy.Scope">
                <strong>Scope:</strong> {{ policy.Scope }}
              </div>
              <div class="policy-detail-item" v-if="policy.Department">
                <strong>Department:</strong> {{ policy.Department }}
              </div>
              <div class="policy-detail-item" v-if="policy.Applicability">
                <strong>Applicability:</strong> {{ policy.Applicability }}
              </div>
              <div class="policy-detail-item" v-if="policy.Identifier">
                <strong>Identifier:</strong> {{ policy.Identifier }}
              </div>
              <div class="policy-detail-item" v-if="policy.CoverageRate">
                <strong>Coverage Rate:</strong> {{ policy.CoverageRate }}%
              </div>
              <div class="policy-detail-item" v-if="policy.PolicyType">
                <strong>Policy Type:</strong> {{ policy.PolicyType }}
              </div>
              <div class="policy-detail-item" v-if="policy.PolicyCategory">
                <strong>Policy Category:</strong> {{ policy.PolicyCategory }}
              </div>
              <div class="policy-detail-item" v-if="policy.PolicySubCategory">
                <strong>Policy Sub Category:</strong> {{ policy.PolicySubCategory }}
            </div>

              <!-- Subpolicies Section - Multiple conditions to catch all cases -->
              <div v-if="policy.subpolicies && Array.isArray(policy.subpolicies) && policy.subpolicies.length > 0" class="subpolicies-section">
                <h6 class="subpolicies-heading">
                  <i class="fas fa-list-ul"></i>
                  Sub-Policies ({{ policy.subpolicies.length }})
                </h6>
                <div v-for="subpolicy in policy.subpolicies" :key="subpolicy.SubPolicyId || subpolicy.id" class="subpolicy-item">
                  <div class="subpolicy-header">
                    <div class="subpolicy-name">
                      <strong>{{ subpolicy.SubPolicyName || subpolicy.name || subpolicy.Identifier || 'Unnamed Subpolicy' }}</strong>
              </div>
                    <div class="subpolicy-actions" v-if="isReviewer && selectedApproval.ApprovedNot === null">
                      <button 
                        class="approve-btn" 
                        @click="approveSubpolicy(policy, subpolicy)"
                        :disabled="subpolicy.Status === 'Approved'"
                        :class="{ 'approved': subpolicy.Status === 'Approved' }"
                      >
                        <i class="fas fa-check"></i>
                      </button>
                      <button 
                        class="reject-btn" 
                        @click="rejectSubpolicy(policy, subpolicy)"
                        :disabled="subpolicy.Status === 'Rejected'"
                        :class="{ 'rejected': subpolicy.Status === 'Rejected' }"
                      >
                        <i class="fas fa-times"></i>
                      </button>
            </div>
          </div>
                  <div class="subpolicy-content">
                    <div class="subpolicy-detail" v-if="subpolicy.Description">
                      <strong>Description:</strong> {{ subpolicy.Description }}
        </div>
                    <div class="subpolicy-detail" v-if="subpolicy.Control">
                      <strong>Control:</strong> {{ subpolicy.Control }}
      </div>
                    <div class="subpolicy-detail" v-if="subpolicy.Identifier">
                      <strong>Identifier:</strong> {{ subpolicy.Identifier }}
    </div>
                    <div class="subpolicy-status" :class="getStatusClass(subpolicy.Status || 'Under Review')">
                      Status: {{ subpolicy.Status || 'Under Review' }}
        </div>
          </div>
                </div>
              </div>
              
              <!-- Alternative check for different subpolicy structures -->
              <div v-else-if="policy.SubPolicies && Array.isArray(policy.SubPolicies) && policy.SubPolicies.length > 0" class="subpolicies-section">
                <h6 class="subpolicies-heading">
                  <i class="fas fa-list-ul"></i>
                  Sub-Policies ({{ policy.SubPolicies.length }})
                </h6>
                <div v-for="subpolicy in policy.SubPolicies" :key="subpolicy.SubPolicyId || subpolicy.id" class="subpolicy-item">
                  <div class="subpolicy-header">
                    <div class="subpolicy-name">
                      <strong>{{ subpolicy.SubPolicyName || subpolicy.name || subpolicy.Identifier || 'Unnamed Subpolicy' }}</strong>
                    </div>
                    <div class="subpolicy-actions" v-if="isReviewer && selectedApproval.ApprovedNot === null">
                      <button 
                        class="approve-btn" 
                        @click="approveSubpolicy(policy, subpolicy)"
                        :disabled="subpolicy.Status === 'Approved'"
                        :class="{ 'approved': subpolicy.Status === 'Approved' }"
                      >
                        <i class="fas fa-check"></i>
            </button>
                      <button 
                        class="reject-btn" 
                        @click="rejectSubpolicy(policy, subpolicy)"
                        :disabled="subpolicy.Status === 'Rejected'"
                        :class="{ 'rejected': subpolicy.Status === 'Rejected' }"
                      >
                        <i class="fas fa-times"></i>
                      </button>
          </div>
        </div>
                  <div class="subpolicy-content">
                    <div class="subpolicy-detail" v-if="subpolicy.Description">
                      <strong>Description:</strong> {{ subpolicy.Description }}
      </div>
                    <div class="subpolicy-detail" v-if="subpolicy.Control">
                      <strong>Control:</strong> {{ subpolicy.Control }}
    </div>
                    <div class="subpolicy-detail" v-if="subpolicy.Identifier">
                      <strong>Identifier:</strong> {{ subpolicy.Identifier }}
          </div>
                    <div class="subpolicy-status" :class="getStatusClass(subpolicy.Status || 'Under Review')">
                      Status: {{ subpolicy.Status || 'Under Review' }}
                    </div>
                  </div>
        </div>
      </div>

              <!-- Message when no subpolicies found -->
              <div v-else class="no-subpolicies-message">
                <p><em>No sub-policies found for this policy.</em></p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Add a message for rejected frameworks -->
        <div v-if="selectedApproval.ApprovedNot === false" class="rejected-framework-message">
          <div class="rejection-note">
            <i class="fas fa-exclamation-triangle"></i>
            This framework has been rejected. All policies and subpolicies within this framework have been automatically rejected.
            </div>
          </div>
        </div>
        
      <!-- Rejection Modal -->
      <div v-if="showRejectModal" class="reject-modal">
        <div class="reject-modal-content">
          <h4>Rejection Reason</h4>
          <p>Please provide a reason for rejecting this {{ currentRejectionType }}</p>
          <textarea 
            v-model="rejectionComment" 
            class="rejection-comment" 
            placeholder="Enter your comments here..."></textarea>
          <div class="reject-modal-actions">
            <button class="cancel-btn" @click="cancelRejection">Cancel</button>
            <button class="confirm-btn" @click="confirmRejection">Confirm Rejection</button>
          </div>
          </div>
        </div>
      </div>

    <!-- Replace the rejected frameworks list with a table -->
    <div class="rejected-approvals-section" v-if="rejectedFrameworks.length">
      <h3>Rejected Frameworks (Edit & Resubmit)</h3>
      <div class="table-container">
        <table class="frameworks-table">
          <thead>
            <tr>
              <th @click="sortRejected('FrameworkId')">FRAMEWORK ID 
                <i class="fas fa-sort"></i>
              </th>
              <th @click="sortRejected('FrameworkName')">NAME 
                <i class="fas fa-sort"></i>
              </th>
              <th @click="sortRejected('Category')">CATEGORY 
                <i class="fas fa-sort"></i>
              </th>
              <th @click="sortRejected('CreatedByName')">CREATED BY 
                <i class="fas fa-sort"></i>
              </th>
              <th @click="sortRejected('CreatedByDate')">CREATED DATE 
                <i class="fas fa-sort"></i>
              </th>
              <th>STATUS</th>
              <th>ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="framework in sortedRejectedFrameworks" :key="framework.FrameworkId">
              <td>
                <a href="#" class="framework-id-link" @click.prevent="openRejectedItem(framework)">
                  {{ getFrameworkId(framework) }}
                </a>
              </td>
              <td>{{ framework.ExtractedData.FrameworkName }}</td>
              <td>{{ framework.ExtractedData.Category || 'No Category' }}</td>
              <td>{{ framework.ExtractedData.CreatedByName }}</td>
              <td>{{ formatDate(framework.ExtractedData.CreatedByDate) }}</td>
              <td>
                <span class="status-badge rejected">Rejected</span>
              </td>
              <td class="actions-cell">
                <button class="view-btn" @click="openApprovalDetails({originalData: framework})">
                  <i class="fas fa-eye"></i> View
          </button>
                <button class="edit-btn" @click="openRejectedItem(framework)">
                  <i class="fas fa-edit"></i> Edit
          </button>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>

    <!-- Edit Modal for Rejected Framework -->
    <div v-if="showEditModal && editingFramework" class="edit-framework-modal">
      <div class="edit-framework-content">
        <h3>Edit & Resubmit Framework: {{ getFrameworkId(editingFramework) }}</h3>
        <button class="close-btn" @click="closeEditModal">Close</button>
        
        <!-- Framework fields -->
        <div>
          <label>Framework Name:</label>
          <input v-model="editingFramework.ExtractedData.FrameworkName" />
          </div>
        <div>
          <label>Framework Description:</label>
          <textarea v-model="editingFramework.ExtractedData.FrameworkDescription"></textarea>
            </div>
        <div>
          <label>Category:</label>
          <input v-model="editingFramework.ExtractedData.Category" />
          </div>
        <div>
          <label>Effective Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.EffectiveDate" />
        </div>
        <div>
          <label>Start Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.StartDate" />
        </div>
        <div>
          <label>End Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.EndDate" />
        </div>

        <!-- Show rejection reason -->
        <div v-if="editingFramework.rejection_reason">
          <label>Rejection Reason:</label>
          <div class="rejection-reason">{{ editingFramework.rejection_reason }}</div>
        </div>
        
        <!-- Edit Policies -->
        <div v-if="editingFramework.ExtractedData.policies" class="edit-policies-section">
          <h4>Edit Policies</h4>
          <div v-for="(policy, policyIndex) in editingFramework.ExtractedData.policies" :key="policyIndex" class="edit-policy-item">
            <h5>{{ policy.PolicyName }}</h5>
            <div class="form-row">
              <div class="form-group">
                <label>Policy Name:</label>
                <input v-model="policy.PolicyName" />
              </div>
              <div class="form-group">
                <label>Description:</label>
                <textarea v-model="policy.PolicyDescription"></textarea>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Objective:</label>
                <textarea v-model="policy.Objective"></textarea>
              </div>
              <div class="form-group">
                <label>Scope:</label>
                <textarea v-model="policy.Scope"></textarea>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Policy Type:</label>
                <select v-model="policy.PolicyType" class="form-control" @change="handlePolicyTypeChange(policy)">
                  <option value="">Select Type</option>
                  <option v-for="type in policyTypeOptions" :key="type" :value="type">{{ type }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Policy Category:</label>
                <select v-model="policy.PolicyCategory" class="form-control" @change="handlePolicyCategoryChange(policy)">
                  <option value="">Select Category</option>
                  <option v-for="category in filteredPolicyCategories(policy.PolicyType)" :key="category" :value="category">{{ category }}</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Policy Sub Category:</label>
                <select v-model="policy.PolicySubCategory" class="form-control">
                  <option value="">Select Sub Category</option>
                  <option v-for="subCategory in filteredPolicySubCategories(policy.PolicyType, policy.PolicyCategory)" :key="subCategory" :value="subCategory">{{ subCategory }}</option>
                </select>
              </div>
          </div>
        
            <!-- Edit Subpolicies -->
            <div v-if="policy.subpolicies" class="edit-subpolicies-section">
              <h6>Edit Sub-Policies</h6>
              <div v-for="(subpolicy, subIndex) in policy.subpolicies" :key="subIndex" class="edit-subpolicy-item">
                <div class="form-row">
                  <div class="form-group">
                    <label>Sub-Policy Name:</label>
                    <input v-model="subpolicy.SubPolicyName" />
            </div>
                  <div class="form-group">
                    <label>Description:</label>
                    <textarea v-model="subpolicy.Description"></textarea>
          </div>
        </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Control:</label>
                    <textarea v-model="subpolicy.Control"></textarea>
      </div>
                  <div class="form-group">
                    <label>Identifier:</label>
                    <input v-model="subpolicy.Identifier" />
    </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <button class="resubmit-btn" @click="resubmitFramework(editingFramework)">Resubmit for Review</button>
      </div>
    </div>

    <!-- Popup Modal -->
    <PopupModal />
  </div>
</template>

<script>
import axios from 'axios'
import { PopupService } from '@/modules/popus/popupService'
import PopupModal from '@/modules/popus/PopupModal.vue'
import CollapsibleTable from '@/components/CollapsibleTable.vue'

export default {
  name: 'FrameworkApprover',
  components: {
    PopupModal,
    CollapsibleTable
  },
  data() {
    return {
      approvals: [],
      selectedApproval: null,
      showFrameworkDetails: false,
      showRejectModal: false,
      rejectionComment: '',
      currentRejectionType: 'framework',
      currentRejectionItem: null,
      rejectedFrameworks: [],
      showEditModal: false,
      editingFramework: null,
      // User management - updated from hardcoded values
      currentUserId: null,
      selectedUserId: null,
      isGRCAdministrator: false,
      availableUsers: [],
      userInitialized: false,
      isReviewer: true,
      policyCategories: [],
      policyCategoriesMap: {},
      expandedSections: {
        'Under Review': true,
        'Approved': true,
        'Rejected': true
      },
      tableHeaders: [
        { key: 'id', label: 'Framework ID', sortable: true, width: '150px' },
        { key: 'name', label: 'Name', sortable: true },
        { key: 'category', label: 'Category', sortable: true },
        { key: 'createdBy', label: 'Created By', sortable: true },
        { key: 'createdDate', label: 'Created Date', sortable: true },
        { key: 'status', label: 'Status', sortable: true },
        { key: 'actions', label: 'Actions', width: '120px' }
      ],
      rejectedSortConfig: {
        key: 'CreatedByDate',
        direction: 'desc'
      },
      activeTab: 'myTasks'
    }
  },
  mounted() {
    this.initializeUser();
  },
  methods: {
    // Initialize user and check role
    async initializeUser() {
      try {
        console.log('Initializing user and checking role...');
        
        // Get current user role
        const response = await axios.get('http://localhost:8000/api/user-role/');
        console.log('User role API response:', response.data);
        
        if (response.data.success) {
          this.currentUserId = response.data.user_id;
          
          // Check specifically for "GRC Administrator" role
          const userRole = response.data.role;
          console.log('User role received:', userRole);
          
          // Only GRC Administrator should see the user dropdown
          this.isGRCAdministrator = userRole === 'GRC Administrator';
          
          console.log('Is GRC Administrator:', this.isGRCAdministrator);
          
          if (this.isGRCAdministrator) {
            console.log('User is GRC Administrator, fetching all users for dropdown...');
            // Fetch all users for dropdown
            await this.fetchUsers();
            
            // Don't set selectedUserId initially for administrators - let them choose
            this.selectedUserId = null;
          } else {
            console.log('User is not GRC Administrator, setting selected user to current user');
            // Set selected user to current user for non-administrators
            this.selectedUserId = this.currentUserId;
            
            // Load frameworks for the current user
    this.fetchFrameworks();
    this.fetchRejectedFrameworks();
          }
          
          this.userInitialized = true;
    this.fetchPolicyTypes();
        } else {
          console.error('User role API did not return success:', response.data);
          // Fallback for development/testing
          console.log('Using fallback user role for testing...');
          this.currentUserId = 2; // Default user ID
          this.isGRCAdministrator = false; // Default to non-administrator
          this.selectedUserId = this.currentUserId;
          this.userInitialized = true;
          
          // Load frameworks for the current user
          this.fetchFrameworks();
          this.fetchRejectedFrameworks();
          this.fetchPolicyTypes();
        }
      } catch (error) {
        console.error('Error initializing user:', error);
        // Fallback for development/testing
        console.log('Using fallback user role due to error...');
        this.currentUserId = 2; // Default user ID
        this.isGRCAdministrator = false; // Default to non-administrator  
        this.selectedUserId = this.currentUserId;
        this.userInitialized = true;
        
        // Load frameworks for the current user
        this.fetchFrameworks();
        this.fetchRejectedFrameworks();
        this.fetchPolicyTypes();
      }
    },

    // Fetch all users for administrator dropdown
    async fetchUsers() {
      try {
        console.log('Fetching users for dropdown...');
        const response = await axios.get('http://localhost:8000/api/users-for-dropdown/');
        console.log('Users API response:', response.data);
        
        if (Array.isArray(response.data)) {
          this.availableUsers = response.data;
        } else if (response.data && response.data.success && Array.isArray(response.data.data)) {
          this.availableUsers = response.data.data;
        } else {
          this.availableUsers = response.data || [];
        }
        
        console.log('Available users loaded:', this.availableUsers.length, 'users');
        
        // If no users found, show error
        if (this.availableUsers.length === 0) {
          console.error('No users found in database');
          alert('Error: No users found. Please contact administrator.');
        }
      } catch (error) {
        console.error('Error fetching users:', error);
        this.availableUsers = [];
        alert('Error: Could not load users list. Please contact administrator.');
      }
    },

    // Handle user selection change
    onUserSelectionChange() {
      console.log('User selection changed to:', this.selectedUserId);
      if (this.selectedUserId) {
        // Fetch frameworks for the selected user
        this.fetchFrameworks();
        this.fetchRejectedFrameworks();
      } else {
        // Clear frameworks if no user selected
        this.approvals = [];
        this.rejectedFrameworks = [];
      }
    },

    fetchFrameworks() {
      console.log('Fetching frameworks...');
      
      // Determine which user ID to use for API calls
      const userIdForAPI = this.selectedUserId || this.currentUserId;
      console.log('Using user ID for API:', userIdForAPI);
      
      if (!userIdForAPI) {
        console.warn('No user ID available for fetching frameworks');
        return;
      }
      
      // Fetch all frameworks for approval workflow (including Under Review)
      const params = { 
        include_all_status: true,
        // Add user filter if not GRC Administrator or if specific user selected
        ...((!this.isGRCAdministrator || this.selectedUserId) && { user_id: userIdForAPI })
      };
      
      axios.get('http://localhost:8000/api/frameworks/', { params })
        .then(response => {
          console.log('Frameworks response:', response.data);
          this.approvals = response.data.map(framework => {
            // Get latest version for framework
            let frameworkVersion = framework.CurrentVersion?.toString() || 'u1';
            
            return {
              FrameworkId: framework.FrameworkId,
              ExtractedData: {
                type: 'framework',
                FrameworkName: framework.FrameworkName,
                CreatedByName: framework.CreatedByName,
                CreatedByDate: framework.CreatedByDate,
                Category: framework.Category,
                Status: framework.Status,
                FrameworkDescription: framework.FrameworkDescription,
                EffectiveDate: framework.EffectiveDate,
                StartDate: framework.StartDate,
                EndDate: framework.EndDate,
                Identifier: framework.Identifier,
                DocURL: framework.DocURL,
                Reviewer: framework.Reviewer,
                InternalExternal: framework.InternalExternal
              },
              ApprovedNot: framework.Status === 'Approved' ? true : 
                          framework.Status === 'Rejected' ? false : null,
              version: frameworkVersion
            };
          })
          // Filter to show only frameworks that need approval or are in review
          .filter(framework => 
            framework.ExtractedData.Status === 'Under Review' || 
            framework.ExtractedData.Status === 'Approved' ||
            framework.ExtractedData.Status === 'Rejected'
          );
          console.log('Processed frameworks for approval:', this.approvals);
        })
        .catch(error => {
          console.error('Error fetching frameworks:', error);
        });
    },
    
    openApprovalDetails(task) {
      const framework = task.originalData; // Get the original framework data
      if (!framework) return;

      // If clicking the same framework, toggle the details
      if (this.selectedApproval && this.selectedApproval.FrameworkId === framework.FrameworkId) {
        this.showFrameworkDetails = !this.showFrameworkDetails;
        if (!this.showFrameworkDetails) {
          this.selectedApproval = null;
        }
        return;
      }

      // Get the framework ID
      const frameworkId = this.getFrameworkId(framework);

      // For pending frameworks, use the framework data directly
      if (framework.ApprovedNot === null) {
        // Create initial framework data structure
        const frameworkData = {
          ...framework,
          ExtractedData: {
            ...framework.ExtractedData,
            FrameworkName: framework.ExtractedData.FrameworkName || '',
            CreatedByName: framework.ExtractedData.CreatedByName || '',
            CreatedByDate: framework.ExtractedData.CreatedByDate || '',
            Category: framework.ExtractedData.Category || '',
            Status: 'Under Review',
            FrameworkDescription: framework.ExtractedData.FrameworkDescription || '',
            EffectiveDate: framework.ExtractedData.EffectiveDate || '',
            StartDate: framework.ExtractedData.StartDate || '',
            EndDate: framework.ExtractedData.EndDate || '',
            Identifier: framework.ExtractedData.Identifier || '',
            DocURL: framework.ExtractedData.DocURL || '',
            Reviewer: framework.ExtractedData.Reviewer || '',
            InternalExternal: framework.ExtractedData.InternalExternal || 'Internal',
            policies: []
          }
        };

        this.selectedApproval = frameworkData;
        this.showFrameworkDetails = true;

        // First fetch framework policies
        axios.get(`http://localhost:8000/api/frameworks/${frameworkId}/get-policies/`)
          .then(response => {
            console.log('Framework policies:', response.data);
            if (response.data) {
              // Update policies with status
              const policies = response.data.map(policy => ({
                ...policy,
                Status: policy.Status || 'Under Review',
                subpolicies: []
              }));

              // Update the framework data with policies
              this.selectedApproval.ExtractedData.policies = policies;

              // For each policy, fetch its subpolicies
              const subpolicyPromises = policies.map(policy => 
                axios.get(`http://localhost:8000/api/policies/${policy.PolicyId}/get-subpolicies/`)
                  .then(subResponse => {
                    console.log(`Subpolicies for policy ${policy.PolicyId}:`, subResponse.data);
                    if (subResponse.data) {
                      // Find the policy and update its subpolicies
                      const policyToUpdate = this.selectedApproval.ExtractedData.policies.find(p => p.PolicyId === policy.PolicyId);
                      if (policyToUpdate) {
                        policyToUpdate.subpolicies = subResponse.data.map(sub => ({
                          ...sub,
                          Status: sub.Status || 'Under Review'
                        }));
                        console.log(`Updated policy ${policy.PolicyId} with ${subResponse.data.length} subpolicies`);
                      }
                    }
                  })
                  .catch(error => {
                    console.error(`Error fetching subpolicies for policy ${policy.PolicyId}:`, error);
                  })
              );

              // Wait for all subpolicy requests to complete
              Promise.all(subpolicyPromises)
                .then(() => {
                  console.log('All policies and subpolicies loaded');
                })
                .catch(error => {
                  console.error('Error loading some subpolicies:', error);
                });
            }
          })
          .catch(error => {
            console.error('Error fetching policies:', error);
            PopupService.error('Error loading policies. Please try again.', 'Loading Error');
          });
          return;
        }

      // For approved/rejected frameworks, use the existing approval endpoint
      axios.get(`http://localhost:8000/api/framework-approvals/latest/${frameworkId}/`)
        .then(approvalResponse => {
          console.log('Latest framework approval:', approvalResponse.data);
          
          if (approvalResponse.data && approvalResponse.data.ExtractedData) {
            const latestApproval = approvalResponse.data;
            
            const updatedApproval = {
              ...framework,
              ...latestApproval,
              ExtractedData: latestApproval.ExtractedData
            };
            
            // Update status consistency
            if (updatedApproval.ApprovedNot === true && updatedApproval.ExtractedData) {
              if (updatedApproval.ExtractedData.Status === 'Approved') {
                if (updatedApproval.ExtractedData.policies) {
                  updatedApproval.ExtractedData.policies.forEach(policy => {
                    if (policy.Status !== 'Approved') {
                      policy.Status = 'Approved';
                    }
                    
                    if (policy.subpolicies) {
                      policy.subpolicies.forEach(subpolicy => {
                        if (subpolicy.Status !== 'Approved') {
                          subpolicy.Status = 'Approved';
                        }
                      });
                    }
                  });
                }
              }
            }
            
            this.selectedApproval = updatedApproval;
            this.showFrameworkDetails = true;
            
            // Scroll to top of modal when opened
            this.$nextTick(() => {
              if (this.$refs.frameworkDetailsContent) {
                this.$refs.frameworkDetailsContent.scrollTop = 0;
              }
            });
          } else {
            console.error('Invalid approval data received:', approvalResponse.data);
            PopupService.error('Error: Could not load framework approval details', 'Loading Error');
          }
        })
        .catch(error => {
          this.handleError(error, 'loading framework approval details');
        });
    },
    
    refreshData() {
      this.fetchFrameworks();
      
      if (this.selectedApproval && this.selectedApproval.FrameworkId) {
        this.openApprovalDetails(this.selectedApproval);
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return ''; // Invalid date
      
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    isNewFramework(framework) {
      const createdDate = framework.ExtractedData?.CreatedByDate || framework.created_at;
      if (!createdDate) return false;
      
      const date = new Date(createdDate);
      if (isNaN(date.getTime())) return false; // Invalid date
      
      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3); // Show new badge for 3 days
      
      return date > threeDaysAgo;
    },
    
    getFrameworkId(framework) {
      if (framework.FrameworkId) {
        return typeof framework.FrameworkId === 'object' ? framework.FrameworkId.FrameworkId : framework.FrameworkId;
      }
      return framework.ApprovalId;
    },
    
    closeApprovalDetails() {
      this.selectedApproval = null;
      this.showFrameworkDetails = false;
    },
    
    approveFramework() {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for approval');
          return;
        }

      // Initialize framework approval if doesn't exist
      if (!this.selectedApproval.ExtractedData.framework_approval) {
        this.selectedApproval.ExtractedData.framework_approval = {};
      }
      this.selectedApproval.ExtractedData.framework_approval.approved = true;
      this.selectedApproval.ExtractedData.framework_approval.remarks = '';
      
      // Update the overall approval status
      this.selectedApproval.ApprovedNot = true;
      this.selectedApproval.ExtractedData.Status = 'Approved';
    },
    
    rejectFramework() {
      this.currentRejectionType = 'framework';
      this.currentRejectionItem = null;
      this.showRejectModal = true;
    },
    
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectionComment = '';
      this.currentRejectionType = 'framework';
      this.currentRejectionItem = null;
    },
    
    confirmRejection() {
      if (!this.rejectionComment.trim()) {
        PopupService.warning('Please provide a rejection reason', 'Missing Reason');
        return;
      }

      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      if (this.currentRejectionType === 'subpolicy' && this.currentRejectionItem) {
        const { policy, subpolicy } = this.currentRejectionItem;
        
        // Call backend endpoint for subpolicy rejection
        axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/policies/${policy.PolicyId}/subpolicies/${subpolicy.SubPolicyId}/approve-reject/`, {
            approved: false,
          rejection_reason: this.rejectionComment,
          submit_review: true // Add flag to submit review automatically
        })
          .then(response => {
            console.log('Subpolicy rejected successfully:', response.data);

          // Update local state
            subpolicy.Status = 'Rejected';
            policy.Status = 'Rejected';
            if (policy.subpolicies) {
              policy.subpolicies.forEach(sp => {
                sp.Status = 'Rejected';
              });
            }
            this.selectedApproval.ExtractedData.Status = 'Rejected';
            this.selectedApproval.ApprovedNot = false;
            
            PopupService.success('Subpolicy rejected. Framework has been rejected and sent back for revision.', 'Subpolicy Rejected');
            this.cancelRejection();
            this.fetchFrameworks();
            this.fetchRejectedFrameworks();
            this.closeApprovalDetails(); // Close the details modal
          })
          .catch(error => {
            this.handleError(error, 'rejecting subpolicy');
          });
          
      } else if (this.currentRejectionType === 'policy' && this.currentRejectionItem) {
        const policy = this.currentRejectionItem;
        
        // Call backend endpoint for policy rejection
        axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/policies/${policy.PolicyId}/approve-reject/`, {
          approved: false,
          rejection_reason: this.rejectionComment,
          submit_review: true // Add flag to submit review automatically
        })
          .then(response => {
            console.log('Policy rejected successfully:', response.data);

          // Update local state
            policy.Status = 'Rejected';
            if (policy.subpolicies) {
              policy.subpolicies.forEach(subpolicy => {
                subpolicy.Status = 'Rejected';
              });
            }
            this.selectedApproval.ExtractedData.Status = 'Rejected';
            this.selectedApproval.ApprovedNot = false;
            
            PopupService.success('Policy rejected. Framework has been rejected and sent back for revision.', 'Policy Rejected');
            this.cancelRejection();
            this.fetchFrameworks();
            this.fetchRejectedFrameworks();
            this.closeApprovalDetails(); // Close the details modal
          })
          .catch(error => {
            this.handleError(error, 'rejecting policy');
          });
          
      } else if (this.currentRejectionType === 'framework') {
        // For direct framework rejection, use submitFrameworkReview with rejection reason
        if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
          console.error('No framework selected for rejection');
          this.cancelRejection();
            return;
          }
        
        // Initialize framework approval if doesn't exist
        if (!this.selectedApproval.ExtractedData.framework_approval) {
          this.selectedApproval.ExtractedData.framework_approval = {};
        }
        
        // Update the framework status and approval state in the UI
        this.selectedApproval.ExtractedData.framework_approval.approved = false;
        this.selectedApproval.ExtractedData.framework_approval.remarks = this.rejectionComment;
        this.selectedApproval.ExtractedData.Status = 'Rejected';
        this.selectedApproval.ApprovedNot = false;
        
        // Submit the review with rejection data
        this.submitFrameworkReview(false, this.rejectionComment);
        
        this.cancelRejection();
      }
    },
    
    // Helper method to handle and display errors
    handleError(error, context) {
      console.error(`Error ${context}:`, error);
      let errorMessage = 'An unexpected error occurred';
      
      if (error.response) {
        // The server responded with a status code outside of 2xx range
        if (error.response.data && error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data && typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else {
          errorMessage = `Server error: ${error.response.status}`;
        }
      } else if (error.request) {
        // The request was made but no response was received
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        // Something happened in setting up the request
        errorMessage = error.message || errorMessage;
      }
      
      PopupService.error(`Error ${context}: ${errorMessage}`, 'Error');
      return errorMessage;
    },
    
    // Helper method to submit framework review
    submitFrameworkReview(approved, remarks = '') {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for review submission');
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      console.log(`Submitting framework review for framework ${frameworkId}`, {
        approved: approved,
        remarks: remarks
      });
      
      // Create the framework review data
      const reviewData = {
        ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
        ApprovedNot: approved,
        remarks: remarks,
        UserId: this.currentUserId,
        ReviewerId: this.currentUserId,
        currentVersion: this.selectedApproval.version || 'u1'
      };
      
      // If approving, set all policies and subpolicies to Approved status
      if (approved === true && reviewData.ExtractedData.policies) {
        reviewData.ExtractedData.policies.forEach(policy => {
          policy.Status = 'Approved';
          policy.ActiveInactive = 'Active'; // Set policies to Active when framework is approved
          
              if (policy.subpolicies) {
            policy.subpolicies.forEach(subpolicy => {
              subpolicy.Status = 'Approved';
            });
              }
            });
          }

      // Set framework ActiveInactive to Active when approved
      if (approved === true) {
        reviewData.ExtractedData.ActiveInactive = 'Active';
      }
      
      // If rejecting, ensure framework_approval contains rejection remarks
      if (approved === false && remarks) {
        if (!reviewData.ExtractedData.framework_approval) {
          reviewData.ExtractedData.framework_approval = {};
        }
        reviewData.ExtractedData.framework_approval.remarks = remarks;
      }
      
      // Submit framework review
      axios.post(`http://localhost:8000/api/frameworks/${frameworkId}/submit-review/`, reviewData)
        .then(response => {
          console.log('Framework review submitted successfully:', response.data);
          
          // Update the approval data with the response
          this.selectedApproval.ApprovedNot = approved;
          this.selectedApproval.Version = response.data.Version;
          
          if (approved) {
            this.selectedApproval.ExtractedData.Status = 'Approved';
            
            // Store the approval date from the response
            if (response.data.ApprovedDate) {
              this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
            }
            
            // Update all policies and subpolicies to Approved status in the UI
            if (this.selectedApproval.ExtractedData.policies) {
              this.selectedApproval.ExtractedData.policies.forEach(policy => {
                policy.Status = 'Approved';
                
                if (policy.subpolicies) {
                  policy.subpolicies.forEach(subpolicy => {
                    subpolicy.Status = 'Approved';
                  });
                }
              });
            }
            
            PopupService.success('Framework approved successfully!', 'Framework Approved');
      } else {
            this.selectedApproval.ExtractedData.Status = 'Rejected';
            PopupService.success('Framework rejected successfully!', 'Framework Rejected');
          }
          
          // Refresh the frameworks list
          this.fetchFrameworks();
        })
        .catch(error => {
          this.handleError(error, 'submitting framework review');
        });
    },
    
    fetchRejectedFrameworks() {
      console.log('Fetching rejected frameworks...');
      
      // Determine which user ID to use for API calls
      const userIdForAPI = this.selectedUserId || this.currentUserId;
      console.log('Using user ID for rejected frameworks:', userIdForAPI);
      
      if (!userIdForAPI) {
        console.warn('No user ID available for fetching rejected frameworks');
        return;
      }
      
      // Use the selected user ID or current user ID for fetching rejected frameworks
      axios.get(`http://localhost:8000/api/frameworks/rejected/`, {
        params: { user_id: userIdForAPI }
      })
        .then(response => {
          console.log('Rejected frameworks response:', response.data);
          this.rejectedFrameworks = response.data.map(framework => {
            // Make sure framework data is properly structured
            if (!framework.ExtractedData) {
              framework.ExtractedData = {};
            }
            return framework;
          });
        })
        .catch(error => {
          console.error('Error fetching rejected frameworks:', error);
        });
    },
    
    openRejectedItem(framework) {
      console.log('Opening rejected framework for editing:', framework);
      this.editingFramework = JSON.parse(JSON.stringify(framework)); // Deep copy
      
      // Ensure the framework has the proper structure for editing
      if (!this.editingFramework.ExtractedData) {
        this.editingFramework.ExtractedData = {};
      }
      
      // Ensure policies array exists
      if (!this.editingFramework.ExtractedData.policies) {
        console.warn('No policies found in rejected framework, initializing empty policies array');
        this.editingFramework.ExtractedData.policies = [];
        } else {
        console.log(`Found ${this.editingFramework.ExtractedData.policies.length} policies in framework`);
        
        // Process each policy
        this.editingFramework.ExtractedData.policies.forEach(policy => {
          // Initialize policy category fields if they don't exist
          if (!policy.PolicyType) policy.PolicyType = '';
          if (!policy.PolicyCategory) policy.PolicyCategory = '';
          if (!policy.PolicySubCategory) policy.PolicySubCategory = '';
          
          console.log(`Policy ${policy.PolicyId} category fields:`, {
            PolicyType: policy.PolicyType,
            PolicyCategory: policy.PolicyCategory,
            PolicySubCategory: policy.PolicySubCategory
          });
          
          // Ensure each policy has subpolicies array
          if (!policy.subpolicies) {
            policy.subpolicies = [];
          }
        });
      }
      
      this.showEditModal = true;
    },
    
    closeEditModal() {
      this.showEditModal = false;
      this.editingFramework = null;
    },
    
    resubmitFramework(framework) {
      const frameworkId = this.getFrameworkId(framework);
      console.log('Resubmitting framework with ID:', frameworkId);
      console.log('Framework data before preparing:', framework);
      
      // Validate framework data
      const validationErrors = this.validateFrameworkData(framework);
      if (validationErrors.length > 0) {
        PopupService.warning(`Please fix the following errors before resubmitting:\n${validationErrors.join('\n')}`, 'Validation Errors');
        return;
      }
      
      // Check if policies exist and have proper structure
      if (framework.ExtractedData.policies && framework.ExtractedData.policies.length > 0) {
        // Ensure each policy has the correct fields
        framework.ExtractedData.policies.forEach((policy, index) => {
          console.log(`Checking policy ${index} with ID: ${policy.PolicyId}`);
          console.log(`Policy category fields:`, {
            PolicyType: policy.PolicyType,
            PolicyCategory: policy.PolicyCategory,
            PolicySubCategory: policy.PolicySubCategory
          });
          
          // Ensure subpolicies are properly formatted
          if (policy.subpolicies && policy.subpolicies.length > 0) {
            policy.subpolicies.forEach((subpolicy, subIndex) => {
              console.log(`Checking subpolicy ${subIndex} with ID: ${subpolicy.SubPolicyId}`);
              
              // Make sure required fields exist
              if (!subpolicy.SubPolicyName) {
                console.warn(`SubpolicyName is missing for subpolicy ${subIndex} in policy ${index}`);
              }
              if (!subpolicy.Description) {
                console.warn(`Description is missing for subpolicy ${subIndex} in policy ${index}`);
              }
            });
      } else {
            console.log(`Policy ${index} has no subpolicies or they are not properly structured`);
          }
        });
      } else {
        console.warn('No policies found in framework data or policies array is not properly structured');
      }
      
      // Prepare data for resubmission
      const resubmitData = {
        FrameworkName: framework.ExtractedData.FrameworkName,
        FrameworkDescription: framework.ExtractedData.FrameworkDescription,
        Category: framework.ExtractedData.Category,
        EffectiveDate: framework.ExtractedData.EffectiveDate,
        StartDate: framework.ExtractedData.StartDate,
        EndDate: framework.ExtractedData.EndDate,
        policies: framework.ExtractedData.policies ? framework.ExtractedData.policies.map(policy => {
          // Log each policy's category fields before mapping
          console.log(`Processing policy ${policy.PolicyId} for resubmission with category fields:`, {
            PolicyType: policy.PolicyType,
            PolicyCategory: policy.PolicyCategory,
            PolicySubCategory: policy.PolicySubCategory
          });
          
          // Ensure all policy fields are included, especially the category fields
          const mappedPolicy = {
            ...policy,
            PolicyId: policy.PolicyId,
            PolicyName: policy.PolicyName,
            PolicyDescription: policy.PolicyDescription,
            Status: policy.Status,
            StartDate: policy.StartDate,
            EndDate: policy.EndDate,
            Department: policy.Department,
            Objective: policy.Objective,
            Scope: policy.Scope,
            Applicability: policy.Applicability,
            Identifier: policy.Identifier,
            CoverageRate: policy.CoverageRate,
            // Explicitly include category fields with fallbacks
            PolicyType: policy.PolicyType || '',
            PolicyCategory: policy.PolicyCategory || '',
            PolicySubCategory: policy.PolicySubCategory || '',
            subpolicies: policy.subpolicies || []
          };
          
          return mappedPolicy;
        }) : []
      };
      
      console.log('Prepared resubmission data:', resubmitData);
      console.log('Policies in resubmission data:', resubmitData.policies);
      console.log('Number of policies:', resubmitData.policies.length);
      
      // Submit resubmission request
      console.log('Final resubmission data to be sent:', JSON.stringify(resubmitData));
      
      // Add explicit logging for policy category fields
      if (resubmitData.policies && resubmitData.policies.length > 0) {
        console.log('CRITICAL - Policy category fields in final resubmission data:');
        resubmitData.policies.forEach((policy, index) => {
          // Ensure policy category fields are properly set (not undefined)
          policy.PolicyType = policy.PolicyType || '';
          policy.PolicyCategory = policy.PolicyCategory || '';
          policy.PolicySubCategory = policy.PolicySubCategory || '';
          
          console.log(`Policy ${index} (${policy.PolicyId}):`, {
            PolicyType: policy.PolicyType,
            PolicyCategory: policy.PolicyCategory,
            PolicySubCategory: policy.PolicySubCategory
          });
        });
      }
      
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/resubmit-approval/`, resubmitData)
        .then(response => {
          console.log('Framework resubmitted successfully:', response.data);
          
          // Show version information in the alert
          PopupService.success(`Framework resubmitted for review! New version: ${response.data.Version}`, 'Framework Resubmitted');
          
          this.closeEditModal();
          this.fetchRejectedFrameworks();
          this.fetchFrameworks();
        })
        .catch(error => {
          console.error('Error data:', error.response ? error.response.data : 'No response data');
          this.handleError(error, 'resubmitting framework');
        });
    },
    
    formatFieldName(field) {
      // Convert camelCase or PascalCase to display format
      return field
        // Insert space before all uppercase letters
        .replace(/([A-Z])/g, ' $1')
        // Replace first char with uppercase
        .replace(/^./, str => str.toUpperCase())
        .trim();
    },
    
    approvePolicy(policy) {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for policy approval');
        return;
      }

      // Check if all subpolicies are approved
      if (policy.subpolicies && policy.subpolicies.length > 0) {
        const allSubpoliciesApproved = policy.subpolicies.every(sub => sub.Status === 'Approved');
        if (!allSubpoliciesApproved) {
          PopupService.warning('All subpolicies must be approved before approving the policy', 'Subpolicies Not Approved');
          return;
        }
      }

      const frameworkId = this.getFrameworkId(this.selectedApproval);

      // Call backend endpoint
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/policies/${policy.PolicyId}/approve-reject/`, {
        approved: true,
        submit_review: false // Don't submit review automatically
      })
        .then(response => {
          console.log('Policy approved successfully:', response.data);

          // Update policy status
          policy.Status = 'Approved';

          // Check if all policies are approved to update framework status
          const allPoliciesApproved = this.selectedApproval.ExtractedData.policies.every(p => 
            p.Status === 'Approved' || (p.subpolicies && p.subpolicies.every(sub => sub.Status === 'Approved'))
          );

          if (allPoliciesApproved) {
            this.selectedApproval.ExtractedData.Status = 'Ready for Final Approval';
          }

          PopupService.success('Policy approved successfully!', 'Policy Approved');
        })
        .catch(error => {
          this.handleError(error, 'approving policy');
        });
    },
    
    rejectPolicy(policy) {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for policy rejection');
        return;
      }
      
      this.currentRejectionType = 'policy';
      this.currentRejectionItem = policy;
      this.showRejectModal = true;
    },
    
    rejectSubpolicy(policy, subpolicy) {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for subpolicy rejection');
        return;
      }
      
      this.currentRejectionType = 'subpolicy';
      this.currentRejectionItem = { policy, subpolicy };
      this.showRejectModal = true;
    },
    
    canApprovePolicy(policy) {
      // Can't approve if already approved or rejected
      if (policy.Status === 'Approved' || policy.Status === 'Rejected') {
        return false;
      }

      // If policy has subpolicies, all must be approved
      if (policy.subpolicies && policy.subpolicies.length > 0) {
        return policy.subpolicies.every(sub => sub.Status === 'Approved');
      }

      // If no subpolicies, can approve
      return true;
    },
    
    approveSubpolicy(policy, subpolicy) {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for subpolicy approval');
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      // Call backend endpoint
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/policies/${policy.PolicyId}/subpolicies/${subpolicy.SubPolicyId}/approve-reject/`, {
          approved: true,
        submit_review: false // Don't submit review automatically
      })
        .then(response => {
          console.log('Subpolicy approved successfully:', response.data);
          
          // Update subpolicy status
          subpolicy.Status = 'Approved';
          
          // Check if all subpolicies in this policy are approved
          const allSubpoliciesApproved = policy.subpolicies && 
            policy.subpolicies.every(sp => sp.Status === 'Approved');
          
          if (allSubpoliciesApproved) {
            // Update policy status to indicate it's ready for approval
            policy.Status = 'Ready for Approval';
            PopupService.success('All subpolicies approved. Policy is now ready for approval.', 'Subpolicies Approved');
          } else {
            PopupService.success('Subpolicy approved successfully!', 'Subpolicy Approved');
          }
        })
        .catch(error => {
          this.handleError(error, 'approving subpolicy');
        });
    },
    
    areAllSubpoliciesApproved(policy) {
      if (!policy.subpolicies || policy.subpolicies.length === 0) return true;
      return policy.subpolicies.every(subpolicy => subpolicy.Status === 'Approved');
    },
    
    areAllPoliciesApproved() {
      if (!this.selectedApproval?.ExtractedData?.policies) return false;
      
      return this.selectedApproval.ExtractedData.policies.every(policy => {
        // Check policy status
        if (policy.Status !== 'Approved') {
          // If not approved, check if all subpolicies are approved
          return policy.subpolicies && policy.subpolicies.every(sub => sub.Status === 'Approved');
        }
        return true;
      });
    },
    
    getFrameworkApprovalStatus() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return 'Unknown';
      
      const policies = this.selectedApproval.ExtractedData.policies || [];
      if (policies.length === 0) return 'No Policies';
      
      const approvedCount = policies.filter(p => p.Status === 'Approved').length;
      const rejectedCount = policies.filter(p => p.Status === 'Rejected').length;
      const totalCount = policies.length;
      
      if (rejectedCount > 0) {
        return `Rejected (${rejectedCount}/${totalCount} policies rejected)`;
      } else if (approvedCount === totalCount) {
        return `Ready for Final Approval (${approvedCount}/${totalCount} policies approved)`;
      } else {
        return `Under Review (${approvedCount}/${totalCount} policies approved)`;
      }
    },
    
    canApproveFramework() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return false;
      if (this.selectedApproval.ApprovedNot !== null) return false; // Already approved/rejected
      
      // Check if all policies are approved
      return this.areAllPoliciesApproved();
    },
    
    approveEntireFramework() {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for entire framework approval');
        return;
      }
      
      if (!this.canApproveFramework()) {
        PopupService.warning('All policies must be approved before approving the framework', 'Policies Not Approved');
        return;
      }
      
      PopupService.confirm(
        'Are you sure you want to give final approval to this entire framework?',
        'Confirm Final Approval',
        () => {
          this.proceedWithFrameworkApproval();
        }
      );
    },
    
    proceedWithFrameworkApproval() {
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      // Call backend endpoint for final framework approval
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/approve-final/`)
        .then(response => {
          console.log('Framework approved successfully:', response.data);
          
          // Update framework status and store approval date
          this.selectedApproval.ExtractedData.Status = 'Approved';
          this.selectedApproval.ApprovedNot = true;
          
          // Store the approval date from the response
          if (response.data.ApprovedDate) {
            this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
          }
          
          // Update all policies and subpolicies to Approved status
          if (this.selectedApproval.ExtractedData.policies) {
            this.selectedApproval.ExtractedData.policies.forEach(policy => {
              policy.Status = 'Approved';
              
              if (policy.subpolicies) {
                policy.subpolicies.forEach(subpolicy => {
                  subpolicy.Status = 'Approved';
                });
              }
            });
          }
          
          PopupService.success('Framework approved successfully!', 'Framework Approved');
          
          // Refresh the frameworks list
          this.fetchFrameworks();
        })
        .catch(error => {
          this.handleError(error, 'approving entire framework');
        });
    },
    
    // Update the existing submitReview method to use our helper method
    submitReview() {
      console.log('submitReview called with approval:', this.selectedApproval);
      if (this.selectedApproval && this.selectedApproval.ApprovedNot !== null) {
        console.log('Delegating to submitFrameworkReview with approval status:', this.selectedApproval.ApprovedNot);
        this.submitFrameworkReview(this.selectedApproval.ApprovedNot);
      } else {
        console.error('Cannot submit review - no approval or approval status set');
      }
    },
    
    // Helper method to validate framework data before submission
    validateFrameworkData(framework) {
      const validationErrors = [];
      
      // Check required framework fields
      if (!framework.ExtractedData.FrameworkName) {
        validationErrors.push('Framework Name is required');
      }
      
      if (!framework.ExtractedData.FrameworkDescription) {
        validationErrors.push('Framework Description is required');
      }
      
      // Check policies if they exist
      if (framework.ExtractedData.policies && framework.ExtractedData.policies.length > 0) {
        framework.ExtractedData.policies.forEach((policy, index) => {
          if (!policy.PolicyName) {
            validationErrors.push(`Policy #${index + 1} is missing a name`);
          }
          
          // Log policy category fields to help with debugging
          console.log(`Validating policy #${index + 1} category fields:`, {
            PolicyType: policy.PolicyType,
            PolicyCategory: policy.PolicyCategory,
            PolicySubCategory: policy.PolicySubCategory
          });
          
          // Check subpolicies if they exist
          if (policy.subpolicies && policy.subpolicies.length > 0) {
            policy.subpolicies.forEach((subpolicy, subIndex) => {
              if (!subpolicy.SubPolicyName) {
                validationErrors.push(`Subpolicy #${subIndex + 1} in Policy "${policy.PolicyName || `#${index + 1}`}" is missing a name`);
              }
            });
          }
        });
      }
      
      return validationErrors;
    },
    
    fetchPolicyTypes() {
      console.log('Fetching policy categories...');
      axios.get('http://localhost:8000/api/policy-categories/')
        .then(response => {
          console.log('Policy categories response:', response.data);
          // Store the raw categories data
          this.policyCategories = response.data;
          
          // Create a structured map for easier filtering
          const typeMap = {};
          
          // Process the categories into a nested structure
          response.data.forEach(category => {
            if (!typeMap[category.PolicyType]) {
              typeMap[category.PolicyType] = {
                categories: {}
              };
            }
            
            if (!typeMap[category.PolicyType].categories[category.PolicyCategory]) {
              typeMap[category.PolicyType].categories[category.PolicyCategory] = {
                subCategories: []
              };
            }
            
            typeMap[category.PolicyType].categories[category.PolicyCategory].subCategories.push(
              category.PolicySubCategory
            );
          });
          
          this.policyCategoriesMap = typeMap;
          console.log('Processed policy categories map:', this.policyCategoriesMap);
        })
        .catch(error => {
          console.error('Error fetching policy categories:', error);
        });
    },
    
    // Helper method to initialize or update policy category fields
    initializePolicyCategoryFields(policy) {
      console.log(`Initializing policy category fields for policy: ${policy.PolicyId || 'New Policy'}`);
      
      // Log current values
      console.log('Current policy category fields:', {
        PolicyType: policy.PolicyType,
        PolicyCategory: policy.PolicyCategory,
        PolicySubCategory: policy.PolicySubCategory
      });
      
      // If policy type changes, reset category and subcategory
      this.$watch(() => policy.PolicyType, (newType, oldType) => {
        if (newType !== oldType) {
          console.log(`Policy type changed from ${oldType} to ${newType}, resetting category and subcategory`);
          policy.PolicyCategory = '';
          policy.PolicySubCategory = '';
        }
      });
      
      // If policy category changes, reset subcategory
      this.$watch(() => policy.PolicyCategory, (newCategory, oldCategory) => {
        if (newCategory !== oldCategory) {
          console.log(`Policy category changed from ${oldCategory} to ${newCategory}, resetting subcategory`);
          policy.PolicySubCategory = '';
        }
      });
      
      return policy;
    },
    
    // Handle policy type change
    handlePolicyTypeChange(policy) {
      console.log(`Policy type changed to: ${policy.PolicyType}`);
      // Reset dependent fields when type changes
      policy.PolicyCategory = '';
      policy.PolicySubCategory = '';
    },
    
    // Handle policy category change
    handlePolicyCategoryChange(policy) {
      console.log(`Policy category changed to: ${policy.PolicyCategory}`);
      // Reset subcategory when category changes
      policy.PolicySubCategory = '';
    },

    // Add new methods for CollapsibleTable
    toggleSection(sectionName) {
      this.expandedSections[sectionName] = !this.expandedSections[sectionName];
    },
    mapFrameworkToTableRow(framework) {
    return {
        id: this.getFrameworkId(framework),
        name: framework.ExtractedData.FrameworkName,
        category: framework.ExtractedData.Category || 'No Category',
        createdBy: framework.ExtractedData.CreatedByName || 'System',
        createdDate: this.formatDate(framework.ExtractedData.CreatedByDate || framework.created_at),
        status: this.getStatusBadge(framework),
        actions: 'VIEW DETAILS',
        // Store original framework data for reference
        originalData: framework
      };
    },
    getStatusBadge(framework) {
      const status = framework.ApprovedNot === true ? 'Approved' :
                    framework.ApprovedNot === false ? 'Rejected' : 'Pending';
      return `<span class="status-badge ${status.toLowerCase()}">${status}</span>`;
    },
    sortRejected(key) {
      if (this.rejectedSortConfig.key === key) {
        this.rejectedSortConfig.direction = 
          this.rejectedSortConfig.direction === 'asc' ? 'desc' : 'asc';
      } else {
        this.rejectedSortConfig.key = key;
        this.rejectedSortConfig.direction = 'asc';
      }
    },
    
    checkPolicyApprovalStatus(policy) {
      if (!policy.subpolicies || policy.subpolicies.length === 0) return;
      
      const allSubpoliciesApproved = policy.subpolicies.every(sub => sub.Status === 'Approved');
      if (allSubpoliciesApproved) {
        policy.Status = 'Approved';
      }
    },
    
    getStatusClass(status) {
      return {
        'status-approved': status === 'Approved',
        'status-rejected': status === 'Rejected',
        'status-pending': status === 'Under Review' || !status
      };
    },

    // Helper method to check if framework belongs to current user's tasks
    isMyFramework(framework) {
      const currentUserId = this.selectedUserId || this.currentUserId;
      if (!currentUserId) return false;
      
      // Check if framework was created by the current user
      // This might need adjustment based on how user info is stored in frameworks
      return framework.ExtractedData.CreatedBy === currentUserId ||
             framework.ExtractedData.CreatedByName === this.getCurrentUserName();
    },

    // Helper method to check if framework is assigned for review
    isReviewerFramework(framework) {
      const currentUserId = this.selectedUserId || this.currentUserId;
      if (!currentUserId) return false;
      
      // For GRC Administrators, show all frameworks as reviewer tasks
      if (this.isGRCAdministrator) {
        return true;
      }
      
      // For regular users, show frameworks assigned to them for review
      return framework.ExtractedData.Reviewer === currentUserId ||
             framework.ExtractedData.ReviewerName === this.getCurrentUserName() ||
             (this.isReviewer && framework.ApprovedNot === null); // Pending approval
    },

    // Helper method to get current user name
    getCurrentUserName() {
      if (this.selectedUserId && this.availableUsers.length > 0) {
        const selectedUser = this.availableUsers.find(u => u.UserId === this.selectedUserId);
        return selectedUser ? selectedUser.UserName : '';
      }
      // For current user, we might need to fetch this separately or store it during initialization
      return localStorage.getItem('user_name') || '';
    },

    // Get frameworks for My Tasks
    getMyTasksFrameworks() {
      if (!this.userInitialized) {
        return [];
      }

      if (this.isGRCAdministrator && !this.selectedUserId) {
        return [];
      }

      // For both GRC Administrators (viewing selected user) and regular users
      return this.approvals.filter(f => {
        return this.isMyFramework(f);
      });
    },

    // Get frameworks for Reviewer Tasks
    getReviewerTasksFrameworks() {
      if (!this.userInitialized) {
        return [];
      }

      if (this.isGRCAdministrator && !this.selectedUserId) {
        return [];
      }

      // For both GRC Administrators (viewing selected user) and regular users
      return this.approvals.filter(f => {
        return this.isReviewerFramework(f) && !this.isMyFramework(f);
      });
    },
  },
  computed: {
    pendingApprovalsCount() {
      return this.approvals.filter(a => a.ApprovedNot === null).length;
    },
    approvedApprovalsCount() {
      return this.approvals.filter(a => a.ApprovedNot === true).length;
    },
    rejectedApprovalsCount() {
      return this.approvals.filter(a => a.ApprovedNot === false).length;
    },
    sortedFrameworks() {
      return [...this.approvals].sort((a, b) => {
        const dateA = new Date(a.ExtractedData?.CreatedByDate || 0);
        const dateB = new Date(b.ExtractedData?.CreatedByDate || 0);
        return dateB - dateA; // Most recent first
      });
    },
    policyTypeOptions() {
      // Get unique policy types from the structured map
      return Object.keys(this.policyCategoriesMap);
    },
    filteredPolicyCategories() {
      return (policyType) => {
        if (!policyType || !this.policyCategoriesMap[policyType]) return [];
        // Get categories for the selected policy type
        return Object.keys(this.policyCategoriesMap[policyType].categories);
      };
    },
    filteredPolicySubCategories() {
      return (policyType, policyCategory) => {
        if (!policyType || !policyCategory || 
            !this.policyCategoriesMap[policyType] || 
            !this.policyCategoriesMap[policyType].categories[policyCategory]) {
          return [];
        }
        // Get subcategories for the selected policy type and category
        return this.policyCategoriesMap[policyType].categories[policyCategory].subCategories;
      };
    },
    sortedRejectedFrameworks() {
      return [...this.rejectedFrameworks].sort((a, b) => {
        const key = this.rejectedSortConfig.key;
        let aValue = key.includes('.') ? 
          key.split('.').reduce((obj, k) => obj?.[k], a) : 
          a[key];
        let bValue = key.includes('.') ? 
          key.split('.').reduce((obj, k) => obj?.[k], b) : 
          b[key];
        
        // Handle dates
        if (key === 'CreatedByDate') {
          aValue = new Date(aValue || 0);
          bValue = new Date(bValue || 0);
        }
        
        // Handle strings
        if (typeof aValue === 'string') {
          aValue = aValue.toLowerCase();
          bValue = bValue.toLowerCase();
        }
        
        if (this.rejectedSortConfig.direction === 'asc') {
          return aValue > bValue ? 1 : -1;
        } else {
          return aValue < bValue ? 1 : -1;
        }
      });
    },
    myTasksSections() {
      const myTasksFrameworks = this.getMyTasksFrameworks();
      const sections = [
        {
          name: 'Under Review',
          statusClass: 'pending',
          tasks: myTasksFrameworks
            .filter(f => f.ApprovedNot === null)
            .map(this.mapFrameworkToTableRow)
        },
        {
          name: 'Approved',
          statusClass: 'approved',
          tasks: myTasksFrameworks
            .filter(f => f.ApprovedNot === true)
            .map(this.mapFrameworkToTableRow)
        },
        {
          name: 'Rejected',
          statusClass: 'rejected',
          tasks: myTasksFrameworks
            .filter(f => f.ApprovedNot === false)
            .map(this.mapFrameworkToTableRow)
        }
      ];
      return sections;
    },
    reviewerTasksSections() {
      const reviewerTasksFrameworks = this.getReviewerTasksFrameworks();
      const sections = [
        {
          name: 'Under Review',
          statusClass: 'pending',
          tasks: reviewerTasksFrameworks
            .filter(f => f.ApprovedNot === null)
            .map(this.mapFrameworkToTableRow)
        },
        {
          name: 'Approved',
          statusClass: 'approved',
          tasks: reviewerTasksFrameworks
            .filter(f => f.ApprovedNot === true)
            .map(this.mapFrameworkToTableRow)
        },
        {
          name: 'Rejected',
          statusClass: 'rejected',
          tasks: reviewerTasksFrameworks
            .filter(f => f.ApprovedNot === false)
            .map(this.mapFrameworkToTableRow)
        }
      ];
      return sections;
    },
    myTasksCount() {
      return this.getMyTasksFrameworks().length;
    },
    reviewerTasksCount() {
      return this.getReviewerTasksFrameworks().length;
    }
  }
}
</script>

<style scoped>
@import './FrameworkApprover.css';

/* User Selection Dropdown Styles */
.dashboard-controls {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.user-selection-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.user-select-label {
  font-weight: 500;
  color: #495057;
  margin: 0;
  white-space: nowrap;
}

.user-select-dropdown {
  padding: 6px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
  min-width: 200px;
  cursor: pointer;
}

.user-select-dropdown:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.user-select-dropdown option {
  padding: 8px;
}

/* Info Cards Styles */
.no-user-selected-message,
.loading-message {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  margin: 2rem 0;
}

.info-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  max-width: 500px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.info-card i {
  font-size: 3rem;
  color: #6c757d;
  margin-bottom: 1rem;
}

.info-card h3 {
  color: #495057;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.info-card p {
  color: #6c757d;
  margin-bottom: 0;
  line-height: 1.5;
}

.info-card .fa-spinner {
  color: #007bff;
}

/* Add new styles for table integration */
.frameworks-table-container {
  margin-top: 2rem;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  display: inline-block;
}

.status-badge.pending {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.approved {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.rejected {
  background-color: #fee2e2;
  color: #991b1b;
}

/* Add new styles for rejected frameworks table */
.rejected-approvals-section {
  margin-top: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.table-container {
  overflow-x: auto;
  margin-top: 1rem;
}

.frameworks-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.frameworks-table th {
  background: #f8f9fa;
  padding: 12px 16px;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  cursor: pointer;
  user-select: none;
}

.frameworks-table th i {
  margin-left: 4px;
  font-size: 0.75rem;
  color: #9ca3af;
}

.frameworks-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  color: #1f2937;
}

.framework-id-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}

.framework-id-link:hover {
  text-decoration: underline;
}

.actions-cell {
  white-space: nowrap;
}

.view-btn, .edit-btn {
  padding: 6px 12px;
  margin: 0 4px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.view-btn {
  background: #e5e7eb;
  color: #374151;
}

.edit-btn {
  background: #3b82f6;
  color: white;
}

.view-btn:hover {
  background: #d1d5db;
}

.edit-btn:hover {
  background: #2563eb;
}

.status-badge.rejected {
  background-color: #fee2e2;
  color: #991b1b;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Add/update styles for subpolicy actions */
.subpolicy-actions {
  display: flex;
  gap: 8px;
  margin-left: 12px;
}

.approve-subpolicy-btn,
.reject-subpolicy-btn {
  padding: 6px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  transition: all 0.2s ease;
}

.approve-subpolicy-btn {
  background-color: #22c55e;
  color: white;
}

.reject-subpolicy-btn {
  background-color: #ef4444;
  color: white;
}

.approve-subpolicy-btn:hover:not(:disabled) {
  background-color: #16a34a;
}

.reject-subpolicy-btn:hover:not(:disabled) {
  background-color: #dc2626;
}

.approve-subpolicy-btn:disabled,
.reject-subpolicy-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.subpolicy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 4px 4px 0 0;
}

.subpolicy-header-actions {
  display: flex;
  align-items: center;
}

.subpolicy-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.subpolicy-status.status-approved {
  background-color: #dcfce7;
  color: #166534;
}

.subpolicy-status.status-rejected {
  background-color: #fee2e2;
  color: #991b1b;
}

.subpolicy-status.status-pending {
  background-color: #fef3c7;
  color: #92400e;
}

.subpolicy-item {
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  margin-bottom: 12px;
}

.subpolicy-details {
  padding: 12px;
  background-color: white;
  border-radius: 0 0 4px 4px;
}

.subpolicy-detail-item {
  margin-bottom: 8px;
}

.subpolicy-detail-item:last-child {
  margin-bottom: 0;
}

/* Tab Navigation Styles */
.tab-navigation {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e9ecef;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
  padding: 0;
}

.tab-button {
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  color: #6c757d;
  cursor: pointer;
  padding: 1rem 2rem;
  transition: all 0.3s ease;
  border-radius: 8px 8px 0 0;
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.tab-button:hover {
  background: #e9ecef;
  color: #495057;
}

.tab-button.active {
  background: #fff;
  color: #2563eb;
  border-bottom: 3px solid #2563eb;
  margin-bottom: -2px;
}

.tab-button i {
  font-size: 0.9rem;
}

/* Tab Content Styles */
.tab-content {
  background: #fff;
  border-radius: 0 0 8px 8px;
  min-height: 400px;
}

.tab-panel {
  padding: 1.5rem;
}
</style> 