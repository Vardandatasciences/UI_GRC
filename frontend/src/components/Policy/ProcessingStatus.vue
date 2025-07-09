<template>
  <div class="processing-status">
    <div class="status-header">
      <h4>Processing Status</h4>
      <div class="status-badge" :class="currentStatus.toLowerCase()">
        {{ currentStatus }}
      </div>
    </div>

    <div class="status-timeline">
      <div v-for="(status, index) in processingSteps" 
           :key="index"
           class="timeline-item"
           :class="{ 
             'completed': status.completed, 
             'current': status.current,
             'pending': !status.completed && !status.current 
           }">
        <div class="timeline-icon">
          <i :class="status.icon"></i>
        </div>
        <div class="timeline-content">
          <div class="timeline-title">{{ status.title }}</div>
          <div class="timeline-details" v-if="status.details">{{ status.details }}</div>
          <div class="timeline-time" v-if="status.time">{{ status.time }}</div>
        </div>
      </div>
    </div>

    <div class="current-operation" v-if="currentOperation">
      <div class="operation-header">
        <i class="fas fa-sync-alt fa-spin"></i>
        <span>Current Operation</span>
      </div>
      <div class="operation-details">
        <div class="detail-item">
          <span class="label">File:</span>
          <span class="value">{{ currentOperation.file }}</span>
        </div>
        <div class="detail-item">
          <span class="label">Action:</span>
          <span class="value">{{ currentOperation.action }}</span>
        </div>
        <div class="detail-item">
          <span class="label">Progress:</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: currentOperation.progress + '%' }"></div>
          </div>
          <span class="progress-text">{{ currentOperation.progress }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessingStatus',
  props: {
    currentStatus: {
      type: String,
      default: 'Processing'
    },
    processingSteps: {
      type: Array,
      default: () => []
    },
    currentOperation: {
      type: Object,
      default: null
    }
  }
}
</script>

<style scoped>
.processing-status {
  background: #ffffff;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin: 1rem 0;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.status-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.status-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.processing {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-badge.completed {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-badge.error {
  background-color: #ffebee;
  color: #c62828;
}

.status-timeline {
  margin: 2rem 0;
}

.timeline-item {
  display: flex;
  margin-bottom: 1.5rem;
  position: relative;
}

.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 15px;
  top: 30px;
  bottom: -20px;
  width: 2px;
  background: #e0e0e0;
}

.timeline-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  z-index: 1;
}

.timeline-item.completed .timeline-icon {
  background: #e8f5e9;
  color: #2e7d32;
}

.timeline-item.current .timeline-icon {
  background: #e3f2fd;
  color: #1976d2;
}

.timeline-content {
  flex: 1;
}

.timeline-title {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.timeline-details {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.timeline-time {
  font-size: 0.8rem;
  color: #999;
}

.current-operation {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 1rem;
  margin-top: 1.5rem;
}

.operation-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  color: #2c3e50;
  font-weight: 500;
}

.operation-header i {
  margin-right: 0.5rem;
  color: #1976d2;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.detail-item .label {
  width: 80px;
  color: #666;
  font-size: 0.9rem;
}

.detail-item .value {
  flex: 1;
  color: #2c3e50;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  margin: 0 1rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #1976d2;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  min-width: 45px;
  text-align: right;
  font-size: 0.9rem;
  color: #666;
}
</style> 