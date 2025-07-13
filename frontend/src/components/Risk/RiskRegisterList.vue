<template>
  <div class="risk-register-container">
    <!-- Export Controls -->
    <div class="risk-register-export-controls" style="display: flex; justify-content: flex-end; align-items: center; gap: 8px; margin-bottom: 16px;">
      <select v-model="selectedExportFormat" class="risk-register-export-dropdown" style="min-width: 120px; height: 32px; border-radius: 8px; border: 1.5px solid #e2e8f0; font-size: 0.85rem; padding: 0 10px; background: #fff; color: #222;">
        <option value="" disabled>Select format</option>
        <option value="xlsx">Excel (.xlsx)</option>
        <option value="pdf">PDF (.pdf)</option>
        <option value="csv">CSV (.csv)</option>
        <option value="json">JSON (.json)</option>
        <option value="xml">XML (.xml)</option>
        <option value="txt">Text (.txt)</option>
      </select>
      <button @click="exportRiskRegister" :disabled="!selectedExportFormat" style="padding: 6px 16px; border-radius: 8px; border: none; font-size: 0.85rem; font-weight: 600; cursor: pointer; background: #4f6cff; color: #fff; transition: background 0.2s;">
        Export
      </button>
    </div>
    <!-- Add PopupModal component -->
    <PopupModal />
    
    <div class="risk-register-header-row">
      <h2 class="risk-register-title"> Risk Register List</h2>
    </div>
    
    <!-- Filters Section - Search bar and dropdowns -->
    <div class="risk-register-filters-section">
      <!-- Search bar row -->
      <div class="risk-register-search-row">
        <Dynamicalsearch 
          v-model="searchQuery" 
          placeholder="Search risks..."
        />
      </div>
      
      <!-- Dropdowns row -->
      <div class="risk-register-dropdowns-row">
        <CustomDropdown
          :config="criticalityFilter"
          v-model="selectedCriticality"
          @change="handleFilterChange"
        />
        <CustomDropdown
          :config="categoryFilter"
          v-model="selectedCategory"
          @change="handleFilterChange"
        />
      </div>
    </div>

    <!-- Dynamic Table -->
    <DynamicTable
      :title="''"
      :data="tableData"
      :columns="tableColumns"
      :filters="[]"
      :show-checkbox="false"
      :show-actions="true"
      :show-pagination="true"
      :default-page-size="10"
      unique-key="RiskId"
      @filter-change="handleFilterChange"
      @sort-change="handleSortChange"
      @page-change="handlePageChange"
    >
      <template #actions="{ row }">
        <button @click="viewRiskDetails(row.RiskId)" class="risk-register-view-btn">
          View Risk
        </button>
      </template>
    </DynamicTable>
  </div>
</template>

<script>
import './RiskRegisterList.css'
import axios from 'axios'
import DynamicTable from '../DynamicTable.vue'
import Dynamicalsearch from '../Dynamicalsearch.vue'
import CustomDropdown from '../CustomDropdown.vue'
import { PopupModal } from '@/modules/popup'

export default {
  name: 'RiskRegisterList',
  components: {
    DynamicTable,
    Dynamicalsearch,
    CustomDropdown,
    PopupModal
  },
  data() {
    return {
      risks: [],
      selectedCriticality: '',
      selectedCategory: '',
      searchQuery: '',
      loading: false,
      selectedExportFormat: '',
      // Filter configurations for CustomDropdown
      criticalityFilter: {
        name: 'criticality',
        label: 'Criticality',
        values: [],
        defaultValue: ''
      },
      categoryFilter: {
        name: 'category',
        label: 'Category',
        values: [],
        defaultValue: ''
      },
      // Table columns configuration
      tableColumns: [
        {
          key: 'RiskId',
          label: 'RISK ID',
          sortable: true,
          cellClass: 'risk-register-id'
        },
        {
          key: 'RiskTitle',
          label: 'RISK TITLE',
          sortable: true
        },
        {
          key: 'RiskType',
          label: 'RISK TYPE',
          sortable: true
        },
        {
          key: 'ComplianceId',
          label: 'COMPLIANCE ID',
          sortable: true
        },
        {
          key: 'Category',
          label: 'CATEGORY',
          sortable: true
        },
        {
          key: 'Criticality',
          label: 'CRITICALITY',
          sortable: true
        }
      ]
    }
  },
  computed: {
    uniqueCriticality() {
      return [...new Set(this.risks.map(i => i.Criticality).filter(Boolean))]
    },
    uniqueCategory() {
      return [...new Set(this.risks.map(i => i.Category).filter(Boolean))]
    },

    filteredRisks() {
      let filtered = this.risks
      
      // Search filter - add type checking to prevent toLowerCase error
      if (this.searchQuery && typeof this.searchQuery === 'string' && this.searchQuery.trim() !== '') {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(risk =>
          (risk.RiskTitle && risk.RiskTitle.toLowerCase().includes(query)) ||
          (risk.RiskDescription && risk.RiskDescription.toLowerCase().includes(query)) ||
          (risk.Category && risk.Category.toLowerCase().includes(query)) ||
          (risk.Criticality && risk.Criticality.toLowerCase().includes(query))
        )
      }
      
      // Criticality filter
      if (this.selectedCriticality) {
        filtered = filtered.filter(risk => risk.Criticality === this.selectedCriticality)
      }
      
      // Category filter
      if (this.selectedCategory) {
        filtered = filtered.filter(risk => risk.Category === this.selectedCategory)
      }
      
      return filtered
    },
    
    // Transform data for DynamicTable with proper status formatting
    tableData() {
      return this.filteredRisks.map(risk => ({
        ...risk,
        RiskType: risk.RiskType || 'N/A'
      }))
    }
  },
  watch: {
    searchQuery() {
      // Reset to first page when search changes
    },
    selectedCriticality() {
      // Reset to first page when filter changes
    },
    selectedCategory() {
      // Reset to first page when filter changes
    }
  },
  mounted() {
    this.fetchRisks()
  },
  methods: {
    fetchRisks() {
      this.loading = true
      axios.get('http://localhost:8000/api/risks/')
        .then(response => {
          this.risks = response.data
          this.updateFilterOptions()
          this.loading = false
          // Send push notification for successful risk data fetch
          this.sendPushNotification({
            title: 'Risk Register Updated',
            message: `Successfully loaded ${this.risks.length} risks from the Risk Register.`,
            category: 'risk',
            priority: 'medium',
            user_id: 'default_user'
          })
        })
        .catch(error => {
          console.error('Error fetching risks:', error)
          this.loading = false
          // Send push notification for error
          this.sendPushNotification({
            title: 'Risk Register Load Failed',
            message: `Failed to load risks from the Risk Register: ${error.response?.data?.error || error.message}`,
            category: 'risk',
            priority: 'high',
            user_id: 'default_user'
          })
        })
    },
    async exportRiskRegister() {
      if (!this.selectedExportFormat) return;
      try {
        // Prepare export data (filtered risks)
        const exportData = this.tableData;
        const payload = {
          export_format: this.selectedExportFormat,
          risk_data: exportData,
          user_id: 'default_user',
          file_name: 'risk_register_export'
        };
        const response = await fetch('http://localhost:8000/api/export-risk-register/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (result.success) {
          alert('Export successful!');
        } else {
          alert('Export failed: ' + (result.error || 'Unknown error'));
        }
      } catch (error) {
        alert('Export error: ' + error.message);
      }
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
    
    updateFilterOptions() {
      // Update criticality filter options
      const criticalityOptions = this.uniqueCriticality.map(c => ({
        value: c,
        label: c
      }))
      this.criticalityFilter.values = [
        { value: '', label: 'All Criticality' },
        ...criticalityOptions
      ]
      
      // Update category filter options
      const categoryOptions = this.uniqueCategory.map(cat => ({
        value: cat,
        label: cat
      }))
      this.categoryFilter.values = [
        { value: '', label: 'All Category' },
        ...categoryOptions
      ]
    },
    
    handleSearch(value) {
      this.searchQuery = value
    },
    
    handleFilterChange(filter) {
      if (filter.name === 'criticality') {
        this.selectedCriticality = filter.value
      } else if (filter.name === 'category') {
        this.selectedCategory = filter.value
      }
    },
    
    handleSortChange(sortInfo) {
      // Handle sorting if needed
      console.log('Sort changed:', sortInfo)
    },
    
    handlePageChange(page) {
      // Handle page change if needed
      console.log('Page changed:', page)
    },
    
    viewRiskDetails(riskId) {
      // Find the risk data for the notification
      const risk = this.risks.find(r => r.RiskId === riskId)
      
      // Send push notification for risk view action
      this.sendPushNotification({
        title: 'Risk Details Viewed',
        message: `Risk "${risk?.RiskTitle || 'Untitled Risk'}" (ID: ${riskId}) details have been viewed.`,
        category: 'risk',
        priority: 'low',
        user_id: 'default_user'
      })
      
      this.$router.push(`/view-risk/${riskId}`)
    },

    getCriticalityClass(criticality) {
      if (!criticality || typeof criticality !== 'string') return ''
      
      criticality = criticality.toLowerCase()
      if (criticality === 'critical') return 'risk-register-priority-critical'
      if (criticality === 'high') return 'risk-register-priority-high'
      if (criticality === 'medium') return 'risk-register-priority-medium'
      if (criticality === 'low') return 'risk-register-priority-low'
      return ''
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      
      const date = new Date(dateString)
      return date.toLocaleDateString()
    }
  }
}
</script>