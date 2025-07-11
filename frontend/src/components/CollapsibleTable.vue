<template>
  <div class="task-section" :class="sectionConfig.statusClass">
    <div class="task-section-header" @click="toggleSection">
      <div class="header-left">
        <component 
          :is="isExpanded ? PhCaretDown : PhCaretRight" 
          :size="16" 
        />
        <div :class="['status-chip', sectionConfig.statusClass]">
          <component :is="headerIcon" :size="14" :weight="headerIconWeight" />
          <span>{{ sectionConfig.name }}</span>
        </div>
      </div>
      <div class="header-right">
        <PhDotsThree :size="20" />
      </div>
    </div>
    
    <div v-if="isExpanded">
      <table class="task-table">
        <thead>
          <tr>
            <th v-for="header in tableHeaders" :key="header.key" :class="header.className" :style="{ width: columnWidths[header.key] ? columnWidths[header.key] + 'px' : (header.width ? header.width : 'auto') }">
              <div class="column-header" style="position: relative;">
                {{ header.label }}
                <span v-if="header.sortable" class="filter-arrows">
                  <button 
                    class="sort-btn"
                    v-if="sortKey === header.key && sortOrder === 'asc'"
                    @click.stop="sortByDesc(header.key)"
                    :aria-label="'Sort ' + header.label + ' descending'"
                  >
                    ▲
                  </button>
                  <button 
                    class="sort-btn"
                    v-if="sortKey !== header.key || sortOrder === 'desc'"
                    @click.stop="sortByDesc(header.key)"
                    :aria-label="'Sort ' + header.label + ' descending'"
                  >
                    ▼
                  </button>
                  <button 
                    class="sort-btn"
                    v-if="sortKey === header.key && sortOrder === 'desc'"
                    @click.stop="sortByAsc(header.key)"
                    :aria-label="'Sort ' + header.label + ' ascending'"
                  >
                    ▼
                  </button>
                </span>
                <!-- Resize handle -->
                <div 
                  class="resize-handle"
                  @mousedown="startResize($event, header.key)"
                  @touchstart="startResize($event, header.key)"
                ></div>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in sortedTasks" :key="task.incidentId">
            <td v-for="header in tableHeaders" :key="header.key" :class="header.className" :style="{ width: columnWidths[header.key] ? columnWidths[header.key] + 'px' : (header.width ? header.width : 'auto') }">
              <template v-if="header.key === 'actions'">
                <button class="view-details-btn" @click="$emit('taskClick', task)">
                  <i class="fas fa-eye"></i> VIEW DETAILS
                </button>
              </template>
              <template v-else-if="['criticality','priority','status'].includes(header.key)">
                <span v-html="task[header.key]"></span>
              </template>
              <template v-else>
                <div 
                  class="cell-content"
                  :class="{ 'truncated': isTextTruncated(task[header.key]) }"
                  :title="isTextTruncated(task[header.key]) ? task[header.key] : ''"
                >
                  {{ task[header.key] }}
                </div>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
      <Pagination
        v-if="pagination"
        :current-page="pagination.currentPage"
        :total-pages="pagination.totalPages"
        :page-size="pagination.pageSize"
        :total-items="pagination.totalCount"
        :page-size-options="pagination.pageSizeOptions || [6, 15, 30, 50]"
        @update:page="page => { if (page > pagination.currentPage) { onNextPage && onNextPage(); } else if (page < pagination.currentPage) { onPrevPage && onPrevPage(); } }"
        @update:pageSize="size => pagination.onPageSizeChange && pagination.onPageSizeChange(size)"
      />
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { computed, ref, onMounted, onBeforeUnmount } from 'vue';
import Pagination from './Pagination.vue';
import { 
  PhCaretDown, 
  PhCaretRight, 
  PhDotsThree, 
  PhCircleNotch,
  PhCircle,
  PhCheckCircle
} from '@phosphor-icons/vue';

const props = defineProps({
  sectionConfig: {
    type: Object,
    required: true
  },
  tableHeaders: {
    type: Array,
    required: true
  },
  isExpanded: {
    type: Boolean,
    default: true
  },
  pagination: {
    type: Object,
    default: null
  },
  onNextPage: {
    type: Function,
    default: null
  },
  onPrevPage: {
    type: Function,
    default: null
  }
});

// Add debugging for pagination
console.log('CollapsibleTable props:', {
  sectionName: props.sectionConfig?.name,
  pagination: props.pagination,
  isExpanded: props.isExpanded,
  tasksCount: props.sectionConfig?.tasks?.length
});

const emit = defineEmits(['toggle', 'addTask', 'taskClick']);

const toggleSection = () => {
  emit('toggle');
};

const headerIcon = computed(() => {
  switch (props.sectionConfig.name) {
    case 'Pending':
    case 'Open':
    case 'Assigned':
      return PhCircle;
    case 'In Progress':
    case 'Under Review':
    case 'Pending Review':
    case 'Scheduled':
      return PhCircleNotch;
    case 'Completed':
    case 'Closed':
    case 'Approved':
      return PhCheckCircle;
    case 'Rejected':
      return PhCircle;
    case 'Not Assigned':
    case 'Unknown':
      return PhCircle;
    default:
      return PhCircle;
  }
});

const headerIconWeight = computed(() => {
  const status = props.sectionConfig.name;
  return (status === 'Pending' || status === 'Open' || status === 'Rejected' || status === 'Assigned' || status === 'Not Assigned' || status === 'Unknown') ? 'light' : 'fill';
});

// Function to check if text should be truncated
const isTextTruncated = (text) => {
  if (!text || typeof text !== 'string') return false;
  return text.length > 50; // Adjust this threshold as needed
};

// Sorting state
const sortKey = ref('');
const sortOrder = ref('asc');

const sortByAsc = (key) => {
  sortKey.value = key;
  sortOrder.value = 'asc';
};
const sortByDesc = (key) => {
  sortKey.value = key;
  sortOrder.value = 'desc';
};

const sortedTasks = computed(() => {
  if (!sortKey.value) return props.sectionConfig.tasks;
  return [...props.sectionConfig.tasks].sort((a, b) => {
    const aVal = a[sortKey.value];
    const bVal = b[sortKey.value];
    if (aVal == null) return 1;
    if (bVal == null) return -1;
    if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1;
    return 0;
  });
});

// Resizable columns
const columnWidths = ref({});
const resizing = ref({ active: false, columnKey: null, startX: 0, startWidth: 0 });

const startResize = (e, columnKey) => {
  e.preventDefault();
  resizing.value.active = true;
  resizing.value.columnKey = columnKey;
  resizing.value.startX = e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;
  resizing.value.startWidth = columnWidths.value[columnKey] || 150;
};

const onResizeMove = (e) => {
  if (!resizing.value.active) return;
  const clientX = e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;
  const delta = clientX - resizing.value.startX;
  let newWidth = resizing.value.startWidth + delta;
  if (newWidth < 50) newWidth = 50;
  columnWidths.value = { ...columnWidths.value, [resizing.value.columnKey]: newWidth };
};

const onResizeEnd = () => {
  if (resizing.value.active) {
    resizing.value.active = false;
    resizing.value.columnKey = null;
  }
};

onMounted(() => {
  window.addEventListener('mousemove', onResizeMove);
  window.addEventListener('mouseup', onResizeEnd);
  window.addEventListener('touchmove', onResizeMove);
  window.addEventListener('touchend', onResizeEnd);
});
onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onResizeMove);
  window.removeEventListener('mouseup', onResizeEnd);
  window.removeEventListener('touchmove', onResizeMove);
  window.removeEventListener('touchend', onResizeEnd);
});
</script>

<style scoped>
/* CSS Variables for status colors */
:root {
  --chip-pending-text: #2196f3;
  --chip-pending-bg: #e3f2fd;
  --chip-pending-border: rgba(33, 150, 243, 0.3);
  --chip-pending-icon: #2196f3;
  
  --chip-inprogress-text: #ff9800;
  --chip-inprogress-bg: #fff8e1;
  --chip-inprogress-border: rgba(255, 152, 0, 0.3);
  --chip-inprogress-icon: #ff9800;
  
  --chip-completed-text: #4caf50;
  --chip-completed-bg: #e8f5e8;
  --chip-completed-border: rgba(76, 175, 80, 0.3);
  --chip-completed-icon: #4caf50;
  
  --chip-rejected-text: #f44336;
  --chip-rejected-bg: #ffebee;
  --chip-rejected-border: rgba(244, 67, 54, 0.3);
  --chip-rejected-icon: #f44336;
  
  --table-section-border: #e0e0e0;
  --table-section-bg: #ffffff;
  --table-header-text: #333333;
  --table-header-dots: #666666;
  --table-row-text: #333333;
  --table-subheader-text: #666666;
  --incident-primary: #6a5acd;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.task-section {
  border: 1px solid var(--table-section-border);
  border-radius: 8px;
  margin-bottom: 24px;
  background: var(--table-section-bg);
}

.task-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 500;
  color: var(--table-header-text);
  transition: background-color 0.2s ease;
}

.task-section-header:hover {
  background-color: #f8f9fa;
}

.task-section-header:active {
  background-color: #e9ecef;
}

.task-section-header .header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-section-header .header-right {
  color: var(--table-header-dots);
}

.toggle-icon {
  font-size: 14px;
  color: var(--table-header-text);
  transition: transform 0.2s ease;
}

.status-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
}

.status-chip.pending {
  color: var(--chip-pending-text);
  background-color: var(--chip-pending-bg);
  border-color: var(--chip-pending-border);
}

.status-chip.pending .ph-circle {
  color: var(--chip-pending-icon);
}

.status-chip.in-progress {
  color: var(--chip-inprogress-text);
  background-color: var(--chip-inprogress-bg);
  border-color: var(--chip-inprogress-border);
}

.status-chip.in-progress .ph-circle-notch {
  color: var(--chip-inprogress-icon);
  animation: spin 2s linear infinite;
}

.status-chip.completed {
  color: var(--chip-completed-text);
  background-color: var(--chip-completed-bg);
  border-color: var(--chip-completed-border);
}

.status-chip.completed .ph-check-circle {
  color: var(--chip-completed-icon);
}

.status-chip.rejected {
  color: var(--chip-rejected-text);
  background-color: var(--chip-rejected-bg);
  border-color: var(--chip-rejected-border);
}

.status-chip.rejected .ph-circle {
  color: var(--chip-rejected-icon);
}

/* Remove flex/grid for .task-list-header and .task-item, add table styling */
.task-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 0;
}
.task-table th, .task-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}
.task-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #495057;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #e0e0e0;
  border-right: 1px solid #e0e0e0;
  border-top: 1px solid #e0e0e0;
  border-left: 1px solid #e0e0e0;
}
.task-table td {
  border-bottom: 1px solid #e0e0e0;
  border-right: 1px solid #e0e0e0;
  border-left: 1px solid #e0e0e0;
  border-top: 1px solid #e0e0e0;
}
.filter-arrows {
  display: inline-flex;
  flex-direction: column;
  margin-left: 4px;
}
.sort-btn {
  background: none;
  border: none;
  padding: 0 2px;
  font-size: 18px;
  color: #333;
  cursor: pointer;
  line-height: 1;
  transition: color 0.2s;
  margin-left: 2px;
}
.sort-btn:focus, .sort-btn:hover {
  color: #7B6FDD;
}
.task-table tr:last-child td {
  border-bottom: none;
}

/* Cell content with truncation */
.cell-content {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: default;
}

.cell-content.truncated {
  position: relative;
}

.cell-content.truncated:hover::after {
  content: attr(title);
  position: absolute;
  left: 0;
  top: 100%;
  background: #333;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  white-space: normal;
  max-width: 300px;
  word-wrap: break-word;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  margin-top: 4px;
}

/* Ensure the actions column has a minimum width */
.task-list-header .task-actions,
.task-item .task-actions {
  min-width: 140px;
  max-width: 180px;
}

.incident-id {
  font-weight: 600;
  color: var(--table-row-text);
}

.incident-title {
  font-weight: 500;
  color: var(--table-row-text);
}

.incident-priority {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.incident-status {
  display: flex;
  align-items: center;
}

.incident-origin {
  color: var(--table-row-text);
  font-size: 14px;
}

.incident-date {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--table-subheader-text);
  font-size: 14px;
}

.incident-time {
  color: var(--table-subheader-text);
  font-size: 14px;
}

.incident-description {
  color: var(--table-row-text);
  font-size: 14px;
}

.incident-actions {
  display: flex;
  justify-content: center;
  color: var(--table-header-dots);
  cursor: pointer;
}

.clickable-task-name {
  cursor: pointer;
  color: var(--table-row-text);
  text-decoration: none;
}

.clickable-task-name:hover {
  color: var(--incident-primary);
  text-decoration: underline;
}

/* Status Badge Styles */
.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  min-width: 120px;
}

.status-badge.status-open {
  background-color: #fff3e0;
  color: #ff9800;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.status-badge.status-assigned {
  background-color: #e3f2fd;
  color: #2196f3;
  border: 1px solid rgba(33, 150, 243, 0.3);
}

.status-badge.status-closed {
  background-color: #e8f5e9;
  color: #4caf50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.status-badge.status-rejected {
  background-color: #ffebee;
  color: #f44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.status-badge.status-escalated {
  background-color: #f3e5f5;
  color: #9c27b0;
  border: 1px solid rgba(156, 39, 176, 0.3);
}

/* Action Button Styles */
.actions-dropdown {
  position: relative;
  display: inline-block;
  z-index: 9999;
}

.actions-button {
  background: linear-gradient(135deg, #7B6FDD 0%, #9B8CEB 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(123, 111, 221, 0.25);
  position: relative;
  animation: actionPulse 2s infinite ease-in-out, buttonBreath 3s infinite ease-in-out;
}

.actions-button:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(123, 111, 221, 0.4);
  background: linear-gradient(135deg, #8F7EE7 0%, #A994F1 100%);
  animation: buttonGlow 1.5s infinite ease-in-out;
}

.actions-button .gear-icon {
  animation: rotateGear 3s linear infinite;
}

.actions-button:hover .gear-icon {
  animation: rotateGear 1s linear infinite;
}

.dropdown-arrow {
  transition: transform 0.2s;
}

.dropdown-arrow.rotate {
  transform: rotate(180deg);
}

.actions-dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 180px;
  background: #ffffff !important;
  border: 2px solid #d0d0d0;
  border-radius: 8px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3), 0 5px 15px rgba(0, 0, 0, 0.2);
  z-index: 999999;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  margin-top: 8px;
  backdrop-filter: blur(0px);
}

.actions-dropdown-menu.show {
  opacity: 1 !important;
  visibility: visible !important;
  transform: translateY(0) !important;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 500;
  color: #333333 !important;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
  background: #ffffff !important;
  background-color: #ffffff !important;
  width: 100%;
  text-align: left;
  position: relative;
  z-index: 1000000;
  opacity: 1 !important;
  filter: none !important;
  -webkit-backdrop-filter: none !important;
  backdrop-filter: none !important;
}

.dropdown-item:hover {
  background: #f0f0f0 !important;
  background-color: #f0f0f0 !important;
  color: #7B6FDD !important;
  transform: translateX(2px);
  opacity: 1 !important;
  filter: none !important;
  -webkit-backdrop-filter: none !important;
  backdrop-filter: none !important;
}

.dropdown-item:not(:last-child) {
  border-bottom: 1px solid #f0f0f0;
}

.dropdown-item i {
  width: 16px;
  text-align: center;
  font-size: 14px;
}

/* View Details Button for Processed Items */
.view-details-btn {
  background: linear-gradient(135deg, #6C757D 0%, #8A9BA8 100%);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.view-details-btn:hover {
  background: linear-gradient(135deg, #5A6268 0%, #78909C 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
}

.view-details-btn i {
  font-size: 13px;
}

/* Priority Classes */
.priority-high-priority {
  color: var(--priority-high-text);
}

.priority-normal-priority {
  color: var(--priority-normal-text);
}

.priority-low-priority {
  color: var(--priority-low-text);
}

.priority-none {
  color: var(--priority-none-text);
}

/* Keyframe Animations */
@keyframes actionPulse {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(123, 111, 221, 0.25);
  }
  50% {
    box-shadow: 0 4px 16px rgba(123, 111, 221, 0.4);
  }
}

@keyframes rotateGear {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes buttonBreath {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

@keyframes buttonGlow {
  0%, 100% {
    box-shadow: 0 6px 20px rgba(123, 111, 221, 0.4);
  }
  50% {
    box-shadow: 0 8px 30px rgba(123, 111, 221, 0.6);
  }
}

/* Resize handle styles */
.resize-handle {
  position: absolute;
  right: 0;
  top: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  z-index: 10;
  background: transparent;
}
.resize-handle:hover {
  background: #e0e0e0;
}
</style> 