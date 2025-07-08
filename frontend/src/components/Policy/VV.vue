<template>
    <div class="VV-page-wrapper">
      <div class="VV-page-header">
        <h2>Policy Versioning</h2>
      </div>
      <div class="VV-toggle-group">
        <button :class="['VV-toggle', { 'VV-active': selectedTab === 'framework' } ]" @click="selectTab('framework')">Framework</button>
        <button :class="['VV-toggle', { 'VV-active': selectedTab === 'policy' } ]" @click="selectTab('policy')">Policy</button>
        </div>
      <div v-if="selectedTab === 'framework'" class="VV-top-dropdowns">
        <CustomDropdown
          v-model="selectedFramework"
          :config="{
            label: 'Framework',
            values: frameworks.map(fw => ({ value: fw.id, label: fw.name })),
            defaultLabel: 'Select Framework'
          }"
          :showSearchBar="true"
          style="min-width: 300px; max-width: 360px; width: 340px;"
        />
        </div>
      <div v-else class="VV-top-dropdowns">
        <CustomDropdown
          v-model="selectedFramework"
          :config="{
            label: 'Framework',
            values: frameworks.map(fw => ({ value: fw.id, label: fw.name })),
            defaultLabel: 'Select Framework'
          }"
          :showSearchBar="true"
          style="min-width: 300px; max-width: 360px; width: 360px;"
        />
        <CustomDropdown
          v-model="selectedPolicy"
          :config="{
            label: 'Policy',
            values: policies.map(pol => ({ value: pol.id, label: pol.name })),
            defaultLabel: 'Select Policy'
          }"
          :showSearchBar="true"
          style="min-width: 300px; max-width: 360px; width: 360px;"
        />
        </div>
      <div v-if="selectedTab === 'framework' && selectedFramework">
        <div class="VV-container">
          <!-- Framework Form -->
          <form @submit.prevent="submitFramework">
            <div class="VV-form-group">
              <label class="VV-label">FRAMEWORK NAME *</label>
              <input class="VV-input" v-model="frameworkForm.name" type="text" required placeholder="Enter Framework name" />
              <small class="VV-desc">Enter a descriptive name for your framework</small>
                </div>
            <div class="VV-form-group">
              <label class="VV-label">DESCRIPTION *</label>
              <textarea class="VV-textarea" v-model="frameworkForm.description" rows="3" required placeholder="Enter framework description"></textarea>
              <small class="VV-desc">Describe the purpose, scope, and objectives of this framework</small>
              </div>
            <div class="VV-row">
              <div class="VV-form-group VV-half">
                <label class="VV-label">IDENTIFIER *</label>
                <input class="VV-input" v-model="frameworkForm.identifier" type="text" required placeholder="Enter Identifier" />
                <small class="VV-desc">Use a unique code like 'FW-001' or 'ISO-27001'</small>
            </div>
              <div class="VV-form-group VV-half">
                <label class="VV-label">CATEGORY *</label>
                <input class="VV-input" v-model="frameworkForm.category" type="text" required placeholder="Enter category" />
                <small class="VV-desc">e.g., Security, Compliance, Risk Management, etc.</small>
                </div>
                  </div>
            <div class="VV-row">
              <div class="VV-form-group VV-half">
                <label class="VV-label">INTERNAL/EXTERNAL *</label>
                <select class="VV-input" v-model="frameworkForm.internalExternal" required>
                  <option value="" disabled>Select Type</option>
                      <option value="Internal">Internal</option>
                      <option value="External">External</option>
                    </select>
                <small class="VV-desc">Select whether this framework is for internal or external use</small>
                  </div>
              <div class="VV-form-group VV-half">
                <label class="VV-label">UPLOAD DOCUMENT</label>
                <input class="VV-input" type="file" @change="handleFileUpload" />
                <small class="VV-desc">Upload a supporting document for this framework (optional)</small>
                    </div>
                  </div>
            <div class="VV-row">
              <div class="VV-form-group VV-half">
                <label class="VV-label">EFFECTIVE START DATE *</label>
                <input class="VV-input" v-model="frameworkForm.startDate" type="date" required />
                <small class="VV-desc">Date when the framework implementation begins</small>
                </div>
              <div class="VV-form-group VV-half">
                <label class="VV-label">EFFECTIVE END DATE *</label>
                <input class="VV-input" v-model="frameworkForm.endDate" type="date" required />
                <small class="VV-desc">Date when the framework expires or requires review</small>
                  </div>
                  </div>
          <div class="VV-row">
            <div class="VV-form-group VV-half">
              <label class="VV-label">CREATED BY *</label>
              <select class="VV-input" v-model="frameworkForm.createdByName" required>
                <option value="">Select Creator</option>
                <option v-for="user in users" :key="user.id" :value="user.name">{{ user.name }}</option>
              </select>
              <small class="VV-desc">Select who created this framework</small>
            </div>
            <div class="VV-form-group VV-half">
              <label class="VV-label">REVIEWER *</label>
              <select class="VV-input" v-model="frameworkForm.reviewer" required>
                <option value="">Select Reviewer</option>
                <option v-for="user in users" :key="user.id" :value="user.name">{{ user.name }}</option>
              </select>
              <small class="VV-desc">Select who will review this framework</small>
            </div>
          </div>
          </form>
              </div>
        <!-- Policy Tabbed/Stepper Container (Framework Mode) -->
        <div class="VV-policy-tabs-container">
          <div class="VV-policy-tabs-row">
            <div class="VV-policy-tabs">
              <button v-for="(tab, idx) in policyTabs" :key="tab.id" :class="['VV-policy-tab', { 'VV-policy-tab-active': idx === activePolicyTab, 'excluded': tab.exclude }]" @click="activePolicyTab = idx">
                Policy {{ idx + 1 }}
              </button>
              <button class="VV-add-policy-tab" @click="addPolicyTab">+ Add Policy</button>
                </div>
              </div>
          <div v-if="policyTabs.length && policyTabs[activePolicyTab]" class="VV-policy-form-container">
            <button 
              class="VV-exclude-policy-btn" 
              @click="excludePolicyTab(activePolicyTab)"
              :class="{ 'excluded': policyTabs[activePolicyTab].exclude }"
            >
              {{ policyTabs[activePolicyTab].exclude ? 'Include' : 'Exclude' }}
            </button>
            <div v-if="policyTabs[activePolicyTab].exclude" class="TT-excluded-message">
              This policy has been excluded and will not be included in the submission.
            </div>
            <!-- Hide form when policy is excluded -->
            <form v-else @submit.prevent="submitPolicy(activePolicyTab)" :key="policyTabs[activePolicyTab].id">
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">POLICY NAME *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].name" type="text" required placeholder="Enter policy name" />
                  <small class="VV-desc">Use a clear, descriptive name</small>
            </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">POLICY IDENTIFIER *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].identifier" type="text" required placeholder="Enter policy identifier" />
                  <small class="VV-desc">Use a unique code like 'POL-001'</small>
          </div>
              </div>
              <div class="VV-form-group">
                <label class="VV-label">DESCRIPTION *</label>
                <textarea class="VV-textarea" v-model="policyTabs[activePolicyTab].description" rows="3" required placeholder="Enter policy description"></textarea>
                <small class="VV-desc">Describe the policy's purpose, requirements, and key provisions</small>
            </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">SCOPE *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].scope" type="text" required placeholder="Enter policy scope" />
                  <small class="VV-desc">Specify what areas/processes/systems policy applies to</small>
              </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">DEPARTMENT *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].department" type="text" required placeholder="Enter department" />
                  <small class="VV-desc">e.g., IT, HR, Finance, Legal, Operations</small>
            </div>
                </div>
              <div class="VV-form-group">
                <label class="VV-label">OBJECTIVE *</label>
                <textarea class="VV-textarea" v-model="policyTabs[activePolicyTab].objective" rows="3" required placeholder="Enter policy objective"></textarea>
                <small class="VV-desc">Explain what this policy is designed to accomplish</small>
                  </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">COVERAGE RATE (%) *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].coverageRate" type="number" min="0" max="100" step="0.01" required placeholder="Enter coverage rate" />
                  <small class="VV-desc">Range: 0-100, step: 0.01</small>
                  </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">APPLICABILITY *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].applicability" type="text" required placeholder="Enter applicability" />
                  <small class="VV-desc">Define the target audience, roles, or entities</small>
                </div>
                </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">POLICY TYPE *</label>
                  <select 
                  class="VV-input" 
                  v-model="policyTabs[activePolicyTab].type"
                  @change="handlePolicyTypeChange(activePolicyTab, $event.target.value)"
                  :disabled="policyTabs[activePolicyTab].exclude"
                  required
                >
                  <option value="">Select Policy Type</option>
                  <option v-for="type in policyTypes" :key="type" :value="type">{{ type }}</option>
                </select>
                  <small class="VV-desc">e.g., Security Policy, HR Policy</small>
                  </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">POLICY CATEGORY *</label>
                <select 
                  class="VV-input" 
                  v-model="policyTabs[activePolicyTab].category"
                  @change="handlePolicyCategoryChange(activePolicyTab, $event.target.value)"
                  :disabled="!policyTabs[activePolicyTab].type || policyTabs[activePolicyTab].exclude"
                  required
                >
                  <option value="">Select Policy Category</option>
                  <option v-for="category in policyCategories" 
                          :key="category" 
                          :value="category">{{ category }}</option>
                </select>
                  <small class="VV-desc">Choose a category that best describes this policy's focus area</small>
                  </div>
                </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">POLICY SUB CATEGORY *</label>
                <select 
                  class="VV-input" 
                  v-model="policyTabs[activePolicyTab].subCategory"
                  @change="handlePolicySubCategoryChange(activePolicyTab, $event.target.value)"
                  :disabled="!policyTabs[activePolicyTab].category || policyTabs[activePolicyTab].exclude"
                  required
                >
                  <option value="">Select Policy Sub Category</option>
                  <option v-for="subCategory in policySubCategories" 
                          :key="subCategory" 
                          :value="subCategory">{{ subCategory }}</option>
                </select>
                  <small class="VV-desc">Provide more specific classification</small>
                </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">APPLICABLE ENTITIES *</label>
                <div class="form-row">
                  <div class="form-group entities-group">
                    <div class="entities-multi-select" @click.stop>
                      <div class="entities-dropdown">
                        <div 
                          class="selected-entities" 
                          :class="{ 
                            'active': policyTabs[activePolicyTab]?.showEntitiesDropdown,
                            'error': error && error.includes('entities')
                          }"
                          @click="toggleEntitiesDropdown(activePolicyTab)"
                        >
                          <div class="entity-content">
                            <span v-if="loading" class="loading-text">
                              Loading entities...
                            </span>
                            <span v-else-if="isAllEntitiesSelected(activePolicyTab)" class="entity-tag all-tag">
                              All Locations
                            </span>
                            <span v-else-if="getSelectedEntitiesCount(activePolicyTab) === 0" class="placeholder">
                              Select entities...
                            </span>
                            <span v-else class="entity-count">
                              {{ getSelectedEntitiesCount(activePolicyTab) }} location(s) selected
                            </span>
                          </div>
                          <i class="fas fa-chevron-down dropdown-arrow"></i>
                        </div>
                        <div v-if="policyTabs[activePolicyTab]?.showEntitiesDropdown" class="entities-options">
                          <div v-if="loading" class="entities-loading">
                            Loading entities...
                          </div>
                          <div v-else-if="error" class="entities-error">
                            {{ error }}
                          </div>
                          <template v-else>
                            <div 
                              v-for="entity in entities" 
                              :key="entity.id" 
                              :class="['entity-option', { 'all-option': entity.id === 'all' }]"
                              @click="selectEntity(activePolicyTab, entity.id)"
                            >
                              <input 
                                type="checkbox" 
                                :checked="entity.id === 'all' ? isAllEntitiesSelected(activePolicyTab) : isEntitySelected(activePolicyTab, entity.id)"
                                @change="handleEntitySelection(activePolicyTab, entity.id, $event.target.checked)"
                                @click.stop
                              />
                              <span class="entity-label">{{ entity.label }}</span>
                            </div>
                          </template>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                  <small class="VV-desc">Select the locations/entities this policy applies to</small>
                  </div>
                  </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">START DATE *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].startDate" type="date" required />
                  <small class="VV-desc">Date when this policy takes effect</small>
                </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">END DATE *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].endDate" type="date" required />
                  <small class="VV-desc">Date when this policy expires or requires review/renewal</small>
                    </div>
                  </div>
              <!-- Show CreatedByName and Reviewer only in policy tab -->
              <div v-if="selectedTab === 'policy'" class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">CREATED BY *</label>
                  <select 
                    class="VV-input" 
                    v-model="policyTabs[activePolicyTab].createdByName" 
                    required
                  >
                    <option value="">Select Creator</option>
                    <option v-for="user in users" :key="user.id" :value="user.name">{{ user.name }}</option>
                  </select>
                  <small class="VV-desc">Select who created this policy</small>
                </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">REVIEWER *</label>
                  <select 
                    class="VV-input" 
                    v-model="policyTabs[activePolicyTab].reviewer" 
                    required
                  >
                    <option value="">Select Reviewer</option>
                    <option v-for="user in users" :key="user.id" :value="user.name">{{ user.name }}</option>
                  </select>
                  <small class="VV-desc">Select who will review this policy</small>
                    </div>
                  </div>
              <div class="VV-form-group">
                <label class="VV-label">UPLOAD DOCUMENT</label>
                <input class="VV-input" type="file" @change="e => handlePolicyFileUpload(e, activePolicyTab)" />
                <small class="VV-desc">Upload supporting documentation (optional)</small>
                    </div>
            </form>
                  </div>
                </div>
        <div v-if="policyTabs.length && policyTabs[activePolicyTab]" class="VV-subpolicy-tabs-container">
          <div class="VV-subpolicy-tabs-row">
            <div class="VV-subpolicy-tabs">
              <button v-for="(subTab, subIdx) in policyTabs[activePolicyTab].subPolicies" :key="subTab.id" :class="['VV-subpolicy-tab', { 'VV-subpolicy-tab-active': subIdx === policyTabs[activePolicyTab].activeSubPolicyTab, 'excluded': subTab.exclude }]" @click="policyTabs[activePolicyTab].activeSubPolicyTab = subIdx">
                Subpolicy {{ subIdx + 1 }}
              </button>
              <button class="VV-add-subpolicy-tab" @click="addSubPolicyTab(activePolicyTab)">+ Add Sub Policy</button>
                    </div>
                  </div>
          <div v-if="policyTabs[activePolicyTab].subPolicies && policyTabs[activePolicyTab].subPolicies.length" class="VV-subpolicy-form-container">
            <button 
              class="VV-exclude-subpolicy-btn" 
              @click="excludeSubPolicyTab(activePolicyTab, policyTabs[activePolicyTab].activeSubPolicyTab)"
              :class="{ 'excluded': policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].exclude }"
            >
              {{ policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].exclude ? 'Include' : 'Exclude' }}
            </button>
            <div v-if="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].exclude" class="TT-excluded-message">
              This subpolicy has been excluded and will not be included in the submission.
            </div>
            <!-- Hide form when subpolicy is excluded -->
            <form v-else>
              <div class="VV-form-group">
                <label class="VV-label">SUB POLICY NAME *</label>
                <input class="VV-input" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].name" type="text" required placeholder="Enter sub policy name" />
                <small class="VV-desc">Use a clear name that describes this sub-policy's specific focus</small>
                          </div>
              <div class="VV-form-group">
                <label class="VV-label">IDENTIFIER *</label>
                <input class="VV-input" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].identifier" type="text" required placeholder="Enter identifier" />
                <small class="VV-desc">Use a unique code like 'SUB-001' or append to parent policy ID</small>
                        </div>
              <div class="VV-form-group">
                <label class="VV-label">CONTROL *</label>
                <textarea class="VV-textarea" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].control" rows="3" required placeholder="Enter control"></textarea>
                <small class="VV-desc">Specify the control mechanisms, procedures, or safeguards to be implemented</small>
                          </div>
              <div class="VV-form-group">
                <label class="VV-label">DESCRIPTION *</label>
                <textarea class="VV-textarea" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].description" rows="3" required placeholder="Enter description"></textarea>
                <small class="VV-desc">Explain the intent, requirements, or significance of this sub-policy</small>
                        </div>
            </form>
                      </div>
                    </div>
                  </div>
      <div v-else-if="selectedTab === 'framework' && !selectedFramework">
        <!-- Optionally, you can show a message here: Please select a framework -->
      </div>
      <div v-if="selectedTab === 'framework' && selectedFramework" class="VV-universal-submit-wrapper">
        <button class="VV-universal-submit-btn" @click.prevent="showVersionModal = true">Submit</button>
      </div>
      <!-- Version Type Modal Popup -->
      <div v-if="showVersionModal" class="version-modal-overlay" @click="showVersionModal = false">
        <div class="version-modal" @click.stop>
          <h2>Version Type</h2>
          <div class="version-type-options">
            <label class="version-type-option">
              <input type="radio" value="minor" v-model="selectedVersionType" />
              <span class="radio-custom" :class="{ checked: selectedVersionType === 'minor' }"></span>
              <span class="version-type-title">Minor Version</span>
              <span class="version-type-desc">Incremental changes and improvements<br/><span class="version-type-example">Example: 1.0 → 1.1</span></span>
            </label>
            <label class="version-type-option">
              <input type="radio" value="major" v-model="selectedVersionType" />
              <span class="radio-custom" :class="{ checked: selectedVersionType === 'major' }"></span>
              <span class="version-type-title">Major Version</span>
              <span class="version-type-desc">Significant changes or overhauls<br/><span class="version-type-example">Example: 1.5 → 2.0</span></span>
            </label>
          </div>
          <div class="version-modal-actions">
            <button class="btn-primary" @click.prevent="confirmVersionType">OK</button>
            <button class="btn-secondary" @click.prevent="showVersionModal = false">Cancel</button>
          </div>
        </div>
      </div>
      <div v-if="selectedTab === 'policy' && selectedFramework && selectedPolicy">
        <div class="VV-policy-tabs-container">
          <div class="VV-policy-tabs-row">
            <div class="VV-policy-tabs">
              <button v-for="(tab, idx) in policyTabs" :key="tab.id" :class="['VV-policy-tab', { 'VV-policy-tab-active': idx === activePolicyTab, 'excluded': tab.exclude }]" @click="activePolicyTab = idx">
                Policy {{ idx + 1 }}
              </button>
              <!-- Only show + Add Policy in framework mode -->
              <button v-if="selectedTab === 'framework'" class="VV-add-policy-tab" @click="addPolicyTab">+ Add Policy</button>
                </div>
                  </div>
          <div v-if="policyTabs.length && policyTabs[activePolicyTab]" class="VV-policy-form-container">
            <!-- Only show Exclude in framework mode -->
            <button v-if="selectedTab === 'framework'" class="VV-exclude-policy-btn" @click="excludePolicyTab(activePolicyTab)">Exclude</button>
            <form @submit.prevent="submitPolicy(activePolicyTab)" :key="policyTabs[activePolicyTab].id">
              <!-- Same policy form as above -->
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">POLICY NAME *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].name" type="text" required placeholder="Enter policy name" />
                  <small class="VV-desc">Use a clear, descriptive name</small>
                  </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">POLICY IDENTIFIER *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].identifier" type="text" required placeholder="Enter policy identifier" />
                  <small class="VV-desc">Use a unique code like 'POL-001'</small>
                </div>
                </div>
              <div class="VV-form-group">
                <label class="VV-label">DESCRIPTION *</label>
                <textarea class="VV-textarea" v-model="policyTabs[activePolicyTab].description" rows="3" required placeholder="Enter policy description"></textarea>
                <small class="VV-desc">Describe the policy's purpose, requirements, and key provisions</small>
              </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">SCOPE *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].scope" type="text" required placeholder="Enter policy scope" />
                  <small class="VV-desc">Specify what areas/processes/systems policy applies to</small>
                </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">DEPARTMENT *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].department" type="text" required placeholder="Enter department" />
                  <small class="VV-desc">e.g., IT, HR, Finance, Legal, Operations</small>
                  </div>
                </div>
              <div class="VV-form-group">
                <label class="VV-label">OBJECTIVE *</label>
                <textarea class="VV-textarea" v-model="policyTabs[activePolicyTab].objective" rows="3" required placeholder="Enter policy objective"></textarea>
                <small class="VV-desc">Explain what this policy is designed to accomplish</small>
                  </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">COVERAGE RATE (%) *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].coverageRate" type="number" min="0" max="100" step="0.01" required placeholder="Enter coverage rate" />
                  <small class="VV-desc">Range: 0-100, step: 0.01</small>
                  </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">APPLICABILITY *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].applicability" type="text" required placeholder="Enter applicability" />
                  <small class="VV-desc">Define the target audience, roles, or entities</small>
                  </div>
                  </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">POLICY TYPE *</label>
                  <select 
                    class="VV-input" 
                    v-model="policyTabs[activePolicyTab].type"
                    @change="handlePolicyTypeChange(activePolicyTab, $event.target.value)"
                    required
                  >
                    <option value="">Select Policy Type</option>
                    <option v-for="type in policyTypes" :key="type" :value="type">{{ type }}</option>
                  </select>
                  <small class="VV-desc">e.g., Security Policy, HR Policy</small>
                  </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">POLICY CATEGORY *</label>
                  <select 
                    class="VV-input" 
                    v-model="policyTabs[activePolicyTab].category"
                    @change="handlePolicyCategoryChange(activePolicyTab, $event.target.value)"
                    :disabled="!policyTabs[activePolicyTab].type"
                    required
                  >
                    <option value="">Select Policy Category</option>
                    <option v-for="category in policyCategories" 
                            :key="category" 
                            :value="category">{{ category }}</option>
                  </select>
                  <small class="VV-desc">Choose a category that best describes this policy's focus area</small>
                </div>
              </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">POLICY SUB CATEGORY *</label>
                  <select 
                    class="VV-input" 
                    v-model="policyTabs[activePolicyTab].subCategory"
                    :disabled="!policyTabs[activePolicyTab].category"
                    required
                  >
                    <option value="">Select Policy Sub Category</option>
                    <option v-for="subCategory in policySubCategories" 
                            :key="subCategory" 
                            :value="subCategory">{{ subCategory }}</option>
                  </select>
                  <small class="VV-desc">Provide more specific classification</small>
            </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">APPLICABLE ENTITIES *</label>
                  <div class="form-row">
                    <div class="form-group entities-group">
                      <div class="entities-multi-select" @click.stop>
                        <div class="entities-dropdown">
                          <div 
                            class="selected-entities" 
                            :class="{ 
                              'active': policyTabs[activePolicyTab]?.showEntitiesDropdown,
                              'error': error && error.includes('entities')
                            }"
                            @click="toggleEntitiesDropdown(activePolicyTab)"
                          >
                            <div class="entity-content">
                              <span v-if="loading" class="loading-text">
                                Loading entities...
                              </span>
                              <span v-else-if="isAllEntitiesSelected(activePolicyTab)" class="entity-tag all-tag">
                                All Locations
                              </span>
                              <span v-else-if="getSelectedEntitiesCount(activePolicyTab) === 0" class="placeholder">
                                Select entities...
                              </span>
                              <span v-else class="entity-count">
                                {{ getSelectedEntitiesCount(activePolicyTab) }} location(s) selected
                              </span>
                            </div>
                            <i class="fas fa-chevron-down dropdown-arrow"></i>
                          </div>
                          <div v-if="policyTabs[activePolicyTab]?.showEntitiesDropdown" class="entities-options">
                            <div v-if="loading" class="entities-loading">
                              Loading entities...
                            </div>
                            <div v-else-if="error" class="entities-error">
                              {{ error }}
                            </div>
                            <template v-else>
                              <div 
                                v-for="entity in entities" 
                                :key="entity.id" 
                                :class="['entity-option', { 'all-option': entity.id === 'all' }]"
                                @click="selectEntity(activePolicyTab, entity.id)"
                              >
                                <input 
                                  type="checkbox" 
                                  :checked="entity.id === 'all' ? isAllEntitiesSelected(activePolicyTab) : isEntitySelected(activePolicyTab, entity.id)"
                                  @change="handleEntitySelection(activePolicyTab, entity.id, $event.target.checked)"
                                  @click.stop
                                />
                                <span class="entity-label">{{ entity.label }}</span>
                              </div>
                            </template>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <small class="VV-desc">Select the locations/entities this policy applies to</small>
            </div>
          </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">START DATE *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].startDate" type="date" required />
                  <small class="VV-desc">Date when this policy takes effect</small>
        </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">END DATE *</label>
                  <input class="VV-input" v-model="policyTabs[activePolicyTab].endDate" type="date" required />
                  <small class="VV-desc">Date when this policy expires or requires review/renewal</small>
          </div>
              </div>
              <div class="VV-row">
                <div class="VV-form-group VV-half">
                  <label class="VV-label">CREATED BY *</label>
                  <select 
                    class="VV-input" 
                    v-model="policyTabs[activePolicyTab].createdByName" 
                    required
                  >
                    <option value="">Select Creator</option>
                    <option v-for="user in users" :key="user.id" :value="user.name">{{ user.name }}</option>
                  </select>
                  <small class="VV-desc">Select who created this policy</small>
                </div>
                <div class="VV-form-group VV-half">
                  <label class="VV-label">REVIEWER *</label>
                  <select 
                    class="VV-input" 
                    v-model="policyTabs[activePolicyTab].reviewer" 
                    required
                  >
                    <option value="">Select Reviewer</option>
                    <option v-for="user in users" :key="user.id" :value="user.name">{{ user.name }}</option>
                  </select>
                  <small class="VV-desc">Select who will review this policy</small>
          </div>
              </div>
              <div class="VV-form-group">
                <label class="VV-label">UPLOAD DOCUMENT</label>
                <input class="VV-input" type="file" @change="e => handlePolicyFileUpload(e, activePolicyTab)" />
                <small class="VV-desc">Upload supporting documentation (optional)</small>
              </div>
            </form>
                </div>
              </div>
        <div v-if="policyTabs.length && policyTabs[activePolicyTab]" class="VV-subpolicy-tabs-container">
          <div class="VV-subpolicy-tabs-row">
            <div class="VV-subpolicy-tabs">
              <button v-for="(subTab, subIdx) in policyTabs[activePolicyTab].subPolicies" :key="subTab.id" :class="['VV-subpolicy-tab', { 'VV-subpolicy-tab-active': subIdx === policyTabs[activePolicyTab].activeSubPolicyTab, 'excluded': subTab.exclude }]" @click="policyTabs[activePolicyTab].activeSubPolicyTab = subIdx">
                Subpolicy {{ subIdx + 1 }}
              </button>
              <button class="VV-add-subpolicy-tab" @click="addSubPolicyTab(activePolicyTab)">+ Add Sub Policy</button>
            </div>
          </div>
          <div v-if="policyTabs[activePolicyTab].subPolicies && policyTabs[activePolicyTab].subPolicies.length" class="VV-subpolicy-form-container">
            <button 
              class="VV-exclude-subpolicy-btn" 
              @click="excludeSubPolicyTab(activePolicyTab, policyTabs[activePolicyTab].activeSubPolicyTab)"
              :class="{ 'excluded': policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].exclude }"
            >
              {{ policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].exclude ? 'Include' : 'Exclude' }}
            </button>
            <div v-if="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].exclude" class="TT-excluded-message">
              This subpolicy has been excluded and will not be included in the submission.
            </div>
            <form>
              <div class="VV-form-group">
                <label class="VV-label">SUB POLICY NAME *</label>
                <input class="VV-input" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].name" type="text" required placeholder="Enter sub policy name" />
                <small class="VV-desc">Use a clear name that describes this sub-policy's specific focus</small>
        </div>
              <div class="VV-form-group">
                <label class="VV-label">IDENTIFIER *</label>
                <input class="VV-input" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].identifier" type="text" required placeholder="Enter identifier" />
                <small class="VV-desc">Use a unique code like 'SUB-001' or append to parent policy ID</small>
          </div>
              <div class="VV-form-group">
                <label class="VV-label">CONTROL *</label>
                <textarea class="VV-textarea" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].control" rows="3" required placeholder="Enter control"></textarea>
                <small class="VV-desc">Specify the control mechanisms, procedures, or safeguards to be implemented</small>
              </div>
              <div class="VV-form-group">
                <label class="VV-label">DESCRIPTION *</label>
                <textarea class="VV-textarea" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].description" rows="3" required placeholder="Enter description"></textarea>
                <small class="VV-desc">Explain the intent, requirements, or significance of this sub-policy</small>
              </div>
            </form>
          </div>
        </div>
        </div>
      </div>
      <!-- Add submit button for policy tab -->
      <div v-if="selectedTab === 'policy' && selectedFramework && selectedPolicy" class="VV-universal-submit-wrapper">
        <button class="VV-universal-submit-btn" @click.prevent="showVersionModal = true">Submit</button>
      </div>
    </template>
    
    <script>
  import './VV.css'
  import CustomDropdown from '../CustomDropdown.vue'
  import axios from 'axios'
  import { PopupService } from '@/modules/popup'  // Fix the import path

const API_BASE_URL = 'http://localhost:8000/api'

    export default {
  name: 'VV',
    components: {
      CustomDropdown
    },
    data() {
      return {
        selectedTab: 'framework',
        selectedFramework: '',
        selectedPolicy: '',
        frameworks: [],
        policies: [],
        policyTypes: [],
        policyCategories: [],
        policySubCategories: [],
        policyData: [], // Store all policy category data
        users: [], // Add users array
        entities: [], // Initialize as empty array
        frameworkForm: {
          name: '',
          description: '',
          identifier: '',
          category: '',
          internalExternal: '',
          file: null,
          startDate: '',
          endDate: '',
          createdByName: '',
          reviewer: ''
        },
        policyTabs: [],
        activePolicyTab: 0,
        loading: false,
        error: null,
        showVersionModal: false,
        selectedVersionType: 'minor' // Default version type
      }
    },
    watch: {
      selectedFramework(newVal) {
        this.handleFrameworkSelection(newVal)
      },
      selectedPolicy(newVal) {
        if (this.selectedTab === 'policy' && this.selectedFramework && newVal) {
          this.fetchPolicyDetails(newVal)
        }
      },
      selectedTab(newVal) {
        if (newVal === 'framework') {
          this.selectedPolicy = ''
          this.fetchFrameworks()
          if (this.selectedFramework) {
            this.handleFrameworkSelection(this.selectedFramework)
          }
        } else if (newVal === 'policy') {
          this.selectedPolicy = ''
          this.policyTabs = []
          this.fetchFrameworks()
        }
      }
    },
    async created() {
      try {
        await Promise.all([
          this.fetchFrameworks(),
          this.fetchPolicyData(),
          this.fetchEntities(),
          this.fetchUsers()
        ])
      } catch (error) {
        console.error('Error in component creation:', error)
        this.error = 'Failed to initialize component'
      }
    },
    methods: {
      selectTab(tab) {
        this.selectedTab = tab
      },
      handleFileUpload(e) {
        this.frameworkForm.file = e.target.files[0]
      },
      // Add the missing addSubPolicyTab method
      addSubPolicyTab(policyIdx) {
        const currentPolicy = this.policyTabs[policyIdx];
        this.policyTabs[policyIdx].subPolicies.push({
          id: `new-subpolicy-${Date.now()}`, // Add 'new-' prefix to identify new subpolicies
          name: '',
          identifier: '',
          control: '',
          description: '',
          createdByName: currentPolicy.createdByName, // Use policy's createdByName
          exclude: false
        })
        this.policyTabs[policyIdx].activeSubPolicyTab = this.policyTabs[policyIdx].subPolicies.length - 1
      },
      // Add method to handle policy file upload
      async handlePolicyFileUpload(e, idx) {
        const file = e.target.files[0];
        if (file) {
          this.policyTabs[idx].file = file;
          
          // If we need to upload immediately, we can use the following code:
          // try {
          //   const userId = localStorage.getItem('user_id') || 'default-user';
          //   const uploadResponse = await policyService.uploadPolicyDocument(
          //     file,
          //     userId,
          //     this.policyTabs[idx].name || 'Unnamed Policy',
          //     'policy'
          //   );
          //   
          //   if (uploadResponse.data.success) {
          //     this.policyTabs[idx].docUrl = uploadResponse.data.file.url;
          //     PopupService.success('Document uploaded successfully', 'Upload Success');
          //   }
          // } catch (error) {
          //   console.error('Error uploading policy document:', error);
          //   PopupService.error('Failed to upload document: ' + (error.response?.data?.error || error.message), 'Upload Error');
          // }
        }
      },
      // Add method to handle policy tab addition
      addPolicyTab() {
        const newPolicyId = `new-policy-${Date.now()}`;
        console.log('Creating new policy with ID:', newPolicyId);
        
        const createdByName = this.selectedTab === 'framework' ? this.frameworkForm.createdByName : '';
        const reviewer = this.selectedTab === 'framework' ? this.frameworkForm.reviewer : '';
        
        this.policyTabs.push({
          id: newPolicyId, // Use the new ID format
          name: '',
          identifier: '',
          description: '',
          scope: '',
          department: '',
          objective: '',
          coverageRate: '',
          applicability: '',
          type: '',
          category: '',
          subCategory: '',
          entities: [],
          startDate: '',
          endDate: '',
          file: null,
          createdByName: createdByName,
          reviewer: reviewer,
          exclude: false,
          subPolicies: [
            {
              id: `new-subpolicy-${Date.now()}`, // Use new ID format for subpolicy
              name: '',
              identifier: '',
              control: '',
              description: '',
              createdByName: createdByName,
              exclude: false
            }
          ],
          activeSubPolicyTab: 0
        });
        this.activePolicyTab = this.policyTabs.length - 1;
      },

      async fetchFrameworks() {
        try {
          this.loading = true
          const response = await axios.get(`${API_BASE_URL}/frameworks/`)
          console.log('Raw framework response:', response.data)
          
          // Map frameworks
          this.frameworks = response.data.map(fw => ({ 
            id: fw.FrameworkId, 
            name: fw.FrameworkName,
            description: fw.FrameworkDescription,
            category: fw.Category,
            internalExternal: fw.InternalExternal,
            startDate: fw.StartDate,
            endDate: fw.EndDate,
            status: fw.Status
          }))

          console.log('Mapped frameworks:', this.frameworks)

          if (this.frameworks.length === 0) {
            PopupService.info('No frameworks found', 'No Data');
          }

        } catch (error) {
          console.error('Error fetching frameworks:', error)
          this.error = 'Failed to fetch frameworks'
          PopupService.error('Failed to fetch frameworks', 'Error')
        } finally {
          this.loading = false
        }
      },

      // Add new methods for policy type/category handling
      async fetchPolicyData() {
        try {
          const response = await axios.get(`${API_BASE_URL}/policy-categories/`)
          this.policyData = response.data
          
          // Extract unique policy types
          this.policyTypes = [...new Set(this.policyData.map(item => item.PolicyType))]
          console.log('Fetched policy types:', this.policyTypes)
        } catch (error) {
          console.error('Error fetching policy data:', error)
          this.error = 'Failed to fetch policy data'
          PopupService.error('Failed to fetch policy data', 'Error')
        }
      },

      handlePolicyTypeChange(idx, value) {
        console.log('Policy type changed:', value)
        const policy = this.policyTabs[idx]
        policy.type = value
        policy.category = '' // Clear category when type changes
        policy.subCategory = '' // Clear subcategory when type changes
        
        // Update available categories for this type
        this.updatePolicyCategoriesByType(value)
      },

      handlePolicyCategoryChange(idx, value) {
        console.log('Policy category changed:', value)
        const policy = this.policyTabs[idx]
        policy.category = value
        policy.subCategory = '' // Clear subcategory when category changes
        
        // Update available subcategories for this type and category
        this.updateSubCategoriesByCategory(policy.type, value)
      },

      handlePolicySubCategoryChange(idx, value) {
        console.log('Policy subcategory changed:', value)
        this.policyTabs[idx].subCategory = value
      },

      updatePolicyCategoriesByType(policyType) {
        console.log('Updating categories for type:', policyType)
        if (!policyType || !this.policyData) {
          this.policyCategories = []
          this.policySubCategories = []
          return
        }

        // Filter categories based on selected type
        const filteredData = this.policyData.filter(item => item.PolicyType === policyType)
        console.log('Filtered data:', filteredData)

        const categories = [...new Set(filteredData.map(item => item.PolicyCategory))]
        console.log('Available categories for type:', categories)
        this.policyCategories = categories

        // Reset category and subcategory in the active policy tab
        if (this.policyTabs[this.activePolicyTab]) {
          this.policyTabs[this.activePolicyTab].category = ''
          this.policyTabs[this.activePolicyTab].subCategory = ''
        }
        this.policySubCategories = []
      },

      updateSubCategoriesByCategory(policyType, policyCategory) {
        console.log('Updating subcategories for type:', policyType, 'and category:', policyCategory)
        if (!policyType || !policyCategory || !this.policyData) {
          this.policySubCategories = []
          return
        }

        // Filter subcategories based on selected type and category
        const filteredData = this.policyData.filter(item => 
          item.PolicyType === policyType && 
          item.PolicyCategory === policyCategory
        )
        console.log('Filtered data:', filteredData)

        const subcategories = [...new Set(filteredData.map(item => item.PolicySubCategory))]
        console.log('Available subcategories:', subcategories)
        this.policySubCategories = subcategories

        // Reset subcategory in the active policy tab
        if (this.policyTabs[this.activePolicyTab]) {
          this.policyTabs[this.activePolicyTab].subCategory = ''
        }
      },

      // Add entity handling methods
      async fetchEntities() {
        try {
          this.loading = true
          const response = await axios.get(`${API_BASE_URL}/entities/`)
          console.log('Raw entities response:', response.data)
          
          if (response.data.entities) {
            // Map entities directly from the backend response
            this.entities = response.data.entities.map(entity => ({
              id: entity.id,
              label: entity.label
            }))
            console.log('Mapped entities:', this.entities)
          } else {
            throw new Error('Invalid response format')
          }
        } catch (error) {
          console.error('Error fetching entities:', error)
          this.error = 'Failed to fetch entities'
        } finally {
          this.loading = false
        }
      },

      handleEntitySelection(idx, entityId, isChecked) {
        if (idx < 0 || !this.policyTabs[idx]) return
        
        console.log('handleEntitySelection:', { idx, entityId, isChecked })
        
        // Initialize entities if undefined
        if (!this.policyTabs[idx].entities) {
          this.policyTabs[idx].entities = []
        }
        
        if (entityId === 'all') {
          // When "All Locations" is selected, set entities to "all" string
          this.policyTabs[idx].entities = isChecked ? "all" : []
        } else {
          // Ensure we're working with an array
          let currentEntities = this.policyTabs[idx].entities === "all" ? [] 
            : Array.isArray(this.policyTabs[idx].entities) ? this.policyTabs[idx].entities 
            : []
          
          const numericId = Number(entityId)
          
          if (isChecked) {
            if (!currentEntities.includes(numericId)) {
              currentEntities.push(numericId)
            }
          } else {
            currentEntities = currentEntities.filter(id => id !== numericId)
          }
          
          // Store as array of numeric IDs
          this.policyTabs[idx].entities = currentEntities
        }
        
        console.log('Updated entities:', this.policyTabs[idx].entities)
      },

      selectEntity(idx, entityId) {
        if (idx < 0 || !this.policyTabs[idx]) return
        
        const isSelected = entityId === 'all' 
          ? this.isAllEntitiesSelected(idx)
          : this.isEntitySelected(idx, entityId)
        
        this.handleEntitySelection(idx, entityId, !isSelected)
      },

      isEntitySelected(idx, entityId) {
        const policy = this.policyTabs[idx]
        if (!policy || !policy.entities) return false
        
        if (policy.entities === "all") {
          return entityId === 'all'
        }
        
        return Array.isArray(policy.entities) && policy.entities.includes(Number(entityId))
      },

      isAllEntitiesSelected(idx) {
        const policy = this.policyTabs[idx]
        return policy && policy.entities === "all"
      },

      getSelectedEntitiesCount(idx) {
        const policy = this.policyTabs[idx]
        if (!policy || !policy.entities) return 0
        
        if (policy.entities === "all") {
          return this.entities.length - 1 // Subtract 1 for the "All" option
        }
        
        return Array.isArray(policy.entities) ? policy.entities.length : 0
      },

      toggleEntitiesDropdown(idx) {
        if (idx < 0 || !this.policyTabs[idx]) return
        
        // Close all other dropdowns first
        this.policyTabs.forEach((policy, index) => {
          if (index !== idx) {
            policy.showEntitiesDropdown = false
          }
        })
        
        // Toggle current dropdown
        const currentPolicy = this.policyTabs[idx]
        currentPolicy.showEntitiesDropdown = !currentPolicy.showEntitiesDropdown
        
        // If opening the dropdown and no entities loaded yet, fetch them
        if (currentPolicy.showEntitiesDropdown && this.entities.length <= 1) {
          this.fetchEntities()
        }
      },

      closeAllEntityDropdowns() {
        this.policyTabs.forEach(policy => {
          policy.showEntitiesDropdown = false
        })
      },
      async handleFrameworkSelection(newVal) {
        if (!newVal) {
          this.resetForm()
          this.policies = [] // Clear policies when no framework is selected
          return
        }

        try {
          this.loading = true
          const [frameworkResponse, policiesResponse] = await Promise.all([
            axios.get(`${API_BASE_URL}/frameworks/${newVal}/`),
            axios.get(`${API_BASE_URL}/frameworks/${newVal}/get-policies/`)
          ])

          console.log('Raw framework details:', frameworkResponse.data)
          console.log('Raw framework policies:', policiesResponse.data)

          const framework = frameworkResponse.data
          
          // Log reviewer data before assignment
          console.log('DEBUG: Framework reviewer data:', {
            reviewer: framework.Reviewer,
            reviewerName: framework.ReviewerName
          })
          
          // Get the reviewer name from the framework
          const frameworkReviewer = framework.ReviewerName || framework.Reviewer || ''
          
          this.frameworkForm = {
            name: framework.FrameworkName,
            description: framework.FrameworkDescription,
            identifier: framework.Identifier,
            category: framework.Category,
            internalExternal: framework.InternalExternal,
            file: null,
            startDate: framework.StartDate,
            endDate: framework.EndDate,
            createdByName: framework.CreatedByName,
            reviewer: frameworkReviewer
          }
          
          // Log frameworkForm after assignment
          console.log('DEBUG: Framework form after assignment:', {
            reviewer: this.frameworkForm.reviewer
          })

          // Filter for Approved and Active policies only
          const approvedActivePolicies = policiesResponse.data.filter(p => 
            p.Status === 'Approved' && p.ActiveInactive === 'Active'
          )

          // Populate the policies array for the dropdown
          this.policies = approvedActivePolicies.map(p => ({
            id: p.PolicyId,
            name: p.PolicyName
          }))

          // Map policies for policy tabs
          const policiesWithDetails = await Promise.all(
            approvedActivePolicies.map(async p => {
              const subpoliciesResponse = await axios.get(`${API_BASE_URL}/policies/${p.PolicyId}/get-subpolicies/`)
              
              // In framework mode, use framework's reviewer for all policies and subpolicies
              const policyReviewer = this.selectedTab === 'framework' ? frameworkReviewer : (p.ReviewerName || p.Reviewer || '')
              
              return {
                id: p.PolicyId.toString(), // Ensure ID is a string
                name: p.PolicyName,
                description: p.PolicyDescription,
                status: p.Status,
                department: p.Department,
                scope: p.Scope,
                objective: p.Objective,
                identifier: p.Identifier,
                coverageRate: p.CoverageRate,
                applicability: p.Applicability,
                type: p.PolicyType,
                category: p.PolicyCategory,
                subCategory: p.PolicySubCategory,
                entities: p.Entities,
                startDate: p.StartDate,
                endDate: p.EndDate,
              file: null,
                createdByName: p.CreatedByName || framework.CreatedByName,
                reviewer: policyReviewer,
                exclude: false, // Initialize exclude as false
                activeSubPolicyTab: 0,
                subPolicies: subpoliciesResponse.data.map(sp => ({
                  id: sp.SubPolicyId.toString(), // Ensure ID is a string
                  name: sp.SubPolicyName,
                  identifier: sp.Identifier,
                  control: sp.Control,
                  description: sp.Description,
                  status: sp.Status
                }))
              }
            })
          )

          if (policiesWithDetails.length === 0) {
            PopupService.info('No approved and active policies found for this framework', 'No Policies')
          }

          this.policyTabs = policiesWithDetails
            this.activePolicyTab = 0

        } catch (error) {
          console.error('Error handling framework selection:', error)
          this.error = 'Failed to load framework details'
          PopupService.error('Failed to load framework details', 'Error')
        } finally {
          this.loading = false
        }
      },
      async submitFrameworkVersion() {
        try {
          this.loading = true;
          console.log('Submitting framework version with policies:', this.policyTabs);
          
          // Validate required fields
          if (!this.validateForm('framework')) {
            return;
          }

          // Format data for submission
          const versionData = {
            version_type: this.selectedVersionType,
            FrameworkName: this.frameworkForm.name,
            FrameworkDescription: this.frameworkForm.description,
            Category: this.frameworkForm.category,
            StartDate: this.frameworkForm.startDate,
            EndDate: this.frameworkForm.endDate,
            Identifier: this.frameworkForm.identifier,
            CreatedByName: this.frameworkForm.createdByName,
            ReviewerName: this.frameworkForm.reviewer,
            InternalExternal: this.frameworkForm.internalExternal,
            policies: [],
            new_policies: []
          };

          // Process each policy tab
          this.policyTabs.forEach(policy => {
            // Skip excluded policies
            if (policy.exclude) {
              return;
            }

            const policyData = {
              PolicyName: policy.name,
              PolicyDescription: policy.description,
              Department: policy.department,
              Scope: policy.scope,
              Objective: policy.objective,
              Identifier: policy.identifier,
              CoverageRate: policy.coverageRate,
              Applicability: policy.applicability,
              PolicyType: policy.type,
              PolicyCategory: policy.category,
              PolicySubCategory: policy.subCategory,
              Entities: policy.entities,
              StartDate: policy.startDate,
              EndDate: policy.endDate,
              CreatedByName: policy.createdByName,
              ReviewerName: policy.reviewer,
              subpolicies: [],
              new_subpolicies: []
            };

            // Process subpolicies
            policy.subPolicies.forEach(sp => {
              // Skip excluded subpolicies
              if (sp.exclude) {
                return;
              }

              const subpolicyData = {
                SubPolicyName: sp.name,
                Description: sp.description,
                Identifier: sp.identifier,
                Control: sp.control,
                CreatedByName: sp.createdByName || policy.createdByName
              };

              // Check if it's a new subpolicy or existing one
              if (sp.id && !String(sp.id).startsWith('new-')) {
                // Existing subpolicy
                subpolicyData.original_subpolicy_id = parseInt(sp.id);
                policyData.subpolicies.push(subpolicyData);
              } else {
                // New subpolicy
                policyData.new_subpolicies.push(subpolicyData);
              }
            });

            // Check if it's a new policy or existing one
            if (policy.id && !String(policy.id).startsWith('new-')) {
              // Existing policy
              policyData.original_policy_id = parseInt(policy.id);
              versionData.policies.push(policyData);
            } else {
              // New policy
              versionData.new_policies.push(policyData);
            }
          });

          console.log('Submitting version data:', versionData);
          
          const response = await axios.post(
            `${API_BASE_URL}/frameworks/${this.selectedFramework}/create-version/`,
            versionData,
            {
              headers: {
                'Content-Type': 'application/json'
              }
            }
          );

          console.log('Framework version creation response:', response.data);
          
          // Show success message with popup
          PopupService.success('Framework version created successfully!', 'Success');
          
          // Reset form and stay on the same page
          setTimeout(() => {
            this.resetForm();
            window.location.href = '/create-policy/versioning';
          }, 1500);

        } catch (error) {
          console.error('Error submitting framework version:', error);
          const errorMessage = error.response?.data?.error || 'Failed to submit framework version';
          PopupService.error(errorMessage, 'Error Creating Framework Version');
        } finally {
          this.loading = false;
        }
      },
      validateForm(type) {
        if (type === 'framework') {
          if (!this.frameworkForm.name) {
            PopupService.warning('Framework name is required', 'Validation Error');
            return false;
          }
          if (!this.frameworkForm.description) {
            PopupService.warning('Framework description is required', 'Validation Error');
            return false;
          }
          if (!this.frameworkForm.identifier) {
            PopupService.warning('Framework identifier is required', 'Validation Error');
            return false;
          }
          if (!this.frameworkForm.category) {
            PopupService.warning('Framework category is required', 'Validation Error');
            return false;
          }
          if (!this.frameworkForm.internalExternal) {
            PopupService.warning('Internal/External selection is required', 'Validation Error');
            return false;
          }
          if (!this.frameworkForm.startDate) {
            PopupService.warning('Start date is required', 'Validation Error');
            return false;
          }
          if (!this.frameworkForm.createdByName) {
            PopupService.warning('Created By is required', 'Validation Error');
            return false;
          }
          if (!this.frameworkForm.reviewer) {
            PopupService.warning('Reviewer is required', 'Validation Error');
            return false;
          }
          return true;
        } else if (type === 'policy') {
          const policy = this.policyTabs[0];
          if (!policy.name) {
            PopupService.warning('Policy name is required', 'Validation Error');
            return false;
          }
          if (!policy.description) {
            PopupService.warning('Policy description is required', 'Validation Error');
            return false;
          }
          if (!policy.identifier) {
            PopupService.warning('Policy identifier is required', 'Validation Error');
            return false;
          }
          if (!policy.type) {
            PopupService.warning('Policy type is required', 'Validation Error');
            return false;
          }
          if (!policy.category) {
            PopupService.warning('Policy category is required', 'Validation Error');
            return false;
          }
          if (!policy.subCategory) {
            PopupService.warning('Policy sub-category is required', 'Validation Error');
            return false;
          }
          if (!policy.createdByName) {
            PopupService.warning('Created By is required', 'Validation Error');
            return false;
          }
          if (!policy.reviewer) {
            PopupService.warning('Reviewer is required', 'Validation Error');
            return false;
          }
          return true;
        }
        return false;
      },
      resetForm() {
          this.frameworkForm = {
          name: '',
          description: '',
          identifier: '',
          category: '',
          internalExternal: '',
          file: null,
          startDate: '',
          endDate: '',
          createdByName: '',
          reviewer: ''
        }
          this.policyTabs = []
          this.activePolicyTab = 0
          this.selectedFramework = ''
          this.selectedPolicy = ''
          this.showVersionModal = false
          this.selectedVersionType = 'minor' // Changed from this.versionType to this.selectedVersionType
        this.policies = [] // Clear policies array
      },
      async submitPolicyVersion() {
        try {
          this.loading = true;
          console.log('Submitting policy version with data:', this.policyTabs[0]);

          // Validate required fields
          if (!this.validateForm('policy')) {
            return;
          }

          // Format data for submission
          const versionData = {
            version_type: this.selectedVersionType,
            PolicyName: this.policyTabs[0].name,
            PolicyDescription: this.policyTabs[0].description,
            Department: this.policyTabs[0].department,
            Scope: this.policyTabs[0].scope,
            Objective: this.policyTabs[0].objective,
            Identifier: this.policyTabs[0].identifier,
            CoverageRate: this.policyTabs[0].coverageRate,
            Applicability: this.policyTabs[0].applicability,
            CreatedByName: this.policyTabs[0].createdByName,
            StartDate: this.policyTabs[0].startDate,
            EndDate: this.policyTabs[0].endDate,
            PermanentTemporary: this.policyTabs[0].permanentTemporary || '',
            DocURL: this.policyTabs[0].docURL || '',
            PolicyType: this.policyTabs[0].type,
            PolicyCategory: this.policyTabs[0].category,
            PolicySubCategory: this.policyTabs[0].subCategory,
            Entities: this.policyTabs[0].entities,
            Reviewer: this.policyTabs[0].reviewer
          };

          // Handle existing subpolicies
          const subpolicies = [];
          const new_subpolicies = [];

          this.policyTabs[0].subPolicies.forEach(sp => {
            if (sp.id && !String(sp.id).startsWith('new-')) {
              // Existing subpolicy
              subpolicies.push({
                original_subpolicy_id: parseInt(sp.id),
                SubPolicyName: sp.name,
                Description: sp.description,
                Identifier: sp.identifier,
                CreatedByName: sp.createdByName,
                PermanentTemporary: sp.permanentTemporary || '',
                Control: sp.control,
                exclude: sp.exclude || false
              });
            } else if (!sp.exclude) {
              // New subpolicy (only include if not excluded)
              new_subpolicies.push({
                SubPolicyName: sp.name,
                Description: sp.description,
                Identifier: sp.identifier,
                CreatedByName: sp.createdByName,
                PermanentTemporary: sp.permanentTemporary || '',
                Control: sp.control
              });
            }
          });

          versionData.subpolicies = subpolicies;
          versionData.new_subpolicies = new_subpolicies;

          console.log('Submitting version data:', versionData);

          // Make API call to create policy version
          const response = await axios.post(
            `${API_BASE_URL}/policies/${this.selectedPolicy}/create-version/`,
            versionData
          );

          console.log('Policy version created:', response.data);
          
          // Show success message with popup
          PopupService.success('Policy version created successfully!', 'Success');
          
          // Reset form and stay on the same page
          setTimeout(() => {
            this.resetForm();
            window.location.href = '/create-policy/versioning';
          }, 1500);

        } catch (error) {
          console.error('Error creating policy version:', error);
          const errorMessage = error.response?.data?.error || 'Failed to create policy version';
          PopupService.error(errorMessage, 'Error Creating Policy Version');
        } finally {
          this.loading = false;
        }
      },
      async confirmVersionType() {
        this.showVersionModal = false;
        if (this.selectedTab === 'framework') {
          await this.submitFrameworkVersion();
        } else if (this.selectedTab === 'policy') {
          await this.submitPolicyVersion();
        }
      },
      async fetchUsers() {
        try {
          const response = await axios.get(`${API_BASE_URL}/users/`)
          console.log('Raw users response:', response.data)
          this.users = response.data.map(user => ({
            id: user.UserId,
            name: user.UserName
          }))
          console.log('Mapped users:', this.users)
        } catch (error) {
          console.error('Error fetching users:', error)
          this.error = 'Failed to fetch users'
          PopupService.error('Failed to fetch users', 'Error')
        }
      },
      async fetchPolicyDetails(policyId) {
        if (!policyId) return;
        
        try {
          this.loading = true;
          const [policyResponse, subpoliciesResponse] = await Promise.all([
            axios.get(`${API_BASE_URL}/policies/${policyId}/`),
            axios.get(`${API_BASE_URL}/policies/${policyId}/get-subpolicies/`)
          ]);

          console.log('Raw policy details:', policyResponse.data);
          console.log('Raw subpolicies:', subpoliciesResponse.data);

          const policy = policyResponse.data;
          
          // Create a single policy tab with the fetched details
          this.policyTabs = [{
            id: policy.PolicyId,
            name: policy.PolicyName,
            description: policy.PolicyDescription,
            status: policy.Status,
            department: policy.Department,
            scope: policy.Scope,
            objective: policy.Objective,
            identifier: policy.Identifier,
            coverageRate: policy.CoverageRate,
            applicability: policy.Applicability,
            type: policy.PolicyType,
            category: policy.PolicyCategory,
            subCategory: policy.PolicySubCategory,
            entities: policy.Entities,
            startDate: policy.StartDate,
            endDate: policy.EndDate,
            file: null,
            createdByName: policy.CreatedByName,
            reviewer: policy.Reviewer,
            activeSubPolicyTab: 0,
            subPolicies: subpoliciesResponse.data.map(sp => ({
              id: sp.SubPolicyId,
              name: sp.SubPolicyName,
              identifier: sp.Identifier,
              control: sp.Control,
              description: sp.Description,
              status: sp.Status
            }))
          }];

          this.activePolicyTab = 0;
          
        } catch (error) {
          console.error('Error fetching policy details:', error);
          this.error = 'Failed to fetch policy details';
          PopupService.error('Failed to fetch policy details', 'Error');
          this.policyTabs = [];
        } finally {
          this.loading = false;
        }
      },
      excludePolicyTab(idx) {
        // Instead of removing the policy, mark it as excluded
        if (this.policyTabs[idx]) {
          this.policyTabs[idx].exclude = !this.policyTabs[idx].exclude;
          console.log(`Policy ${idx} exclude status:`, this.policyTabs[idx].exclude);
          
          // If excluding, also exclude all subpolicies
          if (this.policyTabs[idx].exclude) {
            this.policyTabs[idx].subPolicies.forEach(subPolicy => {
              subPolicy.exclude = true;
            });
          }
        }
      },
      excludeSubPolicyTab(policyIdx, subIdx) {
        // Toggle exclude status instead of removing
        if (this.policyTabs[policyIdx] && this.policyTabs[policyIdx].subPolicies[subIdx]) {
          this.policyTabs[policyIdx].subPolicies[subIdx].exclude = !this.policyTabs[policyIdx].subPolicies[subIdx].exclude;
        }
      }
      }
    }
    </script>

<style scoped>
.TT-exclude-policy-btn,
.TT-exclude-subpolicy-btn {
  padding: 8px 16px;
  margin-bottom: 16px;
  border: 1px solid #dc3545;
  background-color: white;
  color: #dc3545;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.TT-exclude-policy-btn:hover,
.TT-exclude-subpolicy-btn:hover {
  background-color: #dc3545;
  color: white;
}

.TT-exclude-policy-btn.excluded,
.TT-exclude-subpolicy-btn.excluded {
  border-color: #28a745;
  color: #28a745;
}

.TT-exclude-policy-btn.excluded:hover,
.TT-exclude-subpolicy-btn.excluded:hover {
  background-color: #28a745;
  color: white;
}

.TT-policy-tab.excluded,
.TT-subpolicy-tab.excluded {
  opacity: 0.6;
  background-color: #f8d7da;
  border-color: #dc3545;
  text-decoration: line-through;
}

.TT-policy-form-container,
.TT-subpolicy-form-container {
  position: relative;
  transition: opacity 0.3s ease, max-height 0.3s ease;
}

.TT-policy-form-container form,
.TT-subpolicy-form-container form {
  transition: opacity 0.3s ease, max-height 0.3s ease;
}

.TT-excluded-message {
  text-align: center;
  padding: 20px;
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  margin: 10px 0;
}

.version-modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.version-modal {
  background: #fff; padding: 2rem 2.5rem; border-radius: 12px; min-width: 350px; box-shadow: 0 2px 16px rgba(0,0,0,0.15);
}
.version-type-options {
  display: flex; gap: 2rem; margin: 1.5rem 0;
}
.version-type-option {
  display: flex; flex-direction: column; align-items: center; cursor: pointer; position: relative;
}
.version-type-option input[type="radio"] {
  display: none;
}
.radio-custom {
  width: 28px; height: 28px; border: 2px solid #3b6cf6; border-radius: 50%; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: center;
  background: #fff;
}
.radio-custom.checked {
  background: #3b6cf6;
  box-shadow: 0 0 0 2px #3b6cf6;
}
.version-type-title {
  font-weight: bold; font-size: 1.2rem; margin-bottom: 0.3rem;
}
.version-type-desc {
  color: #666; text-align: center; font-size: 1rem;
}
.version-type-example {
  color: #aaa; font-size: 0.95rem;
}
.version-modal-actions {
  display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem;
}
.version-modal-actions button {
  padding: 0.5rem 1.2rem; 
  border: none; 
  border-radius: 4px; 
  font-weight: bold; 
  cursor: pointer;
  min-width: 80px;
  transition: all 0.2s ease;
}
.version-modal-actions .btn-primary {
  background: #3b6cf6; 
  color: #fff;
}
.version-modal-actions .btn-primary:hover {
  background: #2951c3;
}
.version-modal-actions .btn-secondary {
  background: #e0e0e0;
  color: #333;
}
.version-modal-actions .btn-secondary:hover {
  background: #d0d0d0;
}
.version-modal-actions button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Entity Dropdown Styles */
.entities-group {
  width: 100%;
}

.entities-multi-select {
  position: relative;
  width: 100%;
}

.entities-dropdown {
  width: 100%;
}

.selected-entities {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  min-height: 40px;
}

.selected-entities.active {
  border-color: #3b6cf6;
}

.selected-entities.error {
  border-color: #dc3545;
}

.entity-content {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.entity-tag {
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 4px;
  margin-right: 4px;
  font-size: 0.9em;
}

.all-tag {
  background: #3b6cf6;
  color: #fff;
}

.placeholder {
  color: #6c757d;
}

.dropdown-arrow {
  margin-left: 8px;
  transition: transform 0.2s;
}

.active .dropdown-arrow {
  transform: rotate(180deg);
}

.entities-options {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-top: 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.entity-option {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.2s;
}

.entity-option:hover {
  background: #f8f9fa;
}

.entity-option input[type="checkbox"] {
  margin-right: 8px;
}

.entity-label {
  flex: 1;
}

.all-option {
  border-bottom: 1px solid #dee2e6;
  font-weight: bold;
}

.entities-loading,
.entities-error {
  padding: 12px;
  text-align: center;
  color: #6c757d;
}

.entities-error {
  color: #dc3545;
}
</style>
