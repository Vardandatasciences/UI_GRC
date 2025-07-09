<template>
  <div v-if="!showRejectModal">
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h2 class="dashboard-heading">Framework Approver</h2>
        <div class="dashboard-actions">
          <!-- User dropdown for GRC Administrators -->
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
        </div>
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
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import CollapsibleTable from '@/components/CollapsibleTable.vue';
import axios from 'axios';

export default {
  name: 'FrameworkApprover',
  components: {
    CollapsibleTable
  },
  setup() {
    // State
    const activeTab = ref('myTasks');
    const selectedUserId = ref('');
    const availableUsers = ref([]);
    const selectedUserInfo = ref(null);
    const showDetails = ref(false);
    const selectedFramework = ref(null);
    const showRejectModal = ref(false);
    const rejectionComment = ref('');
    const expandedSections = ref({});
    const isLoading = ref(false);
    
    // Counts
    const pendingApprovalsCount = ref(0);
    const approvedApprovalsCount = ref(0);
    const rejectedApprovalsCount = ref(0);
    const myTasksCount = ref(0);
    const reviewerTasksCount = ref(0);

    // Table headers
    const tableHeaders = [
      { key: 'id', label: 'ID' },
      { key: 'name', label: 'Name' },
      { key: 'type', label: 'Type' },
      { key: 'status', label: 'Status' },
      { key: 'submittedBy', label: 'Submitted By' },
      { key: 'submittedDate', label: 'Submitted Date' }
    ];

    // Computed
    const isAdministrator = computed(() => {
      // Check if user has administrator role
      return true; // Replace with actual role check
    });

    const myTasksCollapsibleSections = ref([]);
    const reviewerTasksCollapsibleSections = ref([]);

    // Methods
    const fetchUsers = async () => {
      try {
        const response = await axios.get('/api/users/');
        availableUsers.value = response.data;
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    };

    const onUserChange = async () => {
      if (selectedUserId.value) {
        selectedUserInfo.value = availableUsers.value.find(user => user.UserId === selectedUserId.value);
      } else {
        selectedUserInfo.value = null;
      }
      await refreshData();
    };

    const refreshData = async () => {
      isLoading.value = true;
      try {
        const userId = selectedUserId.value || 'current';
        const response = await axios.get(`/api/frameworks/approvals/${userId}`);
        
        // Update counts
        pendingApprovalsCount.value = response.data.pendingCount || 0;
        approvedApprovalsCount.value = response.data.approvedCount || 0;
        rejectedApprovalsCount.value = response.data.rejectedCount || 0;
        
        // Update tasks
        myTasksCollapsibleSections.value = formatTasksForCollapsibleTable(response.data.myTasks || []);
        reviewerTasksCollapsibleSections.value = formatTasksForCollapsibleTable(response.data.reviewerTasks || []);
        
        // Update task counts
        myTasksCount.value = response.data.myTasks?.length || 0;
        reviewerTasksCount.value = response.data.reviewerTasks?.length || 0;
      } catch (error) {
        console.error('Error refreshing data:', error);
      } finally {
        isLoading.value = false;
      }
    };

    const formatTasksForCollapsibleTable = (tasks) => {
      // Group tasks by status
      const grouped = tasks.reduce((acc, task) => {
        const status = task.status || 'Pending';
        if (!acc[status]) {
          acc[status] = [];
        }
        acc[status].push(task);
        return acc;
      }, {});

      // Convert to collapsible sections
      return Object.entries(grouped).map(([status, tasks]) => ({
        name: status,
        items: tasks,
        pagination: {
          total: tasks.length,
          perPage: 10,
          currentPage: 1
        }
      }));
    };

    const switchTab = (tab) => {
      activeTab.value = tab;
    };

    const toggleSection = (sectionName) => {
      expandedSections.value[sectionName.toLowerCase()] = !expandedSections.value[sectionName.toLowerCase()];
    };

    const handleTaskClick = (task) => {
      selectedFramework.value = task;
      showDetails.value = true;
    };

    // Lifecycle hooks
    onMounted(async () => {
      await fetchUsers();
      await refreshData();
    });

    return {
      // State
      activeTab,
      selectedUserId,
      availableUsers,
      selectedUserInfo,
      showDetails,
      selectedFramework,
      showRejectModal,
      rejectionComment,
      expandedSections,
      isLoading,
      
      // Counts
      pendingApprovalsCount,
      approvedApprovalsCount,
      rejectedApprovalsCount,
      myTasksCount,
      reviewerTasksCount,
      
      // Computed
      isAdministrator,
      myTasksCollapsibleSections,
      reviewerTasksCollapsibleSections,
      tableHeaders,
      
      // Methods
      onUserChange,
      refreshData,
      switchTab,
      toggleSection,
      handleTaskClick
    };
  }
};
</script>

<style scoped>
@import './FrameworkApprover.css';
</style> 