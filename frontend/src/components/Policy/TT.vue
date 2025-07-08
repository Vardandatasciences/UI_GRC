<template>
  <div class="TT-page-wrapper">
    <!-- Add PopupModal component -->
    <PopupModal />
    
    <div class="tt-page-header">
      <h2>Tailoring &amp; Templating</h2>
      <p class="tt-page-description">Only Internal Frameworks can be tailored</p>
    </div>
    <div class="TT-toggle-group">
      <button :class="['TT-toggle', { 'TT-active': selectedTab === 'framework' } ]" @click="selectTab('framework')">Framework</button>
      <button :class="['TT-toggle', { 'TT-active': selectedTab === 'policy' } ]" @click="selectTab('policy')">Policy</button>
      </div>
    <div v-if="selectedTab === 'framework'" class="TT-top-dropdowns">
      <CustomDropdown
        v-model="selectedFramework"
        :config="{
          label: 'Framework',
          values: frameworks.map(fw => ({ 
            value: fw.id, 
            label: `${fw.name} (${fw.category || 'No Category'}) - ${fw.status || 'No Status'}`
          })),
          defaultLabel: 'Select Framework'
        }"
        :showSearchBar="true"
        style="min-width: 300px; max-width: 360px; width: 340px;"
      />
      <div v-if="error" class="TT-error">{{ error }}</div>
      <div v-if="loading" class="TT-loading">Loading...</div>
      </div>
    <div v-else class="TT-top-dropdowns">
      <CustomDropdown
        v-model="selectedFramework"
        :config="{
          label: 'Framework',
          values: frameworks.map(fw => ({ 
            value: fw.id, 
            label: `${fw.name} (${fw.category || 'No Category'}) - ${fw.status || 'No Status'}`
          })),
          defaultLabel: 'Select Framework'
        }"
        :showSearchBar="true"
        style="min-width: 300px; max-width: 360px; width: 360px;"
      />
      <CustomDropdown
        v-model="selectedPolicy"
        :config="{
          label: 'Policy',
          values: policies.map(pol => ({ 
            value: pol.id, 
            label: `${pol.name} (${pol.status || 'No Status'})`
          })),
          defaultLabel: 'Select Policy'
        }"
        :showSearchBar="true"
        style="min-width: 300px; max-width: 360px; width: 360px;"
      />
      <div v-if="error" class="TT-error">{{ error }}</div>
      <div v-if="loading" class="TT-loading">Loading...</div>
      </div>
    <div v-if="selectedTab === 'framework' && selectedFramework">
      <div class="TT-container">
        <!-- Framework Form -->
        <form @submit.prevent="submitFramework">
          <div class="TT-form-group">
            <label class="TT-label">FRAMEWORK NAME *</label>
            <input class="TT-input" v-model="frameworkForm.name" type="text" required placeholder="Enter Framework name" />
            <small class="TT-desc">Enter a descriptive name for your framework</small>
              </div>
          <div class="TT-form-group">
            <label class="TT-label">DESCRIPTION *</label>
            <textarea class="TT-textarea" v-model="frameworkForm.description" rows="3" required placeholder="Enter framework description"></textarea>
            <small class="TT-desc">Describe the purpose, scope, and objectives of this framework</small>
            </div>
          <div class="TT-row">
            <div class="TT-form-group TT-half">
              <label class="TT-label">IDENTIFIER *</label>
              <input class="TT-input" v-model="frameworkForm.identifier" type="text" required placeholder="Enter Identifier" />
              <small class="TT-desc">Use a unique code like 'FW-001' or 'ISO-27001'</small>
          </div>
            <div class="TT-form-group TT-half">
              <label class="TT-label">CATEGORY *</label>
              <input class="TT-input" v-model="frameworkForm.category" type="text" required placeholder="Enter category" />
              <small class="TT-desc">e.g., Security, Compliance, Risk Management, etc.</small>
              </div>
                </div>
          <div class="TT-row">
            <div class="TT-form-group TT-half">
              <label class="TT-label">INTERNAL/EXTERNAL *</label>
              <select class="TT-input" v-model="frameworkForm.internalExternal" required>
                <option value="" disabled>Select Type</option>
                    <option value="Internal">Internal</option>
                    <option value="External">External</option>
                  </select>
              <small class="TT-desc">Select whether this framework is for internal or external use</small>
                </div>
            <div class="TT-form-group TT-half">
              <label class="TT-label">UPLOAD DOCUMENT</label>
              <input class="TT-input" type="file" @change="handleFileUpload" />
              <small class="TT-desc">Upload a supporting document for this framework (optional)</small>
                  </div>
                </div>
          <div class="TT-row">
            <div class="TT-form-group TT-half">
              <label class="TT-label">EFFECTIVE START DATE *</label>
              <input class="TT-input" v-model="frameworkForm.startDate" type="date" required />
              <small class="TT-desc">Date when the framework implementation begins</small>
              </div>
            <div class="TT-form-group TT-half">
              <label class="TT-label">EFFECTIVE END DATE</label>
              <input class="TT-input" v-model="frameworkForm.endDate" type="date" />
              <small class="TT-desc">Date when the framework expires or requires review</small>
                </div>
                </div>
          <div class="TT-row">
            <div class="TT-form-group TT-half">
              <label class="TT-label">CREATED BY *</label>
              <input class="TT-input" :value="loggedInUsername" type="text" disabled />
              <small class="TT-desc">Automatically set to logged in user</small>
            </div>
            <div class="TT-form-group TT-half">
              <label class="TT-label">REVIEWER *</label>
              <select class="TT-input" v-model="frameworkForm.reviewer" required>
                <option value="">Select Reviewer</option>
                <option v-for="user in users" :key="user.id" :value="user.name">{{ user.name }}</option>
              </select>
              <small class="TT-desc">Select who will review this framework</small>
                </div>
                </div>
        </form>
            </div>
      <!-- Policy Tabbed/Stepper Container (Framework Mode) -->
      <div class="TT-policy-tabs-container">
        <div class="TT-policy-tabs-row">
          <div class="TT-policy-tabs">
            <button v-for="(tab, idx) in policyTabs" :key="tab.id" :class="['TT-policy-tab', { 'TT-policy-tab-active': idx === activePolicyTab }]" @click="activePolicyTab = idx">
              Policy {{ idx + 1 }}
            </button>
            <button class="TT-add-policy-tab" @click="addPolicyTab">+ Add Policy</button>
              </div>
            </div>
        <div v-if="policyTabs.length && policyTabs[activePolicyTab]" class="TT-policy-form-container">
          <button class="TT-exclude-policy-btn" @click="excludePolicyTab(activePolicyTab)">Exclude</button>
          <form @submit.prevent="submitPolicy(activePolicyTab)" :key="policyTabs[activePolicyTab].id">
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">POLICY NAME *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].name" type="text" required placeholder="Enter policy name" />
                <small class="TT-desc">Use a clear, descriptive name</small>
          </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">POLICY IDENTIFIER *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].identifier" type="text" required placeholder="Enter policy identifier" />
                <small class="TT-desc">Use a unique code like 'POL-001'</small>
        </div>
            </div>
            <div class="TT-form-group">
              <label class="TT-label">DESCRIPTION *</label>
              <textarea class="TT-textarea" v-model="policyTabs[activePolicyTab].description" rows="3" required placeholder="Enter policy description"></textarea>
              <small class="TT-desc">Describe the policy's purpose, requirements, and key provisions</small>
          </div>
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">SCOPE *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].scope" type="text" required placeholder="Enter policy scope" />
                <small class="TT-desc">Specify what areas/processes/systems policy applies to</small>
            </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">DEPARTMENT *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].department" type="text" required placeholder="Enter department" />
                <small class="TT-desc">e.g., IT, HR, Finance, Legal, Operations</small>
          </div>
              </div>
            <div class="TT-form-group">
              <label class="TT-label">OBJECTIVE *</label>
              <textarea class="TT-textarea" v-model="policyTabs[activePolicyTab].objective" rows="3" required placeholder="Enter policy objective"></textarea>
              <small class="TT-desc">Explain what this policy is designed to accomplish</small>
                </div>
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">COVERAGE RATE (%) *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].coverageRate" type="number" min="0" max="100" step="0.01" required placeholder="Enter coverage rate" />
                <small class="TT-desc">Range: 0-100, step: 0.01</small>
                </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">APPLICABILITY *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].applicability" type="text" required placeholder="Enter applicability" />
                <small class="TT-desc">Define the target audience, roles, or entities</small>
              </div>
              </div>
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">POLICY TYPE *</label>
                <select 
                  class="TT-input" 
                  v-model="policyTabs[activePolicyTab].type"
                  @change="handlePolicyTypeChange(activePolicyTab, $event.target.value)"
                  :disabled="policyTabs[activePolicyTab].exclude"
                  required
                >
                  <option value="">Select Policy Type</option>
                  <option v-for="type in policyTypes" :key="type" :value="type">{{ type }}</option>
                </select>
                </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">POLICY CATEGORY *</label>
                <select 
                  class="TT-input" 
                  v-model="policyTabs[activePolicyTab].category"
                  @change="handlePolicyCategoryChange(activePolicyTab, $event.target.value)"
                  :disabled="!policyTabs[activePolicyTab].type || policyTabs[activePolicyTab].exclude"
                  required
                >
                  <option value="">Select Policy Category</option>
                  <option v-for="category in getCategoriesForType(policyTabs[activePolicyTab].type)" 
                          :key="category" 
                          :value="category">{{ category }}</option>
                </select>
                </div>
              </div>
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">POLICY SUB CATEGORY *</label>
                <select 
                  class="TT-input" 
                  v-model="policyTabs[activePolicyTab].subCategory"
                  @change="handlePolicySubCategoryChange(activePolicyTab, $event.target.value)"
                  :disabled="!policyTabs[activePolicyTab].category || policyTabs[activePolicyTab].exclude"
                  required
                >
                  <option value="">Select Policy Sub Category</option>
                  <option v-for="subCategory in getSubCategoriesForCategory(policyTabs[activePolicyTab].type, policyTabs[activePolicyTab].category)" 
                          :key="subCategory" 
                          :value="subCategory">{{ subCategory }}</option>
                </select>
              </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">APPLICABLE ENTITIES *</label>
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
                <small v-if="error && error.includes('entities')" class="TT-error-text">
                  {{ error }}
                </small>
                </div>
                </div>
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">START DATE *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].startDate" type="date" required />
                <small class="TT-desc">Date when this policy takes effect</small>
              </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">END DATE</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].endDate" type="date" />
                <small class="TT-desc">Date when this policy expires or requires review/renewal</small>
                  </div>
                </div>
            <div class="TT-form-group">
              <label class="TT-label">UPLOAD DOCUMENT</label>
              <input class="TT-input" type="file" @change="e => handlePolicyFileUpload(e, activePolicyTab)" />
              <small class="TT-desc">Upload supporting documentation (optional)</small>
                  </div>
          </form>
                </div>
              </div>
      <div v-if="policyTabs.length && policyTabs[activePolicyTab]" class="TT-subpolicy-tabs-container">
        <div class="TT-subpolicy-tabs-row">
          <div class="TT-subpolicy-tabs">
            <button v-for="(subTab, subIdx) in policyTabs[activePolicyTab].subPolicies" :key="subTab.id" :class="['TT-subpolicy-tab', { 'TT-subpolicy-tab-active': subIdx === policyTabs[activePolicyTab].activeSubPolicyTab }]" @click="policyTabs[activePolicyTab].activeSubPolicyTab = subIdx">
              Subpolicy {{ subIdx + 1 }}
            </button>
            <button class="TT-add-subpolicy-tab" @click="addSubPolicyTab(activePolicyTab)">+ Add Sub Policy</button>
                  </div>
                </div>
        <div v-if="policyTabs[activePolicyTab].subPolicies && policyTabs[activePolicyTab].subPolicies.length" class="TT-subpolicy-form-container">
          <button class="TT-exclude-subpolicy-btn" @click="excludeSubPolicyTab(activePolicyTab, policyTabs[activePolicyTab].activeSubPolicyTab)">Exclude</button>
          <form>
            <div class="TT-form-group">
              <label class="TT-label">SUB POLICY NAME *</label>
              <input class="TT-input" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].name" type="text" required placeholder="Enter sub policy name" />
              <small class="TT-desc">Use a clear name that describes this sub-policy's specific focus</small>
                        </div>
            <div class="TT-form-group">
              <label class="TT-label">IDENTIFIER *</label>
              <input class="TT-input" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].identifier" type="text" required placeholder="Enter identifier" />
              <small class="TT-desc">Use a unique code like 'SUB-001' or append to parent policy ID</small>
                      </div>
            <div class="TT-form-group">
              <label class="TT-label">CONTROL *</label>
              <textarea class="TT-textarea" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].control" rows="3" required placeholder="Enter control"></textarea>
              <small class="TT-desc">Specify the control mechanisms, procedures, or safeguards to be implemented</small>
                        </div>
            <div class="TT-form-group">
              <label class="TT-label">DESCRIPTION *</label>
              <textarea class="TT-textarea" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].description" rows="3" required placeholder="Enter description"></textarea>
              <small class="TT-desc">Explain the intent, requirements, or significance of this sub-policy</small>
                      </div>
          </form>
                    </div>
                  </div>
                </div>
    <div v-else-if="selectedTab === 'framework' && !selectedFramework">
      <!-- Optionally, you can show a message here: Please select a framework -->
    </div>
    <div v-if="selectedTab === 'framework' && selectedFramework" class="TT-universal-submit-wrapper">
      <button class="TT-universal-submit-btn" @click="submitTailoredFramework">Submit</button>
    </div>
    <div v-if="selectedTab === 'policy' && selectedFramework && selectedPolicy">
      <div class="TT-policy-tabs-container">
        <div class="TT-policy-tabs-row">
          <div class="TT-policy-tabs">
            <button v-for="(tab, idx) in policyTabs" :key="tab.id" :class="['TT-policy-tab', { 'TT-policy-tab-active': idx === activePolicyTab }]" @click="activePolicyTab = idx">
              Policy {{ idx + 1 }}
            </button>
            <!-- Only show + Add Policy in framework mode -->
            <button v-if="selectedTab === 'framework'" class="TT-add-policy-tab" @click="addPolicyTab">+ Add Policy</button>
              </div>
                </div>
        <div v-if="policyTabs.length && policyTabs[activePolicyTab]" class="TT-policy-form-container">
          <!-- Only show Exclude in framework mode -->
          <button v-if="selectedTab === 'framework'" class="TT-exclude-policy-btn" @click="excludePolicyTab(activePolicyTab)">Exclude</button>
          <form @submit.prevent="submitPolicy(activePolicyTab)" :key="policyTabs[activePolicyTab].id">
            <!-- Same policy form as above -->
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">POLICY NAME *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].name" type="text" required placeholder="Enter policy name" />
                <small class="TT-desc">Use a clear, descriptive name</small>
                </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">POLICY IDENTIFIER *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].identifier" type="text" required placeholder="Enter policy identifier" />
                <small class="TT-desc">Use a unique code like 'POL-001'</small>
              </div>
              </div>
            <div class="TT-form-group">
              <label class="TT-label">DESCRIPTION *</label>
              <textarea class="TT-textarea" v-model="policyTabs[activePolicyTab].description" rows="3" required placeholder="Enter policy description"></textarea>
              <small class="TT-desc">Describe the policy's purpose, requirements, and key provisions</small>
            </div>
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">SCOPE *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].scope" type="text" required placeholder="Enter policy scope" />
                <small class="TT-desc">Specify what areas/processes/systems policy applies to</small>
              </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">DEPARTMENT *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].department" type="text" required placeholder="Enter department" />
                <small class="TT-desc">e.g., IT, HR, Finance, Legal, Operations</small>
                </div>
              </div>
            <div class="TT-form-group">
              <label class="TT-label">OBJECTIVE *</label>
              <textarea class="TT-textarea" v-model="policyTabs[activePolicyTab].objective" rows="3" required placeholder="Enter policy objective"></textarea>
              <small class="TT-desc">Explain what this policy is designed to accomplish</small>
                </div>
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">COVERAGE RATE (%) *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].coverageRate" type="number" min="0" max="100" step="0.01" required placeholder="Enter coverage rate" />
                <small class="TT-desc">Range: 0-100, step: 0.01</small>
                </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">APPLICABILITY *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].applicability" type="text" required placeholder="Enter applicability" />
                <small class="TT-desc">Define the target audience, roles, or entities</small>
                </div>
                </div>
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">POLICY TYPE *</label>
                <select 
                  class="TT-input" 
                  v-model="policyTabs[activePolicyTab].type"
                  @change="handlePolicyTypeChange(activePolicyTab, $event.target.value)"
                  :disabled="policyTabs[activePolicyTab].exclude"
                  required
                >
                  <option value="">Select Policy Type</option>
                  <option v-for="type in policyTypes" :key="type" :value="type">{{ type }}</option>
                </select>
                </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">POLICY CATEGORY *</label>
                <select 
                  class="TT-input" 
                  v-model="policyTabs[activePolicyTab].category"
                  @change="handlePolicyCategoryChange(activePolicyTab, $event.target.value)"
                  :disabled="!policyTabs[activePolicyTab].type || policyTabs[activePolicyTab].exclude"
                  required
                >
                  <option value="">Select Policy Category</option>
                  <option v-for="category in getCategoriesForType(policyTabs[activePolicyTab].type)" 
                          :key="category" 
                          :value="category">{{ category }}</option>
                </select>
              </div>
            </div>
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">POLICY SUB CATEGORY *</label>
                <select 
                  class="TT-input" 
                  v-model="policyTabs[activePolicyTab].subCategory"
                  @change="handlePolicySubCategoryChange(activePolicyTab, $event.target.value)"
                  :disabled="!policyTabs[activePolicyTab].category || policyTabs[activePolicyTab].exclude"
                  required
                >
                  <option value="">Select Policy Sub Category</option>
                  <option v-for="subCategory in getSubCategoriesForCategory(policyTabs[activePolicyTab].type, policyTabs[activePolicyTab].category)" 
                          :key="subCategory" 
                          :value="subCategory">{{ subCategory }}</option>
                </select>
          </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">APPLICABLE ENTITIES *</label>
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
          </div>
        </div>
            <div class="TT-row">
              <div class="TT-form-group TT-half">
                <label class="TT-label">START DATE *</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].startDate" type="date" required />
                <small class="TT-desc">Date when this policy takes effect</small>
      </div>
              <div class="TT-form-group TT-half">
                <label class="TT-label">END DATE</label>
                <input class="TT-input" v-model="policyTabs[activePolicyTab].endDate" type="date" />
                <small class="TT-desc">Date when this policy expires or requires review/renewal</small>
        </div>
            </div>
            <div class="TT-form-group">
              <label class="TT-label">UPLOAD DOCUMENT</label>
              <input class="TT-input" type="file" @change="e => handlePolicyFileUpload(e, activePolicyTab)" />
              <small class="TT-desc">Upload supporting documentation (optional)</small>
            </div>
            <!-- Show CreatedByName and Reviewer fields only in policy tab -->
            <template v-if="selectedTab === 'policy'">
              <div class="TT-row">
                <div class="TT-form-group TT-half">
                  <label class="TT-label">CREATED BY *</label>
                  <input class="TT-input" :value="loggedInUsername" type="text" disabled />
                  <small class="TT-desc">Automatically set to logged in user</small>
                </div>
                <div class="TT-form-group TT-half">
                  <label class="TT-label">REVIEWER *</label>
                  <select class="TT-input" v-model="policyTabs[activePolicyTab].reviewer" required>
                    <option value="">Select Reviewer</option>
                    <option v-for="user in users" :key="user.id" :value="user.name">{{ user.name }}</option>
                  </select>
                  <small class="TT-desc">Select who will review this policy</small>
                </div>
              </div>
            </template>
          </form>
              </div>
            </div>
      <div v-if="policyTabs.length && policyTabs[activePolicyTab]" class="TT-subpolicy-tabs-container">
        <div class="TT-subpolicy-tabs-row">
          <div class="TT-subpolicy-tabs">
            <button v-for="(subTab, subIdx) in policyTabs[activePolicyTab].subPolicies" :key="subTab.id" :class="['TT-subpolicy-tab', { 'TT-subpolicy-tab-active': subIdx === policyTabs[activePolicyTab].activeSubPolicyTab }]" @click="policyTabs[activePolicyTab].activeSubPolicyTab = subIdx">
              Subpolicy {{ subIdx + 1 }}
            </button>
            <button class="TT-add-subpolicy-tab" @click="addSubPolicyTab(activePolicyTab)">+ Add Sub Policy</button>
          </div>
        </div>
        <div v-if="policyTabs[activePolicyTab].subPolicies && policyTabs[activePolicyTab].subPolicies.length" class="TT-subpolicy-form-container">
          <button class="TT-exclude-subpolicy-btn" @click="excludeSubPolicyTab(activePolicyTab, policyTabs[activePolicyTab].activeSubPolicyTab)">Exclude</button>
          <form>
            <div class="TT-form-group">
              <label class="TT-label">SUB POLICY NAME *</label>
              <input class="TT-input" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].name" type="text" required placeholder="Enter sub policy name" />
              <small class="TT-desc">Use a clear name that describes this sub-policy's specific focus</small>
      </div>
            <div class="TT-form-group">
              <label class="TT-label">IDENTIFIER *</label>
              <input class="TT-input" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].identifier" type="text" required placeholder="Enter identifier" />
              <small class="TT-desc">Use a unique code like 'SUB-001' or append to parent policy ID</small>
        </div>
            <div class="TT-form-group">
              <label class="TT-label">CONTROL *</label>
              <textarea class="TT-textarea" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].control" rows="3" required placeholder="Enter control"></textarea>
              <small class="TT-desc">Specify the control mechanisms, procedures, or safeguards to be implemented</small>
            </div>
            <div class="TT-form-group">
              <label class="TT-label">DESCRIPTION *</label>
              <textarea class="TT-textarea" v-model="policyTabs[activePolicyTab].subPolicies[policyTabs[activePolicyTab].activeSubPolicyTab].description" rows="3" required placeholder="Enter description"></textarea>
              <small class="TT-desc">Explain the intent, requirements, or significance of this sub-policy</small>
            </div>
          </form>
        </div>
      </div>
      </div>
    <!-- Add submit button for policy tab -->
    <div v-if="selectedTab === 'policy' && selectedFramework && selectedPolicy" class="TT-universal-submit-wrapper">
      <button class="TT-universal-submit-btn" @click="submitTailoredPolicy">Submit</button>
      </div>
    </div>
  </template>
  
  <script>
import './TT.css'
import CustomDropdown from '../CustomDropdown.vue'
import axios from 'axios'
import { PopupService, PopupModal } from '@/modules/popus'

const API_BASE_URL = 'http://localhost:8000/api'

  export default {
  name: 'TT',
  components: {
    CustomDropdown,
    PopupModal
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
      loggedInUsername: localStorage.getItem('username') || '', // Add logged in username
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
      entities: [], // Initialize as empty array
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
    },
    'policyTabs[activePolicyTab].type': {
      immediate: true,
      handler(newVal) {
        console.log('Policy type changed to:', newVal)
        this.updatePolicyCategoriesByType(newVal)
      }
    },
    'policyTabs[activePolicyTab].category': {
      immediate: true,
      handler(newVal) {
        console.log('Policy category changed to:', newVal)
        const policyType = this.policyTabs[this.activePolicyTab]?.type
        this.updateSubCategoriesByCategory(policyType, newVal)
      }
    }
  },
  async created() {
    try {
      await Promise.all([
        this.fetchFrameworks(),
        this.fetchPolicyCategories(),
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
    async fetchFrameworks() {
      try {
        this.loading = true
        const response = await axios.get(`${API_BASE_URL}/frameworks/`)
        console.log('Raw framework response:', response.data)
        
        // Filter frameworks based on selected tab
        const allFrameworks = response.data.map(fw => ({ 
          id: fw.FrameworkId, 
          name: fw.FrameworkName,
          description: fw.FrameworkDescription,
          category: fw.Category,
          internalExternal: fw.InternalExternal,
          startDate: fw.StartDate,
          endDate: fw.EndDate,
          status: fw.Status
        }))

        // Only show Internal frameworks in framework tailoring mode
        this.frameworks = this.selectedTab === 'framework' 
          ? allFrameworks.filter(fw => fw.internalExternal === 'Internal')
          : allFrameworks

        console.log('Mapped frameworks:', this.frameworks)
      } catch (error) {
        console.error('Error fetching frameworks:', error)
        this.error = 'Failed to fetch frameworks'
      } finally {
        this.loading = false
      }
    },
    async fetchPoliciesByFramework(frameworkId) {
      try {
        this.loading = true
        const response = await axios.get(`${API_BASE_URL}/frameworks/${frameworkId}/get-policies/`)
        console.log('Raw policies response:', response.data)
        
        // Filter policies to only show Approved and Active ones
        this.policies = response.data
          .filter(p => p.Status === 'Approved' && p.ActiveInactive === 'Active')
          .map(p => ({ 
            id: p.PolicyId, 
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
            endDate: p.EndDate
          }))
        console.log('Mapped and filtered policies:', this.policies)
      } catch (error) {
        console.error('Error fetching policies:', error)
        this.error = 'Failed to fetch policies'
      } finally {
        this.loading = false
      }
    },
    async fetchPolicyDetails(policyId) {
      try {
        this.loading = true
        const [policyResponse, subpoliciesResponse] = await Promise.all([
          axios.get(`${API_BASE_URL}/policies/${policyId}/`),
          axios.get(`${API_BASE_URL}/policies/${policyId}/get-subpolicies/`)
        ])
        
        console.log('Raw policy details:', policyResponse.data)
        console.log('Raw subpolicies:', subpoliciesResponse.data)
        
        const policy = policyResponse.data
        const mappedSubpolicies = subpoliciesResponse.data.map(sp => ({
          id: sp.SubPolicyId,
          name: sp.SubPolicyName,
          identifier: sp.Identifier,
          control: sp.Control,
          description: sp.Description,
          status: sp.Status
        }))

        const policyTab = {
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
          subPolicies: mappedSubpolicies,
          activeSubPolicyTab: 0
        }

        this.policyTabs = [policyTab]
        this.activePolicyTab = 0
      } catch (error) {
        console.error('Error fetching policy details:', error)
        this.error = 'Failed to fetch policy details'
      } finally {
        this.loading = false
      }
    },
    async submitTailoredFramework() {
      if (!this.validateForm('framework')) {
        return;
      }
      try {
        this.loading = true;
        
        // Format framework data
        const frameworkData = {
          title: this.frameworkForm.name,
          description: this.frameworkForm.description,
          identifier: this.frameworkForm.identifier,
          category: this.frameworkForm.category,
          internalExternal: this.frameworkForm.internalExternal,
          startDate: this.frameworkForm.startDate,
          endDate: this.frameworkForm.endDate,
          createdByName: this.loggedInUsername,
          reviewer: this.frameworkForm.reviewer,
          policies: this.policyTabs.map(policy => {
            // Convert entities to proper format
            let entities = policy.entities;
            if (Array.isArray(entities)) {
              // Convert Proxy array to regular array and ensure numeric values
              entities = Array.from(entities).map(Number);
            }
            // If empty array or invalid, default to empty array
            if (!entities || (Array.isArray(entities) && entities.length === 0)) {
              entities = [];
            }

            return {
              title: policy.name,
              description: policy.description,
              identifier: policy.identifier,
              department: policy.department,
              scope: policy.scope,
              objective: policy.objective,
              coverageRate: policy.coverageRate,
              applicability: policy.applicability,
              PolicyType: policy.type,
              PolicyCategory: policy.category,
              PolicySubCategory: policy.subCategory,
              Entities: entities,
              startDate: policy.startDate,
              endDate: policy.endDate,
              createdByName: this.selectedTab === 'framework' ? this.loggedInUsername : policy.createdByName,
              reviewer: this.selectedTab === 'framework' ? this.frameworkForm.reviewer : policy.reviewer,
              subPolicies: policy.subPolicies.map(sub => ({
                title: sub.name,
                identifier: sub.identifier,
                description: sub.description,
                control: sub.control,
                createdByName: this.selectedTab === 'framework' ? this.loggedInUsername : policy.createdByName
              }))
            };
          })
        };

        console.log('Submitting framework data:', frameworkData);

        // Send as JSON
        const response = await axios.post(
          `${API_BASE_URL}/tailoring/create-framework/`,
          frameworkData,
          {
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        console.log('Framework creation response:', response.data);
        this.$emit('framework-created');
        this.resetForm();
        this.error = null;

        // Show success popup
        PopupService.success(
          'Framework created successfully!',
          'Success'
        );

      } catch (error) {
        console.error('Error submitting framework:', error);
        this.error = error.response?.data?.error || 'Failed to submit framework';
        
        // Show error popup
        PopupService.error(
          this.error,
          'Error Creating Framework'
        );
      } finally {
        this.loading = false;
      }
    },
    async submitPolicy(idx) {
      if (!this.validateForm('policy')) {
        return;
      }
      try {
        this.loading = true
        const formData = new FormData()
        const policy = this.policyTabs[idx]

        // Append policy data
        Object.keys(policy).forEach(key => {
          if (key === 'file' && policy[key]) {
            formData.append('file', policy[key])
          } else if (key !== 'subPolicies' && key !== 'activeSubPolicyTab') {
            formData.append(key, policy[key])
          }
        })

        // Append subpolicies data
        policy.subPolicies.forEach((subpolicy, subIndex) => {
          Object.keys(subpolicy).forEach(key => {
            formData.append(`subPolicies[${subIndex}][${key}]`, subpolicy[key])
          })
        })

        await axios.post(`${API_BASE_URL}/tailoring/create-policy/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        this.$emit('policy-created')
        this.resetForm()
      } catch (error) {
        console.error('Error submitting policy:', error)
        this.error = 'Failed to submit policy'
      } finally {
        this.loading = false
      }
    },
    async handleFrameworkSelection(newVal) {
      if (!newVal) {
        this.resetForm()
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
          reviewer: framework.Reviewer
        }

        // Filter policies to only show Approved and Active ones
        this.policies = policiesResponse.data
          .filter(p => p.Status === 'Approved' && p.ActiveInactive === 'Active')
          .map(p => ({ 
            id: p.PolicyId, 
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
            endDate: p.EndDate
          }))

        if (this.selectedTab === 'framework') {
          const policiesWithDetails = await Promise.all(
            policiesResponse.data
              .filter(p => p.Status === 'Approved' && p.ActiveInactive === 'Active')
              .map(async p => {
                const subpoliciesResponse = await axios.get(`${API_BASE_URL}/policies/${p.PolicyId}/get-subpolicies/`)
                return {
                  id: p.PolicyId,
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
                  createdByName: p.CreatedByName,
                  reviewer: p.Reviewer,
                  activeSubPolicyTab: 0,
                  subPolicies: subpoliciesResponse.data.map(sp => ({
                    id: sp.SubPolicyId,
                    name: sp.SubPolicyName,
                    identifier: sp.Identifier,
                    control: sp.Control,
                    description: sp.Description,
                    status: sp.Status
                  }))
                }
              })
          )
          this.policyTabs = policiesWithDetails
          this.activePolicyTab = 0
        } else {
          this.policyTabs = []
          this.activePolicyTab = 0
        }

        this.selectedPolicy = ''
      } catch (error) {
        console.error('Error handling framework selection:', error)
        this.error = 'Failed to load framework details'
      } finally {
        this.loading = false
      }
    },
    handlePolicyFileUpload(e, idx) {
      this.policyTabs[idx].file = e.target.files[0]
    },
    addPolicyTab() {
      const reviewer = this.selectedTab === 'framework' ? this.frameworkForm.reviewer : '';
      
      this.policyTabs.push({
        id: Date.now(),
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
        showEntitiesDropdown: false,
        startDate: '',
        endDate: '',
        file: null,
        createdByName: this.loggedInUsername,
        reviewer: reviewer,
        subPolicies: [
          {
            id: Date.now(),
            name: '',
            identifier: '',
            control: '',
            description: '',
            createdByName: this.loggedInUsername // Use logged in username
          }
        ],
        activeSubPolicyTab: 0
      })
      this.activePolicyTab = this.policyTabs.length - 1
    },
    excludePolicyTab(idx) {
      if (this.policyTabs.length > 1) {
        this.policyTabs.splice(idx, 1)
        if (this.activePolicyTab >= this.policyTabs.length) {
          this.activePolicyTab = this.policyTabs.length - 1
        }
      }
    },
    addSubPolicyTab(policyIdx) {
      const currentPolicy = this.policyTabs[policyIdx];
      this.policyTabs[policyIdx].subPolicies.push({
        id: Date.now(),
        name: '',
        identifier: '',
        control: '',
        description: '',
        createdByName: currentPolicy.createdByName // Inherit createdByName from parent policy
      })
      this.policyTabs[policyIdx].activeSubPolicyTab = this.policyTabs[policyIdx].subPolicies.length - 1
    },
    excludeSubPolicyTab(policyIdx, subIdx) {
      const subPolicies = this.policyTabs[policyIdx].subPolicies
      if (subPolicies.length > 1) {
        subPolicies.splice(subIdx, 1)
        if (this.policyTabs[policyIdx].activeSubPolicyTab >= subPolicies.length) {
          this.policyTabs[policyIdx].activeSubPolicyTab = subPolicies.length - 1
        }
      }
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
        endDate: ''
      }
          this.policyTabs = []
          this.activePolicyTab = 0
      this.selectedFramework = ''
        this.selectedPolicy = ''
    },
    async fetchPolicyCategories() {
      try {
        this.loading = true;
        const response = await axios.get(`${API_BASE_URL}/policy-categories/`);
        console.log('Raw policy categories response:', response.data);
        
        // Store complete policy data
        this.policyData = response.data;
        
        // Extract unique policy types
        this.policyTypes = [...new Set(response.data.map(item => item.PolicyType))];
        
        console.log('Available policy types:', this.policyTypes);
      } catch (error) {
        console.error('Error fetching policy categories:', error);
        this.error = 'Failed to fetch policy categories';
      } finally {
        this.loading = false;
      }
    },
    getCategoriesForType(policyType) {
      if (!policyType || !this.policyData) return [];
      const categories = this.policyData
        .filter(item => item.PolicyType === policyType)
        .map(item => item.PolicyCategory);
      return [...new Set(categories)];
    },

    getSubCategoriesForCategory(policyType, policyCategory) {
      if (!policyType || !policyCategory || !this.policyData) return [];
      const subCategories = this.policyData
        .filter(item => item.PolicyType === policyType && item.PolicyCategory === policyCategory)
        .map(item => item.PolicySubCategory);
      return [...new Set(subCategories)];
    },

    handlePolicyTypeChange(idx, value) {
      console.log('Policy type changed:', value);
      const policy = this.policyTabs[idx];
      policy.PolicyType = value;
      policy.PolicyCategory = ''; // Clear category when type changes
      policy.PolicySubCategory = ''; // Clear subcategory when type changes
      
      // Update available categories for this type
      this.policyCategories = this.getCategoriesForType(value);
      console.log('Updated categories:', this.policyCategories);
    },

    handlePolicyCategoryChange(idx, value) {
      console.log('Policy category changed:', value);
      const policy = this.policyTabs[idx];
      policy.PolicyCategory = value;
      policy.PolicySubCategory = ''; // Clear subcategory when category changes
      
      // Update available subcategories for this type and category
      this.policySubCategories = this.getSubCategoriesForCategory(policy.PolicyType, value);
      console.log('Updated subcategories:', this.policySubCategories);
    },

    handlePolicySubCategoryChange(idx, value) {
      console.log('Policy subcategory changed:', value);
      this.policyTabs[idx].PolicySubCategory = value;
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
    async fetchEntities() {
      try {
        this.loading = true;
        const response = await axios.get(`${API_BASE_URL}/entities/`);
        console.log('Raw entities response:', response.data);
        
        if (response.data.entities) {
          // Map entities directly from the backend response
          this.entities = response.data.entities.map(entity => ({
            id: entity.id,
            label: entity.label
          }));
          console.log('Mapped entities:', this.entities);
      } else {
          throw new Error('Invalid response format');
        }
      } catch (error) {
        console.error('Error fetching entities:', error);
        this.error = 'Failed to fetch entities';
      } finally {
        this.loading = false;
      }
    },

    handleEntitySelection(idx, entityId, isChecked) {
      if (idx < 0 || !this.policyTabs[idx]) return;
      
      console.log('handleEntitySelection:', { idx, entityId, isChecked });
      
      // Initialize entities if undefined
      if (!this.policyTabs[idx].entities) {
        this.policyTabs[idx].entities = [];
      }
      
      if (entityId === 'all') {
        // When "All Locations" is selected, set entities to "all" string
        this.policyTabs[idx].entities = isChecked ? "all" : [];
      } else {
        // Ensure we're working with an array
        let currentEntities = this.policyTabs[idx].entities === "all" ? [] 
          : Array.isArray(this.policyTabs[idx].entities) ? this.policyTabs[idx].entities 
          : [];
        
        const numericId = Number(entityId);
        
        if (isChecked) {
          if (!currentEntities.includes(numericId)) {
            currentEntities.push(numericId);
          }
        } else {
          currentEntities = currentEntities.filter(id => id !== numericId);
        }
        
        // Store as array of numeric IDs
        this.policyTabs[idx].entities = currentEntities;
      }
      
      console.log('Updated entities:', this.policyTabs[idx].entities);
    },

    selectEntity(idx, entityId) {
      if (idx < 0 || !this.policyTabs[idx]) return;
      
      const isSelected = entityId === 'all' 
        ? this.isAllEntitiesSelected(idx)
        : this.isEntitySelected(idx, entityId);
      
      this.handleEntitySelection(idx, entityId, !isSelected);
    },

    isEntitySelected(idx, entityId) {
      const policy = this.policyTabs[idx];
      if (!policy || !policy.entities) return false;
      
      if (policy.entities === "all") {
        return entityId === 'all';
      }
      
      return Array.isArray(policy.entities) && policy.entities.includes(Number(entityId));
    },

    isAllEntitiesSelected(idx) {
      const policy = this.policyTabs[idx];
      return policy && policy.entities === "all";
    },

    getSelectedEntitiesCount(idx) {
      const policy = this.policyTabs[idx];
      if (!policy || !policy.entities) return 0;
      
      if (policy.entities === "all") {
        return this.entities.length - 1; // Subtract 1 for the "All" option
      }
      
      return Array.isArray(policy.entities) ? policy.entities.length : 0;
    },

    toggleEntitiesDropdown(idx) {
      if (idx < 0 || !this.policyTabs[idx]) return;
      
      // Close all other dropdowns first
      this.policyTabs.forEach((policy, index) => {
        if (index !== idx) {
          policy.showEntitiesDropdown = false;
        }
      });
      
      // Toggle current dropdown
      const currentPolicy = this.policyTabs[idx];
      currentPolicy.showEntitiesDropdown = !currentPolicy.showEntitiesDropdown;
      
      // If opening the dropdown and no entities loaded yet, fetch them
      if (currentPolicy.showEntitiesDropdown && this.entities.length <= 1) {
        this.fetchEntities();
      }
    },

    closeAllEntityDropdowns() {
      this.policyTabs.forEach(policy => {
        policy.showEntitiesDropdown = false;
      });
    },

    handleClickOutside(event) {
      const dropdowns = document.querySelectorAll('.entities-multi-select');
      dropdowns.forEach(dropdown => {
        if (!dropdown.contains(event.target)) {
          this.closeAllEntityDropdowns();
        }
      });
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
      }
    },
    // Add new method to handle CreatedByName changes
    handleCreatedByNameChange() {
      // Update CreatedByName for all subpolicies when policy's CreatedByName changes
      if (this.selectedTab === 'policy' && this.policyTabs[this.activePolicyTab]) {
        const newCreatedByName = this.policyTabs[this.activePolicyTab].createdByName;
        this.policyTabs[this.activePolicyTab].subPolicies.forEach(subPolicy => {
          subPolicy.createdByName = newCreatedByName;
        });
      }
    },
    async submitTailoredPolicy() {
      if (!this.validateForm('policy')) {
        return;
      }
      try {
        this.loading = true;
        
        // Validate coverage rate
        const coverageRate = parseFloat(this.policyTabs[this.activePolicyTab].coverageRate);
        if (isNaN(coverageRate) || coverageRate < 0 || coverageRate > 100) {
          throw new Error('Coverage Rate must be a number between 0 and 100');
        }
        
        // Format policy data
        const policyData = {
          TargetFrameworkId: this.selectedFramework,
          PolicyName: this.policyTabs[this.activePolicyTab].name,
          PolicyDescription: this.policyTabs[this.activePolicyTab].description,
          Department: this.policyTabs[this.activePolicyTab].department,
          Scope: this.policyTabs[this.activePolicyTab].scope,
          Objective: this.policyTabs[this.activePolicyTab].objective,
          CoverageRate: coverageRate,
          Applicability: this.policyTabs[this.activePolicyTab].applicability,
          PolicyType: this.policyTabs[this.activePolicyTab].type,
          PolicyCategory: this.policyTabs[this.activePolicyTab].category,
          PolicySubCategory: this.policyTabs[this.activePolicyTab].subCategory,
          Entities: this.policyTabs[this.activePolicyTab].entities,
          StartDate: this.policyTabs[this.activePolicyTab].startDate,
          EndDate: this.policyTabs[this.activePolicyTab].endDate,
          CreatedByName: this.loggedInUsername,
          Reviewer: this.policyTabs[this.activePolicyTab].reviewer,
          Identifier: this.policyTabs[this.activePolicyTab].identifier,
          subpolicies: this.policyTabs[this.activePolicyTab].subPolicies.map(sub => ({
            SubPolicyName: sub.name,
            Identifier: sub.identifier,
            Description: sub.description,
            Control: sub.control,
            exclude: false
          }))
        };

        console.log('Submitting policy data:', policyData);

        const response = await axios.post(
          `${API_BASE_URL}/tailoring/create-policy/`,
          policyData,
          {
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        console.log('Policy creation response:', response.data);
        this.$emit('policy-created');
        this.resetForm();
        this.error = null;

        // Show success popup
        PopupService.success(
          'Policy created successfully!',
          'Success'
        );

      } catch (error) {
        console.error('Error submitting policy:', error);
        this.error = error.response?.data?.error || 'Failed to submit policy';
        
        // Show error popup
        PopupService.error(
          this.error,
          'Error Creating Policy'
        );
      } finally {
        this.loading = false;
      }
    },
    // Add validation method
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
        if (!this.loggedInUsername) {
          PopupService.warning('You must be logged in to create a framework', 'Validation Error');
          return false;
        }
        if (!this.frameworkForm.reviewer) {
          PopupService.warning('Reviewer is required', 'Validation Error');
          return false;
        }
        return true;
      }

      if (type === 'policy') {
        const policy = this.policyTabs[this.activePolicyTab];
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
        if (!policy.department) {
          PopupService.warning('Department is required', 'Validation Error');
          return false;
        }
        if (!policy.scope) {
          PopupService.warning('Scope is required', 'Validation Error');
          return false;
        }
        if (!policy.objective) {
          PopupService.warning('Objective is required', 'Validation Error');
          return false;
        }
        if (!policy.coverageRate) {
          PopupService.warning('Coverage Rate is required', 'Validation Error');
          return false;
        }
        if (!policy.applicability) {
          PopupService.warning('Applicability is required', 'Validation Error');
          return false;
        }
        if (!policy.type) {
          PopupService.warning('Policy Type is required', 'Validation Error');
          return false;
        }
        if (!policy.category) {
          PopupService.warning('Policy Category is required', 'Validation Error');
          return false;
        }
        if (!policy.subCategory) {
          PopupService.warning('Policy Sub Category is required', 'Validation Error');
          return false;
        }
        if (!policy.startDate) {
          PopupService.warning('Start Date is required', 'Validation Error');
          return false;
        }
        if (!this.loggedInUsername) {
          PopupService.warning('You must be logged in to create a policy', 'Validation Error');
          return false;
        }
        if (!policy.reviewer) {
          PopupService.warning('Reviewer is required', 'Validation Error');
          return false;
        }
        if (!policy.entities || (Array.isArray(policy.entities) && policy.entities.length === 0)) {
          PopupService.warning('At least one entity must be selected', 'Validation Error');
          return false;
        }
        return true;
      }
      return false;
    },
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  }
  </script>
<style scoped>
.tt-page-header {
  margin-bottom: 32px;
  padding-top: 24px;
  padding-bottom: 8px;
}

.tt-page-header h1 {
  font-size: 48px;
  font-weight: 700;
  color: #23272f;
  margin: 0 0 8px 0;
  letter-spacing: -1px;
  font-family: inherit;
}

.tt-header-underline {
  width: 120px;
  height: 5px;
  border-radius: 3px;
  background: linear-gradient(90deg, #3b82f6 0%, #7b6fdd 100%);
  margin-top: 0;
  margin-left: 4px;
}

.TT-error {
  color: #dc3545;
  margin-top: 10px;
  font-size: 14px;
}

.TT-loading {
  color: #666;
  margin-top: 10px;
  font-size: 14px;
}

.entities-group {
  width: 100%;
}

.entities-multi-select {
  position: relative;
  width: 100%;
  z-index: 1000;
}

.entities-dropdown {
  position: relative;
  width: 100%;
}

.selected-entities {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  background: white;
  min-height: 40px;
  transition: all 0.2s ease;
}

.selected-entities:hover {
  border-color: #2196f3;
}

.selected-entities.active {
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.entity-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.entity-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.entity-tag.all-tag {
  background: #e8f5e9;
  color: #2e7d32;
}

.placeholder {
  color: #999;
}

.entity-count {
  color: #666;
  font-size: 0.9em;
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
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 4px;
  max-height: 250px;
  overflow-y: auto;
  z-index: 1001;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.entity-option {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.entity-option:hover {
  background: #f5f5f5;
}

.entity-option input[type="checkbox"] {
  margin-right: 8px;
}

.entity-label {
  flex: 1;
}

.TT-error-text {
  color: #dc3545;
  font-size: 0.8em;
  margin-top: 4px;
  display: block;
}

.tt-page-description {
  color: #475569;
  font-size: 0.95rem;
  margin: 8px 0 0 0;
  font-style: italic;
}
</style>