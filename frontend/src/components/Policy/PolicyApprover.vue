<template>
  <!-- Only show main content if reject modal is NOT open -->
  <div v-if="!showRejectModal">
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h2 class="dashboard-heading">Policy Approver</h2>
        <div class="dashboard-actions">
          <!-- Add user dropdown for GRC Administrators -->
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
          <button class="action-btn" @click="refreshData"><i class="fas fa-sync-alt"></i></button>
          <button class="action-btn"><i class="fas fa-download"></i></button>
        </div>
      </div>



      <!-- Performance Summary Cards for Policy Approver -->
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

      <!-- Add tabs for My Tasks and Reviewer Tasks -->
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
        
      <!-- Tab Content -->
      <div class="tab-content">
        <!-- My Tasks Tab -->
        <div v-if="activeTab === 'myTasks'" class="approvals-list">
          <h3>
            My Approval Tasks
            <span v-if="selectedUserInfo && isAdministrator" class="user-info-badge">
              (Viewing: {{ selectedUserInfo.UserName }})
            </span>
          </h3>
          
          <!-- Collapsible Table for My Tasks -->
          <div class="collapsible-table-container">
            <CollapsibleTable
              v-for="section in myTasksCollapsibleSections"
              :key="section.name"
              :section-config="section"
              :table-headers="tableHeaders"
              :is-expanded="expandedSections[section.name.toLowerCase()]"
              :pagination="section.pagination"
              @toggle="toggleSection(section.name)"
              @task-click="handleTaskClick"
            />
      </div>

          <!-- Empty state when no tasks -->
          <div v-if="myTasksCollapsibleSections.length === 0" class="no-tasks-message">
            <div class="no-tasks-icon">
              <i class="fas fa-clipboard-check"></i>
            </div>
            <h4>No My Tasks</h4>
            <p>{{ selectedUserInfo && isAdministrator ? `${selectedUserInfo.UserName} doesn't have` : 'You don\'t have' }} any tasks at the moment.</p>
          </div>
        </div>

        <!-- Reviewer Tasks Tab -->
        <div v-if="activeTab === 'reviewerTasks'" class="approvals-list">
          <h3>
            Reviewer Tasks
            <span v-if="selectedUserInfo && isAdministrator" class="user-info-badge">
              (Viewing: {{ selectedUserInfo.UserName }})
            </span>
          </h3>
        
          <!-- Collapsible Table for Reviewer Tasks -->
        <div class="collapsible-table-container">
          <CollapsibleTable
              v-for="section in reviewerTasksCollapsibleSections"
            :key="section.name"
            :section-config="section"
            :table-headers="tableHeaders"
            :is-expanded="expandedSections[section.name.toLowerCase()]"
            :pagination="section.pagination"
            @toggle="toggleSection(section.name)"
            @task-click="handleTaskClick"
          />
        </div>
        
        <!-- Empty state when no tasks -->
          <div v-if="reviewerTasksCollapsibleSections.length === 0" class="no-tasks-message">
          <div class="no-tasks-icon">
            <i class="fas fa-clipboard-check"></i>
          </div>
            <h4>No Reviewer Tasks</h4>
            <p>{{ selectedUserInfo && isAdministrator ? `${selectedUserInfo.UserName} doesn't have` : 'You don\'t have' }} any reviewer tasks at the moment.</p>
          </div>
        </div>
      </div>

      <!-- Policy/Compliance Details Modal/Section -->
      <div v-if="showDetails && selectedApproval && !showRejectModal" class="policy-details-modal-overlay">
        <div class="policy-details-modal">
          <div class="policy-details-content">
            <!-- Show different header based on user type -->
            <h3 v-if="isUserViewingReviewHistory">
              <span class="detail-type-indicator">
                <i class="fas fa-clock"></i>
                Review Status
              </span>
              {{ getPolicyId(selectedApproval) }}
              <span class="status-pill" :class="getPolicyStatusClass(selectedApproval)">
                {{ getApprovalStatus(selectedApproval) === 'pending' ? 'Under Review' : 
                   getApprovalStatus(selectedApproval) === 'approved' ? 'Approved' : 'Rejected' }}
              </span>
            </h3>
            
            <!-- Regular details header for reviewers -->
            <h3 v-else>
              <span class="detail-type-indicator">
                {{ isComplianceApproval ? 'Compliance' : 'Policy' }}
              </span>
              Details: {{ getPolicyId(selectedApproval) }}
              <span class="version-pill">Version: {{ selectedApproval.version || 'u1' }}</span>
              <span v-if="selectedApproval.showingApprovedOnly" class="approved-only-badge">
                Showing Approved Only
              </span>
            </h3>

            <!-- 2. Version history section -->
            <div class="version-history" v-if="selectedApproval.ExtractedData">
              <div class="version-info">
                <div class="version-label">Current Version:</div>
                <div class="version-value">{{ selectedApproval.version || 'u1' }}</div>
              </div>
              <div v-if="selectedApproval.ExtractedData.subpolicies && selectedApproval.ExtractedData.subpolicies.length > 0" 
                   class="subpolicies-versions">
                <h4>Subpolicies Versions:</h4>
                <ul class="version-list">
                  <li v-for="sub in selectedApproval.ExtractedData.subpolicies" :key="sub.SubPolicyId">
                    <span class="subpolicy-name">{{ sub.SubPolicyName }}</span>
                    <span class="version-tag">v{{ sub.version || 'u1' }}</span>
                    <span v-if="sub.resubmitted" class="resubmitted-tag">Resubmitted</span>
                  </li>
                </ul>
              </div>
            </div>
            
            <button class="close-btn" @click="closeApprovalDetails">Close</button>
            
            <!-- Show different content based on user type -->
            <div v-if="isUserViewingReviewHistory" class="review-status-section">
              <h4><i class="fas fa-clock"></i> Review Status</h4>
              
              <!-- Policy status indicator -->
              <div class="policy-status-indicator">
                <span class="status-label">Current Status:</span>
                <span class="status-value" :class="getPolicyStatusClass(selectedApproval)">
                  {{ getApprovalStatus(selectedApproval) === 'pending' ? 'Under Review' : 
                     getApprovalStatus(selectedApproval) === 'approved' ? 'Approved' : 'Rejected' }}
                </span>
              </div>
              
              <!-- Review progress message -->
              <div class="review-progress-message">
                <div class="progress-icon">
                  <i class="fas fa-info-circle"></i>
                </div>
                <div class="progress-text">
                  <p><strong>Your policy is currently under review.</strong></p>
                  <p>The reviewer will either approve or reject your policy. Once a decision is made, you'll receive a notification with the outcome.</p>
                  <p>Click the <strong>"View Review History"</strong> button below to see detailed review progress and any reviewer actions.</p>
                </div>
              </div>
              
              <!-- Action button to view full review history -->
              <div class="review-action-section">
                <button class="review-history-btn" @click="showReviewHistory(getPolicyId(selectedApproval), selectedApproval.ExtractedData?.PolicyName || getPolicyId(selectedApproval), getApprovalStatus(selectedApproval))">
                  <i class="fas fa-history"></i>
                  View Review History
                </button>
              </div>
            </div>
            
            <!-- Regular Policy/Compliance Approval Section for reviewers -->
            <div v-else class="policy-approval-section">
              <h4>{{ isComplianceApproval ? 'Compliance' : 'Policy' }} Approval</h4>
              
              <!-- Add policy status indicator -->
              <div class="policy-status-indicator">
                <span class="status-label">Status:</span>
                <span class="status-value" :class="{
                  'status-approved': selectedApproval.dbStatus === 'Approved' || selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved',
                  'status-rejected': selectedApproval.dbStatus === 'Rejected' || selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected',
                  'status-pending': !(['Approved', 'Rejected'].includes(selectedApproval.dbStatus)) && selectedApproval.ApprovedNot === null && !(['Approved', 'Rejected'].includes(selectedApproval.ExtractedData?.Status))
                }">
                  {{ selectedApproval.dbStatus === 'Approved' || selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved' ? 'Approved' : 
                     selectedApproval.dbStatus === 'Rejected' || selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected' ? 'Rejected' : 
                     'Under Review' }}
                </span>
              </div>
              
              <div class="policy-actions">
                <button class="submit-btn" @click="submitReview()" data-action="submit-policy-review">
                  <i class="fas fa-paper-plane"></i> Submit Review
                </button>
              </div>
              
              <!-- Add this section to show policy approval status - hide when already showing in the indicator -->
              <div v-if="approvalStatus && 
                        !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved') && 
                        !(selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected')" 
                   class="policy-approval-status">
                <div class="status-container">
                  <div class="status-label">Status:</div>
                  <div class="status-value" :class="{
                    'approved': approvalStatus.approved === true,
                    'rejected': approvalStatus.approved === false,
                    'pending': approvalStatus.approved === null
                  }">
                    {{ approvalStatus.approved === true ? 'Approved' : 
                       approvalStatus.approved === false ? 'Rejected' : 'Pending' }}
                  </div>
                </div>
                
                <!-- Show approved date if approved -->
                <div v-if="approvalStatus.approved === true && selectedApproval.ApprovedDate" class="policy-approved-date">
                  <div class="date-label">Approved Date:</div>
                  <div class="date-value">{{ formatDate(selectedApproval.ApprovedDate) }}</div>
                </div>
                
                <!-- Show remarks if rejected -->
                <div v-if="approvalStatus.approved === false && 
                          approvalStatus.remarks" class="policy-rejection-remarks">
                  <div class="remarks-label">Rejection Reason:</div>
                  <div class="remarks-value">{{ approvalStatus.remarks }}</div>
                </div>
              </div>
            </div>
            
            <!-- Display details based on type -->
            <div v-if="selectedApproval.ExtractedData">
              <!-- For compliance approvals -->
              <div v-if="isComplianceApproval" class="compliance-details">
                <div class="compliance-detail-row">
                  <strong>Description:</strong> <span>{{ selectedApproval.ExtractedData.ComplianceItemDescription }}</span>
                </div>
                <div class="compliance-detail-row">
                  <strong>Criticality:</strong> <span>{{ selectedApproval.ExtractedData.Criticality }}</span>
                </div>
                <div class="compliance-detail-row">
                  <strong>Impact:</strong> <span>{{ selectedApproval.ExtractedData.Impact }}</span>
                </div>
                <div class="compliance-detail-row">
                  <strong>Probability:</strong> <span>{{ selectedApproval.ExtractedData.Probability }}</span>
                </div>
                <div class="compliance-detail-row">
                  <strong>Mitigation:</strong> <span>{{ selectedApproval.ExtractedData.mitigation }}</span>
                </div>
                <div class="policy-actions">
                  <button class="approve-btn" @click="approveCompliance()">Approve</button>
                  <button class="reject-btn" @click="rejectCompliance()">Reject</button>
                </div>
              </div>
              
              <!-- For policy approvals (existing code) -->
              <div v-else v-for="(value, key) in selectedApproval.ExtractedData" :key="key" class="policy-detail-row">
                <template v-if="key !== 'subpolicies' && key !== 'policy_approval'">
                  <strong>{{ key }}:</strong> <span>{{ value }}</span>
                </template>
                
                <!-- Subpolicies Section -->
                <template v-if="key === 'subpolicies' && Array.isArray(value)">
                  <h4>Subpolicies</h4>
                  <ul v-if="value && value.length">
                    <li v-for="sub in value" :key="sub.Identifier" class="subpolicy-status">
                      <div>
                        <span class="subpolicy-id">{{ sub.Identifier }}</span> :
                        <span class="subpolicy-name">{{ sub.SubPolicyName }}</span>
                        <span class="item-type-badge subpolicy-badge">Subpolicy</span>
                        <span
                          class="badge"
                          :class="{
                            approved: sub.approval?.approved === true || (selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'),
                            rejected: sub.approval?.approved === false && !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'),
                            pending: sub.approval?.approved === null && !sub.resubmitted && !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'),
                            resubmitted: sub.approval?.approved === null && sub.resubmitted && !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved')
                          }"
                        >
                          {{
                            (sub.approval?.approved === true || (selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'))
                              ? 'Approved'
                              : sub.approval?.approved === false
                              ? 'Rejected'
                              : sub.resubmitted
                              ? 'Resubmitted'
                              : 'Pending'
                          }}
                        </span>
                      </div>
                      <div><strong>Description:</strong> {{ sub.Description }}</div>
                      <div><strong>Control:</strong> {{ sub.Control }}</div>
                      <div v-if="sub.approval?.approved === false">
                        <strong>Reason:</strong> {{ sub.approval?.remarks }}
                      </div>
                      <!-- Add these buttons inside the subpolicies view, under the approval buttons -->
                      <div class="subpolicy-actions">
                        <template v-if="isReviewer">
                          <!-- Show approve/reject buttons for reviewer -->
                          <button 
                            v-if="sub.Status === 'Under Review' || !sub.Status"
                            @click="approveSubpolicy(sub)" 
                            class="approve-button"
                          >
                            Approve
                          </button>
                          <button 
                            v-if="sub.Status === 'Under Review' || !sub.Status"
                            @click="rejectSubpolicy(sub)" 
                            class="reject-button"
                          >
                            Reject
                          </button>
                        </template>
                        
                        <!-- For users (not reviewers), add edit button for rejected subpolicies -->
                        <template v-else>
                          <button 
                            v-if="sub.Status === 'Rejected'"
                            @click="openEditSubpolicyModal(sub)" 
                            class="edit-button"
                          >
                            Edit & Resubmit
                          </button>
                        </template>
                      </div>
                    </li>
                  </ul>
                </template>
              </div>
            </div>

            <!-- Add this inside the policy-details-content div -->
            <div v-if="selectedApproval && selectedApproval.PolicyId" class="policy-detail-row">
              <strong>Policy ID:</strong> <span>{{ getPolicyId(selectedApproval) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Rejected Policies & Compliances List -->
      <div class="rejected-approvals-list" v-if="rejectedPolicies.length">
        <h3>Rejected Policies & Compliances (Edit & Resubmit)</h3>
        
        <!-- Dynamic Table for Rejected Policies -->
        <DynamicTable
          :data="rejectedTableData"
          :columns="rejectedTableColumns"
          :filters="rejectedTableFilters"
          :show-actions="true"
          :show-pagination="true"
          :default-page-size="10"
          :page-size-options="[5, 10, 20, 50]"
          unique-key="id"
          @row-select="handleRejectedPolicyAction"
        >
          <!-- Custom Actions Slot -->
          <template #actions="{ row }">
            <button 
              class="edit-action-btn" 
              @click="handleRejectedPolicyAction(row)"
              :title="`Edit & Resubmit ${row.type}`"
            >
              <i class="fas fa-edit"></i>
              Edit
            </button>
          </template>
        </DynamicTable>
        
        <!-- Empty state when no rejected policies -->
        <div v-if="rejectedTableData.length === 0" class="no-rejected-items">
          <div class="no-items-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <h4>No Rejected Items</h4>
          <p>All policies and compliances have been approved or are pending review.</p>
        </div>
      </div>

      <!-- Edit Modal for Rejected Compliance -->
      <div v-if="showEditComplianceModal && editingCompliance" class="edit-policy-modal">
        <div class="edit-policy-content">
          <h3>Edit & Resubmit Compliance: {{ getPolicyId(editingCompliance) }}</h3>
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
            <label>Impact:</label>
            <input v-model="editingCompliance.ExtractedData.Impact" />
          </div>
          <div>
            <label>Probability:</label>
            <input v-model="editingCompliance.ExtractedData.Probability" />
          </div>
          <div>
            <label>Mitigation:</label>
            <textarea v-model="editingCompliance.ExtractedData.mitigation"></textarea>
          </div>
          <!-- Show rejection reason -->
          <div>
            <label>Rejection Reason:</label>
            <div class="rejection-reason">{{ editingCompliance.ExtractedData.compliance_approval?.remarks }}</div>
          </div>
          
          <button class="resubmit-btn" @click="resubmitCompliance(editingCompliance)">Resubmit for Review</button>
        </div>
      </div>

      <!-- Edit Modal for Rejected Policy -->
      <div v-if="showEditModal && editingPolicy" class="edit-policy-modal">
        <div class="edit-policy-content">
          <h3>Edit & Resubmit Policy: {{ getPolicyId(editingPolicy) }}</h3>
          <button class="close-btn" @click="closeEditModal">Close</button>
          
          <!-- Show policy rejection reason if it exists -->
          <div v-if="editingPolicy.ExtractedData.rejection_reason || editingPolicy.rejectionReason" class="rejection-reason-container">
            <div class="rejection-reason-header">
              <i class="fas fa-exclamation-triangle"></i> Policy Rejection Reason
            </div>
            <div class="rejection-reason-content">
              {{ editingPolicy.ExtractedData.rejection_reason || editingPolicy.rejectionReason || 'No rejection reason provided' }}
            </div>
          </div>
          
          <!-- Main policy fields -->
          <div>
            <label>Scope:</label>
            <input v-model="editingPolicy.ExtractedData.Scope" />
          </div>
          <div>
            <label>Objective:</label>
            <input v-model="editingPolicy.ExtractedData.Objective" />
          </div>
          
          <!-- Policy Category fields -->
          <div>
            <label>Policy Type:</label>
            <select v-model="editingPolicy.ExtractedData.PolicyType" class="form-control" @change="handlePolicyTypeChange(editingPolicy)">
              <option value="">Select Type</option>
              <option v-for="type in policyTypeOptions" :key="type" :value="type">{{ type }}</option>
            </select>
          </div>
          <div>
            <label>Policy Category:</label>
            <select v-model="editingPolicy.ExtractedData.PolicyCategory" class="form-control" @change="handlePolicyCategoryChange(editingPolicy)">
              <option value="">Select Category</option>
              <option v-for="category in filteredPolicyCategories(editingPolicy.ExtractedData.PolicyType)" :key="category" :value="category">{{ category }}</option>
            </select>
          </div>
          <div>
            <label>Policy Sub Category:</label>
            <select v-model="editingPolicy.ExtractedData.PolicySubCategory" class="form-control">
              <option value="">Select Sub Category</option>
              <option v-for="subCategory in filteredPolicySubCategories(editingPolicy.ExtractedData.PolicyType, editingPolicy.ExtractedData.PolicyCategory)" :key="subCategory" :value="subCategory">{{ subCategory }}</option>
            </select>
          </div>
          
          <!-- Rejected Subpolicies Section -->
          <div class="edit-subpolicy-section" v-if="hasRejectedSubpolicies">
            <h4>Rejected Subpolicies</h4>
            
            <div v-for="sub in rejectedSubpoliciesInPolicy" :key="sub.Identifier" class="subpolicy-edit-item">
              <div class="subpolicy-edit-header">
                <span>{{ sub.Identifier }}: {{ sub.SubPolicyName }}</span>
                <span class="subpolicy-badge">Rejected</span>
              </div>
              
              <div class="subpolicy-edit-field">
                <label>Name:</label>
                <input v-model="sub.SubPolicyName" />
              </div>
              
              <div class="subpolicy-edit-field">
                <label>Description:</label>
                <textarea v-model="sub.Description"></textarea>
              </div>
              
              <div class="subpolicy-edit-field">
                <label>Control:</label>
                <textarea v-model="sub.Control"></textarea>
              </div>
              
              <div class="subpolicy-edit-field">
                <label>Rejection Reason:</label>
                <div class="rejection-reason">{{ sub.approval?.remarks }}</div>
              </div>
            </div>
          </div>
          
          <button class="resubmit-btn" @click="resubmitPolicy(editingPolicy)">Resubmit for Review</button>
        </div>
      </div>

      <!-- Edit Modal for Rejected Subpolicy -->
      <div v-if="showEditSubpolicyModal" class="modal">
        <div class="modal-content edit-modal">
          <span class="close" @click="closeEditSubpolicyModal">&times;</span>
          <h2>Edit Rejected Subpolicy
            <span v-if="editingSubpolicy && (editingSubpolicy.Status === 'Rejected' || editingSubpolicy.approval?.approved === false)" 
                  class="version-tag reviewer-version">
              Version: {{ editingSubpolicy.reviewerVersion || 'R1' }}
            </span>
          </h2>
          <div v-if="editingSubpolicy">
            <div class="form-group">
              <label>Subpolicy Name:</label>
              <input type="text" v-model="editingSubpolicy.SubPolicyName" disabled />
            </div>
            <div class="form-group">
              <label>Identifier:</label>
              <input type="text" v-model="editingSubpolicy.Identifier" disabled />
            </div>
            
            <!-- Add this prominent rejection reason section -->
            <div v-if="editingSubpolicy.approval && editingSubpolicy.approval.remarks" class="rejection-reason-container">
              <div class="rejection-reason-header">
                <i class="fas fa-exclamation-triangle"></i> Rejection Reason
              </div>
              <div class="rejection-reason-content">
                {{ editingSubpolicy.approval.remarks }}
              </div>
            </div>
            
            <div class="form-group">
              <label>Description:</label>
              <textarea v-model="editingSubpolicy.Description" @input="trackChanges"></textarea>
            </div>
            <div class="form-group">
              <label>Control:</label>
              <textarea v-model="editingSubpolicy.Control" @input="trackChanges"></textarea>
            </div>
            
            <div v-if="hasChanges" class="changes-summary">
              <div class="changes-header">
                <i class="fas fa-exclamation-circle"></i> Changes detected
              </div>
              <div class="changes-content">
                <div v-if="editingSubpolicy.Description !== editingSubpolicy.originalDescription" class="change-item">
                  Description has been modified
                </div>
                <div v-if="editingSubpolicy.Control !== editingSubpolicy.originalControl" class="change-item">
                  Control has been modified
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button 
                class="resubmit-btn" 
                @click="resubmitSubpolicy()" 
                :disabled="!hasChanges"
              >
                {{ hasChanges ? 'Resubmit with Changes' : 'Make changes to resubmit' }}
              </button>
              <button class="cancel-btn" @click="closeEditSubpolicyModal">Cancel</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Subpolicies Modal -->
      <div v-if="showSubpoliciesModal && selectedPolicyForSubpolicies">
        <div class="modal-overlay"></div>
        <div class="subpolicies-modal">
          <div class="subpolicies-modal-content">
            <h3>
              <span v-if="isReviewer">Subpolicies for {{ getPolicyId(selectedPolicyForSubpolicies) }}</span>
              <span v-else>Edit Rejected Subpolicies for {{ getPolicyId(selectedPolicyForSubpolicies) }}</span>
              
              <!-- Show appropriate version based on status -->
              <span v-if="selectedPolicyForSubpolicies.ApprovedNot === false || selectedPolicyForSubpolicies.ExtractedData?.Status === 'Rejected'"
                    class="version-pill reviewer-version">
                Version: {{ selectedPolicyForSubpolicies.reviewerVersion || 'R1' }}
              </span>
              <span v-else class="version-pill">
                Version: {{ selectedPolicyForSubpolicies.version || 'u1' }}
              </span>
            </h3>
            <button class="close-btn" @click="closeSubpoliciesModal">Close</button>
            
            <!-- Filter to only show rejected subpolicies in user mode -->
            <div v-for="sub in filteredSubpolicies" :key="sub.Identifier" class="subpolicy-status" :class="{'resubmitted-item': sub.resubmitted}">
              <div class="subpolicy-header">
                <span class="subpolicy-id">{{ sub.Identifier }}</span>
                <span class="subpolicy-name">{{ sub.SubPolicyName }}</span>
                
                <!-- Show R version for rejected items, u version otherwise -->
                <span v-if="sub.Status === 'Rejected' || (sub.approval && sub.approval.approved === false)" 
                      class="version-tag reviewer-version">
                  Version: {{ sub.reviewerVersion || 'R1' }}
                </span>
                <span v-else class="version-tag">
                  Version: {{ sub.version || 'u1' }}
                </span>
              </div>

              <div class="subpolicy-content">
                <div><strong>Description:</strong> {{ sub.Description }}</div>
                <div><strong>Control:</strong> {{ sub.Control }}</div>
                
                <!-- Show rejection reason for rejected items -->
                <div v-if="sub.approval?.approved === false">
                  <strong>Rejection Reason:</strong> {{ sub.approval?.remarks }}
                </div>
                
                <!-- Show edit history for resubmitted items -->
                <div v-if="sub.resubmitted && isReviewer" class="edit-history">
                  <div class="edit-history-header">
                    <i class="fas fa-history"></i> Resubmitted with Changes
                  </div>
                  <div class="edit-history-content">
                    <div class="edit-field">
                      <div v-if="sub.previousVersion">
                        <div class="field-label">Original Description:</div>
                        <div class="field-previous">{{ sub.previousVersion.Description || 'Not available' }}</div>
                      </div>
                      <div class="field-current">
                        <div class="field-label">Updated Description:</div>
                        <div class="field-value">{{ sub.Description }}</div>
                      </div>
                    </div>
                    <div class="edit-field">
                      <div v-if="sub.previousVersion">
                        <div class="field-label">Original Control:</div>
                        <div class="field-previous">{{ sub.previousVersion.Control || 'Not available' }}</div>
                      </div>
                      <div class="field-current">
                        <div class="field-label">Updated Control:</div>
                        <div class="field-value">{{ sub.Control }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Show Approve/Reject buttons if pending and in reviewer mode -->
              <div v-if="isReviewer && (sub.approval?.approved === null || sub.approval?.approved === undefined)" class="subpolicy-actions">
                <button class="approve-btn" @click="approveSubpolicyFromModal(sub)">Approve</button>
                <button class="reject-btn" @click="rejectSubpolicyFromModal(sub)">Reject</button>
              </div>
              
              <!-- Edit form for rejected subpolicies -->
              <div v-if="sub.approval?.approved === false || sub.Status === 'Rejected'">
                <div v-if="sub.showEditForm">
                  <!-- Inline edit form -->
                  <div class="subpolicy-inline-edit">
                    <h4>Edit Rejected Subpolicy
                      <span class="version-tag reviewer-version">Version: {{ sub.reviewerVersion || 'R1' }}</span>
                    </h4>
                    <div>
                      <label>Name:</label>
                      <input v-model="sub.SubPolicyName" disabled />
                    </div>
                    <div>
                      <label>Description:</label>
                      <textarea v-model="sub.Description"></textarea>
                    </div>
                    <div>
                      <label>Control:</label>
                      <textarea v-model="sub.Control"></textarea>
                    </div>
                    <div>
                      <label>Rejection Reason:</label>
                      <div class="rejection-reason">
                        {{ sub.approval && sub.approval.remarks ? sub.approval.remarks : 'No rejection reason provided' }}
                      </div>
                    </div>
                    <div class="subpolicy-edit-actions">
                      <button class="resubmit-btn" @click="resubmitSubpolicyDirect(sub)">Resubmit for Review</button>
                      <button v-if="isReviewer" class="cancel-btn" @click="hideEditFormInline(sub)">Cancel</button>
                    </div>
                  </div>
                </div>
                <button v-else class="edit-btn" @click="showEditFormInline(sub)">Edit & Resubmit</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      

      <!-- Popup Modal -->
      <PopupModal />
    </div>
  </div>

  <!-- Show only the reject modal when open -->
  <div v-if="showRejectModal" class="reject-modal">
    <div class="reject-modal-content">
      <h4>Rejection Reason</h4>
      <p>Please provide a reason for rejecting {{ rejectingType === 'policy' ? 'the policy' : 'subpolicy ' + rejectingSubpolicy?.Identifier }}</p>
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

  <!-- Review History Modal -->
  <ReviewHistoryModal
    v-if="showReviewHistoryModal"
    :policy-id="selectedPolicyId"
    :policy-name="selectedPolicyName"
    :current-status="selectedPolicyStatus"
    @close="closeReviewHistoryModal"
  />
</template>

<script>
import axios from 'axios'
import { PopupService } from '@/modules/popus/popupService'
import PopupModal from '@/modules/popus/PopupModal.vue'
import CollapsibleTable from '@/components/CollapsibleTable.vue'
import DynamicTable from '@/components/DynamicTable.vue'
import ReviewHistoryModal from './ReviewHistoryModal.vue'

export default {
  name: 'PolicyApprover',
  components: {
    PopupModal,
    CollapsibleTable,
    DynamicTable,
    ReviewHistoryModal
  },
  data() {
    return {
      approvals: [],
      selectedApproval: null,
      showDetails: false,
      showRejectModal: false,
      rejectingSubpolicy: null,
      rejectingType: '', // 'policy' or 'subpolicy'
      rejectionComment: '',
      rejectedPolicies: [],
      rejectedSubpolicies: [],
      showEditModal: false,
      editingPolicy: null,
      showEditSubpolicyModal: false,
      editingSubpolicy: null,
      editingSubpolicyParent: null,
      userId: 2, // Default user id
      showSubpoliciesModal: false,
      selectedPolicyForSubpolicies: null,
      showEditComplianceModal: false,
      editingCompliance: null,
      isReviewer: true, // Set based on user role, for testing
      
      // Review History Modal
      showReviewHistoryModal: false,
      selectedPolicyId: null,
      selectedPolicyName: '',
      selectedPolicyStatus: '',
      
      // New RBAC and tab functionality
      activeTab: 'myTasks', // Default to My Tasks tab
      isAdministrator: false, // Will be set based on user role
      availableUsers: [], // List of users for administrator dropdown
      selectedUserId: null, // Currently selected user (for administrators)
      selectedUserInfo: null, // Information about selected user
      currentUserId: 2, // Current logged-in user ID
      myTasks: [], // Tasks assigned to user
      reviewerTasks: [], // Tasks where user is reviewer
      
      policyCategories: [], // Store all policy categories
      policyCategoriesMap: {}, // Structured map of policy categories
      
      // Collapsible Table Data
      tableHeaders: [
        { key: 'policyName', label: 'Policy Name', sortable: true, width: '200px' },
        { key: 'type', label: 'Type', sortable: true, width: '100px' },
        { key: 'scope', label: 'Scope', sortable: true, width: '150px' },
        { key: 'createdBy', label: 'Created By', sortable: true, width: '120px' },
        { key: 'createdDate', label: 'Created Date', sortable: true, width: '120px' },
        { key: 'status', label: 'Status', sortable: true, width: '100px' },
        { key: 'actions', label: 'Actions', sortable: false, width: '120px' }
      ],
      expandedSections: {
        pending: true,
        approved: true,
        rejected: true
      },
      
      // Dynamic Table Data for Rejected Policies
      rejectedTableColumns: [
        { 
          key: 'policyId', 
          label: 'Policy ID', 
          sortable: true, 
          headerStyle: { width: '150px' },
          maxLength: 20
        },
        { 
          key: 'type', 
          label: 'Type', 
          sortable: true, 
          headerStyle: { width: '100px' },
          type: 'status'
        },
        { 
          key: 'description', 
          label: 'Description', 
          sortable: true, 
          headerStyle: { width: '200px' },
          maxLength: 50
        },
        { 
          key: 'rejectionReason', 
          label: 'Rejection Reason', 
          sortable: false, 
          headerStyle: { width: '250px' },
          maxLength: 60
        },
        { 
          key: 'createdDate', 
          label: 'Created Date', 
          sortable: true, 
          headerStyle: { width: '120px' }
        }
      ],
      rejectedTableFilters: [
        {
          name: 'type',
          label: 'Type',
          type: 'dropdown',
          options: [
            { value: 'all', label: 'All Types' },
            { value: 'policy', label: 'Policy' },
            { value: 'subpolicy', label: 'Subpolicy' },
            { value: 'compliance', label: 'Compliance' }
          ],
          defaultValue: 'all',
          filterFunction: (row, value) => {
            if (value === 'all') return true;
            return row.type.toLowerCase() === value.toLowerCase();
          }
        }
      ],
      collapsiblePagination: {
        pending: { currentPage: 1, pageSize: 6 },
        approved: { currentPage: 1, pageSize: 6 },
        rejected: { currentPage: 1, pageSize: 6 }
      }
    }
  },
  mounted() {
    console.log('PolicyApprover component mounted');
    console.log('Initial data state:', {
      isAdministrator: this.isAdministrator,
      currentUserId: this.currentUserId,
      selectedUserId: this.selectedUserId,
      availableUsers: this.availableUsers
    });
    this.initializeUser();
  },
  watch: {
    // Watch for changes in isReviewer and fetch appropriate data
    isReviewer(newVal) {
      if (newVal) {
        // If switched to reviewer mode
        this.fetchPolicies();
        this.fetchRejectedPolicies();
      } else {
        // If switched to user mode
        this.fetchRejectedSubpolicies();
      }
    }
  },
  methods: {
    // Push notification method
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

    // Initialize user and check role
    async initializeUser() {
      try {
        console.log('Initializing user and checking role...');
        
        // Get current user role
        const response = await axios.get('http://localhost:8000/api/api/user-role/');
        console.log('User role API response:', response.data);
        
        if (response.data.success) {
          this.currentUserId = response.data.user_id;
          
          // Check specifically for "GRC Administrator" role
          const userRole = response.data.role;
          console.log('User role received:', userRole);
          
          // Only GRC Administrator should see the user dropdown
          this.isAdministrator = userRole === 'GRC Administrator';
          
          console.log('Is GRC Administrator:', this.isAdministrator);
          
          if (this.isAdministrator) {
            console.log('User is GRC Administrator, fetching all users for dropdown...');
            // Fetch all users for dropdown
            await this.fetchUsers();
            
            // Don't set selectedUserId initially for administrators - let them choose
            this.selectedUserId = null;
          } else {
            console.log('User is not GRC Administrator, setting selected user to current user');
            // Set selected user to current user for non-administrators
            this.selectedUserId = this.currentUserId;
            
            // Load tasks for the current user
            await this.loadUserTasks();
          }
          
          this.fetchRejectedPolicies();
          this.fetchPolicyTypes();
        } else {
          console.error('User role API did not return success:', response.data);
          // Show error message instead of fallback
          alert('Error: Could not determine user role. Please contact administrator.');
          this.sendPushNotification({
            title: 'User Role Error',
            message: 'Could not determine user role. Please contact administrator.',
            category: 'policy',
            priority: 'high',
            user_id: this.currentUserId || 'default_user'
          });
        }
      } catch (error) {
        console.error('Error initializing user:', error);
        
        // Show error message instead of fallback
        alert('Error: Could not initialize user. Please refresh the page and try again.');
        this.sendPushNotification({
          title: 'User Initialization Error',
          message: 'Could not initialize user. Please refresh the page and try again.',
          category: 'policy',
          priority: 'high',
          user_id: this.currentUserId || 'default_user'
        });
      }
    },

    // Fetch all users for administrator dropdown
    async fetchUsers() {
      try {
        console.log('Fetching users for dropdown from RBAC...');
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
        console.log('Users:', this.availableUsers);
        
        // If no users found, show error
        if (this.availableUsers.length === 0) {
          console.error('No users found in RBAC table');
          alert('Error: No users found. Please contact administrator.');
          this.sendPushNotification({
            title: 'No Users Found',
            message: 'No users found in RBAC table. Please contact administrator.',
            category: 'policy',
            priority: 'high',
            user_id: this.currentUserId || 'default_user'
          });
        }
      } catch (error) {
        console.error('Error fetching users:', error);
        this.availableUsers = [];
        alert('Error: Could not load users list. Please contact administrator.');
        this.sendPushNotification({
          title: 'Users List Error',
          message: 'Could not load users list. Please contact administrator.',
          category: 'policy',
          priority: 'high',
          user_id: this.currentUserId || 'default_user'
        });
      }
    },

    // Handle user selection change (for administrators)
    async onUserChange() {
      console.log('User selection changed to:', this.selectedUserId);
      console.log('Available users:', this.availableUsers);
      
      if (this.selectedUserId) {
        // Find user info
        this.selectedUserInfo = this.availableUsers.find(u => u.UserId == this.selectedUserId);
        console.log('Selected user info:', this.selectedUserInfo);
        
        if (this.selectedUserInfo) {
          console.log(`Loading tasks for user: ${this.selectedUserInfo.UserName} (ID: ${this.selectedUserId})`);
          // Load tasks for selected user
          await this.loadUserTasks();
        } else {
          console.warn('Could not find user info for selected user ID:', this.selectedUserId);
        }
      } else {
        console.log('No user selected, clearing user info and tasks');
        this.selectedUserInfo = null;
        this.myTasks = [];
        this.reviewerTasks = [];
      }
    },

    // Switch between tabs
    switchTab(tab) {
      this.activeTab = tab;
    },

    // Review History Modal methods
    showReviewHistory(policyId, policyName, currentStatus) {
      this.selectedPolicyId = policyId;
      this.selectedPolicyName = policyName;
      this.selectedPolicyStatus = currentStatus;
      this.showReviewHistoryModal = true;
    },

    closeReviewHistoryModal() {
      this.showReviewHistoryModal = false;
      this.selectedPolicyId = null;
      this.selectedPolicyName = '';
      this.selectedPolicyStatus = '';
    },

    // Load tasks for the selected user
    async loadUserTasks() {
      const targetUserId = this.selectedUserId || this.currentUserId;
      
      console.log('Loading user tasks for user ID:', targetUserId);
      console.log('Selected user ID:', this.selectedUserId);
      console.log('Current user ID:', this.currentUserId);
      console.log('Is Administrator:', this.isAdministrator);
      
      // If administrator and no user selected, don't load any tasks
      if (this.isAdministrator && !this.selectedUserId) {
        console.log('Administrator with no user selected - clearing tasks');
        this.myTasks = [];
        this.reviewerTasks = [];
        return;
      }
      
      try {
        // Fetch My Tasks (where user is the creator/owner)
        await this.fetchMyTasks(targetUserId);
        
        // Fetch Reviewer Tasks (where user is the reviewer)
        await this.fetchReviewerTasks(targetUserId);
      } catch (error) {
        console.error('Error loading user tasks:', error);
        this.myTasks = [];
        this.reviewerTasks = [];
      }
    },

    // Fetch My Tasks (created by user)
    async fetchMyTasks(userId) {
      try {
        // Fetch policy approvals where user is the creator
        const response = await axios.get(`http://localhost:8000/api/policy-approvals/user/${userId}/`);
        
        let approvalsData;
        if (response.data.success && response.data.data) {
          approvalsData = response.data.data;
        } else if (Array.isArray(response.data)) {
          approvalsData = response.data;
        } else {
          approvalsData = [];
        }

        this.myTasks = approvalsData.map(approval => {
          return {
            ApprovalId: approval.ApprovalId,
            PolicyId: approval.PolicyId,
            ExtractedData: approval.ExtractedData,
            ApprovedNot: approval.ApprovedNot,
            ApprovedDate: approval.ApprovedDate,
            version: approval.Version,
            UserId: approval.UserId,
            ReviewerId: approval.ReviewerId,
            dbStatus: null
          };
        });

        // Get policy status from database
        await this.updateTasksWithPolicyStatus(this.myTasks);
      } catch (error) {
        console.error('Error fetching my tasks:', error);
        this.myTasks = [];
      }
    },

    // Fetch Reviewer Tasks (where user is reviewer)
    async fetchReviewerTasks(userId) {
      try {
        // Fetch policy approvals where user is the reviewer
        const response = await axios.get(`http://localhost:8000/api/policy-approvals/reviewer/${userId}/`);
        
        let approvalsData;
        if (response.data.success && response.data.data) {
          approvalsData = response.data.data;
        } else if (Array.isArray(response.data)) {
          approvalsData = response.data;
        } else {
          approvalsData = [];
        }

        this.reviewerTasks = approvalsData.map(approval => {
          return {
            ApprovalId: approval.ApprovalId,
            PolicyId: approval.PolicyId,
            ExtractedData: approval.ExtractedData,
            ApprovedNot: approval.ApprovedNot,
            ApprovedDate: approval.ApprovedDate,
            version: approval.Version,
            UserId: approval.UserId,
            ReviewerId: approval.ReviewerId,
            dbStatus: null
          };
        });

        // Get policy status from database
        await this.updateTasksWithPolicyStatus(this.reviewerTasks);
      } catch (error) {
        console.error('Error fetching reviewer tasks:', error);
        // Fallback to existing behavior for backwards compatibility
        this.fetchPolicies();
      }
    },

    // Helper method to update tasks with policy status
    async updateTasksWithPolicyStatus(tasks) {
      const policyIds = tasks
        .filter(task => task.PolicyId)
        .map(task => typeof task.PolicyId === 'object' ? task.PolicyId.PolicyId : task.PolicyId);
      
      if (policyIds.length > 0) {
        const fetchPromises = policyIds.map(policyId => 
          axios.get(`http://localhost:8000/api/policies/${policyId}/`)
            .then(policyResponse => {
              return {
                policyId: policyId,
                status: policyResponse.data.Status
              };
            })
            .catch(error => {
              console.error(`Error fetching policy ${policyId}:`, error);
              return { policyId: policyId, status: null };
            })
        );
        
        const policyStatuses = await Promise.all(fetchPromises);
        
        // Update tasks with database status
        policyStatuses.forEach(policyStatus => {
          const task = tasks.find(t => {
            const taskPolicyId = typeof t.PolicyId === 'object' ? t.PolicyId.PolicyId : t.PolicyId;
            return taskPolicyId === policyStatus.policyId;
          });
          
          if (task) {
            task.dbStatus = policyStatus.status;
          }
        });
      }
    },

    // Update the method to fetch policies and policy approvals
    fetchPolicies() {
      console.log('Fetching policy approvals for reviewer...');
      axios.get('http://localhost:8000/api/policy-approvals/reviewer/')
        .then(response => {
          console.log('Policy approvals response:', response.data);
          
          // Handle both response formats: direct array or success wrapper
          let approvalsData;
          if (response.data.success && response.data.data) {
            approvalsData = response.data.data;
          } else if (Array.isArray(response.data)) {
            approvalsData = response.data;
          } else {
            console.error('Unexpected response format:', response.data);
            return;
          }
          
          // Create initial approvals array from policy approvals data
          const approvals = approvalsData.map(approval => {
            return {
              ApprovalId: approval.ApprovalId,
              PolicyId: approval.PolicyId,
              ExtractedData: approval.ExtractedData,
              ApprovedNot: approval.ApprovedNot,
              ApprovedDate: approval.ApprovedDate,
              version: approval.Version,
              UserId: approval.UserId,
              ReviewerId: approval.ReviewerId,
              dbStatus: null // Will be populated from database table
            };
          });
          
          // Get policy IDs to fetch their direct status from database
          const policyIds = approvals
            .filter(approval => approval.PolicyId)
            .map(approval => typeof approval.PolicyId === 'object' ? approval.PolicyId.PolicyId : approval.PolicyId);
          
          if (policyIds.length > 0) {
            // Fetch the actual policy status from the database table for all policies
            const fetchPromises = policyIds.map(policyId => 
              axios.get(`http://localhost:8000/api/policies/${policyId}/`)
                .then(policyResponse => {
                  return {
                    policyId: policyId,
                    status: policyResponse.data.Status
                  };
                })
                .catch(error => {
                  console.error(`Error fetching policy ${policyId}:`, error);
                  return { policyId: policyId, status: null };
                })
            );
            
            Promise.all(fetchPromises)
              .then(policyStatuses => {
                // Update the approvals with database status
                policyStatuses.forEach(policyStatus => {
                  const approval = approvals.find(a => {
                    const approvalPolicyId = typeof a.PolicyId === 'object' ? a.PolicyId.PolicyId : a.PolicyId;
                    return approvalPolicyId === policyStatus.policyId;
                  });
                  
                  if (approval) {
                    approval.dbStatus = policyStatus.status;
                    
                    // Update ExtractedData Status as well to ensure consistency
                    if (approval.ExtractedData && policyStatus.status) {
                      approval.ExtractedData.Status = policyStatus.status;
                    }
                  }
                });
                
                this.approvals = approvals;
                console.log('Updated approvals with database status:', this.approvals);
              })
              .catch(error => {
                console.error('Error updating policy statuses:', error);
                this.approvals = approvals;
              });
          } else {
            this.approvals = approvals;
          }
        })
        .catch(error => {
          console.error('Error fetching policy approvals:', error);
        });
    },
    // Remove the fetchLatestApprovalForPolicy method as it's causing errors
    
    openApprovalDetails(approval) {
      // Get the policy ID
      const policyId = this.getPolicyId(approval);

      // First, fetch the policy's current database status to determine which version to fetch
          axios.get(`http://localhost:8000/api/policies/${policyId}/`)
            .then(policyResponse => {
              const dbStatus = policyResponse.data.Status;
              console.log(`Policy database status: ${dbStatus}`);
          
          // Determine which version to fetch based on policy status
          let versionEndpoint;
          if (dbStatus === 'Rejected') {
            // For rejected policies, fetch the latest reviewer version (r1, r2, etc.)
            versionEndpoint = `http://localhost:8000/api/policies/${policyId}/reviewer-version/`;
            console.log('Policy is rejected, fetching latest reviewer version...');
          } else {
            // For other statuses, fetch the latest user version (u1, u2, etc.)
            versionEndpoint = `http://localhost:8000/api/policies/${policyId}/version/`;
            console.log('Policy is not rejected, fetching latest user version...');
          }
          
          // Fetch the appropriate version
          axios.get(versionEndpoint)
            .then(versionResponse => {
              const policyVersion = versionResponse.data.version || 'u1';
              console.log(`Fetched policy version: ${policyVersion} for status: ${dbStatus}`);
              
              // Now fetch the latest policy approval with this version
              axios.get(`http://localhost:8000/api/policy-approvals/latest/${policyId}/`)
                .then(approvalResponse => {
                  console.log('Latest policy approval:', approvalResponse.data);
                  
                  // If we got data and it has ExtractedData, use it
                  if (approvalResponse.data && approvalResponse.data.ExtractedData) {
                    const latestApproval = approvalResponse.data;
                    
                    // Create a complete approval object with the latest data
                    const updatedApproval = {
                      ...approval,
                      ...latestApproval,
                      dbStatus: dbStatus,
                      version: policyVersion,
                      ExtractedData: latestApproval.ExtractedData
                    };
                    
                    // Update ExtractedData Status to match database status for consistency
                    if (updatedApproval.ExtractedData && dbStatus) {
                      updatedApproval.ExtractedData.Status = dbStatus;
                    }
                    
                    // Now get subpolicy versions if there are any
                    if (updatedApproval.ExtractedData && updatedApproval.ExtractedData.subpolicies && updatedApproval.ExtractedData.subpolicies.length > 0) {
                      console.log('Fetching versions for', updatedApproval.ExtractedData.subpolicies.length, 'subpolicies');
                      
                      const promises = updatedApproval.ExtractedData.subpolicies.map(sub => {
                        if (sub.SubPolicyId) {
                          // First fetch subpolicy status to determine which version endpoint to use
                          return axios.get(`http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/`)
                            .then(subpolicyResponse => {
                              const subStatus = subpolicyResponse.data.Status;
                              sub.Status = subStatus;
                              
                              // Determine which version endpoint to use based on subpolicy status
                              let subVersionEndpoint;
                              if (subStatus === 'Rejected') {
                                // For rejected subpolicies, fetch the latest reviewer version
                                subVersionEndpoint = `http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/reviewer-version/`;
                                console.log(`Subpolicy ${sub.SubPolicyId} is rejected, fetching reviewer version...`);
                              } else {
                                // For other statuses, fetch the latest user version
                                subVersionEndpoint = `http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/version/`;
                                console.log(`Subpolicy ${sub.SubPolicyId} is not rejected, fetching user version...`);
                              }
                              
                              // Fetch the appropriate version
                              return axios.get(subVersionEndpoint)
                            .then(subVersionResponse => {
                                  const subVersion = subVersionResponse.data.version || 'u1';
                                  console.log(`Subpolicy ${sub.SubPolicyId} version: ${subVersion} for status: ${subStatus}`);
                                  sub.version = subVersion;
                              return sub;
                            })
                            .catch(err => {
                              console.error(`Error fetching version for subpolicy ${sub.SubPolicyId}:`, err);
                                  sub.version = 'u1'; // Default fallback
                                  return sub;
                                });
                            })
                            .catch(err => {
                              console.error(`Error fetching subpolicy status for ${sub.SubPolicyId}:`, err);
                              sub.version = 'u1'; // Default fallback
                              return sub;
                            });
                        } else {
                          sub.version = 'u1'; // Default for subpolicies without ID
                          return Promise.resolve(sub);
                        }
                      });
                      
                      // Wait for all version fetching to complete
                      Promise.all(promises)
                        .then(updatedSubpolicies => {
                          updatedApproval.ExtractedData.subpolicies = updatedSubpolicies;
                          this.completeApprovalSelection(updatedApproval);
                        })
                        .catch(error => {
                          console.error('Error updating subpolicy versions:', error);
                          this.completeApprovalSelection(updatedApproval);
                        });
                    } else {
                      // No subpolicies to process
                      this.completeApprovalSelection(updatedApproval);
                    }
                  } else {
                    // If we couldn't get the latest approval data, fall back to using existing data with just the version updated
                    const updatedApproval = JSON.parse(JSON.stringify(approval));
                    updatedApproval.version = policyVersion;
                    updatedApproval.dbStatus = dbStatus;
                    
                    // Update ExtractedData Status to match database status for consistency
                    if (updatedApproval.ExtractedData && dbStatus) {
                      updatedApproval.ExtractedData.Status = dbStatus;
                    }
                    
                    this.processSubpolicyVersions(updatedApproval);
                  }
                })
                .catch(approvalError => {
                  console.error('Error fetching latest approval:', approvalError);
                  
                  // Fall back to just updating the version
                  const updatedApproval = JSON.parse(JSON.stringify(approval));
                  updatedApproval.version = policyVersion;
                  updatedApproval.dbStatus = dbStatus;
                  
                  // Update ExtractedData Status to match database status for consistency
                  if (updatedApproval.ExtractedData && dbStatus) {
                    updatedApproval.ExtractedData.Status = dbStatus;
                  }
                  
                  this.processSubpolicyVersions(updatedApproval);
                });
            })
            .catch(error => {
              console.error('Error fetching policy status:', error);
              
              // Fall back to just updating with version
              const updatedApproval = JSON.parse(JSON.stringify(approval));
              updatedApproval.version = approval.version || 'u1'; // Use approval's version or default
              
              this.processSubpolicyVersions(updatedApproval);
            });
        })
        .catch(error => {
          console.error('Error fetching policy version:', error);
          // Fall back to using the approval as-is
          this.completeApprovalSelection(approval);
        });
    },
    
    // Helper method to process subpolicy versions
    processSubpolicyVersions(approval) {
      // Get subpolicy versions if there are any
      if (approval.ExtractedData && approval.ExtractedData.subpolicies && approval.ExtractedData.subpolicies.length > 0) {
        console.log('Fetching versions for', approval.ExtractedData.subpolicies.length, 'subpolicies');
        
        const promises = approval.ExtractedData.subpolicies.map(sub => {
          if (sub.SubPolicyId) {
            // First fetch subpolicy status to determine which version endpoint to use
                return axios.get(`http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/`)
                  .then(subpolicyResponse => {
                const subStatus = subpolicyResponse.data.Status;
                sub.Status = subStatus;
                
                // Determine which version endpoint to use based on subpolicy status
                let subVersionEndpoint;
                if (subStatus === 'Rejected') {
                  // For rejected subpolicies, fetch the latest reviewer version
                  subVersionEndpoint = `http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/reviewer-version/`;
                  console.log(`Subpolicy ${sub.SubPolicyId} is rejected, fetching reviewer version...`);
                } else {
                  // For other statuses, fetch the latest user version
                  subVersionEndpoint = `http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/version/`;
                  console.log(`Subpolicy ${sub.SubPolicyId} is not rejected, fetching user version...`);
                }
                
                // Fetch the appropriate version
                return axios.get(subVersionEndpoint)
                  .then(subVersionResponse => {
                    const subVersion = subVersionResponse.data.version || 'u1';
                    console.log(`Subpolicy ${sub.SubPolicyId} version: ${subVersion} for status: ${subStatus}`);
                    sub.version = subVersion;
                    return sub;
                  })
                  .catch(err => {
                    console.error(`Error fetching version for subpolicy ${sub.SubPolicyId}:`, err);
                    sub.version = 'u1'; // Default fallback
                    return sub;
                  });
              })
              .catch(err => {
                console.error(`Error fetching subpolicy status for ${sub.SubPolicyId}:`, err);
                sub.version = 'u1'; // Default fallback
                return sub;
              });
          } else {
            sub.version = 'u1'; // Default for subpolicies without ID
            return Promise.resolve(sub);
          }
        });
        
        // Wait for all version fetching to complete
        Promise.all(promises)
          .then(updatedSubpolicies => {
            approval.ExtractedData.subpolicies = updatedSubpolicies;
            this.completeApprovalSelection(approval);
          })
          .catch(error => {
            console.error('Error updating subpolicy versions:', error);
            this.completeApprovalSelection(approval);
          });
      } else {
        // No subpolicies to process
        this.completeApprovalSelection(approval);
      }
    },
    
    // Helper method to finish the approval selection process
    completeApprovalSelection(approval) {
      this.selectedApproval = approval;
      
      // Log the version information being displayed
      console.log('Displaying policy details:', {
        policyId: approval.PolicyId,
        version: approval.version,
        dbStatus: approval.dbStatus,
        approvedNot: approval.ApprovedNot,
        extractedDataStatus: approval.ExtractedData?.Status
      });
      
      // If policy is approved, filter subpolicies to only show approved ones
      if (this.selectedApproval.ExtractedData && 
          (this.selectedApproval.ApprovedNot === true || this.selectedApproval.ExtractedData.Status === 'Approved') && 
          this.selectedApproval.ExtractedData.subpolicies) {
        
        // When a policy is approved, all its subpolicies should be treated as approved
        this.selectedApproval.ExtractedData.subpolicies = this.selectedApproval.ExtractedData.subpolicies.map(sub => {
          // Mark all subpolicies as approved when parent policy is approved
          if (!sub.approval) {
            sub.approval = {};
          }
          sub.approval.approved = true;
          sub.Status = 'Approved';
          return sub;
        });
        
        // Add a flag to indicate this is showing only accepted items
        this.selectedApproval.showingApprovedOnly = true;
      }
      
      // If policy is rejected, ensure rejection details are properly displayed
      if (this.selectedApproval.ExtractedData && 
          (this.selectedApproval.ApprovedNot === false || this.selectedApproval.ExtractedData.Status === 'Rejected')) {
        
        console.log('Displaying rejected policy with rejection details:', {
          rejectionReason: this.selectedApproval.ExtractedData.rejection_reason,
          cascadingRejection: this.selectedApproval.ExtractedData.cascading_rejection,
          rejectedSubpolicyNames: this.selectedApproval.ExtractedData.rejected_subpolicy_names
        });
        
        // Add a flag to indicate this is showing rejected items
        this.selectedApproval.showingRejectedDetails = true;
      }
      
      this.showDetails = true;
    },
    // Update the refresh method
    refreshData() {
      // Refresh tasks for the current user
      this.loadUserTasks();
      
      // If there's a selected approval, refresh it with latest data
      if (this.selectedApproval && this.selectedApproval.PolicyId) {
        this.openApprovalDetails(this.selectedApproval);
      }
      
      // If there's a selected policy for subpolicies, refresh it
      if (this.selectedPolicyForSubpolicies && this.selectedPolicyForSubpolicies.PolicyId) {
        const policyId = this.selectedPolicyForSubpolicies.PolicyId;
        
        // Fetch latest data for this policy
        axios.get(`http://localhost:8000/api/policies/${policyId}`)
          .then(response => {
            if (response.data) {
              // Get the version for policy and subpolicies
              axios.get(`http://localhost:8000/api/policies/${policyId}/version/`)
                .then(versionResponse => {
                  const policyVersion = versionResponse.data.version || 'u1';
                  
                  // Create a new object with the policy data
                  const policyData = {
                    ...response.data,
                    version: policyVersion
                  };
                  
                  // If this policy has subpolicies, fetch their version information
                  if (response.data.ExtractedData && response.data.ExtractedData.subpolicies) {
                    const subpolicyPromises = response.data.ExtractedData.subpolicies.map(subpolicy => {
                      return axios.get(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/version/`)
                        .then(subVersionResponse => {
                          return {
                            subpolicyId: subpolicy.SubPolicyId,
                            version: subVersionResponse.data.version || 'u1'
                          };
                        })
                        .catch(() => {
                          return {
                            subpolicyId: subpolicy.SubPolicyId,
                            version: 'u1'
                          };
                        });
                    });
                    
                    Promise.all(subpolicyPromises)
                      .then(subpolicyVersions => {
                        // Update subpolicy versions
                        if (policyData.ExtractedData && policyData.ExtractedData.subpolicies) {
                          policyData.ExtractedData.subpolicies.forEach(subpolicy => {
                            const versionInfo = subpolicyVersions.find(v => v.subpolicyId === subpolicy.SubPolicyId);
                            if (versionInfo) {
                              subpolicy.version = versionInfo.version;
                            }
                          });
                        }
                        
                        // Update the selected policy
                        this.selectedPolicyForSubpolicies = policyData;
                      });
      } else {
                    // No subpolicies, just update the policy
                    this.selectedPolicyForSubpolicies = policyData;
                  }
                })
                .catch(error => {
                  console.error("Error fetching policy version:", error);
                });
            }
          })
          .catch(error => {
            console.error("Error refreshing policy data:", error);
          });
      }
      
      // Refresh rejected subpolicies list if it's being displayed
      if (this.showRejectedSubpolicies) {
        this.fetchRejectedSubpolicies();
      }
    },
    // Update the refresh approvals method
    refreshApprovals() {
      this.fetchPolicies();
    },
    // Update fetchRejectedPolicies to fetch properly from policy approval table
    fetchRejectedPolicies() {
      console.log('Fetching rejected policies...');
      
      // Fetch rejected policy approvals for the current user
      axios.get(`http://localhost:8000/api/policy-approvals/rejected/${this.currentUserId}/`)
        .then(response => {
          console.log('Rejected policy approvals response:', response.data);
          
          if (response.data && Array.isArray(response.data) && response.data.length > 0) {
            // Process each rejected policy approval
            const processedPolicies = response.data.map(approval => {
              console.log('Processing rejected approval:', approval);
              
              // Create a comprehensive rejection reason
              let rejectionReason = 'No rejection reason provided';
              if (approval.ExtractedData) {
                if (approval.ExtractedData.rejection_reason) {
                  rejectionReason = approval.ExtractedData.rejection_reason;
                } else if (approval.ExtractedData.rejection_type === 'cascading') {
                  rejectionReason = `Cascading rejection: ${approval.ExtractedData.rejected_subpolicy_name || 'subpolicy'} was rejected`;
                } else if (approval.ExtractedData.policy_approval?.remarks) {
                  rejectionReason = approval.ExtractedData.policy_approval.remarks;
                }
              }
              
              // Get policy name and description
              const policyName = approval.ExtractedData?.PolicyName || `Policy ${approval.PolicyId?.PolicyId || approval.PolicyId}`;
              const policyScope = approval.ExtractedData?.Scope || 'No Scope';
              
              const processedPolicy = {
                policyId: approval.PolicyId?.PolicyId || approval.PolicyId,
                type: 'POLICY',
                description: policyName,
                rejectionReason: rejectionReason,
                createdDate: approval.ExtractedData?.CreatedByDate || new Date().toISOString().split('T')[0],
                originalPolicy: approval,
                rejectedVersion: approval.Version, // This should be r1, r2, etc.
                cascadingRejection: approval.ExtractedData?.cascading_rejection || false,
                rejectedSubpolicies: approval.ExtractedData?.rejected_subpolicy_names || [],
                // Make sure ExtractedData has the right structure for the edit modal
                ExtractedData: {
                  ...approval.ExtractedData,
                  PolicyName: policyName,
                  Scope: policyScope,
                  rejection_reason: rejectionReason
                }
              };
              
              console.log('Processed policy for table:', processedPolicy);
              return processedPolicy;
            });
            
            this.rejectedPolicies = processedPolicies;
            console.log('All processed rejected policies:', this.rejectedPolicies);
            
          } else {
            console.log('No rejected policy approvals found for user');
            this.rejectedPolicies = [];
          }
        })
        .catch(error => {
          console.error('Error fetching rejected policy approvals:', error);
          // Fallback to old method
          this.fetchRejectedPoliciesFallback();
        });
    },
    
    // Fallback method for fetching rejected policies
    fetchRejectedPoliciesFallback() {
      console.log('Using fallback method to fetch rejected policies...');
      axios.get('http://localhost:8000/api/policies/')
        .then(response => {
          console.log('All policies response:', response.data);
          
          let policiesData = response.data;
          if (response.data.success && response.data.data) {
            policiesData = response.data.data;
          }
          
          if (Array.isArray(policiesData)) {
            // Filter for rejected policies or policies with rejected subpolicies
            const rejectedPolicies = policiesData.filter(policy => 
              policy.Status === 'Rejected' || 
              (policy.subpolicies && policy.subpolicies.some(sub => sub.Status === 'Rejected'))
            );
            
            console.log('Found rejected policies (fallback):', rejectedPolicies.length);
            
            this.rejectedPolicies = rejectedPolicies.map(policy => ({
              policyId: policy.PolicyId,
              type: 'POLICY',
              description: policy.PolicyName || `Policy ${policy.PolicyId}`,
              rejectionReason: 'Policy or subpolicies rejected',
              createdDate: policy.CreatedByDate || new Date().toISOString().split('T')[0],
              originalPolicy: {
              PolicyId: policy.PolicyId,
              ExtractedData: {
                PolicyName: policy.PolicyName,
                CreatedByName: policy.CreatedByName,
                CreatedByDate: policy.CreatedByDate,
                Scope: policy.Scope,
                Status: policy.Status,
                Objective: policy.Objective,
                subpolicies: policy.subpolicies || []
              },
                ApprovedNot: false
              }
            }));
          }
        })
        .catch(error => {
          console.error('Error in fallback method:', error);
          this.rejectedPolicies = [];
        });
    },
    // Add a method to fetch policies that have rejected subpolicies
    fetchPoliciesWithRejectedSubpolicies() {
      console.log('Fetching policies with rejected subpolicies...');
      axios.get('http://localhost:8000/api/policies/')
        .then(response => {
          console.log('All policies response:', response.data);
          
          // Handle both response formats: direct array or success wrapper
          let policiesData;
          if (response.data.success && response.data.data) {
            policiesData = response.data.data;
          } else if (Array.isArray(response.data)) {
            policiesData = response.data;
          } else {
            console.error('Unexpected response format:', response.data);
            return;
          }
          
          console.log('Policies data length:', policiesData.length);
          if (Array.isArray(policiesData)) {
            // Filter policies that have at least one rejected subpolicy
            const policiesWithRejected = policiesData.filter(policy => 
              policy.subpolicies && 
              policy.subpolicies.some(sub => sub.Status === 'Rejected')
            );
            
            console.log('Found policies with rejected subpolicies:', policiesWithRejected.length);
            
            if (policiesWithRejected.length > 0) {
              this.rejectedPolicies = policiesWithRejected.map(policy => ({
                PolicyId: policy.PolicyId,
                ExtractedData: {
                  type: 'policy',
                  PolicyName: policy.PolicyName,
                  CreatedByName: policy.CreatedByName,
                  CreatedByDate: policy.CreatedByDate,
                  Scope: policy.Scope,
                  Status: policy.Status,
                  Objective: policy.Objective,
                  subpolicies: policy.subpolicies || []
                },
                ApprovedNot: policy.Status === 'Rejected' ? false : null,
                main_policy_rejected: policy.Status === 'Rejected'
              }));
            }
          }
      })
      .catch(error => {
          console.error('Error fetching policies with rejected subpolicies:', error);
      });
    },
    // Modify submitReview to update policy status
    submitReview() {
      if (!this.isComplianceApproval) {
        const policyId = this.selectedApproval.PolicyId;
        
        // Create the policy approval data
        const reviewData = {
          ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
          ApprovedNot: this.selectedApproval.ApprovedNot,
          UserId: this.userId,
          ReviewerId: this.userId
        };
        
        // First get the current version
        axios.get(`http://localhost:8000/api/policies/${policyId}/version/`)
          .then(versionResponse => {
            const currentVersion = versionResponse.data.version;
            console.log('Current version before submission:', currentVersion);
            
            // Add logic to check if any subpolicies are rejected
            const hasRejectedSubpolicies = this.selectedApproval.ExtractedData.subpolicies &&
              this.selectedApproval.ExtractedData.subpolicies.some(subpolicy => 
                subpolicy.Status === 'Rejected');
            
            if (this.reviewDecision === 'approve' && hasRejectedSubpolicies) {
              // Show warning
              this.$swal({
                title: 'Warning',
                text: 'One or more subpolicies are rejected. The policy will still be marked as rejected regardless of approval.',
                icon: 'warning',
                confirmButtonText: 'Continue'
              }).then(() => {
                // Continue with submission after warning
                this.submitPolicyReview(policyId, reviewData, currentVersion);
              });
              this.sendPushNotification({
                title: 'Policy Review Warning',
                message: 'One or more subpolicies are rejected. The policy will still be marked as rejected regardless of approval.',
                category: 'policy',
                priority: 'medium',
                user_id: this.currentUserId || 'default_user'
              });
            } else {
              // No rejected subpolicies, proceed normally
              this.submitPolicyReview(policyId, reviewData, currentVersion);
            }
          })
          .catch(error => {
            console.error('Error getting policy version:', error);
            PopupService.error('Error getting policy version: ' + (error.response?.data?.error || error.message), 'Policy Version Error');
            this.sendPushNotification({
              title: 'Policy Version Error',
              message: `Failed to get policy version: ${error.response?.data?.error || error.message}`,
              category: 'policy',
              priority: 'high',
              user_id: this.currentUserId || 'default_user'
            });
          });
        
        return;
      }
      
      // For compliance reviews
      const reviewData = {
        ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
        ApprovedNot: this.selectedApproval.ApprovedNot
      };
      
      axios.put(
        `http://localhost:8000/api/compliance-approvals/${this.selectedApproval.ApprovalId}/review/`,
        reviewData
      )
      .then(response => {
        console.log('Response:', response.data);
        if (response.data.ApprovalId) {
          this.selectedApproval.ApprovalId = response.data.ApprovalId;
          this.selectedApproval.Version = response.data.Version;
          // Update approved date if provided
          if (response.data.ApprovedDate) {
            this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
          }
          PopupService.success('Compliance review submitted successfully!', 'Review Submitted');
          this.sendPushNotification({
            title: 'Compliance Review Submitted',
            message: 'Compliance review has been submitted successfully for approval.',
            category: 'compliance',
            priority: 'medium',
            user_id: this.currentUserId || 'default_user'
          });
          
          // First close the details view
          this.closeApprovalDetails();
          
          // Then refresh the approvals list to update the UI
          this.refreshApprovals();
        }
      })
      .catch(error => {
        console.error('Error submitting compliance review:', error);
                  PopupService.error('Error submitting review: ' + (error.response?.data?.error || error.message), 'Review Error');
          this.sendPushNotification({
            title: 'Compliance Review Error',
            message: `Failed to submit compliance review: ${error.response?.data?.error || error.message}`,
            category: 'compliance',
            priority: 'high',
            user_id: this.currentUserId || 'default_user'
          });
      });
    },
    // Add this helper method to handle the actual submission
    submitPolicyReview(policyId, reviewData, currentVersion) {
      // Submit policy review with current version info
      axios.post(`http://localhost:8000/api/policies/${policyId}/submit-review/`, {
        ...reviewData,
        currentVersion: currentVersion,
        approved: this.reviewDecision === 'approve'
      })
      .then(response => {
        console.log('Policy review submitted successfully:', response.data);
        
        // Update the local approval with the returned data
        this.selectedApproval.Version = response.data.Version;
        
        if (response.data.ApprovedDate) {
          this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
        }
        
        PopupService.success(`Policy review submitted successfully! New version: ${response.data.Version}`, 'Review Submitted');
        this.sendPushNotification({
          title: 'Policy Review Submitted',
          message: `Policy review has been submitted successfully with version ${response.data.Version}.`,
          category: 'policy',
          priority: 'medium',
          user_id: this.currentUserId || 'default_user'
        });
        
        // Close the details view
        this.closeApprovalDetails();
        
        // Refresh the policies list
        this.refreshApprovals();
      })
      .catch(error => {
        console.error('Error submitting review:', error);
        PopupService.error('Error submitting review: ' + (error.response?.data?.error || error.message), 'Submission Error');
        this.sendPushNotification({
          title: 'Policy Review Error',
          message: `Failed to submit policy review: ${error.response?.data?.error || error.message}`,
          category: 'policy',
          priority: 'high',
          user_id: this.currentUserId || 'default_user'
        });
      });
    },
    // Update resubmitPolicy to change status back to "Under Review"
    resubmitPolicy(policy) {
      const policyId = this.getPolicyId(policy);
      console.log('=== RESUBMIT POLICY DEBUG ===');
      console.log('Resubmitting policy with ID:', policyId);
      console.log('Full policy object:', policy);
      console.log('Policy ExtractedData:', policy.ExtractedData);
      console.log('Original policy in policy object:', policy.originalPolicy);
      
      // Use original policy if available (from rejected policies table)
      const actualPolicy = policy.originalPolicy || policy;
      const actualPolicyId = this.getPolicyId(actualPolicy);
      console.log('Using actual policy:', actualPolicy);
      console.log('Using actual policy ID:', actualPolicyId);
      
      // First, check the policy status via debug endpoint
      console.log('Checking policy status before resubmission...');
      axios.get(`http://localhost:8000/api/policies/${actualPolicyId}/debug-status/`)
        .then(debugResponse => {
          console.log('Policy debug status:', debugResponse.data);
      
      // Validate policy data
          const validationErrors = this.validatePolicyData(actualPolicy);
      if (validationErrors.length > 0) {
        PopupService.warning(`Please fix the following errors before resubmitting:\n${validationErrors.join('\n')}`, 'Validation Errors');
        this.sendPushNotification({
          title: 'Policy Validation Errors',
          message: `Policy validation failed: ${validationErrors.join(', ')}`,
          category: 'policy',
          priority: 'medium',
          user_id: this.currentUserId || 'default_user'
        });
        return;
      }
      
          // Continue with resubmission logic
          this.performPolicyResubmission(actualPolicy, actualPolicyId);
        })
        .catch(debugError => {
          console.error('Error checking policy status:', debugError);
          PopupService.warning('Error checking policy status. Proceeding with resubmission attempt.', 'Warning');
          this.sendPushNotification({
            title: 'Policy Status Check Warning',
            message: 'Error checking policy status. Proceeding with resubmission attempt.',
            category: 'policy',
            priority: 'medium',
            user_id: this.currentUserId || 'default_user'
          });
          
          // Still try to proceed with resubmission
          const validationErrors = this.validatePolicyData(actualPolicy);
          if (validationErrors.length > 0) {
            PopupService.warning(`Please fix the following errors before resubmitting:\n${validationErrors.join('\n')}`, 'Validation Errors');
          this.sendPushNotification({
            title: 'Policy Validation Errors',
            message: `Policy validation failed: ${validationErrors.join(', ')}`,
            category: 'policy',
            priority: 'medium',
            user_id: this.currentUserId || 'default_user'
          });
            return;
          }
          
          this.performPolicyResubmission(actualPolicy, actualPolicyId);
        });
    },
    
          performPolicyResubmission(actualPolicy, actualPolicyId) {
      // Check if subpolicies exist and have proper structure
        if (actualPolicy.ExtractedData && actualPolicy.ExtractedData.subpolicies && actualPolicy.ExtractedData.subpolicies.length > 0) {
        // Ensure each subpolicy has the correct fields
          actualPolicy.ExtractedData.subpolicies.forEach((subpolicy, index) => {
          console.log(`Checking subpolicy ${index} with ID: ${subpolicy.SubPolicyId}`);
          
          // Make sure required fields exist
          if (!subpolicy.SubPolicyName) {
            console.warn(`SubPolicyName is missing for subpolicy ${index}`);
          }
          if (!subpolicy.Description) {
            console.warn(`Description is missing for subpolicy ${index}`);
          }
        });
      } else {
        console.warn('No subpolicies found in policy data or subpolicies array is not properly structured');
      }
      
        // Prepare data for resubmission using actual policy data
      const resubmitData = {
          PolicyName: actualPolicy.ExtractedData?.PolicyName || actualPolicy.PolicyName,
          PolicyDescription: actualPolicy.ExtractedData?.PolicyDescription || actualPolicy.PolicyDescription,
          Scope: actualPolicy.ExtractedData?.Scope || actualPolicy.Scope,
          Objective: actualPolicy.ExtractedData?.Objective || actualPolicy.Objective,
          Department: actualPolicy.ExtractedData?.Department || actualPolicy.Department,
          Applicability: actualPolicy.ExtractedData?.Applicability || actualPolicy.Applicability,
          subpolicies: actualPolicy.ExtractedData?.subpolicies || [],
          // Add policy status information to help backend validation
          currentStatus: 'Rejected',
          rejectionReason: actualPolicy.ExtractedData?.rejection_reason || actualPolicy.rejectionReason,
          // Include version information if available
          currentVersion: actualPolicy.Version || actualPolicy.rejectedVersion
      };
      
      console.log('Prepared resubmission data:', resubmitData);
      console.log('Subpolicies in resubmission data:', resubmitData.subpolicies);
      console.log('Number of subpolicies:', resubmitData.subpolicies.length);
      
        // Submit resubmission request using actual policy ID
        console.log(`Making request to: /api/policies/${actualPolicyId}/resubmit-approval/`);
        axios.put(`http://localhost:8000/api/policies/${actualPolicyId}/resubmit-approval/`, resubmitData)
        .then(response => {
          console.log('Policy resubmitted successfully:', response.data);
          
          // Show version information in the alert
          let successMessage = `Policy resubmitted for review! New version: ${response.data.Version}`;
          if (response.data.UserId) {
            successMessage += ` (UserId: ${response.data.UserId})`;
          }
          if (response.data.reviewer_assigned) {
            successMessage += ` (Assigned to ReviewerId: ${response.data.ReviewerId})`;
          }
          
          PopupService.success(successMessage, 'Policy Resubmitted');
          this.sendPushNotification({
            title: 'Policy Resubmitted',
            message: successMessage,
            category: 'policy',
            priority: 'medium',
            user_id: this.currentUserId || 'default_user'
          });
          
          this.closeEditModal();
          this.fetchRejectedPolicies();
          this.fetchPolicies();
        })
        .catch(error => {
          console.error('Error data:', error.response ? error.response.data : 'No response data');
          this.handleError(error, 'resubmitting policy');
        });
    },
    
    // Helper method to validate policy data before submission
    validatePolicyData(policy) {
      const validationErrors = [];
      
      // Check required policy fields - handle different data structures
      const policyName = policy.ExtractedData?.PolicyName || policy.PolicyName;
      const policyDescription = policy.ExtractedData?.PolicyDescription || policy.PolicyDescription;
      const subpolicies = policy.ExtractedData?.subpolicies || [];
      
      if (!policyName) {
        validationErrors.push('Policy Name is required');
      }
      
      if (!policyDescription) {
        validationErrors.push('Policy Description is required');
      }
      
      // Check subpolicies if they exist
      if (subpolicies && subpolicies.length > 0) {
        subpolicies.forEach((subpolicy, index) => {
          if (!subpolicy.SubPolicyName) {
            validationErrors.push(`Subpolicy #${index + 1} is missing a name`);
          }
          
          if (!subpolicy.Description) {
            validationErrors.push(`Subpolicy #${index + 1} is missing a description`);
          }
        });
      }
      
      return validationErrors;
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
      this.sendPushNotification({
        title: 'Policy Error',
        message: `Error ${context}: ${errorMessage}`,
        category: 'policy',
        priority: 'high',
        user_id: this.currentUserId || 'default_user'
      });
      return errorMessage;
    },
    // Update approveSubpolicy to handle subpolicy approval
    approveSubpolicy(subpolicy) {
      // Set subpolicy approval status
      if (!subpolicy.approval) {
        subpolicy.approval = {};
      }
      subpolicy.approval.approved = true;
      subpolicy.approval.remarks = '';
      
      // Update subpolicy status via API
      axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/`, {
        Status: 'Approved'
      })
      .then(response => {
        console.log('Subpolicy status updated successfully:', response.data);
        
        // Create policy approval for this subpolicy approval
        return axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/review/`, {
          Status: 'Approved'
        });
      })
      .then(response => {
        console.log('Subpolicy approval created successfully:', response.data);
        
        // Check if parent policy status was updated (all subpolicies approved)
        if (response.data.PolicyUpdated) {
          console.log(`Policy status updated to: ${response.data.PolicyStatus}`);
          
          // If parent policy was updated, refresh the policies list
          this.fetchPolicies();
          
          // Also update the UI to show policy is now approved
          if (this.selectedApproval && this.selectedApproval.ExtractedData) {
            this.selectedApproval.ExtractedData.Status = response.data.PolicyStatus;
          }
        }
        
        // Check if all subpolicies are now approved
        this.checkAllSubpoliciesApproved();
      })
      .catch(error => {
        console.error('Error approving subpolicy:', error);
        PopupService.error('Error approving subpolicy. Please try again.', 'Approval Error');
        this.sendPushNotification({
          title: 'Subpolicy Approval Error',
          message: 'Error approving subpolicy. Please try again.',
          category: 'policy',
          priority: 'high',
          user_id: this.currentUserId || 'default_user'
        });
      });
    },
    
    // Add a method to check if all subpolicies are approved
    checkAllSubpoliciesApproved() {
      if (!this.selectedApproval || 
          !this.selectedApproval.ExtractedData || 
          !this.selectedApproval.ExtractedData.subpolicies ||
          this.selectedApproval.ExtractedData.subpolicies.length === 0) {
        return;
      }
      
      const subpolicies = this.selectedApproval.ExtractedData.subpolicies;
      const allApproved = subpolicies.every(sub => sub.approval?.approved === true);
      
      if (allApproved) {
        console.log('All subpolicies are approved! The policy should be automatically approved');
        
        // Automatically set policy approval to true
        if (!this.selectedApproval.ExtractedData.policy_approval) {
          this.selectedApproval.ExtractedData.policy_approval = {};
        }
        this.selectedApproval.ExtractedData.policy_approval.approved = true;
        this.selectedApproval.ApprovedNot = true;
        
        // Show notification to user
        PopupService.success('All subpolicies are approved! The policy has been automatically approved.', 'Auto-Approval');
        this.sendPushNotification({
          title: 'All Subpolicies Approved',
          message: 'All subpolicies are approved! The policy has been automatically approved.',
          category: 'policy',
          priority: 'medium',
          user_id: this.currentUserId || 'default_user'
        });
      }
    },
    // Add the missing rejectSubpolicy method
    rejectSubpolicy(subpolicy) {
      // Open rejection modal for subpolicy
      this.rejectingType = 'subpolicy';
      this.rejectingSubpolicy = subpolicy;
      this.showRejectModal = true;
    },
    // Add the missing cancelRejection method
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectingSubpolicy = null;
      this.rejectingType = '';
      this.rejectionComment = '';
    },
    // Update rejectSubpolicy via confirmRejection
    confirmRejection() {
      if (this.rejectingType === 'policy' && this.rejectingPolicy) {
        // Handle policy rejection
        const policyId = typeof this.rejectingPolicy.PolicyId === 'object' 
          ? this.rejectingPolicy.PolicyId.PolicyId 
          : this.rejectingPolicy.PolicyId;
        
        console.log('Rejecting policy with ID:', policyId);
        
        axios.put(`http://localhost:8000/api/policies/${policyId}/`, {
          Status: 'Rejected'
        })
        .then(() => {
          // Update local state
          this.rejectingPolicy.ExtractedData.Status = 'Rejected';
          this.rejectingPolicy.policy_approval = { 
            approved: false, 
            remarks: this.rejectionComment 
          };
          
          // Close modal
          this.showRejectModal = false;
          this.rejectingPolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
        })
        .catch(error => {
          console.error('Error rejecting policy:', error);
          PopupService.error('Error rejecting policy: ' + (error.response?.data?.error || error.message), 'Rejection Error');
          this.sendPushNotification({
            title: 'Policy Rejection Error',
            message: `Error rejecting policy: ${error.response?.data?.error || error.message}`,
            category: 'policy',
            priority: 'high',
            user_id: this.currentUserId || 'default_user'
          });
        });
      } 
      else if (this.rejectingType === 'subpolicy' && this.rejectingSubpolicy) {
        if (!this.rejectingSubpolicy.SubPolicyId) {
          console.error('Missing SubPolicyId, cannot reject subpolicy', this.rejectingSubpolicy);
          PopupService.error('Error: Cannot reject subpolicy - missing SubPolicyId', 'Missing ID Error');
          this.sendPushNotification({
            title: 'Subpolicy Rejection Error',
            message: 'Cannot reject subpolicy - missing SubPolicyId',
            category: 'policy',
            priority: 'high',
            user_id: this.currentUserId || 'default_user'
          });
          this.showRejectModal = false;
          this.rejectingSubpolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
          return;
        }
        
        console.log('Rejecting subpolicy with ID:', this.rejectingSubpolicy.SubPolicyId);
        console.log('Current user info:', {
          userId: this.currentUserId,
          isAdministrator: this.isAdministrator,
          selectedUserId: this.selectedUserId
        });
        
        // Ensure Status is a string, not null
        const statusToSend = 'Rejected';
        console.log('Sending data:', { Status: statusToSend });
        
        // Use the dedicated rejection endpoint
        axios.put(`http://localhost:8000/api/subpolicies/${this.rejectingSubpolicy.SubPolicyId}/reject/`, {
          rejection_reason: this.rejectionComment,
          remarks: this.rejectionComment
        })
      .then(response => {
          console.log('Subpolicy rejected successfully:', response.data);
          
          // Check if this is a cascading rejection
          if (response.data.rejection_type === 'cascading') {
            // Handle cascading rejection
            console.log('Cascading rejection completed:', response.data);
            
            // Show detailed popup message about cascading rejection
            PopupService.success(
              response.data.popup_message || `Policy '${response.data.parent_policy_name}' and all its ${response.data.total_subpolicies_rejected} subpolicies have been rejected and saved as ${response.data.new_version}. This has been sent back to the user for revision.`,
              'Cascading Rejection Complete'
            );
            this.sendPushNotification({
              title: 'Cascading Rejection Complete',
              message: response.data.popup_message || `Policy '${response.data.parent_policy_name}' and all its ${response.data.total_subpolicies_rejected} subpolicies have been rejected and saved as ${response.data.new_version}. This has been sent back to the user for revision.`,
              category: 'policy',
              priority: 'high',
              user_id: this.currentUserId || 'default_user'
            });
            
            // Update local state for all affected subpolicies
            if (this.approvals && this.approvals.length > 0) {
              this.approvals.forEach(approval => {
                if (approval.ExtractedData && approval.ExtractedData.subpolicies) {
                  approval.ExtractedData.subpolicies.forEach(sub => {
                    if (response.data.rejected_subpolicy_names.includes(sub.SubPolicyName)) {
                      sub.Status = 'Rejected';
                      if (sub.approval) {
                        sub.approval.approved = false;
                        sub.approval.remarks = this.rejectionComment;
                      }
                    }
                  });
                }
              });
            }
            
            // Log cascading rejection details
            console.log('Cascading rejection details:', {
              originalSubpolicy: response.data.original_subpolicy_name,
              parentPolicy: response.data.parent_policy_name,
              totalRejected: response.data.total_subpolicies_rejected,
              version: response.data.new_version,
              rejectedSubpolicies: response.data.rejected_subpolicy_names
            });
            
          } else {
            // Handle regular rejection
          if (!this.rejectingSubpolicy.approval) {
            this.rejectingSubpolicy.approval = {};
          }
          
          this.rejectingSubpolicy.Status = 'Rejected';
          this.rejectingSubpolicy.approval.approved = false;
          this.rejectingSubpolicy.approval.remarks = this.rejectionComment;
            
            // Show success message
            PopupService.success('Subpolicy rejected successfully!', 'Rejection Complete');
            this.sendPushNotification({
              title: 'Subpolicy Rejected',
              message: 'Subpolicy has been rejected successfully.',
              category: 'policy',
              priority: 'medium',
              user_id: this.currentUserId || 'default_user'
            });
          }
          
          // Close modal
          this.showRejectModal = false;
          this.rejectingSubpolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
          
          // Refresh data to show updated status
          this.refreshData();
      })
      .catch(error => {
          console.error('Error rejecting subpolicy:', error);
          console.error('Error details:', {
            status: error.response?.status,
            statusText: error.response?.statusText,
            data: error.response?.data,
            message: error.message
          });
          
          let errorMessage = 'Error rejecting subpolicy. Please try again.';
          
          if (error.response?.status === 401) {
            errorMessage = 'Authentication error. Please log in again.';
          } else if (error.response?.status === 403) {
            errorMessage = 'Access denied. You don\'t have permission to reject this subpolicy. Please contact your administrator.';
          } else if (error.response?.data?.error) {
            errorMessage = error.response.data.error;
          }
          
          PopupService.error(errorMessage, 'Rejection Error');
          this.sendPushNotification({
            title: 'Subpolicy Rejection Error',
            message: errorMessage,
            category: 'policy',
            priority: 'high',
            user_id: this.currentUserId || 'default_user'
          });
        });
      }
    },
    getPolicyId(policy) {
      // Handle different policy structure formats
      if (policy.policyId) {
        return policy.policyId; // For processed rejected policies
      }
      if (policy.PolicyId) {
        return typeof policy.PolicyId === 'object' ? policy.PolicyId.PolicyId : policy.PolicyId;
      }
      if (policy.ApprovalId) {
      return policy.ApprovalId;
      }
      if (policy.id) {
        return policy.id; // For table data
      }
      return 'Unknown';
    },
    closeApprovalDetails() {
      this.selectedApproval = null;
      this.showDetails = false;
    },
    approveCompliance() {
      // Initialize compliance approval if doesn't exist
      if (!this.selectedApproval.ExtractedData.compliance_approval) {
        this.selectedApproval.ExtractedData.compliance_approval = {};
      }
      this.selectedApproval.ExtractedData.compliance_approval.approved = true;
      this.selectedApproval.ExtractedData.compliance_approval.remarks = '';
      
      // Update the overall approval status
      this.selectedApproval.ApprovedNot = true;
    },
    rejectCompliance() {
      this.rejectingType = 'compliance';
      this.showRejectModal = true;
    },
    openRejectedItem(item) {
      if (item.is_compliance) {
        // For compliance items
        this.editingCompliance = JSON.parse(JSON.stringify(item)); // Deep copy
        this.showEditComplianceModal = true;
      } else {
        // For rejected policy items, open the edit modal
        console.log('Opening rejected policy item for editing:', item);
        
        if (item.originalPolicy) {
          // Use the original policy data to open edit modal
          this.openRejectedPolicy(item.originalPolicy);
        } else {
          // If no original policy, try to use the item directly
          this.openRejectedPolicy(item);
        }
      }
    },
    closeEditComplianceModal() {
      this.showEditComplianceModal = false;
      this.editingCompliance = null;
    },
    resubmitCompliance(compliance) {
      // Reset approval status
      if (compliance.ExtractedData.compliance_approval) {
        compliance.ExtractedData.compliance_approval.approved = null;
        compliance.ExtractedData.compliance_approval.remarks = '';
      }
      
      axios.put(`http://localhost:8000/api/compliance-approvals/resubmit/${compliance.ApprovalId}/`, {
        ExtractedData: compliance.ExtractedData
      })
      .then(() => {
        PopupService.success('Compliance resubmitted for review!', 'Compliance Resubmitted');
        this.showEditComplianceModal = false;
        this.fetchRejectedPolicies();
        // Force reload to update UI
        setTimeout(() => {
          window.location.reload();
        }, 500);
        this.sendPushNotification({
          title: 'Compliance Resubmitted',
          message: 'Compliance has been resubmitted for review.',
          category: 'compliance',
          priority: 'medium',
          user_id: this.currentUserId || 'default_user'
        });
      })
      .catch(error => {
        PopupService.error('Error resubmitting compliance', 'Resubmission Error');
        console.error(error);
        this.sendPushNotification({
          title: 'Compliance Resubmission Error',
          message: 'Error resubmitting compliance. Please try again.',
          category: 'compliance',
          priority: 'high',
          user_id: this.currentUserId || 'default_user'
        });
      });
    },
    showEditFormInline(subpolicy) {
      console.log('Opening inline edit form for subpolicy:', subpolicy.SubPolicyId);
      
      // Store original values before editing
      subpolicy.originalDescription = subpolicy.Description;
      subpolicy.originalControl = subpolicy.Control;
      
      // Make sure approval object exists before accessing it
      if (!subpolicy.approval) {
        subpolicy.approval = { remarks: '', approved: false };
      }
      
      // If this is a rejected subpolicy, fetch the latest reviewer version
      if (subpolicy.Status === 'Rejected' || (subpolicy.approval && subpolicy.approval.approved === false)) {
        axios.get(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/reviewer-version/`)
          .then(versionResponse => {
            const rVersion = versionResponse.data.version || 'R1';
            console.log(`Using reviewer version ${rVersion} for rejected subpolicy ${subpolicy.SubPolicyId}`);
            subpolicy.reviewerVersion = rVersion;
            
            // If we have approval data with this subpolicy, use it
            if (versionResponse.data.approval_data && 
                versionResponse.data.approval_data.ExtractedData && 
                versionResponse.data.approval_data.ExtractedData.subpolicies) {
              
              const approvalData = versionResponse.data.approval_data;
              
              // Find this subpolicy in the ExtractedData
              const subpolicyData = approvalData.ExtractedData.subpolicies.find(
                s => s.SubPolicyId === subpolicy.SubPolicyId
              );
              
              if (subpolicyData) {
                // Keep original values for comparison
                const originalDescription = subpolicy.originalDescription;
                const originalControl = subpolicy.originalControl;
                
                // Update this subpolicy with the R version data
                Object.assign(subpolicy, subpolicyData);
                
                // Restore original values for comparison
                subpolicy.originalDescription = originalDescription;
                subpolicy.originalControl = originalControl;
                
                // Make sure approval object exists
                if (!subpolicy.approval) {
                  subpolicy.approval = { remarks: '', approved: false };
                }
                
                console.log(`Updated subpolicy ${subpolicy.SubPolicyId} with R version data for inline edit`);
              }
            }
          })
          .catch(error => {
            console.error('Error fetching reviewer version:', error);
            subpolicy.reviewerVersion = 'R1'; // Default fallback
          });
      }
      
      // Show the edit modal
      subpolicy.showEditForm = true;
    },
    hideEditFormInline(subpolicy) {
      subpolicy.showEditForm = false;
    },
    resubmitSubpolicy() {
      if (!this.editingSubpolicy || !this.editingSubpolicy.SubPolicyId) {
        console.error('Missing SubPolicyId, cannot resubmit subpolicy', this.editingSubpolicy);
        PopupService.error('Error: Cannot resubmit subpolicy - missing SubPolicyId', 'Missing ID Error');
        this.sendPushNotification({
          title: 'Subpolicy Resubmission Error',
          message: 'Cannot resubmit subpolicy - missing SubPolicyId',
          category: 'policy',
          priority: 'high',
          user_id: this.currentUserId || 'default_user'
        });
        return;
      }
      
      // Check if any changes were made
      if (!this.hasChanges) {
        PopupService.warning('No changes detected. Please modify the subpolicy before resubmitting.', 'No Changes');
        this.sendPushNotification({
          title: 'No Changes Detected',
          message: 'No changes detected. Please modify the subpolicy before resubmitting.',
          category: 'policy',
          priority: 'medium',
          user_id: this.currentUserId || 'default_user'
        });
        return;
      }
      
      const updateData = {
        Control: this.editingSubpolicy.Control,
        Description: this.editingSubpolicy.Description,
        SubPolicyId: this.editingSubpolicy.SubPolicyId
      };
      
      // Send the resubmit request
      axios.put(`http://localhost:8000/api/subpolicies/${this.editingSubpolicy.SubPolicyId}/resubmit/`, updateData)
          .then(response => {
              console.log('Subpolicy resubmitted successfully:', response.data);
              
              // Update the UI with new version
              const newVersion = response.data.version;
              this.editingSubpolicy.Status = 'Under Review';
              this.editingSubpolicy.version = newVersion;
              
              if (!this.editingSubpolicy.approval) {
                  this.editingSubpolicy.approval = {};
              }
              this.editingSubpolicy.approval.approved = null;
              this.editingSubpolicy.resubmitted = true;
              
              // Show success message with new version
              PopupService.success(`Subpolicy "${this.editingSubpolicy.SubPolicyName}" resubmitted successfully with version ${newVersion}!`, 'Subpolicy Resubmitted');
              this.sendPushNotification({
                title: 'Subpolicy Resubmitted',
                message: `Subpolicy "${this.editingSubpolicy.SubPolicyName}" resubmitted successfully with version ${newVersion}!`,
                category: 'policy',
                priority: 'medium',
                user_id: this.currentUserId || 'default_user'
              });
              
              // Close the edit modal
              this.closeEditSubpolicyModal();
              
              // Refresh data
              this.fetchRejectedSubpolicies();
              this.refreshData();
          })
          .catch(error => {
              console.error('Error resubmitting subpolicy:', error.response || error);
              PopupService.error(`Error resubmitting subpolicy: ${error.response?.data?.error || error.message}`, 'Resubmission Error');
              this.sendPushNotification({
                title: 'Subpolicy Resubmission Error',
                message: `Error resubmitting subpolicy: ${error.response?.data?.error || error.message}`,
                category: 'policy',
                priority: 'high',
                user_id: this.currentUserId || 'default_user'
              });
          });
    },
    
    // Add a helper method to update subpolicy references across the UI
    updateSubpolicyReferences(subpolicyId, updates) {
      // Update in selectedApproval if applicable
      if (this.selectedApproval?.ExtractedData?.subpolicies) {
        const subpolicy = this.selectedApproval.ExtractedData.subpolicies.find(
          sub => sub.SubPolicyId === subpolicyId
        );
        if (subpolicy) {
          Object.assign(subpolicy, updates);
        }
      }
      
      // Update in selectedPolicyForSubpolicies if applicable
      if (this.selectedPolicyForSubpolicies?.ExtractedData?.subpolicies) {
        const subpolicy = this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.find(
          sub => sub.SubPolicyId === subpolicyId
        );
        if (subpolicy) {
          Object.assign(subpolicy, updates);
        }
      }
      
      // Update in rejectedSubpolicies if applicable
      const rejectedSubpolicy = this.rejectedSubpolicies.find(
        sub => sub.SubPolicyId === subpolicyId
      );
      if (rejectedSubpolicy) {
        Object.assign(rejectedSubpolicy, updates);
      }
    },
    resubmitSubpolicyDirect(subpolicy) {
      if (!subpolicy.SubPolicyId) {
        console.error('Missing SubPolicyId, cannot resubmit subpolicy', subpolicy);
        PopupService.error('Error: Cannot resubmit subpolicy - missing SubPolicyId', 'Missing ID Error');
        this.sendPushNotification({
          title: 'Subpolicy Resubmission Error',
          message: 'Cannot resubmit subpolicy - missing SubPolicyId',
          category: 'policy',
          priority: 'high',
          user_id: this.currentUserId || 'default_user'
        });
        return;
      }
      
      // Check if any changes were made
      const hasChanges = (
        subpolicy.Description !== subpolicy.originalDescription ||
        subpolicy.Control !== subpolicy.originalControl
      );
      
      if (!hasChanges) {
        PopupService.warning('No changes detected. Please modify the subpolicy before resubmitting.', 'No Changes');
        this.sendPushNotification({
          title: 'No Changes Detected',
          message: 'No changes detected. Please modify the subpolicy before resubmitting.',
          category: 'policy',
          priority: 'medium',
          user_id: this.currentUserId || 'default_user'
        });
        return;
      }
      
      console.log('Resubmitting subpolicy with ID:', subpolicy.SubPolicyId);
      console.log('Changes detected in inline edit form');
      
      // Store original values before resubmitting
      const previousVersion = {
        Description: subpolicy.originalDescription,
        Control: subpolicy.originalControl
      };
      
      // Mark as resubmitted
      subpolicy.resubmitted = true;
      
      // Prepare data to send to the backend
      const updateData = {
        Control: subpolicy.Control,
        Description: subpolicy.Description,
        previousVersion: previousVersion,
        SubPolicyId: subpolicy.SubPolicyId
      };
      
      // Send the updated subpolicy data to the resubmit endpoint
      axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/resubmit/`, updateData)
      .then(response => {
          console.log('Subpolicy resubmitted successfully:', response.data);
          
          // Update the UI to show resubmitted status
          subpolicy.Status = 'Under Review';
          if (!subpolicy.approval) {
            subpolicy.approval = {};
          }
          subpolicy.approval.approved = null;
          subpolicy.previousVersion = previousVersion;
          
          if (response.data.Version) {
            subpolicy.version = response.data.Version;
          }
          
          // Show success message
          PopupService.success(`Subpolicy "${subpolicy.SubPolicyName}" resubmitted successfully with version ${response.data.Version || 'u1'}!`, 'Subpolicy Resubmitted');
          this.sendPushNotification({
            title: 'Subpolicy Resubmitted',
            message: `Subpolicy "${subpolicy.SubPolicyName}" resubmitted successfully with version ${response.data.Version || 'u1'}!`,
            category: 'policy',
            priority: 'medium',
            user_id: this.currentUserId || 'default_user'
          });
          
          // Hide the edit form
        this.hideEditFormInline(subpolicy);
        
          // Close the modal after successful resubmission
          this.closeSubpoliciesModal();
          
          // Refresh the data
          this.fetchRejectedSubpolicies();
          this.fetchPolicies();
      })
      .catch(error => {
          console.error('Error resubmitting subpolicy:', error.response || error);
          PopupService.error(`Error resubmitting subpolicy: ${error.response?.data?.error || error.message}`, 'Resubmission Error');
          this.sendPushNotification({
            title: 'Subpolicy Resubmission Error',
            message: `Error resubmitting subpolicy: ${error.response?.data?.error || error.message}`,
            category: 'policy',
            priority: 'high',
            user_id: this.currentUserId || 'default_user'
          });
      });
    },
    getSubpolicyVersion(subpolicy) {
      if (subpolicy.version) {
        return subpolicy.version;
      } else if (subpolicy.approval && subpolicy.approval.version) {
        return subpolicy.approval.version;
      } else {
        return 'u1'; // Default version
      }
    },
    openSubpoliciesModal(policy) {
      this.selectedPolicyForSubpolicies = policy;
      
      // If policy is already approved, mark all subpolicies as approved
      if (policy.ExtractedData && 
          (policy.ApprovedNot === true || policy.ExtractedData.Status === 'Approved') && 
          policy.ExtractedData.subpolicies) {
        
        // Make a deep copy to avoid modifying the original data
        this.selectedPolicyForSubpolicies = JSON.parse(JSON.stringify(policy));
        
        // When a policy is approved, mark all subpolicies as approved too
        this.selectedPolicyForSubpolicies.ExtractedData.subpolicies = 
          this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.map(sub => {
            if (!sub.approval) {
              sub.approval = {};
            }
            sub.approval.approved = true;
            sub.Status = 'Approved';
            return sub;
          });
      } else if (policy.ExtractedData && 
          (policy.ApprovedNot === false || policy.ExtractedData.Status === 'Rejected') && 
          policy.ExtractedData.subpolicies) {
        
        // Make a deep copy for rejected policies
        this.selectedPolicyForSubpolicies = JSON.parse(JSON.stringify(policy));
        
        // For rejected policies, fetch the latest reviewer version (R1, R2, etc.) with full data
        const policyId = this.getPolicyId(policy);
        
        // Fetch the latest R version for the policy with its approval data
        axios.get(`http://localhost:8000/api/policies/${policyId}/reviewer-version/`)
          .then(versionResponse => {
            const rVersion = versionResponse.data.version || 'R1';
            console.log(`Using reviewer version: ${rVersion} for policy ${policyId}`);
            
            // If we have approval data, use it to replace the current data
            if (versionResponse.data.approval_data) {
              const approvalData = versionResponse.data.approval_data;
              console.log('Found R version approval data:', approvalData);
              
              // Use the ExtractedData from the R version instead of the current data
              if (approvalData.ExtractedData) {
                // Keep reference to original policy for ID, etc.
                const originalPolicy = this.selectedPolicyForSubpolicies;
                
                // Replace the extracted data with the R version data
                this.selectedPolicyForSubpolicies = {
                  ...originalPolicy,
                  ExtractedData: approvalData.ExtractedData,
                  reviewerVersion: rVersion,
                  ApprovalId: approvalData.ApprovalId,
                  Version: approvalData.Version
                };
                
                console.log('Updated policy data with R version data:', this.selectedPolicyForSubpolicies);
              }
            } else {
              // Just update the version info if we don't have approval data
              this.selectedPolicyForSubpolicies.reviewerVersion = rVersion;
              
              // Now fetch R versions for each subpolicy
              this.fetchSubpolicyVersions();
            }
          })
          .catch(error => {
            console.error('Error fetching policy reviewer version:', error);
            // Try to fetch subpolicy versions anyway
            this.fetchSubpolicyVersions();
          });
      }
      
      this.showSubpoliciesModal = true;

      // If in user mode, ensure rejected subpolicies show edit options immediately
      if (!this.isReviewer) {
        // Process each subpolicy to ensure rejected ones can be edited
        setTimeout(() => {
          if (this.selectedPolicyForSubpolicies && 
              this.selectedPolicyForSubpolicies.ExtractedData && 
              this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
            
            this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.forEach(sub => {
              if (sub.Status === 'Rejected' || 
                 (sub.approval && sub.approval.approved === false)) {
                // Pre-populate the edit form for rejected subpolicies
                sub.showEditForm = true;
              }
            });
          }
        }, 100); // Small delay to ensure DOM is updated
      }
    },
    
    // Helper method to fetch subpolicy versions
    fetchSubpolicyVersions() {
      if (this.selectedPolicyForSubpolicies && 
          this.selectedPolicyForSubpolicies.ExtractedData && 
          this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
        
        const promises = this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.map(sub => {
          if (sub.SubPolicyId) {
            return axios.get(`http://localhost:8000/api/subpolicies/${sub.SubPolicyId}/reviewer-version/`)
              .then(subVersionResponse => {
                const subRVersion = subVersionResponse.data.version || 'R1';
                console.log(`Subpolicy ${sub.SubPolicyId} reviewer version: ${subRVersion}`);
                
                // Store reviewer version
                sub.reviewerVersion = subRVersion;
                
                // If we have approval data for this subpolicy, update its data
                if (subVersionResponse.data.approval_data && 
                    subVersionResponse.data.approval_data.ExtractedData && 
                    subVersionResponse.data.approval_data.ExtractedData.subpolicies) {
                  
                  const approvalData = subVersionResponse.data.approval_data;
                  
                  // Find this subpolicy in the ExtractedData
                  const subpolicyData = approvalData.ExtractedData.subpolicies.find(
                    s => s.SubPolicyId === sub.SubPolicyId
                  );
                  
                  if (subpolicyData) {
                    // Update this subpolicy with the R version data
                    Object.assign(sub, subpolicyData);
                    console.log(`Updated subpolicy ${sub.SubPolicyId} with R version data`);
                  }
                }
                
                return sub;
              })
              .catch(err => {
                console.error(`Error fetching reviewer version for subpolicy ${sub.SubPolicyId}:`, err);
                sub.reviewerVersion = 'R1'; // Default fallback
                return sub;
              });
          } else {
            sub.reviewerVersion = 'R1'; // Default for subpolicies without ID
            return Promise.resolve(sub);
          }
        });
        
        Promise.all(promises).then(() => {
          console.log('All reviewer versions fetched for subpolicies');
        });
      }
    },
    closeSubpoliciesModal() {
      this.selectedPolicyForSubpolicies = null;
      this.showSubpoliciesModal = false;
    },
    approveSubpolicyFromModal(subpolicy) {
      // Set subpolicy approval status in UI
      if (!subpolicy.approval) {
        subpolicy.approval = {};
      }
      subpolicy.approval.approved = true;
      subpolicy.approval.remarks = '';
      
      // Update subpolicy status via API
      axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/`, {
        Status: 'Approved'
      })
      .then(response => {
        console.log('Subpolicy status updated successfully:', response.data);
        
        // Create policy approval for this subpolicy approval
        return axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/review/`, {
          Status: 'Approved'
        });
      })
      .then(response => {
        console.log('Subpolicy approval created successfully:', response.data);
        
        // Check if parent policy status was updated (all subpolicies approved)
        if (response.data.PolicyUpdated) {
          console.log(`Policy status updated to: ${response.data.PolicyStatus}`);
          
          // If parent policy was updated, refresh the policies list
          this.fetchPolicies();
          
          // Update the UI to show the policy is now approved
          if (this.selectedPolicyForSubpolicies && 
              this.selectedPolicyForSubpolicies.ExtractedData) {
            this.selectedPolicyForSubpolicies.ExtractedData.Status = response.data.PolicyStatus;
          }
        }
        
        // Check if all subpolicies in the modal are approved
        this.checkAllModalSubpoliciesApproved();
      })
      .catch(error => {
        console.error('Error approving subpolicy:', error);
        PopupService.error('Error approving subpolicy. Please try again.', 'Approval Error');
        this.sendPushNotification({
          title: 'Subpolicy Approval Error',
          message: 'Error approving subpolicy. Please try again.',
          category: 'policy',
          priority: 'high',
          user_id: this.currentUserId || 'default_user'
        });
      });
    },
    
    // Add a method to check if all subpolicies in the modal view are approved
    checkAllModalSubpoliciesApproved() {
      if (!this.selectedPolicyForSubpolicies || 
          !this.selectedPolicyForSubpolicies.ExtractedData || 
          !this.selectedPolicyForSubpolicies.ExtractedData.subpolicies ||
          this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.length === 0) {
        return;
      }
      
      const subpolicies = this.selectedPolicyForSubpolicies.ExtractedData.subpolicies;
      const allApproved = subpolicies.every(sub => sub.approval?.approved === true);
      
      if (allApproved) {
        console.log('All subpolicies in the modal are approved! The policy should be automatically approved');
        
        // Automatically set policy approval to true
        if (!this.selectedPolicyForSubpolicies.ExtractedData.policy_approval) {
          this.selectedPolicyForSubpolicies.ExtractedData.policy_approval = {};
        }
        this.selectedPolicyForSubpolicies.ExtractedData.policy_approval.approved = true;
        this.selectedPolicyForSubpolicies.ApprovedNot = true;
        
        // Show notification to user
        PopupService.success('All subpolicies are approved! The policy has been automatically approved.', 'Auto-Approval');
        this.sendPushNotification({
          title: 'All Subpolicies Approved',
          message: 'All subpolicies are approved! The policy has been automatically approved.',
          category: 'policy',
          priority: 'medium',
          user_id: this.currentUserId || 'default_user'
        });
      }
    },
    rejectSubpolicyFromModal(subpolicy) {
      // Open rejection modal for subpolicy
      this.rejectingType = 'subpolicy';
      this.rejectingSubpolicy = subpolicy;
      this.showRejectModal = true;
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
    isNewPolicy(policy) {
      const createdDate = policy.ExtractedData?.CreatedByDate || policy.created_at;
      if (!createdDate) return false;
      
      const date = new Date(createdDate);
      if (isNaN(date.getTime())) return false; // Invalid date
      
      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3); // Show new badge for 3 days
      
      return date > threeDaysAgo;
    },
    // Add a new method for opening the edit modal for a rejected subpolicy
    openEditSubpolicyModal(subpolicy) {
      // Create a deep copy of the subpolicy to edit
      this.editingSubpolicy = JSON.parse(JSON.stringify(subpolicy));
      
      // Store original values for comparison
      this.editingSubpolicy.originalDescription = subpolicy.Description;
      this.editingSubpolicy.originalControl = subpolicy.Control;
      
      // Fetch the latest reviewer version for this rejected subpolicy with complete data
      if (subpolicy.SubPolicyId) {
        axios.get(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/reviewer-version/`)
          .then(versionResponse => {
            const rVersion = versionResponse.data.version || 'R1';
            console.log(`Fetched reviewer version for edit modal: ${rVersion}`);
            this.editingSubpolicy.reviewerVersion = rVersion;
            
            // If we have approval data with this subpolicy, use it
            if (versionResponse.data.approval_data && 
                versionResponse.data.approval_data.ExtractedData && 
                versionResponse.data.approval_data.ExtractedData.subpolicies) {
              
              const approvalData = versionResponse.data.approval_data;
              
              // Find this subpolicy in the ExtractedData
              const subpolicyData = approvalData.ExtractedData.subpolicies.find(
                s => s.SubPolicyId === subpolicy.SubPolicyId
              );
              
              if (subpolicyData) {
                // Keep original values for comparison
                const originalDescription = this.editingSubpolicy.originalDescription;
                const originalControl = this.editingSubpolicy.originalControl;
                
                // Update this subpolicy with the R version data
                Object.assign(this.editingSubpolicy, subpolicyData);
                
                // Restore original values for comparison
                this.editingSubpolicy.originalDescription = originalDescription;
                this.editingSubpolicy.originalControl = originalControl;
                
                console.log(`Updated subpolicy ${subpolicy.SubPolicyId} with R version data for edit modal`);
              }
            }
          })
          .catch(err => {
            console.error('Error fetching reviewer version:', err);
            this.editingSubpolicy.reviewerVersion = 'R1'; // Default
          });
      }
      
      // Show the edit modal
      this.showEditSubpolicyModal = true;
      
      console.log('Edit modal opened with subpolicy:', this.editingSubpolicy);
    },
    
    // Add a method to close the edit subpolicy modal
    closeEditSubpolicyModal() {
      this.showEditSubpolicyModal = false;
      this.editingSubpolicy = null;
    },
    
    // Helper method to find a subpolicy by ID
    findSubpolicyById(subpolicyId) {
      if (!this.selectedPolicyForSubpolicies || !this.selectedPolicyForSubpolicies.ExtractedData || !this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
        return null;
      }
      
      return this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.find(
        sub => sub.SubPolicyId === subpolicyId
      );
    },
    // Add method to fetch rejected subpolicies
    fetchRejectedSubpolicies() {
      console.log('Fetching rejected subpolicies...');
      // For now, we'll fetch all policies and filter for rejected subpolicies
      axios.get('http://localhost:8000/api/policies/')
        .then(response => {
          console.log('Received policies for subpolicy check:', response.data.length);
          const allPolicies = response.data;
          let rejectedSubs = [];
          
          // Go through each policy and collect rejected subpolicies
          allPolicies.forEach(policy => {
            if (policy.subpolicies && policy.subpolicies.length > 0) {
              console.log(`Policy ${policy.PolicyId} has ${policy.subpolicies.length} subpolicies`);
              const rejected = policy.subpolicies.filter(sub => sub.Status === 'Rejected');
              console.log(`Policy ${policy.PolicyId} has ${rejected.length} rejected subpolicies`);
              
              // Add policy info to each subpolicy for context
              rejected.forEach(sub => {
                sub.PolicyName = policy.PolicyName;
                sub.PolicyId = policy.PolicyId;
              });
              
              rejectedSubs = [...rejectedSubs, ...rejected];
            }
          });
          
          console.log('Total rejected subpolicies found:', rejectedSubs.length);
          this.rejectedSubpolicies = rejectedSubs;
          
          // If we're in user mode and there are rejected subpolicies, update the view
          if (!this.isReviewer && rejectedSubs.length > 0) {
            this.updateRejectedSubpoliciesView();
          }
        })
        .catch(error => {
          console.error('Error fetching rejected subpolicies:', error);
        });
    },
    // Add a method to update the rejected subpolicies view in user mode
    updateRejectedSubpoliciesView() {
      // Set the active tab to rejected if we have rejected subpolicies
      if (this.rejectedSubpolicies.length > 0) {
        this.activeTab = 'rejected';
      }
    },
    // Method to track changes in the edit form
    trackChanges() {
      // No need for complex logic here - Vue's reactivity will handle updates to the model
      // We just need this method to trigger when input happens
      console.log('Changes detected in form');
    },
    // Add helper method to increment version
    incrementVersion(currentVersion) {
      if (!currentVersion) return 'u1';
      const match = currentVersion.match(/u(\d+)/);
      if (!match) return 'u1';
      const num = parseInt(match[1]) + 1;
      return `u${num}`;
    },
    // Add this helper method
    getSubpolicyRemarks(sub) {
      return sub && sub.approval && sub.approval.remarks ? sub.approval.remarks : 'No reason provided';
    },
    // Add a method to fetch policy categories
    fetchPolicyCategories() {
      axios.get('http://localhost:8000/api/policy-categories/')
        .then(response => {
          // Handle both response formats: direct array or success wrapper
          if (response.data.success && response.data.data) {
            this.policyCategories = response.data.data;
          } else if (Array.isArray(response.data)) {
            this.policyCategories = response.data;
          } else {
            console.error('Unexpected response format:', response.data);
          }
        })
        .catch(error => {
          console.error('Error fetching policy categories:', error);
        });
    },
    fetchPolicyTypes() {
      console.log('Fetching policy categories...');
      axios.get('http://localhost:8000/api/policy-categories/')
        .then(response => {
          console.log('Policy categories response:', response.data);
          
          // Handle both response formats: direct array or success wrapper
          let categoriesData;
          if (response.data.success && response.data.data) {
            categoriesData = response.data.data;
          } else if (Array.isArray(response.data)) {
            categoriesData = response.data;
          } else {
            console.error('Unexpected response format:', response.data);
            return;
          }
          
          // Store the raw categories data
          this.policyCategories = categoriesData;
          
          // Create a structured map for easier filtering
          const typeMap = {};
          
          // Process the categories into a nested structure
          categoriesData.forEach(category => {
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
      
      // Initialize policy category fields if they don't exist
      if (!policy.ExtractedData.PolicyType) policy.ExtractedData.PolicyType = '';
      if (!policy.ExtractedData.PolicyCategory) policy.ExtractedData.PolicyCategory = '';
      if (!policy.ExtractedData.PolicySubCategory) policy.ExtractedData.PolicySubCategory = '';
      
      // Log current values
      console.log('Current policy category fields:', {
        PolicyType: policy.ExtractedData.PolicyType,
        PolicyCategory: policy.ExtractedData.PolicyCategory,
        PolicySubCategory: policy.ExtractedData.PolicySubCategory
      });
      
      return policy;
    },
    openRejectedPolicy(policy) {
      console.log('Opening rejected policy for editing:', policy);
      this.editingPolicy = JSON.parse(JSON.stringify(policy)); // Deep copy
      
      // Initialize policy category fields
      this.initializePolicyCategoryFields(this.editingPolicy);
      
      this.showEditModal = true;
    },
    
    // Close the edit modal
    closeEditModal() {
      this.showEditModal = false;
      this.editingPolicy = null;
    },
    // Handle policy type change
    handlePolicyTypeChange(policy) {
      console.log(`Policy type changed to: ${policy.ExtractedData.PolicyType}`);
      // Reset dependent fields when type changes
      policy.ExtractedData.PolicyCategory = '';
      policy.ExtractedData.PolicySubCategory = '';
    },
    
    // Handle policy category change
    handlePolicyCategoryChange(policy) {
      console.log(`Policy category changed to: ${policy.ExtractedData.PolicyCategory}`);
      // Reset subcategory when category changes
      policy.ExtractedData.PolicySubCategory = '';
    },
    // Collapsible Table Methods
    transformApprovalToTask(approval) {
      if (!approval) {
        return {
          incidentId: 'N/A',
          policyName: 'Unknown',
          type: 'Policy',
          scope: 'No Scope',
          createdBy: 'System',
          createdDate: 'N/A',
          status: this.getStatusBadge('pending'),
          originalApproval: null
        };
      }
      
      const policyId = this.getPolicyId(approval);
      const status = this.getApprovalStatus(approval);
      
      return {
        incidentId: policyId, // Using policyId as incidentId for compatibility
        policyName: approval.ExtractedData?.PolicyName || policyId,
        type: approval.ExtractedData?.type === 'subpolicy' ? 'Subpolicy' : 'Policy',
        scope: approval.ExtractedData?.Scope || 'No Scope',
        createdBy: approval.ExtractedData?.CreatedByName || 'System',
        createdDate: this.formatDate(approval.ExtractedData?.CreatedByDate || approval.created_at),
        status: this.getStatusBadge(status),
        originalApproval: approval // Keep reference to original data
      };
    },
    
    getApprovalStatus(approval) {
      if (!approval) {
        return 'pending';
      }
      
      if (approval.dbStatus === 'Approved' || approval.ApprovedNot === true || approval.ExtractedData?.Status === 'Approved') {
        return 'approved';
      } else if (approval.dbStatus === 'Rejected' || approval.ApprovedNot === false || approval.ExtractedData?.Status === 'Rejected') {
        return 'rejected';
      } else {
        return 'pending';
      }
    },
    
    getStatusBadge(status) {
      const statusConfig = {
        pending: '<span class="status-badge status-pending">Pending</span>',
        approved: '<span class="status-badge status-approved">Approved</span>',
        rejected: '<span class="status-badge status-rejected">Rejected</span>'
      };
      return statusConfig[status] || statusConfig.pending;
    },
    
    toggleSection(sectionName) {
      this.expandedSections[sectionName.toLowerCase()] = !this.expandedSections[sectionName.toLowerCase()];
    },
    
    handleTaskClick(task) {
      // Find the original approval data
      const approval = task.originalApproval;
      if (!approval) return;
      
      // Get policy information
      const policyId = this.getPolicyId(approval);
      const policyName = approval.ExtractedData?.PolicyName || policyId;
      const currentStatus = this.getApprovalStatus(approval);
      
      // Determine if user should see review history or regular details
      const shouldShowReviewHistory = this.shouldShowReviewHistory(approval, currentStatus);
      
      if (shouldShowReviewHistory) {
        // Show review history modal for users viewing their own policies under review
        this.showReviewHistory(policyId, policyName, currentStatus);
      } else {
        // Show regular details modal for reviewers or approved/rejected policies
        this.openApprovalDetails(approval);
      }
    },
    
    // Determine if user should see review history instead of details
    shouldShowReviewHistory(approval, currentStatus) {
      // Show review history if:
      // 1. Current user is NOT a reviewer for this policy AND
      // 2. Policy is under review (pending status) AND
      // 3. Current user is the policy creator
      
      const isReviewerForThisPolicy = approval.ReviewerId === this.currentUserId;
      const isPolicyCreator = approval.UserId === this.currentUserId;
      const isPending = currentStatus === 'pending';
      
      // Show review history for creators viewing their own pending policies
      // Show regular details for reviewers or for approved/rejected policies
      return !isReviewerForThisPolicy && isPolicyCreator && isPending;
    },

    // Get CSS class for policy status pill
    getPolicyStatusClass(approval) {
      const status = this.getApprovalStatus(approval);
      switch (status) {
        case 'approved':
          return 'status-approved';
        case 'rejected':
          return 'status-rejected';
        case 'pending':
        default:
          return 'status-pending';
      }
    },
    
    // Generate collapsible sections for any task array
    generateCollapsibleSections(tasks) {
      if (!tasks || !Array.isArray(tasks)) {
        return [];
      }
      
      const sections = [];
      const sectionNames = [
        { key: 'pending', label: 'Pending' },
        { key: 'approved', label: 'Approved' },
        { key: 'rejected', label: 'Rejected' }
      ];
      
      sectionNames.forEach(({ key, label }) => {
        const allTasks = tasks
          .filter(a => {
            if (key === 'pending') return a.ApprovedNot === null;
            if (key === 'approved') return a.ApprovedNot === true;
            if (key === 'rejected') return a.ApprovedNot === false;
          })
          .map(this.transformApprovalToTask);
        
        const pageSize = this.collapsiblePagination[key].pageSize;
        const currentPage = this.collapsiblePagination[key].currentPage;
        const totalPages = Math.max(1, Math.ceil(allTasks.length / pageSize));
        const pagedTasks = allTasks.slice((currentPage - 1) * pageSize, currentPage * pageSize);
        
        if (allTasks.length > 0) {
          sections.push({
            name: label,
            statusClass: key,
            tasks: pagedTasks,
            pagination: {
              currentPage,
              totalPages,
              pageSize,
              totalCount: allTasks.length,
              pageSizeOptions: [6, 15, 30, 50],
              onPageSizeChange: (size) => {
                this.collapsiblePagination[key].pageSize = size;
                this.collapsiblePagination[key].currentPage = 1;
              },
              onPageChange: (page) => {
                this.collapsiblePagination[key].currentPage = page;
              }
            }
          });
        }
      });
      
      return sections;
    },

    // Dynamic Table Methods
    handleRejectedPolicyAction(row) {
      // Open the rejected item for editing
      console.log('Handle rejected policy action clicked:', row);
      const policy = row.originalPolicy;
      console.log('Original policy data:', policy);
      if (policy) {
        this.openRejectedItem(policy);
      } else {
        console.error('No original policy found in row:', row);
        PopupService.error('Error: Could not find policy data to edit', 'Data Error');
        this.sendPushNotification({
          title: 'Policy Data Error',
          message: 'Could not find policy data to edit',
          category: 'policy',
          priority: 'high',
          user_id: this.currentUserId || 'default_user'
        });
      }
    },
  },
  computed: {
    policyApprovals() {
      // Return all approvals since we're now directly using the policies data
      return this.approvals;
    },
    
    // Combined tasks for overall counts
    allTasks() {
      const myTasks = this.myTasks || [];
      const reviewerTasks = this.reviewerTasks || [];
      return [...myTasks, ...reviewerTasks];
    },
    
    pendingApprovalsCount() {
      return this.allTasks.filter(a => a.ApprovedNot === null).length;
    },
    approvedApprovalsCount() {
      return this.allTasks.filter(a => a.ApprovedNot === true).length;
    },
    rejectedApprovalsCount() {
      return this.allTasks.filter(a => a.ApprovedNot === false).length;
    },
    
    // Tab-specific counts
    myTasksCount() {
      return this.myTasks ? this.myTasks.length : 0;
    },
    reviewerTasksCount() {
      return this.reviewerTasks ? this.reviewerTasks.length : 0;
    },
    sortedPolicies() {
      return [...this.approvals].sort((a, b) => {
        const dateA = new Date(a.ExtractedData?.CreatedByDate || 0);
        const dateB = new Date(b.ExtractedData?.CreatedByDate || 0);
        return dateB - dateA; // Most recent first
      });
    },
    
    // Collapsible Table Computed Properties for My Tasks
    myTasksCollapsibleSections() {
      if (!this.myTasks || !Array.isArray(this.myTasks)) {
        return [];
      }
      return this.generateCollapsibleSections(this.myTasks);
    },
    
    // Collapsible Table Computed Properties for Reviewer Tasks
    reviewerTasksCollapsibleSections() {
      if (!this.reviewerTasks || !Array.isArray(this.reviewerTasks)) {
        return [];
      }
      return this.generateCollapsibleSections(this.reviewerTasks);
    },
    
    // Legacy computed property for backwards compatibility
    collapsibleTableSections() {
      return this.generateCollapsibleSections(this.approvals);
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
    hasUnreviewedSubpolicies() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData || 
          !this.selectedApproval.ExtractedData.subpolicies) {
        return true;
      }
      
      const subpolicies = this.selectedApproval.ExtractedData.subpolicies;
      return subpolicies.some(sub => {
        return sub.approval?.approved === null || sub.approval?.approved === undefined;
      });
    },
    hasRejectedSubpolicies() {
      return this.rejectedSubpolicies && this.rejectedSubpolicies.length > 0;
    },
    hasChanges() {
      if (!this.editingSubpolicy) return false;
      
      // Check if Description or Control have changed from their original values
      const descriptionChanged = this.editingSubpolicy.Description !== this.editingSubpolicy.originalDescription;
      const controlChanged = this.editingSubpolicy.Control !== this.editingSubpolicy.originalControl;
      
      return descriptionChanged || controlChanged;
    },
    rejectedSubpoliciesInPolicy() {
      if (!this.editingPolicy || !this.editingPolicy.ExtractedData || !this.editingPolicy.ExtractedData.subpolicies) {
        return [];
      }
      
      return this.editingPolicy.ExtractedData.subpolicies.filter(sub => 
        sub.approval?.approved === false
      );
    },
    isComplianceApproval() {
      return this.selectedApproval?.ExtractedData?.type === 'compliance';
    },
    
    // Determine if user is viewing review history in the details modal
    isUserViewingReviewHistory() {
      if (!this.selectedApproval) return false;
      
      const currentStatus = this.getApprovalStatus(this.selectedApproval);
      return this.shouldShowReviewHistory(this.selectedApproval, currentStatus);
    },
    approvalStatus() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return null;
      
      if (this.isComplianceApproval) {
        return this.selectedApproval.ExtractedData.compliance_approval || { approved: null, remarks: '' };
      } else {
        return this.selectedApproval.ExtractedData.policy_approval || { approved: null, remarks: '' };
      }
    },
    allSubpoliciesApproved() {
      if (!this.selectedApproval || 
          !this.selectedApproval.ExtractedData || 
          !this.selectedApproval.ExtractedData.subpolicies ||
          this.selectedApproval.ExtractedData.subpolicies.length === 0) {
        return false;
      }
      
      const subpolicies = this.selectedApproval.ExtractedData.subpolicies;
      return subpolicies.every(sub => sub.approval?.approved === true);
    },
    filteredSubpolicies() {
      if (!this.selectedPolicyForSubpolicies || 
          !this.selectedPolicyForSubpolicies.ExtractedData || 
          !this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
        return [];
      }
      
      // If in reviewer mode, show all subpolicies
      if (this.isReviewer) {
        return this.selectedPolicyForSubpolicies.ExtractedData.subpolicies;
      }
      
      // In user mode, only show rejected subpolicies
      return this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.filter(sub => 
        sub.Status === 'Rejected' || 
        (sub.approval && sub.approval.approved === false)
      );
    },
    
    // Dynamic Table Computed Properties
    rejectedTableData() {
      return this.rejectedPolicies.map(policy => {
        const policyId = this.getPolicyId(policy);
        
        // Determine type - default to POLICY for rejected policies
        let type = 'POLICY';
        if (policy.is_compliance) {
          type = 'COMPLIANCE';
        } else if (policy.type === 'subpolicy') {
          type = 'SUBPOLICY';
        }
        
        // Get proper description - use PolicyName first, then Scope as fallback
        let description = 'No Description';
        if (policy.is_compliance) {
          description = policy.ExtractedData?.ComplianceItemDescription || 'No Description';
        } else {
          description = policy.ExtractedData?.PolicyName || 
                       policy.description || 
                       policy.ExtractedData?.Scope || 
                       `Policy ${policyId}`;
        }
        
        // Get rejection reason from multiple possible sources
        let rejectionReason = 'No rejection reason provided';
        if (policy.rejectionReason && policy.rejectionReason !== 'No rejection reason provided') {
          rejectionReason = policy.rejectionReason;
        } else if (policy.ExtractedData?.rejection_reason) {
          rejectionReason = policy.ExtractedData.rejection_reason;
        } else if (policy.ExtractedData?.policy_approval?.remarks) {
          rejectionReason = policy.ExtractedData.policy_approval.remarks;
        } else if (policy.ExtractedData?.cascading_rejection) {
          rejectionReason = `Cascading rejection due to ${policy.ExtractedData.rejected_subpolicy_name || 'subpolicy'} rejection`;
        }
        
        return {
          id: policyId, // Unique key for the table
          policyId: policyId,
          type: type,
          description: description,
          rejectionReason: rejectionReason,
          createdDate: this.formatDate(policy.ExtractedData?.CreatedByDate || policy.createdDate),
          originalPolicy: policy // Keep reference to original data
        };
      });
    }
  }
}
</script>

<style scoped>
@import './PolicyApprover.css';

/* Completely revised modal layering with much higher z-indices */
.subpolicies-modal {
  z-index: 9000 !important;
}

.edit-subpolicy-modal {
  z-index: 10000 !important; /* Dramatically higher z-index */
  position: fixed;
  top: 0; 
  left: 0; 
  right: 0; 
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto !important; /* Force pointer events */
}

.edit-policy-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2), 0 0 0 1000px rgba(0, 0, 0, 0.3);
  position: relative;
  max-height: 80vh;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  animation: fadeIn 0.3s ease-in-out;
  z-index: 10001 !important; /* Content even higher */
}

.reject-modal {
  z-index: 11000 !important; /* Highest z-index to appear on top */
}

/* Override any potential conflicting styles in the base CSS */
.policy-details-modal,
.reject-modal,
.edit-policy-modal,
.subpolicies-modal,
.edit-subpolicy-modal {
  position: fixed !important;
  z-index: auto !important; /* Let our specific z-index values take precedence */
}

/* The rest of your styling remains the same */
.edit-subpolicy-modal label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #4b5563;
}

.edit-subpolicy-modal input,
.edit-subpolicy-modal textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.edit-subpolicy-modal input:focus,
.edit-subpolicy-modal textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.edit-subpolicy-modal button.resubmit-btn {
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.2s;
}

.edit-subpolicy-modal button.resubmit-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Improved styles for subpolicy-inline-edit */
.subpolicy-inline-edit {
  background: #f8fafc;
  border: 2px solid #6366f1;
  border-radius: 8px;
  padding: 24px;
  margin: 15px 0;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.3s ease-out;
  transition: all 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.subpolicy-inline-edit h4 {
  margin-top: 0;
  color: #6366f1;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
}

.subpolicy-inline-edit label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #4b5563;
  font-size: 14px;
}

.subpolicy-inline-edit input,
.subpolicy-inline-edit textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.subpolicy-inline-edit input:focus,
.subpolicy-inline-edit textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.subpolicy-inline-edit input:disabled {
  background-color: #f3f4f6;
  color: #6b7280;
  cursor: not-allowed;
}

.subpolicy-inline-edit textarea {
  min-height: 100px;
  resize: vertical;
}

.subpolicy-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.resubmit-btn {
  background: #6366f1;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

.resubmit-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

.cancel-btn {
  background: #e5e7eb;
  color: #4b5563;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: #d1d5db;
  transform: translateY(-2px);
}

.subpolicy-status {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

.subpolicy-status:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.badge.rejected {
  background-color: #ef4444;
  color: white;
  padding: 4px 12px;
  font-weight: 600;
  font-size: 12px;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.rejection-reason {
  background-color: #fee2e2;
  border-left: 4px solid #ef4444;
  padding: 12px;
  margin: 12px 0;
  color: #991b1b;
  font-size: 14px;
  border-radius: 0 4px 4px 0;
}

.badge.resubmitted {
  background-color: #3b82f6;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
  position: relative;
  animation: pulse-badge 2s infinite;
}

@keyframes pulse-badge {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
  70% { transform: scale(1.05); box-shadow: 0 0 0 5px rgba(59, 130, 246, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}

/* Styles for resubmitted items */
.resubmitted-item {
  border-left: 4px solid #3b82f6 !important;
  background-color: rgba(59, 130, 246, 0.05);
  position: relative;
}

.resubmitted-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -4px;
  height: 100%;
  width: 4px;
  background-color: #3b82f6;
  animation: pulse-border 2s infinite;
}

@keyframes pulse-border {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

/* Subpolicy header with better layout */
.subpolicy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

/* Version tag styling */
.subpolicy-version {
  margin-bottom: 10px;
}

.version-tag {
  background-color: #3b82f6;
  color: white;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  font-weight: 600;
  margin-right: 10px;
}

/* Edit history styling */
.edit-history {
  margin-top: 15px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.edit-history-header {
  background-color: #3b82f6;
  color: white;
  padding: 10px 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-history-content {
  padding: 15px;
  background-color: #f9fafb;
}

.edit-field {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #e5e7eb;
}

.edit-field:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.field-label {
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 5px;
  font-size: 13px;
}

.field-previous {
  padding: 10px;
  background-color: #fee2e2;
  border-radius: 4px;
  margin-bottom: 10px;
  position: relative;
  text-decoration: line-through;
  color: #991b1b;
  font-size: 14px;
}

.field-value {
  padding: 10px;
  background-color: #dcfce7;
  border-radius: 4px;
  color: #166534;
  font-size: 14px;
}

/* Subpolicy content section */
.subpolicy-content {
  margin-bottom: 15px;
}

.view-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}

.view-button:hover {
  background-color: #2563eb;
}

/* Add styles for approved date display */
.policy-approved-date {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border-radius: 6px;
  border-left: 4px solid #22c55e;
}

.date-label {
  font-weight: 600;
  color: #065f46;
}

.date-value {
  color: #059669;
  font-family: 'Courier New', monospace;
}

.approval-status.approved {
  background-color: #dcfce7;
  color: #166534;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
}

/* Styles for changes summary in edit modal */
.changes-summary {
  margin: 15px 0;
  border: 1px solid #3b82f6;
  border-radius: 8px;
  overflow: hidden;
  background-color: rgba(59, 130, 246, 0.05);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.changes-header {
  background-color: #3b82f6;
  color: white;
  padding: 10px 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.changes-content {
  padding: 12px 15px;
}

.change-item {
  padding: 8px 0;
  color: #4b5563;
  font-size: 14px;
  border-bottom: 1px dashed #e5e7eb;
}

.change-item:last-child {
  border-bottom: none;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-actions .resubmit-btn {
  background-color: #6366f1;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.form-actions .resubmit-btn:hover:not(:disabled) {
  background-color: #4f46e5;
  transform: translateY(-2px);
}

.form-actions .resubmit-btn:disabled {
  background-color: #c7d2fe;
  cursor: not-allowed;
  color: #6366f1;
}

.form-actions .cancel-btn {
  background-color: #e5e7eb;
  color: #4b5563;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.form-actions .cancel-btn:hover {
  background-color: #d1d5db;
  transform: translateY(-2px);
}

/* Improve edit modal styling */
.edit-modal {
  width: 90%;
  max-width: 700px;
  padding: 30px;
  border-radius: 12px;
}

.edit-modal h2 {
  color: #4f46e5;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #c7d2fe;
  font-size: 22px;
}

.edit-modal .form-group {
  margin-bottom: 20px;
}

.edit-modal label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #4b5563;
  font-size: 14px;
}

.edit-modal input,
.edit-modal textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.edit-modal input:focus,
.edit-modal textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.edit-modal textarea {
  min-height: 120px;
  resize: vertical;
}

.edit-modal input:disabled {
  background-color: #f3f4f6;
  color: #6b7280;
  cursor: not-allowed;
}

/* Badge for approved-only view */
.approved-only-badge {
  background-color: #10b981;
  color: white;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  margin-left: 10px;
  font-weight: 500;
  display: inline-block;
  vertical-align: middle;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

/* Policy status indicator styles */
.policy-status-indicator {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  background: #f8fafc;
  padding: 10px 15px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.status-label {
  font-weight: 600;
  margin-right: 10px;
  color: #4b5563;
}

.status-value {
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  text-align: center;
}

.status-approved {
  background-color: #10b981;
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.status-rejected {
  background-color: #ef4444;
  color: white;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.status-pending {
  background-color: #f59e0b;
  color: white;
  box-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
}

/* Add these styles to your component */
.rejection-reason-section {
  margin: 15px 0;
  padding: 15px;
  background-color: #fff5f5;
  border-left: 4px solid #ef4444;
  border-radius: 0 4px 4px 0;
}

.rejection-reason-section h4 {
  color: #b91c1c;
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 600;
}

.rejection-message {
  color: #991b1b;
  font-size: 14px;
  line-height: 1.5;
}

/* Add these styles */
.rejected-subpolicy-details {
  margin: 15px 0;
  padding: 15px;
  background-color: #fff5f5;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

.status-badge.rejected {
  background-color: #ef4444;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.rejection-reason {
  margin-top: 12px;
  padding: 10px 15px;
  background-color: #fee2e2;
  border-radius: 6px;
}

.reason-header {
  font-weight: 600;
  color: #b91c1c;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.reason-content {
  color: #991b1b;
  font-size: 14px;
  line-height: 1.5;
}

/* Add these styles */
.policy-rejection-reason {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #fee2e2;
  border-radius: 4px;
  color: #991b1b;
  font-size: 14px;
}

/* Add these styles */
.rejection-reason-container {
  margin: 15px 0 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.rejection-reason-header {
  background-color: #ef4444;
  color: white;
  padding: 12px 15px;
  font-weight: 600;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.rejection-reason-content {
  padding: 15px;
  background-color: #fee2e2;
  color: #991b1b;
  font-size: 14px;
  line-height: 1.6;
}

/* Overlay for modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(30, 41, 59, 0.45); /* dark semi-transparent */
  z-index: 99998; /* below modal, above everything else */
  display: flex;
  align-items: center;
  justify-content: center;
  /* Optional: backdrop blur */
  backdrop-filter: blur(2px);
}

/* Modal itself */
.subpolicies-modal {
  z-index: 99999 !important;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none; /* Only modal content should be interactive */
}

.subpolicies-modal-content {
  z-index: 100000 !important;
  position: relative;
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  min-width: 400px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 32px rgba(0,0,0,0.18);
  pointer-events: auto; /* Make modal content interactive */
}
</style> 