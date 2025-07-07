<template>
  <div class="instance-view-container">
    <PopupModal />
    
    <div class="instance-view-header">
      <h2 class="instance-view-title"><i class="fas fa-exclamation-triangle instance-view-icon"></i> Risk Instance Details</h2>
      <button class="instance-view-back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i> Back to Risk Instances
      </button>
    </div>

    <div class="instance-view-details-card" v-if="instance">
      <div class="instance-view-details-header">
        <div class="instance-view-id-section">
          <span class="instance-view-id-label">Risk ID:</span>
          <span class="instance-view-id-value">{{ instance.RiskId }}</span>
          <span class="instance-view-id-label">Instance ID:</span>
          <span class="instance-view-id-value">{{ instance.RiskInstanceId }}</span>
        </div>
        <div class="instance-view-meta">
          <div class="instance-view-meta-item">
            <span class="instance-view-origin-badge">MANUAL</span>
          </div>
          <div class="instance-view-meta-item">
            <span class="instance-view-category-badge">{{ instance.Category }}</span>
          </div>
          <div class="instance-view-meta-item">
            <span :class="'instance-view-priority-' + instance.Criticality.toLowerCase()">
              {{ instance.Criticality }}
            </span>
          </div>
          <div class="instance-view-meta-item">
            <span :class="'instance-view-status-' + (instance.RiskStatus ? instance.RiskStatus.toLowerCase().replace(/\s+/g, '-') : 'open')">
              {{ instance.RiskStatus || 'Open' }}
            </span>
          </div>
        </div>
      </div>

      <div class="instance-view-content">
        <div class="instance-view-content-row">
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Description:</h4>
            <div class="instance-view-section-content">{{ instance.RiskDescription || 'Not specified' }}</div>
          </div>
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Category:</h4>
            <div class="instance-view-section-content">{{ instance.Category || 'Not specified' }}</div>
          </div>
        </div>

        <div class="instance-view-content-row">
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Criticality:</h4>
            <div class="instance-view-section-content">{{ instance.Criticality || 'Not specified' }}</div>
          </div>
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Status:</h4>
            <div class="instance-view-section-content">{{ instance.RiskStatus || 'Open' }}</div>
          </div>
        </div>

        <div class="instance-view-content-row">
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Possible Damage:</h4>
            <div class="instance-view-section-content">{{ instance.PossibleDamage || 'Not specified' }}</div>
          </div>
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Risk Appetite:</h4>
            <div class="instance-view-section-content">{{ instance.Appetite || 'Not specified' }}</div>
          </div>
        </div>

        <div class="instance-view-content-row">
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Likelihood:</h4>
            <div class="instance-view-section-content">{{ instance.RiskLikelihood || 'Not specified' }}</div>
          </div>
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Impact:</h4>
            <div class="instance-view-section-content">{{ instance.RiskImpact || 'Not specified' }}</div>
          </div>
        </div>

        <div class="instance-view-content-row">
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Exposure Rating:</h4>
            <div class="instance-view-section-content">{{ instance.RiskExposureRating || 'Not specified' }}</div>
          </div>
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Priority:</h4>
            <div class="instance-view-section-content">{{ instance.RiskPriority || 'Not specified' }}</div>
          </div>
        </div>

        <div class="instance-view-content-row">
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Response Type:</h4>
            <div class="instance-view-section-content">{{ instance.RiskResponseType || 'Not specified' }}</div>
          </div>
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Response Description:</h4>
            <div class="instance-view-section-content">{{ instance.RiskResponseDescription || 'Not specified' }}</div>
          </div>
        </div>

        <div class="instance-view-content-row">
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Mitigation:</h4>
            <div class="instance-view-section-content">{{ instance.RiskMitigation || 'Not specified' }}</div>
          </div>
          <div class="instance-view-content-column">
            <h4 class="instance-view-section-title">Risk Owner:</h4>
            <div class="instance-view-section-content">{{ instance.RiskOwner || 'Not assigned' }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="instance-view-no-data">
      Loading instance details or no instance found...
    </div>
  </div>
</template>

<script>
import './ViewInstance.css'
import axios from 'axios'
import { PopupModal } from '@/modules/popup'

export default {
  name: 'ViewInstance',
  components: {
    PopupModal
  },
  data() {
    return {
      instance: null
    }
  },
  created() {
    this.fetchInstanceDetails()
  },
  methods: {
    fetchInstanceDetails() {
      const instanceId = this.$route.params.id
      if (!instanceId) {
        this.$router.push('/risk/riskinstances-list')
        return
      }

      axios.get(`http://localhost:8000/api/risk-instances/${instanceId}/`)
        .then(response => {
          this.instance = response.data
        })
        .catch(error => {
          console.error('Error fetching risk instance details:', error)
          // Try alternative endpoint if the first one fails
          this.tryAlternativeEndpoint(instanceId)
        })
    },
    tryAlternativeEndpoint(instanceId) {
      axios.get(`http://localhost:8000/risk-instances/${instanceId}/`)
        .then(response => {
          this.instance = response.data
        })
        .catch(error => {
          console.error('Error with alternative endpoint:', error)
        })
    },
    goBack() {
      this.$router.push('/risk/riskinstances-list')
    }
  }
}
</script> 