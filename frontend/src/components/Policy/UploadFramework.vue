<template>
    <div class="upload-framework-container">
      <!-- Step Indicator -->
      <div class="step-indicator">
        <div class="step-item" :class="{ active: currentStep === 1, completed: currentStep > 1 }">
          <div class="step-number">1</div>
          <div class="step-label">Upload Document</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: currentStep === 2, completed: currentStep > 2 }">
          <div class="step-number">2</div>
          <div class="step-label">Processing</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: currentStep === 3, completed: currentStep > 3 }">
          <div class="step-number">3</div>
          <div class="step-label">Content Selection</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: currentStep === 4, completed: currentStep > 4 }">
          <div class="step-number">4</div>
          <div class="step-label">Policy Extraction</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: currentStep === 5, completed: currentStep > 5 }">
          <div class="step-number">5</div>
          <div class="step-label">Review Policies</div>
        </div>
        <div class="step-divider"></div>
        <div class="step-item" :class="{ active: currentStep === 6, completed: currentStep > 6 }">
          <div class="step-number">6</div>
          <div class="step-label">Edit Policy Details</div>
        </div>
      </div>
  
      <!-- Back Button (shown when not on first step) -->
      <div v-if="currentStep > 1 && !isProcessing" class="back-button-container">
        <button @click="goBack" class="back-btn">
          <i class="fas fa-arrow-left"></i>
          Back
        </button>
      </div>
  
      <div class="header">
        <h1>Upload Framework</h1>
        <p>Upload framework documents to the system</p>
      </div>
  
      <div class="upload-section">
        <!-- Step 1: Upload Area -->
        <div v-if="currentStep === 1" class="upload-area" :class="{ 'drag-over': isDragOver }" 
             @drop="handleDrop" 
             @dragover.prevent="isDragOver = true" 
             @dragleave="isDragOver = false"
             @click="triggerFileInput">
          <div class="upload-content">
            <div class="upload-icon-container">
              <i class="fas fa-cloud-upload-alt upload-icon"></i>
            </div>
            <h3>Drag & Drop your framework file here</h3>
            <p>or click to browse files</p>
            <div class="supported-formats">
              <small>Supported formats: PDF, DOC, DOCX, TXT, XLS, XLSX</small>
            </div>
          </div>
          <input 
            ref="fileInput" 
            type="file" 
            @change="handleFileSelect" 
            accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
            style="display: none"
          />
        </div>
  
        <!-- OR Divider -->
        <div v-if="currentStep === 1" class="or-divider">
          <div class="divider-line"></div>
          <span class="divider-text">OR</span>
          <div class="divider-line"></div>
        </div>
  
        <!-- Load Default Data Section -->
        <div v-if="currentStep === 1" class="default-data-section">
          <div class="default-data-content">
            <div class="default-icon-container">
              <i class="fas fa-database default-icon"></i>
            </div>
            <h3>Load Default Framework Data</h3>
            <p>Use pre-loaded NIST framework data for quick testing</p>
            <button 
              @click="loadDefaultData" 
              :disabled="isLoadingDefault"
              class="load-default-btn"
            >
              <i class="fas fa-download"></i>
              {{ isLoadingDefault ? 'Loading Default Data...' : 'Load Default Data' }}
            </button>
          </div>
        </div>
  
        <!-- File Preview (Step 1) -->
        <div v-if="selectedFile && currentStep === 1" class="file-preview">
          <div class="file-info">
            <div class="file-icon-container">
              <i class="fas fa-file file-icon"></i>
            </div>
            <div class="file-details">
              <h4>{{ selectedFile.name }}</h4>
              <p>{{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <button @click="removeFile" class="remove-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="upload-actions">
            <button 
              @click="uploadFile" 
              :disabled="!selectedFile || isUploading"
              class="upload-btn"
            >
              <i class="fas fa-upload"></i>
              {{ isUploading ? 'Uploading...' : 'Upload Framework' }}
            </button>
          </div>
        </div>
  
        <!-- Step 2: Processing Progress Section -->
        <div v-if="currentStep === 2" class="processing-section">
          <div class="processing-header">
            <div class="processing-animation-container">
              <div class="document-processing-visual">
                <div class="document-icon">
                  <i class="fas fa-file-pdf"></i>
                </div>
                <div class="processing-waves">
                  <div class="wave wave-1"></div>
                  <div class="wave wave-2"></div>
                  <div class="wave wave-3"></div>
                </div>
                <div class="extraction-particles">
                  <div class="particle" v-for="n in 6" :key="n"></div>
                </div>
              </div>
            </div>
            <h3>Processing Framework Document</h3>
<div class="processing-details-enhanced">
  <p class="main-status">{{ processingStatus.message || 'Extracting document sections...' }}</p>
  <div class="document-info">
    <i class="fas fa-file-alt"></i>
    <span>Analyzing: {{ uploadedFileName }}</span>
  </div>
  
  <!-- Current Section Being Processed -->
  <div v-if="processingStatus.currentSection" class="current-section">
    <div class="section-indicator">
      <i class="fas fa-cog fa-spin"></i>
      <span>Processing: {{ processingStatus.currentSection }}</span>
    </div>
  </div>
  
  <div class="processing-stages">
    <div class="stage" :class="{ active: processingStatus.progress >= 20 }">
      <div class="stage-dot"></div>
      <span>Text Extraction</span>
    </div>
    <div class="stage" :class="{ active: processingStatus.progress >= 40 }">
      <div class="stage-dot"></div>
      <span>Structure Analysis</span>
    </div>
    <div class="stage" :class="{ active: processingStatus.progress >= 60 }">
      <div class="stage-dot"></div>
      <span>Section Identification</span>
    </div>
    <div class="stage" :class="{ active: processingStatus.progress >= 80 }">
      <div class="stage-dot"></div>
      <span>Content Organization</span>
    </div>
  </div>
  
  <!-- Processing Activity Indicator -->
  <div class="processing-activity">
    <div class="activity-dots">
      <div class="dot" v-for="n in 3" :key="n"></div>
    </div>
    <span>Processing framework sections</span>
  </div>
</div>
          </div>
          
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: processingStatus.progress + '%' }"></div>
            </div>
            <div class="progress-text">{{ processingStatus.progress || 0 }}%</div>
          </div>
          
          <div class="processing-details">
            <div class="detail-item">
              <i class="fas fa-file-pdf"></i>
              <span>File: {{ uploadedFileName }}</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-clock"></i>
              <span>Started: {{ processingStartTime }}</span>
            </div>
          </div>
        </div>
  
        <!-- Step 3: Content Selection Complete -->
        <div v-if="currentStep === 3" class="completion-section">
          <div class="completion-icon-container">
            <div class="success-circle">
              <i class="fas fa-check"></i>
            </div>
          </div>
          
          <div class="completion-header">
            <h3>Processing Complete!</h3>
            <p>Your framework document has been successfully processed and extracted.</p>
          </div>
          
          <div class="completion-actions">
            <button @click="viewExtractedContent" class="view-content-btn">
              <i class="fas fa-eye"></i>
              View Extracted Content
            </button>
          </div>
        </div>
  
        <!-- Step 4: Policy Extraction Progress -->
        <div v-if="currentStep === 4" class="extraction-section">
          <div class="extraction-header">
            <div class="ai-extraction-container">
              <div class="ai-brain-visual">
                <div class="brain-core">
                  <i class="fas fa-brain"></i>
                </div>
                <div class="neural-network">
                  <div class="neuron" v-for="n in 8" :key="n"></div>
                </div>
                <div class="data-flow">
                  <div class="data-bit" v-for="n in 12" :key="n"></div>
                </div>
              </div>
            </div>
            <h3>AI Policy Extraction</h3>
            <div class="ai-processing-details">
              <p class="main-status">{{ policyExtractionMessage }}</p>
              <div class="ai-stages">
                <div class="ai-stage" :class="{ active: policyExtractionProgress >= 25 }">
                  <div class="ai-stage-icon">
                    <i class="fas fa-search"></i>
                  </div>
                  <span>Analyzing Content</span>
                </div>
                <div class="ai-stage" :class="{ active: policyExtractionProgress >= 50 }">
                  <div class="ai-stage-icon">
                    <i class="fas fa-robot"></i>
                  </div>
                  <span>AI Processing</span>
                </div>
                <div class="ai-stage" :class="{ active: policyExtractionProgress >= 75 }">
                  <div class="ai-stage-icon">
                    <i class="fas fa-filter"></i>
                  </div>
                  <span>Policy Extraction</span>
                </div>
                <div class="ai-stage" :class="{ active: policyExtractionProgress >= 100 }">
                  <div class="ai-stage-icon">
                    <i class="fas fa-check-circle"></i>
                  </div>
                  <span>Validation</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: policyExtractionProgress + '%' }"></div>
            </div>
            <div class="progress-text">{{ policyExtractionProgress || 0 }}%</div>
          </div>
          
          <div class="extraction-details">
            <div class="detail-item">
              <i class="fas fa-file-alt"></i>
              <span>Analyzing selected sections...</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-robot"></i>
              <span>AI Processing in progress</span>
            </div>
          </div>
        </div>
  
        <!-- Step 5: Policy Review -->
        <div v-if="currentStep === 5" class="policy-review-section">
          <div class="review-header">
            <div class="review-icon-container">
              <div class="success-circle">
                <i class="fas fa-check"></i>
              </div>
            </div>
            <h3>Policy Extraction Complete!</h3>
            <p>Your policies have been successfully extracted and are ready for review.</p>
          </div>
          
          <div class="policy-summary">
            <div class="summary-card">
              <div class="summary-icon">
                <i class="fas fa-file-alt"></i>
              </div>
              <div class="summary-content">
                <h4>{{ extractedPoliciesCount }}</h4>
                <p>Policies Extracted</p>
              </div>
            </div>
            <div class="summary-card">
              <div class="summary-icon">
                <i class="fas fa-layer-group"></i>
              </div>
              <div class="summary-content">
                <h4>{{ selectedSectionsCount }}</h4>
                <p>Sections Processed</p>
              </div>
            </div>
          </div>
          
          <div class="review-actions">
            <button @click="viewPolicyExtractor" class="view-policies-btn">
              <i class="fas fa-table"></i>
              View Extracted Policies
            </button>
            <button @click="resetUpload" class="upload-another-btn">
              <i class="fas fa-plus"></i>
              Upload Another Document
            </button>
          </div>
        </div>
  
        <!-- Step 6: Enhanced Policy Details Section -->
        <div v-if="currentStep === 6" class="policy-details-section">
          <div class="details-header">
            <h3>Framework & Policy Configuration</h3>
            <p>Configure framework details, policies, and compliance requirements</p>
          </div>
          
          <!-- Enhanced Professional Layout -->
          <div class="professional-layout">
            
            <!-- Framework Information Section -->
            <div class="info-section framework-section">
              <div class="section-title">
                <h4><i class="fas fa-building"></i> Framework Information</h4>
              </div>
              <div class="form-grid">
                <div class="form-field">
                  <label>Framework Title</label>
                  <input type="text" v-model="policyDetails.title" placeholder="e.g., ISO 27001" />
                </div>
                <div class="form-field">
                  <label>Category</label>
                  <input type="text" v-model="policyDetails.category" placeholder="e.g., Security" />
                </div>
                <div class="form-field full-width">
                  <label>Description</label>
                  <textarea v-model="policyDetails.description" 
                            placeholder="Information security, cyber security and privacy protection..."></textarea>
                </div>
                <div class="form-field">
                  <label>Effective Date</label>
                  <input type="date" v-model="policyDetails.effectiveDate" />
                </div>
                <div class="form-field">
                  <label>Start Date</label>
                  <input type="date" v-model="policyDetails.startDate" />
                </div>
                <div class="form-field">
                  <label>End Date</label>
                  <input type="date" v-model="policyDetails.endDate" />
                </div>
              </div>
            </div>

            <!-- Policy Sections Management -->
            <div v-for="(sectionName, sectionIndex) in uniqueSectionNames" 
                 :key="'section-' + sectionIndex" 
                 class="policy-management-container">
              
              <!-- Main Policy Section -->
              <div class="info-section policy-section">
                <div class="section-title">
                  <h4><i class="fas fa-shield-alt"></i> Policy {{ sectionIndex + 1 }} - {{ sectionName }}</h4>
                </div>
                <div class="form-grid">
                  <div class="form-field">
                    <label>Document URL</label>
                    <input type="text" v-model="policyFormData[sectionName].documentUrl" 
                           placeholder="https://policy-document-url.com" />
                  </div>
                  <div class="form-field">
                    <label>Identifier</label>
                    <input type="text" v-model="policyFormData[sectionName].identifier" 
                           placeholder="e.g., ISO" />
                  </div>
                  <div class="form-field">
                    <label>Created By</label>
                    <input type="text" v-model="policyFormData[sectionName].createdBy" 
                           placeholder="John Doe" />
                  </div>
                  <div class="form-field">
                    <label>Reviewer</label>
                    <input type="text" v-model="policyFormData[sectionName].reviewer" 
                           placeholder="Jane Smith" />
                  </div>
                  <div class="form-field">
                    <label>Policy Name</label>
                    <input type="text" v-model="policyFormData[sectionName].policyName" 
                           :placeholder="'Enter policy name for ' + sectionName" />
                  </div>
                  <div class="form-field">
                    <label>Department</label>
                    <input type="text" v-model="policyFormData[sectionName].department" 
                           placeholder="Enter department" />
                  </div>
                  <div class="form-field">
                    <label>Scope</label>
                    <input type="text" v-model="policyFormData[sectionName].scope" 
                           placeholder="Enter policy scope" />
                  </div>
                  <div class="form-field">
                    <label>Applicability</label>
                    <input type="text" v-model="policyFormData[sectionName].applicability" 
                           placeholder="Enter applicability" />
                  </div>
                  <div class="form-field full-width">
                    <label>Objective</label>
                    <textarea v-model="policyFormData[sectionName].objective" 
                              placeholder="Enter policy objective"></textarea>
                  </div>
                  <div class="form-field">
                    <label>Coverage Rate (%)</label>
                    <input type="number" v-model="policyFormData[sectionName].coverageRate" 
                           placeholder="Enter coverage rate" min="0" max="100" />
                  </div>
                </div>
              </div>

              <!-- Sub-Policies for this section -->
              <div v-for="(policy, policyIndex) in policies.filter(p => p.section_name === sectionName)" 
                   :key="'subpolicy-' + sectionName + '-' + policyIndex" 
                   class="info-section sub-policy-section">
                <div class="section-title">
                  <h4><i class="fas fa-file-contract"></i> Sub-Policy {{ policyIndex + 1 }} - {{ policy.Sub_policy_id || 'N/A' }}</h4>
                  <span class="section-badge">{{ sectionName }}</span>
                </div>
                <div class="form-grid">
                  <div class="form-field">
                    <label>Policy Name</label>
                    <input type="text" v-model="policy.sub_policy_name" placeholder="Enter policy name" />
                  </div>
                  <div class="form-field">
                    <label>Policy Identifier</label>
                    <input type="text" v-model="policy.Sub_policy_id" placeholder="Enter policy identifier" />
                  </div>
                  <div class="form-field full-width">
                    <label>Description</label>
                    <textarea v-model="policy.control" placeholder="Enter policy description" rows="4"></textarea>
                  </div>
                  <div class="form-field">
                    <label>Scope</label>
                    <input type="text" v-model="policy.scope" placeholder="Enter policy scope" />
                  </div>
                  <div class="form-field">
                    <label>Department</label>
                    <input type="text" v-model="policy.department" placeholder="Enter department" />
                  </div>
                  <div class="form-field full-width">
                    <label>Objective</label>
                    <textarea v-model="policy.objective" placeholder="Enter policy objective" rows="3"></textarea>
                  </div>
                  <div class="form-field">
                    <label>Applicability</label>
                    <input type="text" v-model="policy.applicability" placeholder="Enter applicability" />
                  </div>
                  <div class="form-field">
                    <label>Coverage Rate (%)</label>
                    <input type="number" v-model="policy.coverage_rate" placeholder="Enter coverage rate" min="0" max="100" />
                  </div>
                  <div class="form-field">
                    <label>Related Controls</label>
                    <input type="text" v-model="policy.related_controls" placeholder="Enter related controls" />
                  </div>
                  <div class="form-field">
                    <label>Start Date</label>
                    <input type="date" v-model="policy.start_date" />
                  </div>
                  <div class="form-field">
                    <label>End Date</label>
                    <input type="date" v-model="policy.end_date" />
                  </div>
                  <div class="form-field">
                    <label>Upload Document</label>
                    <div class="file-upload-wrapper">
                      <input type="file" :id="'file-' + sectionName + '-' + policyIndex" 
                             @change="handleSubPolicyFileUpload($event, policies.indexOf(policy))" 
                             accept=".pdf,.doc,.docx,.txt" />
                      <label :for="'file-' + sectionName + '-' + policyIndex" class="file-upload-label">
                        <i class="fas fa-upload"></i>
                        Choose File
                      </label>
                      <span v-if="policy.uploaded_file" class="file-name">{{ policy.uploaded_file.name }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Enhanced Compliance Section -->
              <div v-for="(policy, policyIndex) in policies.filter(p => p.section_name === sectionName)" 
                   :key="'compliance-' + sectionName + '-' + policyIndex" 
                   class="compliance-management-section">
                <div class="compliance-header">
                  <div class="compliance-title">
                    <h4><i class="fas fa-check-circle"></i> Compliance Management</h4>
                    <span class="policy-ref">{{ policy.Sub_policy_id || 'Sub-Policy ' + (policyIndex + 1) }}</span>
                  </div>
                  <div class="compliance-stats">
                    <span class="compliance-count">
                      {{ complianceData[`${sectionName}_${policy.Sub_policy_id}`]?.length || 0 }} Items
                    </span>
                    <button @click="addComplianceItem(`${sectionName}_${policy.Sub_policy_id}`)" 
                            class="add-compliance-btn">
                      <i class="fas fa-plus"></i>
                      Add Item
                    </button>
                  </div>
                </div>
                
                <div class="compliance-grid" v-if="complianceData[`${sectionName}_${policy.Sub_policy_id}`]">
                  <div v-for="(compliance, complianceIndex) in complianceData[`${sectionName}_${policy.Sub_policy_id}`]" 
                       :key="'compliance-item-' + complianceIndex" 
                       class="compliance-card">
                    <div class="compliance-card-header">
                      <div class="compliance-identifier">
                        <span class="compliance-letter">{{ compliance.letter }})</span>
                        <span class="compliance-number">Item {{ complianceIndex + 1 }}</span>
                      </div>
                      <div class="compliance-actions">
                        <span class="status-badge" :class="'status-' + compliance.status">
                          {{ compliance.status }}
                        </span>
                        <button v-if="complianceData[`${sectionName}_${policy.Sub_policy_id}`].length > 1" 
                                @click="removeComplianceItem(`${sectionName}_${policy.Sub_policy_id}`, complianceIndex)" 
                                class="remove-compliance-btn">
                          <i class="fas fa-times"></i>
                        </button>
                      </div>
                    </div>
                    
                    <div class="compliance-form-grid">
                      <div class="form-field">
                        <label>Compliance Name</label>
                        <input type="text" v-model="compliance.name" placeholder="Enter compliance name" />
                      </div>
                      <div class="form-field">
                        <label>Status</label>
                        <select v-model="compliance.status" class="status-select">
                          <option value="pending">Pending</option>
                          <option value="in-progress">In Progress</option>
                          <option value="completed">Completed</option>
                          <option value="not-applicable">Not Applicable</option>
                        </select>
                      </div>
                      <div class="form-field full-width">
                        <label>Description</label>
                        <textarea v-model="compliance.description" 
                                  placeholder="Enter compliance description" 
                                  rows="3"></textarea>
                      </div>
                      <div class="form-field">
                        <label>Assignee</label>
                        <input type="text" v-model="compliance.assignee" placeholder="Enter assignee name" />
                      </div>
                      <div class="form-field">
                        <label>Due Date</label>
                        <input type="date" v-model="compliance.dueDate" />
                      </div>
                      <div class="form-field full-width">
                        <label>Evidence Document</label>
                        <div class="file-upload-wrapper">
                          <input type="file" 
                                 :id="'compliance-file-' + sectionName + '-' + policyIndex + '-' + complianceIndex" 
                                 @change="handleComplianceFileUpload($event, `${sectionName}_${policy.Sub_policy_id}`, complianceIndex)" 
                                 accept=".pdf,.doc,.docx,.txt,.jpg,.png" />
                          <label :for="'compliance-file-' + sectionName + '-' + policyIndex + '-' + complianceIndex" 
                                 class="file-upload-label">
                            <i class="fas fa-upload"></i>
                            Upload Evidence
                          </label>
                          <span v-if="compliance.evidence" class="file-name">{{ compliance.evidence.name }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Global Actions -->
            <div class="global-actions">
              <button @click="saveAllDetails" class="save-btn primary">
                <i class="fas fa-save"></i>
                Save All Details
              </button>
              <button @click="resetAllForms" class="reset-btn secondary">
                <i class="fas fa-undo"></i>
                Reset All Forms
              </button>
            </div>
          </div>
        </div>
  
        <!-- Upload Status Messages -->
        <div v-if="uploadStatus && currentStep === 1" class="status-message" :class="uploadStatus.type">
          <i :class="uploadStatus.type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'"></i>
          {{ uploadStatus.message }}
        </div>
        
        <!-- Congratulations Modal -->
        <div v-if="showCongratulationsModal" class="congratulations-modal">
          <div class="congratulations-container">
            <div class="congratulations-header">
              <div class="congratulations-icon-container">
                <i class="fas fa-check-circle"></i>
              </div>
              <h2>Congratulations!</h2>
              <p class="congratulations-message">Your framework has been successfully added to the system.</p>
            </div>
            <div class="congratulations-content">
              <p>You have completed all the steps to add a new framework to your GRC system.</p>
              <p>Your framework is now ready to be used for compliance management.</p>
            </div>
            <div class="congratulations-actions">
              <button @click="goToPolicyDashboard" class="ok-btn">
                <i class="fas fa-check"></i>
                Go to Policy Dashboard
              </button>
            </div>
          </div>
        </div>
        
        <!-- Global Success Notification -->
        <div v-if="uploadStatus && uploadStatus.type === 'success' && currentStep > 1" class="global-notification success">
          <div class="notification-content">
            <i class="fas fa-check-circle"></i>
            <div class="notification-message">
              {{ uploadStatus.message }}
            </div>
            <button @click="uploadStatus = null" class="notification-close">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
        
        <!-- Content Viewer Modal -->
        <div v-if="showContentViewer" class="content-viewer-modal">
          <div class="content-viewer-container">
            <div class="content-viewer-header">
              <h3>Framework Content Viewer</h3>
              <button @click="closeContentViewer" class="close-btn">
                <i class="fas fa-times"></i>
              </button>
            </div>
            
            <div class="content-viewer-body">
              <div class="search-box">
                <input type="text" v-model="searchQuery" placeholder="Search sections..." />
              </div>
              
              <div class="section-list">
                <div v-for="(section, index) in filteredSections" :key="index" class="section-item">
                  <div class="section-header" @click="toggleSection(section.id)">
                    <div class="section-checkbox">
                      <input type="checkbox" v-model="section.selected" @change="updateSelection(section)" />
                      <span>{{ section.title }}</span>
                    </div>
                    <i class="fas" :class="section.expanded ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
                  </div>
                  <div v-if="section.expanded" class="section-content">
                    <div v-for="(subsection, subIndex) in section.subsections" :key="subIndex" class="subsection-item">
                      <div class="subsection-checkbox">
                        <input type="checkbox" v-model="subsection.selected" @change="updateSubsectionSelection(section)" />
                        <span>{{ subsection.title }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="content-viewer-footer">
              <button @click="selectAllSections" class="select-all-btn">Select All</button>
              <button @click="deselectAllSections" class="deselect-all-btn">Deselect All</button>
              <button @click="saveSelectedSections" class="save-selection-btn">Save Selection</button>
            </div>
          </div>
        </div>

        <!-- Policy Extractor View -->
        <div v-if="showPolicyExtractor" class="policy-extractor-modal">
          <div class="policy-extractor-container">
            <div class="policy-extractor-header">
              <h3>Extracted Policies</h3>
              <div class="policy-actions">
                <button @click="saveAllPolicies" class="save-all-btn">
                  <i class="fas fa-save"></i>
                  Save All
                </button>
                <button @click="closePolicyExtractor" class="close-btn">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            
            <div class="policy-extractor-body">
              <div class="policy-table-container">
                <table class="policy-table" v-if="policies.length > 0">
                  <thead>
                    <tr>
                      <th>Section</th>
                      <th>Control ID</th>
                      <th>Policy Name</th>
                      <th>Control</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <template v-for="(policy, index) in policies" :key="index">
                      <tr :class="{ 'expanded-row': expandedRows[index] }">
                        <td>{{ policy.section_name || 'N/A' }}</td>
                        <td>{{ policy.Sub_policy_id || 'N/A' }}</td>
                        <td>{{ policy.sub_policy_name || 'N/A' }}</td>
                        <td class="control-cell">
                          {{ policy.control ? (policy.control.length > 100 ? policy.control.substring(0, 100) + '...' : policy.control) : 'N/A' }}
                        </td>
                        <td class="actions-cell">
                          <button @click="toggleExpandRow(index)" class="view-btn">
                            <i :class="expandedRows[index] ? 'fas fa-chevron-up' : 'fas fa-eye'"></i>
                            {{ expandedRows[index] ? 'Hide' : 'View' }}
                          </button>
                          <button @click="editPolicy(policy, index)" class="edit-btn">
                            <i class="fas fa-edit"></i>
                            Edit
                          </button>
                        </td>
                      </tr>
                      <tr v-if="expandedRows[index]" class="detail-row">
                        <td colspan="5">
                          <div class="policy-details-container">
                            <div class="policy-details-section">
                              <h4>Control ID</h4>
                              <div class="detail-content">{{ policy.Sub_policy_id || 'N/A' }}</div>
                            </div>
                            
                            <div class="policy-details-section">
                              <h4>Policy Name</h4>
                              <div class="detail-content">{{ policy.sub_policy_name || 'N/A' }}</div>
                            </div>
                            
                            <div class="policy-details-section">
                              <h4>Control</h4>
                              <div class="detail-content control-content">
                                <div v-if="getFormattedControl(policy.control).length > 0">
                                  <ul>
                                    <li v-for="(point, idx) in getFormattedControl(policy.control)" :key="idx">
                                      {{ point }}
                                    </li>
                                  </ul>
                                </div>
                                <div v-else>{{ policy.control || 'N/A' }}</div>
                              </div>
                            </div>
                            
                            <div class="policy-details-section">
                              <h4>Related Controls</h4>
                              <div class="detail-content">{{ policy.related_controls || 'N/A' }}</div>
                            </div>
                            
                            <div class="policy-details-section">
                              <h4>Control Enhancements</h4>
                              <div class="detail-content">{{ policy.control_enhancements || 'N/A' }}</div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    </template>
                  </tbody>
                </table>
                <div v-else class="no-policies-message">
                  <p>No policies found. Please try processing the document again.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Policy Edit Modal -->
        <div v-if="showPolicyDetail" class="policy-edit-modal">
          <div class="policy-edit-container">
            <div class="policy-edit-header">
              <h3>Edit Policy</h3>
              <div class="policy-edit-actions">
                <button @click="savePolicy" class="save-btn">
                  <i class="fas fa-save"></i>
                  Save
                </button>
                <button @click="closePolicyDetail" class="close-btn">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            
            <div class="policy-edit-body">
              <div class="policy-field">
                <label>Section</label>
                <input type="text" v-model="currentPolicy.section_name" />
              </div>
              
              <div class="policy-field">
                <label>Control ID</label>
                <input type="text" v-model="currentPolicy.Sub_policy_id" />
              </div>
              
              <div class="policy-field">
                <label>Policy Name</label>
                <input type="text" v-model="currentPolicy.sub_policy_name" />
              </div>
              
              <div class="policy-field">
                <label>Control</label>
                <textarea v-model="currentPolicy.control" rows="8"></textarea>
              </div>
              
              <div class="policy-field">
                <label>Related Controls</label>
                <input type="text" v-model="currentPolicy.related_controls" />
              </div>
              
              <div class="policy-field">
                <label>Control Enhancements</label>
                <textarea v-model="currentPolicy.control_enhancements" rows="5"></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, onUnmounted, watch } from 'vue'
  import axios from 'axios'
  
  export default {
    name: 'UploadFramework',
    setup() {
      // Basic reactive data
      const selectedFile = ref(null)
      const isDragOver = ref(false)
      const isUploading = ref(false)
      const isLoadingDefault = ref(false)
      const isProcessing = ref(false)
      const processingComplete = ref(false)
      const uploadStatus = ref(null)
      const fileInput = ref(null)
      const processingStatus = ref({ progress: 0, message: '' })
      const taskId = ref(null)
      const uploadedFileName = ref('')
      const processingStartTime = ref('')
      let progressInterval = null
      
      // Step management
      const currentStep = ref(1)
      const stepHistory = ref([1])
      
      // Content viewer related
      const showContentViewer = ref(false)
      const sections = ref([])
      const searchQuery = ref('')
      
      // Policy extraction progress
      const policyExtractionComplete = ref(false)
      const policyExtractionInProgress = ref(false)
      const policyExtractionMessage = ref('')
      const policyExtractionProgress = ref(0)

      // Policy extractor related
      const showPolicyExtractor = ref(false)
      const policies = ref([])
      const extractedPoliciesCount = ref(0)
      const selectedSectionsCount = ref(0)
      
      // Policy detail view related
      const showPolicyDetail = ref(false)
      const currentPolicy = ref({})
      const currentPolicyIndex = ref(null)
      const isEditing = ref(false)
      
      // For expandable rows
      const expandedRows = ref({})
      
      // Policy details for Step 6
      const policyDetails = ref({
        title: '',
        description: '',
        category: '',
        effectiveDate: '',
        startDate: '',
        endDate: ''
      })
      
      // Dynamic forms data
      const policyFormData = ref({})
      
      // Compliance data
      const complianceData = ref({})
      
      // Congratulations modal
      const showCongratulationsModal = ref(false)

      // Computed properties
      const filteredSections = computed(() => {
        if (!searchQuery.value) return sections.value
        
        const query = searchQuery.value.toLowerCase()
        return sections.value.filter(section => 
          section.title.toLowerCase().includes(query) ||
          section.subsections.some(sub => sub.title.toLowerCase().includes(query))
        )
      })

      const uniqueSectionNames = computed(() => {
        if (!policies.value || policies.value.length === 0) return []
        const sections = [...new Set(policies.value.map(p => p.section_name).filter(name => name))]
        return sections.sort()
      })

      // Simplified default data loading
      const loadDefaultData = async () => {
        isLoadingDefault.value = true
        uploadStatus.value = null

        try {
          // Directly load default data without task processing
          const defaultPolicies = [
            {
              section_name: "Access Control",
              Sub_policy_id: "AC-1",
              sub_policy_name: "Access Control Policy and Procedures",
              control: "a. Develop, document, and disseminate access control policy. b. Review and update the current access control policy. c. Designate an official to manage the access control policy and procedures.",
              scope: "Organization-wide",
              department: "IT Security",
              objective: "Establish access control framework",
              applicability: "All systems",
              coverage_rate: 100,
              related_controls: "AC-2, AC-3",
              start_date: "2024-01-01",
              end_date: "2024-12-31"
            },
            {
              section_name: "Access Control", 
              Sub_policy_id: "AC-2",
              sub_policy_name: "Account Management",
              control: "a. Identify and select account types. b. Assign account managers. c. Establish conditions for group membership. d. Monitor the use of accounts.",
              scope: "System accounts",
              department: "IT Security",
              objective: "Manage system accounts",
              applicability: "Information systems",
              coverage_rate: 95,
              related_controls: "AC-1, AC-3",
              start_date: "2024-01-01",
              end_date: "2024-12-31"
            },
            {
              section_name: "Audit and Accountability",
              Sub_policy_id: "AU-1", 
              sub_policy_name: "Audit and Accountability Policy",
              control: "a. Develop, document, and disseminate audit policy. b. Review and update the current audit policy. c. Designate an official to manage the audit policy.",
              scope: "Organization-wide",
              department: "Compliance",
              objective: "Establish audit framework",
              applicability: "All systems and processes",
              coverage_rate: 100,
              related_controls: "AU-2, AU-3",
              start_date: "2024-01-01", 
              end_date: "2024-12-31"
            }
          ]

          // Set up data directly
          policies.value = defaultPolicies
          extractedPoliciesCount.value = defaultPolicies.length
          selectedSectionsCount.value = 2
          uploadedFileName.value = 'NIST.SP.800-53r5.pdf'
          
          // Initialize forms
          initializePolicyFormData()
          initializeComplianceData()
          
          // Go directly to step 6 (policy details)
          currentStep.value = 6
          
          uploadStatus.value = {
            type: 'success',
            message: 'Default NIST framework data loaded successfully!'
          }

          setTimeout(() => {
            uploadStatus.value = null
          }, 3000)

        } catch (error) {
          uploadStatus.value = {
            type: 'error',
            message: 'Failed to load default data. Please try again.'
          }
        } finally {
          isLoadingDefault.value = false
        }
      }

      // File handling methods
      const triggerFileInput = () => {
        fileInput.value.click()
      }

      const handleFileSelect = (event) => {
        const file = event.target.files[0]
        if (file) {
          selectedFile.value = file
          uploadStatus.value = null
        }
      }

      const handleDrop = (event) => {
        event.preventDefault()
        isDragOver.value = false
        const file = event.dataTransfer.files[0]
        if (file) {
          selectedFile.value = file
          uploadStatus.value = null
        }
      }

      const removeFile = () => {
        selectedFile.value = null
        uploadStatus.value = null
        fileInput.value.value = ''
      }

      const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes'
        const k = 1024
        const sizes = ['Bytes', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
      }

      // Upload and processing methods
      const uploadFile = async () => {
        if (!selectedFile.value) return

        isUploading.value = true
        uploadStatus.value = null

        const formData = new FormData()
        formData.append('file', selectedFile.value)

        try {
          const response = await axios.post('/api/upload-framework/', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })

          uploadedFileName.value = response.data.filename
          processingStartTime.value = new Date().toLocaleTimeString()
          
          if (response.data.processing && response.data.task_id) {
            isProcessing.value = true
            taskId.value = response.data.task_id
            goToStep(2)
            startProgressTracking(response.data.task_id)
          } else {
            uploadStatus.value = {
              type: 'success',
              message: `File "${response.data.filename}" uploaded successfully!`
            }
            
            setTimeout(() => {
              removeFile()
              uploadStatus.value = null
            }, 3000)
          }

        } catch (error) {
          uploadStatus.value = {
            type: 'error',
            message: error.response?.data?.error || 'Upload failed. Please try again.'
          }
        } finally {
          isUploading.value = false
        }
      }

      // Progress tracking
      const startProgressTracking = (id, onComplete = null) => {
  taskId.value = id
  let currentProgress = 0
  
  progressInterval = setInterval(async () => {
    try {
      const response = await axios.get(`/api/processing-status/${id}/`)
      
      if (response.data.progress !== undefined) {
        processingStatus.value = response.data
      } else {
        // Enhanced progress calculation based on backend activity
        if (currentProgress < 20) {
          currentProgress += 2
          processingStatus.value = {
            progress: Math.floor(currentProgress),
            message: "Initializing document processing...",
            currentSection: "Starting extraction"
          }
        } else if (currentProgress < 40) {
          currentProgress += 1.5
          processingStatus.value = {
            progress: Math.floor(currentProgress),
            message: "Extracting document structure...",
            currentSection: "THE FUNDAMENTALS"
          }
        } else if (currentProgress < 60) {
          currentProgress += 1
          processingStatus.value = {
            progress: Math.floor(currentProgress),
            message: "Processing control sections...",
            currentSection: "ACCESS CONTROL"
          }
        } else if (currentProgress < 80) {
          currentProgress += 0.8
          processingStatus.value = {
            progress: Math.floor(currentProgress),
            message: "Extracting policy controls...",
            currentSection: "AUDIT AND ACCOUNTABILITY"
          }
        } else if (currentProgress < 95) {
          currentProgress += 0.5
          processingStatus.value = {
            progress: Math.floor(currentProgress),
            message: "Finalizing extraction...",
            currentSection: "Completing processing"
          }
        } else {
          currentProgress = 100
          processingStatus.value = {
            progress: 100,
            message: "Processing complete!",
            currentSection: "Finished"
          }
        }
      }
      
      if (processingStatus.value.progress >= 100) {
        clearInterval(progressInterval)
        isProcessing.value = false
        processingComplete.value = true
        
        if (onComplete) {
          onComplete()
        } else {
          goToStep(3)
          fetchExtractedContent(id)
        }
      }
    } catch (error) {
      console.error('Error fetching progress:', error)
      if (error.response?.status === 404) {
        clearInterval(progressInterval)
        isProcessing.value = false
        uploadStatus.value = {
          type: 'error',
          message: 'Processing task not found or expired'
        }
        currentStep.value = 1
      }
    }
  }, 1500)
}


      // Step navigation
      const goToStep = (step) => {
        if (step !== currentStep.value) {
          stepHistory.value.push(currentStep.value)
          currentStep.value = step
        }
      }

      const goBack = () => {
        currentStep.value = Math.max(1, currentStep.value - 1)
      }

      // Content extraction and viewing
      const fetchExtractedContent = async (id) => {
        try {
          const response = await axios.get(`/api/get-sections/${id}/`)
          
          sections.value = response.data.map((section, index) => {
            const txtSubsections = section.subsections.filter(subsection => 
              subsection.name.startsWith('txt_chunks/') && subsection.name.endsWith('.txt')
            );
            
            const cleanedSubsections = txtSubsections.map((subsection, subIndex) => ({
              id: subIndex,
              title: subsection.name.replace('txt_chunks/extracted_', '')
                                   .replace('.txt', '')
                                   .replace(/_/g, ' '),
              originalName: subsection.name,
              content: subsection.content,
              selected: false
            }));
            
            return {
              id: index,
              title: section.name,
              selected: false,
              expanded: false,
              subsections: cleanedSubsections
            }
          }).filter(section => section.subsections.length > 0);
        } catch (error) {
          console.error('Error fetching extracted content:', error)
        }
      }

      const viewExtractedContent = () => {
        showContentViewer.value = true
      }
      
      const closeContentViewer = () => {
        showContentViewer.value = false
      }
      
      const toggleSection = (sectionId) => {
        const section = sections.value.find(s => s.id === sectionId)
        if (section) {
          section.expanded = !section.expanded
        }
      }
      
      const updateSelection = (section) => {
        section.subsections.forEach(sub => {
          sub.selected = section.selected
        })
      }
      
      const updateSubsectionSelection = (section) => {
        section.selected = section.subsections.every(sub => sub.selected)
      }
      
      const selectAllSections = () => {
        sections.value.forEach(section => {
          section.selected = true
          section.subsections.forEach(sub => {
            sub.selected = true
          })
        })
      }
      
      const deselectAllSections = () => {
        sections.value.forEach(section => {
          section.selected = false
          section.subsections.forEach(sub => {
            sub.selected = false
          })
        })
      }
      
      const saveSelectedSections = async () => {
        try {
          const selectedData = sections.value
            .filter(section => section.selected || section.subsections.some(sub => sub.selected))
            .map(section => ({
              name: section.title,
              subsections: section.subsections
                .filter(sub => sub.selected)
                .map(sub => ({
                  name: sub.originalName,
                  content: sub.content
                }))
            }))
            .filter(section => section.subsections.length > 0)
          
          if (selectedData.length === 0) {
            alert('No sections selected. Please select at least one item.')
            return
          }
          
          selectedSectionsCount.value = selectedData.reduce((total, section) => total + section.subsections.length, 0)
          
          const response = await axios.post('/api/create-checked-structure/', {
            task_id: taskId.value,
            sections: selectedData
          })
          
          if (response.status === 200) {
            closeContentViewer()
            goToStep(4)
            policyExtractionInProgress.value = true
            policyExtractionMessage.value = "Initializing policy extraction..."
            policyExtractionProgress.value = 0
            pollPolicyExtractionStatus()
          }
        } catch (error) {
          console.error('Error saving selected sections:', error)
          alert('Error saving selected sections: ' + error.message)
        }
      }

      // Policy extraction
      const pollPolicyExtractionStatus = () => {
        let statusInterval = setInterval(async () => {
          try {
            const response = await axios.get(`/api/policy-extraction-progress/${taskId.value}/`)
            
            const actualProgress = response.data.progress || 0
            const message = response.data.message || "Processing..."
            
            policyExtractionProgress.value = Math.floor(actualProgress)
            policyExtractionMessage.value = message
            
            if (actualProgress >= 100) {
              clearInterval(statusInterval)
              policyExtractionProgress.value = 100
              policyExtractionMessage.value = "Policy extraction complete!"
              
              setTimeout(async () => {
                policyExtractionComplete.value = true
                policyExtractionInProgress.value = false
                await fetchExtractedPolicies()
                goToStep(5)
              }, 1000)
            }
          } catch (error) {
            console.error('Error checking extraction status:', error)
            try {
              const fallbackResponse = await axios.get(`/api/processing-status/${taskId.value}/`)
              
              if (fallbackResponse.data.progress >= 100) {
                clearInterval(statusInterval)
                policyExtractionProgress.value = 100
                policyExtractionMessage.value = "Policy extraction complete!"
                
                setTimeout(async () => {
                  policyExtractionComplete.value = true
                  policyExtractionInProgress.value = false
                  await fetchExtractedPolicies()
                  goToStep(5)
                }, 1000)
              }
            } catch (fallbackError) {
              console.error('Error with fallback status check:', fallbackError)
              policyExtractionInProgress.value = false
              clearInterval(statusInterval)
            }
          }
        }, 2000)
      }

      const fetchExtractedPolicies = async () => {
        try {
          const response = await axios.get(`/api/get-extracted-policies/${taskId.value}/`)
          policies.value = response.data.policies || []
          extractedPoliciesCount.value = response.data.total_policies || policies.value.length
          
          console.log('Fetched policies:', policies.value.length)
        } catch (error) {
          console.error('Error fetching policies:', error)
          policies.value = []
          extractedPoliciesCount.value = 0
        }
      }

      const viewPolicyExtractor = async () => {
        try {
          const response = await axios.get(`/api/extracted-policies/${taskId.value}/`)
          
          if (response.data.policies) {
            policies.value = response.data.policies
            extractedPoliciesCount.value = response.data.total_policies || policies.value.length
            initializeDynamicForms()
            goToStep(6)
          }
        } catch (error) {
          console.error('Error loading extracted policies:', error)
          uploadStatus.value = {
            type: 'error',
            message: 'Failed to load extracted policies. Please try again.'
          }
        }
      }

      const closePolicyExtractor = () => {
        showPolicyExtractor.value = false
      }

      // Policy editing
      const editPolicy = (policy, index) => {
        currentPolicy.value = {...policy}
        currentPolicyIndex.value = index
        showPolicyDetail.value = true
      }
      
      const savePolicy = async () => {
        try {
          if (currentPolicyIndex.value !== null) {
            policies.value[currentPolicyIndex.value] = {...currentPolicy.value}
          }
          
          const response = await axios.post('/api/save-single-policy/', {
            policy: currentPolicy.value,
            task_id: taskId.value
          })
          
          if (response.status === 200) {
            showPolicyDetail.value = false
            
            uploadStatus.value = {
              type: 'success',
              message: `Policy "${currentPolicy.value.Sub_policy_id}" saved successfully!`
            }
            
            setTimeout(() => {
              uploadStatus.value = null
            }, 5000)
          }
        } catch (error) {
          console.error('Error saving policy:', error)
          uploadStatus.value = {
            type: 'error',
            message: error.response?.data?.error || 'Failed to save policy. Please try again.'
          }
        }
      }
      
      const saveAllPolicies = async () => {
        try {
          const response = await axios.post('/api/save-policies/', {
            policies: policies.value,
            task_id: taskId.value,
            filename: `policies_${taskId.value}`
          })
          
          if (response.status === 200) {
            uploadStatus.value = {
              type: 'success',
              message: `All policies saved successfully! (${policies.value.length} policies)`
            }
            
            setTimeout(() => {
              uploadStatus.value = null
            }, 5000)
          }
        } catch (error) {
          console.error('Error saving all policies:', error)
          uploadStatus.value = {
            type: 'error',
            message: error.response?.data?.error || 'Failed to save policies. Please try again.'
          }
        }
      }

      const closePolicyDetail = () => {
        showPolicyDetail.value = false
        currentPolicy.value = {}
        currentPolicyIndex.value = null
      }

      // Table row expansion
      const toggleExpandRow = (index) => {
        expandedRows.value = {
          ...expandedRows.value,
          [index]: !expandedRows.value[index]
        }
      }
      
      const getFormattedControl = (controlText) => {
        if (!controlText) return []
        
        if (/^\s*[\d*-]+\s+/.test(controlText)) {
          return controlText.split('\n')
            .filter(line => line.trim())
            .map(line => line.trim())
        }
        
        return controlText.split(/\.\s+|\.\n/)
          .filter(sentence => sentence.trim())
          .map(sentence => sentence.trim() + (sentence.endsWith('.') ? '' : '.'))
      }

      // Form management
      const initializePolicyFormData = () => {
        const newFormData = {}
        uniqueSectionNames.value.forEach(sectionName => {
          if (!policyFormData.value[sectionName]) {
            newFormData[sectionName] = {
              documentUrl: '',
              identifier: '',
              createdBy: '',
              reviewer: '',
              policyName: '',
              department: '',
              scope: '',
              applicability: '',
              objective: '',
              coverageRate: 0
            }
          } else {
            newFormData[sectionName] = policyFormData.value[sectionName]
          }
        })
        policyFormData.value = newFormData
      }

      const initializeDynamicForms = () => {
        policyFormData.value = {}
        
        uniqueSectionNames.value.forEach(sectionName => {
          policyFormData.value[sectionName] = {
            documentUrl: '',
            identifier: '',
            createdBy: '',
            reviewer: '',
            policyName: '',
            department: '',
            scope: '',
            applicability: '',
            objective: '',
            coverageRate: 0
          }
        })
      }

      // Compliance management
      const getComplianceItems = (control) => {
        if (!control || control.trim() === '') return [];
        
        const letterPattern = /([a-z])[.)](\s*)/gi;
        const matches = [];
        let match;
        while ((match = letterPattern.exec(control)) !== null) {
          matches.push({
            letter: match[1].toLowerCase(),
            index: match.index,
            matchLength: match[0].length
          });
        }
        
        if (matches.length === 0) {
          if (control.trim().length < 5) return [];
          
          return [{
            id: 'compliance_1',
            letter: 'a',
            name: control.substring(0, 100) + (control.length > 100 ? '...' : ''),
            description: control,
            status: 'pending',
            assignee: '',
            dueDate: '',
            evidence: null
          }];
        }
        
        const items = matches.map((match, index) => {
          const startPos = match.index + match.matchLength;
          const endPos = index < matches.length - 1 ? matches[index + 1].index : control.length;
          const content = control.substring(startPos, endPos).trim();
          
          if (content.length < 5) return null;
          
          return {
            id: `compliance_${index + 1}`,
            letter: match.letter,
            name: content.substring(0, 100) + (content.length > 100 ? '...' : ''),
            description: content,
            status: 'pending',
            assignee: '',
            dueDate: '',
            evidence: null
          };
        }).filter(item => item !== null);
        
        return items;
      }
      
      const initializeComplianceData = () => {
        const newComplianceData = {}
        
        policies.value.forEach(policy => {
          if (!policy.control || policy.control.trim() === '') return;
          
          const policyKey = `${policy.section_name}_${policy.Sub_policy_id}`
          const complianceItems = getComplianceItems(policy.control)
          
          if (complianceItems.length > 0) {
            newComplianceData[policyKey] = complianceItems
          }
        })
        
        complianceData.value = newComplianceData
      }
      
      const handleComplianceFileUpload = (event, policyKey, complianceIndex) => {
        const file = event.target.files[0]
        if (file && complianceData.value[policyKey] && complianceData.value[policyKey][complianceIndex]) {
          complianceData.value[policyKey][complianceIndex].evidence = file
        }
      }
      
      const addComplianceItem = (policyKey) => {
        if (!complianceData.value[policyKey]) {
          complianceData.value[policyKey] = []
        }
        
        const newIndex = complianceData.value[policyKey].length
        const newItem = {
          id: `compliance_${newIndex + 1}`,
          letter: String.fromCharCode(97 + newIndex),
          name: '',
          description: '',
          status: 'pending',
          assignee: '',
          dueDate: '',
          evidence: null
        }
        
        complianceData.value[policyKey].push(newItem)
      }
      
      const removeComplianceItem = (policyKey, index) => {
        if (complianceData.value[policyKey] && complianceData.value[policyKey].length > 1) {
          complianceData.value[policyKey].splice(index, 1)
          
          complianceData.value[policyKey].forEach((item, idx) => {
            item.letter = String.fromCharCode(97 + idx)
            item.id = `compliance_${idx + 1}`
          })
        }
      }

      // File upload handlers
      const handleSubPolicyFileUpload = (event, index) => {
        const file = event.target.files[0]
        if (file && policies.value[index]) {
          policies.value[index].uploaded_file = file
        }
      }

      // Save and reset methods
      const saveAllDetails = async () => {
  try {
    const completePackage = {
      task_id: taskId.value || 'default_task',
      framework_details: policyDetails.value,
      policy_forms: policyFormData.value,
      sub_policies: policies.value,
      compliance_data: complianceData.value,
      unique_sections: uniqueSectionNames.value
    }
    
    const response = await axios.post('/api/save-complete-policy-package/', completePackage)
    
    if (response.status === 200) {
      // Remove the unused saveResponse variable
      
      try {
        const dbResponse = await axios.post('/api/save-framework-to-database/', {
          task_id: taskId.value || 'default_task'
        })
        
        if (dbResponse.status === 200) {
          uploadStatus.value = {
            type: 'success',
            message: `Framework "${policyDetails.value.title}" has been created successfully!`
          }
          
          showCongratulationsModal.value = true
          
          setTimeout(() => {
            uploadStatus.value = null
          }, 8000)
        }
      } catch (dbError) {
        console.error('Error saving to database:', dbError)
        uploadStatus.value = {
          type: 'warning',
          message: 'Files saved successfully, but database save failed.'
        }
      }
    }
  } catch (error) {
    console.error('Error saving complete package:', error)
    uploadStatus.value = {
      type: 'error',
      message: error.response?.data?.error || 'Failed to save package. Please try again.'
    }
  }
}
      
      const resetAllForms = () => {
        policyDetails.value = {
          title: '',
          description: '',
          category: '',
          effectiveDate: '',
          startDate: '',
          endDate: ''
        }
        
        policyFormData.value = {}
        initializePolicyFormData()
        
        policies.value.forEach(policy => {
          policy.scope = ''
          policy.department = ''
          policy.objective = ''
          policy.applicability = ''
          policy.coverage_rate = 0
          policy.start_date = ''
          policy.end_date = ''
          policy.uploaded_file = null
        })
      }

      const resetUpload = () => {
        selectedFile.value = null
        isProcessing.value = false
        isLoadingDefault.value = false
        processingComplete.value = false
        uploadStatus.value = null
        processingStatus.value = { progress: 0, message: '' }
        taskId.value = null
        uploadedFileName.value = ''
        processingStartTime.value = ''
        fileInput.value.value = ''
        sections.value = []
        showContentViewer.value = false
        policyExtractionComplete.value = false
        policyExtractionInProgress.value = false
        policyExtractionMessage.value = ''
        policyExtractionProgress.value = 0
        showPolicyExtractor.value = false
        policies.value = []
        extractedPoliciesCount.value = 0
        selectedSectionsCount.value = 0
        currentStep.value = 1
        stepHistory.value = [1]
      }

      const goToPolicyDashboard = () => {
        showCongratulationsModal.value = false
        window.location.href = '/policy-dashboard'
      }

      // Watch for changes in policies to initialize form data
      watch(policies, () => {
        if (policies.value.length > 0) {
          initializePolicyFormData()
          initializeComplianceData()
        }
      }, { immediate: true })

      // Cleanup interval on component unmount
      onUnmounted(() => {
        if (progressInterval) {
          clearInterval(progressInterval)
        }
      })

      return {
        selectedFile,
        isDragOver,
        isUploading,
        isLoadingDefault,
        isProcessing,
        processingComplete,
        uploadStatus,
        fileInput,
        processingStatus,
        uploadedFileName,
        processingStartTime,
        showContentViewer,
        sections,
        searchQuery,
        filteredSections,
        policyExtractionComplete,
        policyExtractionInProgress,
        policyExtractionMessage,
        policyExtractionProgress,
        showPolicyExtractor,
        policies,
        extractedPoliciesCount,
        selectedSectionsCount,
        currentStep,
        triggerFileInput,
        handleFileSelect,
        handleDrop,
        removeFile,
        formatFileSize,
        uploadFile,
        loadDefaultData,
        resetUpload,
        viewExtractedContent,
        closeContentViewer,
        toggleSection,
        updateSelection,
        updateSubsectionSelection,
        selectAllSections,
        deselectAllSections,
        saveSelectedSections,
        viewPolicyExtractor,
        closePolicyExtractor,
        goBack,
        goToStep,
        showPolicyDetail,
        currentPolicy,
        currentPolicyIndex,
        isEditing,
        editPolicy,
        savePolicy,
        saveAllPolicies,
        expandedRows,
        toggleExpandRow,
        getFormattedControl,
        policyDetails,
        saveAllDetails,
        closePolicyDetail,
        handleSubPolicyFileUpload,
        resetAllForms,
        uniqueSectionNames,
        policyFormData,
        initializePolicyFormData,
        initializeDynamicForms,
        complianceData,
        getComplianceItems,
        initializeComplianceData,
        handleComplianceFileUpload,
        addComplianceItem,
        removeComplianceItem,
        showCongratulationsModal,
        goToPolicyDashboard
      }
    }
  }
  </script>
  
  <style scoped>
  .upload-framework-container {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
    font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
    margin-left: 280px !important;
  }
  
  /* Step Indicator */
  .step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 3rem;
    padding: 2rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
  }
  
  .step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
  }
  
  .step-number {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 1.1rem;
    background: #e2e8f0;
    color: #64748b;
    transition: all 0.3s ease;
  }
  
  .step-item.active .step-number {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: scale(1.1);
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  }
  
  .step-item.completed .step-number {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
  }
  
  .step-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #64748b;
    text-align: center;
    transition: all 0.3s ease;
  }
  
  .step-item.active .step-label {
    color: #1e293b;
    font-weight: 600;
  }
  
  .step-item.completed .step-label {
    color: #0f766e;
  }
  
  .step-divider {
    width: 80px;
    height: 2px;
    background: #e2e8f0;
    margin: 0 1rem;
    transition: all 0.3s ease;
  }
  
  .step-item.completed + .step-divider {
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  }
  
  /* Back Button */
  .back-button-container {
    margin-bottom: 1.5rem;
  }
  
  .back-btn {
    background: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
  
  .back-btn:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }
  
  .header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }
  
  .header h1 {
    color: #1e293b;
    margin-bottom: 0.5rem;
    font-weight: 700;
    font-size: 2.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .header p {
    color: #64748b;
    font-size: 1.2rem;
    font-weight: 400;
  }
  
  .upload-section {
    background: white;
    border-radius: 20px;
    padding: 3rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  /* Upload Area */
  .upload-area {
    border: 3px dashed #cbd5e1;
    border-radius: 16px;
    padding: 4rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    position: relative;
    overflow: hidden;
  }
  
  .upload-area::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .upload-area:hover::before,
  .upload-area.drag-over::before {
    opacity: 1;
  }
  
  .upload-area:hover,
  .upload-area.drag-over {
    border-color: #667eea;
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
  }
  
  .upload-content {
    position: relative;
    z-index: 1;
  }
  
  .upload-icon-container {
    margin-bottom: 2rem;
  }
  
  .upload-icon {
    font-size: 4rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: float 3s ease-in-out infinite;
  }
  
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }
  
  .upload-content h3 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-weight: 600;
    font-size: 1.75rem;
  }
  
  .upload-content p {
    color: #64748b;
    margin-bottom: 2rem;
    font-size: 1.1rem;
  }
  
  .supported-formats {
    color: #94a3b8;
    font-size: 0.9rem;
    padding: 1rem;
    background: rgba(148, 163, 184, 0.1);
    border-radius: 8px;
    display: inline-block;
  }
  
  /* OR Divider */
  .or-divider {
    display: flex;
    align-items: center;
    text-align: center;
    margin: 2rem 0;
    padding: 1rem;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .divider-line {
    flex: 1;
    height: 2px;
    background: #e2e8f0;
  }
  
  .divider-text {
    padding: 0 1rem;
    font-size: 0.9rem;
    color: #64748b;
    font-weight: 500;
  }
  
  .default-data-section {
    text-align: center;
    margin-bottom: 2rem;
    padding: 2rem;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .default-data-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  .default-icon-container {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 2rem;
  }
  
  .load-default-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
  
  .load-default-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }
  
  .load-default-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
  
  /* File Preview */
  .file-preview {
    margin: 2rem 0;
    padding: 2rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 16px;
    border: 2px solid #e2e8f0;
    transition: all 0.3s ease;
  }
  
  .file-preview:hover {
    border-color: #cbd5e1;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }
  
  .file-info {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .file-icon-container {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .file-icon {
    font-size: 2rem;
    color: white;
  }
  
  .file-details h4 {
    margin: 0;
    color: #1e293b;
    font-weight: 600;
    font-size: 1.2rem;
  }
  
  .file-details p {
    margin: 0.5rem 0 0 0;
    color: #64748b;
    font-size: 1rem;
  }
  
  .remove-btn {
    margin-left: auto;
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  }
  
  .remove-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
  }
  
  .upload-actions {
    text-align: center;
  }
  
  .upload-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 1rem 2.5rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  .upload-btn:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
  }
  
  .upload-btn:disabled {
    background: #cbd5e1;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
  }
  
  /* Processing Section */
  .processing-section {
    text-align: center;
    padding: 4rem 2rem;
  }
  
  .processing-header {
    margin-bottom: 3rem;
  }
  
  .processing-icon-container {
    margin-bottom: 2rem;
  }
  
  .processing-icon {
    font-size: 4rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .processing-header h3 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-weight: 600;
    font-size: 2rem;
  }
  
  .processing-header p {
    color: #64748b;
    font-size: 1.2rem;
  }
  
  .progress-container {
    position: relative;
    margin-bottom: 3rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
  }
  
  .progress-bar {
    width: 100%;
    height: 12px;
    background: #e2e8f0;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2, #4facfe);
    border-radius: 20px;
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    background-size: 200% 100%;
    animation: shimmer 2s infinite;
  }
  
  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }
  
  .progress-text {
    position: absolute;
    top: -35px;
    right: 0;
    font-weight: 600;
    color: #1e293b;
    font-size: 1.1rem;
    background: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .processing-details {
    display: flex;
    justify-content: center;
    gap: 3rem;
    flex-wrap: wrap;
  }
  
  .detail-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: #64748b;
    font-size: 0.95rem;
  }
  
  .detail-item i {
    color: #667eea;
    font-size: 1.3rem;
  }
  
  /* Completion Section */
  .completion-section {
    text-align: center;
    padding: 4rem 2rem;
  }
  
  .completion-icon-container {
    margin-bottom: 2rem;
  }
  
  .success-circle {
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    color: white;
    font-size: 48px;
    box-shadow: 0 20px 40px rgba(16, 185, 129, 0.3);
    animation: successPulse 2s ease-in-out infinite;
  }
  
  @keyframes successPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }
  
  .completion-header h3 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-weight: 700;
    font-size: 2.2rem;
  }
  
  .completion-header p {
    color: #64748b;
    font-size: 1.2rem;
    max-width: 600px;
    margin: 0 auto 3rem;
  }
  
  .completion-actions {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .view-content-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  .view-content-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
  }
  
  /* Extraction Section */
  .extraction-section {
    text-align: center;
    padding: 4rem 2rem;
  }
  
  .extraction-header {
    margin-bottom: 3rem;
  }
  
  .extraction-icon-container {
    margin-bottom: 2rem;
  }
  
  .extraction-icon {
    font-size: 4rem;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .extraction-header h3 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-weight: 600;
    font-size: 2rem;
  }
  
  .extraction-header p {
    color: #64748b;
    font-size: 1.2rem;
  }
  
  .extraction-details {
    display: flex;
    justify-content: center;
    gap: 3rem;
    flex-wrap: wrap;
  }
  
  /* Policy Review Section */
  .policy-review-section {
    text-align: center;
    padding: 4rem 2rem;
  }
  
  .review-header {
    margin-bottom: 3rem;
  }
  
  .review-icon-container {
    margin-bottom: 2rem;
  }
  
  .review-header h3 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-weight: 700;
    font-size: 2.2rem;
  }
  
  .review-header p {
    color: #64748b;
    font-size: 1.2rem;
    max-width: 600px;
    margin: 0 auto 3rem;
  }
  
  .policy-summary {
    display: flex;
    gap: 2rem;
    justify-content: center;
    margin-bottom: 3rem;
    flex-wrap: wrap;
  }
  
  .summary-card {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    min-width: 200px;
    transition: all 0.3s ease;
  }
  
  .summary-card:hover {
    border-color: #cbd5e1;
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
  }
  
  .summary-icon {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
  }
  
  .summary-content h4 {
    margin: 0;
    color: #1e293b;
    font-weight: 700;
    font-size: 2rem;
  }
  
  .summary-content p {
    margin: 0.5rem 0 0 0;
    color: #64748b;
    font-weight: 500;
  }
  
  .review-actions {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .view-policies-btn, .upload-another-btn {
    padding: 1rem 2rem;
    border: none;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
  }
  
  .view-policies-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  .view-policies-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
  }
  
  .upload-another-btn {
    background: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
  
  .upload-another-btn:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }
  
  /* Enhanced Professional Layout for Step 6 */
  .policy-details-section {
    padding: 2rem 0;
  }

  .details-header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    color: white;
  }

  .details-header h3 {
    margin: 0 0 0.5rem 0;
    font-weight: 700;
    font-size: 2rem;
  }

  .details-header p {
    margin: 0;
    font-size: 1.1rem;
    opacity: 0.9;
  }

  .professional-layout {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  /* Information Sections */
  .info-section {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    transition: all 0.3s ease;
    border-left: 4px solid transparent;
  }

  .info-section:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  }

  .framework-section {
    border-left-color: #10b981;
  }

  .policy-section {
    border-left-color: #3b82f6;
  }

  .sub-policy-section {
    border-left-color: #f59e0b;
  }

  .section-title {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    padding: 1.5rem 2rem;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .section-title h4 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .section-title h4 i {
    color: #667eea;
  }

  .section-badge {
    background: #e2e8f0;
    color: #64748b;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  /* Form Grid Layout */
  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 2rem;
  }

  .form-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-field.full-width {
    grid-column: 1 / -1;
  }

  .form-field label {
    font-weight: 600;
    color: #374151;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .form-field input,
  .form-field textarea,
  .form-field select {
    width: 100%;
    padding: 0.875rem 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    background: #fafafa;
  }

  .form-field input:focus,
  .form-field textarea:focus,
  .form-field select:focus {
    outline: none;
    border-color: #667eea;
    background: white;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  .form-field textarea {
    min-height: 100px;
    resize: vertical;
  }

  /* File Upload Styling */
  .file-upload-wrapper {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .file-upload-wrapper input[type="file"] {
    display: none;
  }

  .file-upload-label {
    background: #667eea;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s ease;
  }

  .file-upload-label:hover {
    background: #5a67d8;
    transform: translateY(-1px);
  }

  .file-name {
    color: #10b981;
    font-size: 0.875rem;
    font-weight: 500;
    padding: 0.5rem 1rem;
    background: #f0fdf4;
    border-radius: 6px;
  }

  /* Policy Management Container */
  .policy-management-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 12px;
    border: 1px solid #e2e8f0;
  }

  /* Enhanced Compliance Management */
  .compliance-management-section {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    margin-top: 1.5rem;
    border-left: 4px solid #8b5cf6;
  }

  .compliance-header {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    color: white;
    padding: 1.5rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .compliance-title {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .compliance-title h4 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .policy-ref {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .compliance-stats {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .compliance-count {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .add-compliance-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .add-compliance-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }

  /* Compliance Grid - Enhanced Width */
  .compliance-grid {
    padding: 2rem;
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    max-width: none;
  }

  .compliance-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    width: 100%;
    max-width: none;
  }

  .compliance-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }

  .compliance-card-header {
    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .compliance-identifier {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .compliance-letter {
    background: #8b5cf6;
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 0.9rem;
  }

  .compliance-number {
    font-weight: 600;
    color: #1e293b;
    font-size: 1rem;
  }

  .compliance-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: capitalize;
  }

  .status-pending {
    background: #fef3c7;
    color: #92400e;
  }

  .status-in-progress {
    background: #dbeafe;
    color: #1e40af;
  }

  .status-completed {
    background: #d1fae5;
    color: #065f46;
  }

  .status-not-applicable {
    background: #fee2e2;
    color: #991b1b;
  }

  .remove-compliance-btn {
    background: #ef4444;
    color: white;
    border: none;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    font-size: 0.75rem;
  }

  .remove-compliance-btn:hover {
    background: #dc2626;
    transform: scale(1.1);
  }

  /* Compliance Form Grid - Full Width */
  .compliance-form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    padding: 1.5rem;
    width: 100%;
  }

  .compliance-form-grid .form-field.full-width {
    grid-column: 1 / -1;
  }

  .status-select {
    appearance: none;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
    background-position: right 0.5rem center;
    background-repeat: no-repeat;
    background-size: 1.5em 1.5em;
    padding-right: 2.5rem;
  }

  /* Global Actions */
  .global-actions {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-top: 3rem;
    padding: 2rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 16px;
    border: 2px dashed #cbd5e1;
  }

  .save-btn.primary {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  }

  .save-btn.primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
  }

  .reset-btn.secondary {
    background: linear-gradient(135deg, #64748b 0%, #475569 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(100, 116, 139, 0.3);
  }

  .reset-btn.secondary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(100, 116, 139, 0.4);
  }

  /* Status Messages */
  .status-message {
    margin-top: 2rem;
    padding: 1.5rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 1rem;
    font-weight: 500;
    font-size: 1rem;
  }

  .status-message.success {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    color: #065f46;
    border: 2px solid #10b981;
  }

  .status-message.error {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    color: #991b1b;
    border: 2px solid #ef4444;
  }

  /* Global Success Notification */
  .global-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    max-width: 400px;
    z-index: 2000;
    border-radius: 8px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    overflow: hidden;
    animation: slideIn 0.3s ease-out;
  }

  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }

  .global-notification.success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    border-left: 4px solid #047857;
  }

  .notification-content {
    display: flex;
    align-items: flex-start;
    padding: 1rem;
    color: white;
  }

  .notification-content i {
    font-size: 1.2rem;
    margin-right: 0.75rem;
    margin-top: 0.2rem;
  }

  .notification-message {
    flex: 1;
    font-size: 0.95rem;
    white-space: pre-line;
  }

  .notification-close {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    cursor: pointer;
    padding: 0.25rem;
    font-size: 1rem;
    transition: all 0.2s ease;
  }

  .notification-close:hover {
    color: white;
    transform: scale(1.1);
  }

  /* Congratulations Modal */
  .congratulations-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    backdrop-filter: blur(8px);
    animation: fadeIn 0.3s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .congratulations-container {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border-radius: 20px;
    width: 90%;
    max-width: 600px;
    padding: 3rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
    animation: scaleIn 0.5s ease-out;
  }

  @keyframes scaleIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  }

  .congratulations-header {
    margin-bottom: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .congratulations-icon-container {
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.5rem;
    color: white;
    font-size: 48px;
    box-shadow: 0 20px 40px rgba(16, 185, 129, 0.3);
    animation: successPulse 2s ease-in-out infinite;
  }

  .congratulations-header h2 {
    color: #10b981;
    margin-bottom: 1rem;
    font-weight: 700;
    font-size: 2.5rem;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .congratulations-message {
    color: #374151;
    font-size: 1.25rem;
    font-weight: 500;
    margin: 0;
  }

  .congratulations-content {
    margin-bottom: 2rem;
  }

  .congratulations-content p {
    color: #6b7280;
    font-size: 1.1rem;
    line-height: 1.6;
    margin-bottom: 1rem;
  }

  .congratulations-actions {
    margin-top: 1rem;
  }

  .ok-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  }

  .ok-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
  }

  /* Content Viewer Modal */
  .content-viewer-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(8px);
  }

  .content-viewer-container {
    background-color: white;
    border-radius: 20px;
    width: 90%;
    max-width: 1200px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
  }

  .content-viewer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem;
    border-bottom: 2px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }

  .content-viewer-header h3 {
    margin: 0;
    color: #1e293b;
    font-weight: 700;
    font-size: 1.5rem;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #64748b;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
  }

  .close-btn:hover {
    background: #e2e8f0;
    color: #1e293b;
    transform: scale(1.1);
  }

  .content-viewer-body {
    flex-grow: 1;
    overflow-y: auto;
    padding: 2rem;
    max-height: 70vh;
  }

  .search-box {
    margin-bottom: 2rem;
  }

  .search-box input {
    width: 100%;
    padding: 1rem 1.5rem;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: #f8fafc;
  }

  .search-box input:focus {
    outline: none;
    border-color: #667eea;
    background: white;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  }

  .section-list {
    max-height: calc(70vh - 120px);
    overflow-y: auto;
    border-radius: 12px;
    border: 2px solid #e2e8f0;
  }

  .section-item {
    border-bottom: 1px solid #e2e8f0;
  }

  .section-item:last-child {
    border-bottom: none;
  }

  .section-header {
    padding: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    background-color: #f8fafc;
    transition: all 0.3s ease;
  }

  .section-header:hover {
    background-color: #f1f5f9;
  }

  .section-checkbox {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-weight: 600;
    color: #1e293b;
  }

  .section-checkbox input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
    accent-color: #667eea;
  }

  .section-content {
    padding: 1rem 2rem 1.5rem 4rem;
    background-color: white;
  }

  .subsection-item {
    padding: 1rem;
    margin-bottom: 0.5rem;
    border-radius: 8px;
    transition: all 0.3s ease;
  }

  .subsection-item:hover {
    background-color: #f8fafc;
  }

  .subsection-checkbox {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: #475569;
    font-weight: 500;
  }

  .subsection-checkbox input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: #667eea;
  }

  .content-viewer-footer {
    padding: 2rem;
    border-top: 2px solid #e2e8f0;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }

  .select-all-btn, .deselect-all-btn, .save-selection-btn {
    padding: 0.875rem 1.5rem;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
  }

  .select-all-btn, .deselect-all-btn {
    background-color: white;
    color: #64748b;
    border: 2px solid #e2e8f0;
  }

  .select-all-btn:hover, .deselect-all-btn:hover {
    background-color: #f8fafc;
    border-color: #cbd5e1;
    transform: translateY(-2px);
  }

  .save-selection-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }

  .save-selection-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  }

  /* Policy Extractor Modal */
  .policy-extractor-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(8px);
  }

  .policy-extractor-container {
    background-color: white;
    border-radius: 20px;
    width: 95%;
    max-width: 1400px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
  }

  .policy-extractor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem;
    border-bottom: 2px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }

  .policy-extractor-header h3 {
    margin: 0;
    color: #1e293b;
    font-weight: 700;
    font-size: 1.5rem;
  }

  .policy-extractor-body {
    flex-grow: 1;
    overflow: hidden;
    padding: 2rem;
  }

  .policy-table-container {
    height: 100%;
    overflow: auto;
    border-radius: 12px;
    border: 2px solid #e2e8f0;
  }

  .policy-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
  }

  .policy-table th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem 1rem;
    text-align: left;
    font-weight: 600;
    font-size: 1rem;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .policy-table td {
    padding: 1.5rem 1rem;
    border-bottom: 1px solid #e2e8f0;
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.5;
    max-width: 300px;
    word-wrap: break-word;
    vertical-align: top;
  }

  .policy-table tr:hover {
    background-color: #f8fafc;
  }

  .policy-table tr:nth-child(even) {
    background-color: #fafbfc;
  }

  .policy-table tr:nth-child(even):hover {
    background-color: #f1f5f9;
  }

  .policy-table tr.expanded-row {
    background-color: #f1f5f9;
  }

  .control-cell {
    max-width: 300px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .actions-cell {
    display: flex;
    gap: 0.5rem;
  }

  .view-btn, .edit-btn, .save-all-btn {
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    font-size: 0.875rem;
    border: none;
  }

  .view-btn {
    background: #f8fafc;
    color: #1e293b;
    border: 1px solid #e2e8f0;
  }

  .view-btn:hover {
    background: #f1f5f9;
    transform: translateY(-1px);
  }

  .edit-btn {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  }

  .edit-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }

  .save-all-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    margin-right: 1rem;
  }

  .save-all-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  }

  .policy-actions {
    display: flex;
    align-items: center;
  }

  /* Detail row styling */
  .detail-row {
    background-color: #f8fafc;
  }

  .policy-details-container {
    padding: 1.5rem;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .policy-details-section {
    margin-bottom: 1rem;
  }

  .policy-details-section h4 {
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 0.5rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .detail-content {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 0.875rem;
    color: #334155;
  }

  .policy-details-section .control-content {
    grid-column: 1 / -1;
    white-space: pre-line;
  }

  .control-content ul {
    margin: 0;
    padding-left: 1.5rem;
  }

  .control-content li {
    margin-bottom: 0.5rem;
  }

  /* No policies message */
  .no-policies-message {
    padding: 3rem;
    text-align: center;
    color: #64748b;
    background: #f8fafc;
    border-radius: 12px;
    border: 2px dashed #e2e8f0;
  }

  .no-policies-message p {
    font-size: 1.1rem;
    font-weight: 500;
    margin: 0;
  }

  /* Policy Edit Modal */
  .policy-edit-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1100;
    backdrop-filter: blur(8px);
  }

  .policy-edit-container {
    background-color: white;
    border-radius: 20px;
    width: 90%;
    max-width: 900px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
  }

  .policy-edit-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    border-bottom: 2px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }

  .policy-edit-header h3 {
    margin: 0;
    color: #1e293b;
    font-weight: 700;
    font-size: 1.5rem;
  }

  .policy-edit-actions {
    display: flex;
    gap: 1rem;
  }

  .policy-edit-body {
    padding: 2rem;
    overflow-y: auto;
    max-height: calc(90vh - 90px);
  }

  .policy-field {
    margin-bottom: 1.5rem;
  }

  .policy-field label {
    display: block;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }

  .policy-field input,
  .policy-field textarea {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.3s ease;
  }

  .policy-field input:focus,
  .policy-field textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  /* Responsive Design */
  @media (max-width: 1200px) {
    .form-grid {
      grid-template-columns: 1fr;
    }
    
    .compliance-form-grid {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 768px) {
    .upload-framework-container {
      padding: 1rem;
      margin-left: 0 !important;
    }
    
    .step-indicator {
      flex-direction: column;
      gap: 1rem;
    }
    
    .step-divider {
      width: 2px;
      height: 40px;
      margin: 0;
    }
    
    .header h1 {
      font-size: 2rem;
    }
    
    .upload-section {
      padding: 2rem 1.5rem;
    }
    
    .processing-details,
    .extraction-details {
      flex-direction: column;
      gap: 1rem;
    }
    
    .policy-summary {
      flex-direction: column;
      align-items: center;
    }
    
    .completion-actions,
    .review-actions {
      flex-direction: column;
      align-items: center;
    }
    
    .content-viewer-footer {
      flex-direction: column;
    }
    
    .policy-table {
      font-size: 0.875rem;
    }
    
    .policy-table th,
    .policy-table td {
      padding: 1rem 0.5rem;
    }
    
    .compliance-header {
      flex-direction: column;
      align-items: stretch;
      text-align: center;
      gap: 1rem;
    }
    
    .compliance-stats {
      flex-direction: column;
      gap: 0.5rem;
    }
    
    .add-compliance-btn {
      width: 100%;
      justify-content: center;
    }
    
    .global-actions {
      flex-direction: column;
      gap: 1rem;
    }
    
    .save-btn.primary,
    .reset-btn.secondary {
      width: 100%;
    }
    
    .file-upload-wrapper {
      flex-direction: column;
      align-items: stretch;
    }
    
    .compliance-card-header {
      flex-direction: column;
      text-align: center;
      gap: 0.5rem;
    }
    
    .compliance-identifier {
      justify-content: center;
    }
  }

  @media (max-width: 480px) {
    .details-header {
      padding: 1.5rem;
    }
    
    .details-header h3 {
      font-size: 1.5rem;
    }
    
    .section-title {
      padding: 1rem 1.5rem;
    }
    
    .section-title h4 {
      font-size: 1rem;
    }
    
    .form-grid {
      padding: 1.5rem;
    }
    
    .compliance-grid {
      padding: 1.5rem;
    }
    
    .compliance-form-grid {
      padding: 1rem;
    }
  }
  /* Enhanced Processing Animations */
.processing-animation-container {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.document-processing-visual {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.document-icon {
  position: relative;
  z-index: 10;
  background: #f8fafc;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.document-icon i {
  font-size: 2rem;
  color: #475569;
}

.processing-waves {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.wave {
  position: absolute;
  border: 2px solid #e2e8f0;
  border-radius: 50%;
  animation: wave-pulse 2s ease-in-out infinite;
}

.wave-1 {
  width: 80px;
  height: 80px;
  top: 20px;
  left: 20px;
  animation-delay: 0s;
}

.wave-2 {
  width: 100px;
  height: 100px;
  top: 10px;
  left: 10px;
  animation-delay: 0.5s;
}

.wave-3 {
  width: 120px;
  height: 120px;
  top: 0;
  left: 0;
  animation-delay: 1s;
}

@keyframes wave-pulse {
  0% {
    transform: scale(0.8);
    opacity: 1;
    border-color: #cbd5e1;
  }
  50% {
    transform: scale(1);
    opacity: 0.7;
    border-color: #94a3b8;
  }
  100% {
    transform: scale(1.2);
    opacity: 0;
    border-color: #64748b;
  }
}

.extraction-particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #64748b;
  border-radius: 50%;
  animation: particle-float 3s ease-in-out infinite;
}

.particle:nth-child(1) { top: 10%; left: 20%; animation-delay: 0s; }
.particle:nth-child(2) { top: 30%; right: 15%; animation-delay: 0.5s; }
.particle:nth-child(3) { bottom: 20%; left: 25%; animation-delay: 1s; }
.particle:nth-child(4) { bottom: 35%; right: 20%; animation-delay: 1.5s; }
.particle:nth-child(5) { top: 60%; left: 10%; animation-delay: 2s; }
.particle:nth-child(6) { top: 50%; right: 10%; animation-delay: 2.5s; }

@keyframes particle-float {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: translateY(-20px) scale(1.2);
    opacity: 1;
  }
}

.processing-details-enhanced {
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

.main-status {
  font-size: 1.1rem;
  color: #475569;
  margin-bottom: 1.5rem;
}

.document-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  color: #64748b;
}

.processing-stages {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.4;
  transition: all 0.3s ease;
}

.stage.active {
  opacity: 1;
}

.stage-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #cbd5e1;
  transition: all 0.3s ease;
}

.stage.active .stage-dot {
  background: #64748b;
  transform: scale(1.2);
}

.stage span {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

/* AI Extraction Animations */
.ai-extraction-container {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.ai-brain-visual {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brain-core {
  position: relative;
  z-index: 10;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 50%;
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  animation: brain-pulse 2s ease-in-out infinite;
}

.brain-core i {
  font-size: 2.5rem;
  color: #64748b;
}

@keyframes brain-pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 6px 30px rgba(0, 0, 0, 0.15);
  }
}

.neural-network {
  position: absolute;
  width: 100%;
  height: 100%;
}

.neuron {
  position: absolute;
  width: 6px;
  height: 6px;
  background: #94a3b8;
  border-radius: 50%;
  animation: neuron-pulse 2s ease-in-out infinite;
}

.neuron:nth-child(1) { top: 15%; left: 30%; animation-delay: 0s; }
.neuron:nth-child(2) { top: 25%; right: 20%; animation-delay: 0.25s; }
.neuron:nth-child(3) { top: 45%; left: 15%; animation-delay: 0.5s; }
.neuron:nth-child(4) { top: 55%; right: 25%; animation-delay: 0.75s; }
.neuron:nth-child(5) { bottom: 25%; left: 25%; animation-delay: 1s; }
.neuron:nth-child(6) { bottom: 35%; right: 15%; animation-delay: 1.25s; }
.neuron:nth-child(7) { bottom: 15%; left: 40%; animation-delay: 1.5s; }
.neuron:nth-child(8) { top: 35%; left: 50%; animation-delay: 1.75s; }

@keyframes neuron-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.5);
    opacity: 1;
  }
}

.data-flow {
  position: absolute;
  width: 100%;
  height: 100%;
}

.data-bit {
  position: absolute;
  width: 3px;
  height: 3px;
  background: #64748b;
  border-radius: 50%;
  animation: data-flow-animation 4s linear infinite;
}

.data-bit:nth-child(odd) {
  animation-direction: normal;
}

.data-bit:nth-child(even) {
  animation-direction: reverse;
}

@keyframes data-flow-animation {
  0% {
    transform: rotate(0deg) translateX(60px) rotate(0deg);
    opacity: 0;
  }
  25% {
    opacity: 1;
  }
  75% {
    opacity: 1;
  }
  100% {
    transform: rotate(360deg) translateX(60px) rotate(-360deg);
    opacity: 0;
  }
}

.ai-processing-details {
  text-align: center;
  max-width: 700px;
  margin: 0 auto;
}

.ai-stages {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
  margin-top: 2rem;
}

.ai-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  opacity: 0.3;
  transition: all 0.3s ease;
  padding: 1rem;
  border-radius: 8px;
}

.ai-stage.active {
  opacity: 1;
  background: #f8fafc;
  transform: translateY(-2px);
}

.ai-stage-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.ai-stage.active .ai-stage-icon {
  background: #64748b;
  color: white;
  transform: scale(1.1);
}

.ai-stage span {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
  text-align: center;
}

/* Responsive Design */
@media (max-width: 768px) {
  .processing-stages,
  .ai-stages {
    gap: 1rem;
  }
  
  .stage,
  .ai-stage {
    min-width: 80px;
  }
  
  .document-processing-visual,
  .ai-brain-visual {
    width: 100px;
    height: 100px;
  }
  
  .document-icon {
    width: 50px;
    height: 50px;
  }
  
  .brain-core {
    width: 60px;
    height: 60px;
  }
}
/* Current Section Indicator */
.current-section {
  margin: 1.5rem 0;
  padding: 1rem;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-radius: 8px;
  border-left: 4px solid #64748b;
}

.section-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #475569;
  font-weight: 500;
}

.section-indicator i {
  color: #64748b;
}

/* Processing Activity Indicator */
.processing-activity {
  margin-top: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: #64748b;
  font-size: 0.9rem;
}

.activity-dots {
  display: flex;
  gap: 0.25rem;
}

.activity-dots .dot {
  width: 6px;
  height: 6px;
  background: #64748b;
  border-radius: 50%;
  animation: activity-pulse 1.5s ease-in-out infinite;
}

.activity-dots .dot:nth-child(1) {
  animation-delay: 0s;
}

.activity-dots .dot:nth-child(2) {
  animation-delay: 0.3s;
}

.activity-dots .dot:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes activity-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* Enhanced stage indicators */
.stage.active {
  opacity: 1;
  transform: translateY(-2px);
}

.stage.active .stage-dot {
  background: #64748b;
  transform: scale(1.2);
  box-shadow: 0 0 10px rgba(100, 116, 139, 0.3);
}
  </style>