<template>
  <div class="user-profile-container">
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        <i :class="tab.icon" class="tab-icon"></i>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </div>
    <div class="tab-content">
      <div v-if="activeTab === 'account'" class="account-section">
        <!-- Error/Success Messages -->
        <div v-if="error" class="message error-message">
          <i class="fas fa-exclamation-circle"></i> {{ error }}
        </div>
        <div v-if="success" class="message success-message">
          <i class="fas fa-check-circle"></i> {{ success }}
        </div>

        <div class="account-container">
          <!-- Personal Information Section -->
          <div class="account-section-left">
            <form class="profile-form" @submit.prevent="savePersonalInfo">
              <h2 class="section-title"><i class="fas fa-user"></i> Personal Information</h2>
              <p class="section-helper">Update your personal details and contact information.</p>
              
              <div class="form-group">
                <label>First Name:</label>
                <input type="text" v-model="form.firstName" :disabled="loading" />
              </div>
              <div class="form-group">
                <label>Last Name:</label>
                <input type="text" v-model="form.lastName" :disabled="loading" />
              </div>
              <div class="form-group">
                <label>Email:</label>
                <input type="email" v-model="form.email" :disabled="loading" />
              </div>
              <div class="form-group">
                <label>Phone Number:</label>
                <input type="text" v-model="form.phone" :disabled="loading" />
              </div>
              <div class="form-row center">
                <button class="submit-btn" type="submit" :disabled="loading">
                  <i v-if="loading" class="fas fa-spinner fa-spin"></i>
                  <i v-else class="fas fa-save"></i> 
                  {{ loading ? 'Saving...' : 'Save Personal Info' }}
                </button>
              </div>
            </form>
          </div>

          <!-- Business Information Section -->
          <div class="account-section-right">
            <form class="profile-form" @submit.prevent="saveBusinessInfo">
              <h2 class="section-title"><i class="fas fa-building"></i> Business Information</h2>
              <p class="section-helper">View your organizational details and business unit information.</p>
              
              <div class="form-group">
                <label>Department:</label>
                <input type="text" v-model="businessInfo.departmentName" disabled />
              </div>
              <div class="form-group">
                <label>Business Unit:</label>
                <input type="text" v-model="businessInfo.businessUnitName" disabled />
              </div>
              <div class="form-group">
                <label>Entity:</label>
                <input type="text" v-model="businessInfo.entityName" disabled />
              </div>
              <div class="form-group">
                <label>Location:</label>
                <input type="text" v-model="businessInfo.location" disabled />
              </div>
              <div class="form-group">
                <label>Department Head:</label>
                <input type="text" v-model="businessInfo.departmentHead" disabled />
              </div>
            </form>
          </div>
        </div>
      </div>
      <div v-else-if="activeTab === 'role'">
        <form class="profile-form">
          <h2 class="section-title"><i class="fas fa-exchange-alt"></i> Role Management</h2>
          <p class="section-helper">View or request changes to your user role. Role changes may require approval from an administrator.</p>
          <div class="form-row">
            <label>User Name:</label>
            <input type="text" v-model="form.username" />
            <label>Role:</label>
            <input type="text" v-model="form.role" />
          </div>
          <div class="form-row center">
            <button class="submit-btn" type="button">
              <i class="fas fa-check"></i> Request Role Change
            </button>
          </div>
        </form>
      </div>
      <div v-else-if="activeTab === 'password'">
        <form class="profile-form password-form" @submit.prevent="updatePassword">
          <h2 class="section-title"><i class="fas fa-key"></i> Change Your Password</h2>
          <p class="section-helper">For your security, please enter your email and a new password. You will need to verify with an OTP sent to your registered email or phone.</p>
          
          <!-- Error/Success Messages -->
          <div v-if="error" class="message error-message">
            <i class="fas fa-exclamation-circle"></i> {{ error }}
          </div>
          <div v-if="success" class="message success-message">
            <i class="fas fa-check-circle"></i> {{ success }}
          </div>
          
          <div class="form-row password-row">
            <label>Email</label>
            <input type="email" v-model="form.email" placeholder="Enter your email address" :disabled="loading" />
            <button class="verify-btn" type="button" :disabled="loading">
              <i class="fas fa-shield-alt"></i> Verify
            </button>
          </div>
          <div class="form-row password-row">
            <label>Enter OTP</label>
            <input type="text" v-model="form.otp" placeholder="Enter OTP" :disabled="loading" />
          </div>
          <div class="form-row password-row">
            <label>New Password</label>
            <input type="password" v-model="form.newPassword" placeholder="Enter new password" :disabled="loading" />
          </div>
          <div class="form-row password-row">
            <label>Confirm Password</label>
            <input type="password" v-model="form.confirmPassword" placeholder="Re-enter new password" :disabled="loading" />
          </div>
          <div class="form-row password-submit-row">
            <button class="submit-btn" type="submit" style="width: 100%; max-width: 320px;" :disabled="loading">
              <i v-if="loading" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-paper-plane"></i> 
              {{ loading ? 'Updating...' : 'Update Password' }}
            </button>
          </div>
        </form>
      </div>
      <div v-else-if="activeTab === 'notification'">
        <div class="notification-settings">
          <h2 class="section-title"><i class="fas fa-bell"></i> Notification Preferences</h2>
          <p class="section-helper">Manage how you receive notifications and update your contact details for alerts.</p>

          <!-- Email Notification Dropdown -->
          <div class="notif-dropdown-section">
            <div class="notification-row notif-dropdown-toggle" @click="notifDropdownOpen = notifDropdownOpen === 'email' ? null : 'email'">
              <span style="display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-envelope"></i> Email Notification updates
              </span>
              <label class="switch" @click.stop>
                <input type="checkbox" v-model="form.emailNotif" />
                <span class="slider"></span>
              </label>
              <span class="notif-dropdown-arrow">
                <i :class="notifDropdownOpen === 'email' ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </span>
            </div>
            <transition name="fade">
              <div v-if="notifDropdownOpen === 'email'" class="notif-dropdown-content">
                <form class="notif-change-form" @submit.prevent>
                  <div class="notif-form-row">
                    <label>Email</label>
                    <input type="email" v-model="form.notifEmail" placeholder="Enter new notification email" />
                  </div>
                  <div class="notif-form-row center">
                    <button class="submit-btn" type="submit" style="width: 100%; max-width: 320px;">
                      <i class="fas fa-save"></i> Save 
                    </button>
                  </div>
                </form>
              </div>
            </transition>
          </div>

          <!-- WhatsApp Notification Dropdown -->
          <div class="notif-dropdown-section">
            <div class="notification-row notif-dropdown-toggle" @click="notifDropdownOpen = notifDropdownOpen === 'whatsapp' ? null : 'whatsapp'">
              <span style="display: flex; align-items: center; gap: 10px;">
                <i class="fab fa-whatsapp"></i> WhatsApp Notification updates
              </span>
              <label class="switch" @click.stop>
                <input type="checkbox" v-model="form.whatsappNotif" />
                <span class="slider"></span>
              </label>
              <span class="notif-dropdown-arrow">
                <i :class="notifDropdownOpen === 'whatsapp' ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </span>
            </div>
            <transition name="fade">
              <div v-if="notifDropdownOpen === 'whatsapp'" class="notif-dropdown-content">
                <form class="notif-change-form" @submit.prevent>
                  <div class="notif-form-row">
                    <label>Mobile Number</label>
                    <input type="text" v-model="form.notifMobile" placeholder="Enter new WhatsApp number" />
                  </div>
                  <div class="notif-form-row center">
                    <button class="submit-btn" type="submit" style="width: 100%; max-width: 320px;">
                      <i class="fas fa-save"></i> Save 
                    </button>
                  </div>
                </form>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data() {
    return {
      activeTab: 'account',
      tabs: [
        { key: 'account', label: 'Account', icon: 'fas fa-user' },
        { key: 'role', label: 'Role', icon: 'fas fa-exchange-alt' },
        { key: 'password', label: 'Password', icon: 'fas fa-key' },
        { key: 'notification', label: 'Notification', icon: 'fas fa-bell' }
      ],
      form: {
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        newPassword: '',
        confirmPassword: '',
        otp: '',
        emailNotif: false,
        whatsappNotif: false,
        notifEmail: '',
        notifMobile: ''
      },
      businessInfo: {
        departmentName: '',
        businessUnitName: '',
        entityName: '',
        location: '',
        departmentHead: ''
      },
      notifDropdownOpen: null,
      loading: false,
      error: null,
      success: null
    }
  },
  mounted() {
    this.loadUserData()
  },
  methods: {
    async loadUserData() {
      this.loading = true
      this.error = null

      try {
        // Get user ID from localStorage
        const userData = localStorage.getItem('user')
        if (userData) {
          const user = JSON.parse(userData)
          const userId = user.UserId

          // Fetch personal info
          const profileResponse = await fetch(`http://localhost:8000/api/user-profile/${userId}/`)
          if (profileResponse.ok) {
            const profileData = await profileResponse.json()
            if (profileData.status === 'success') {
              const data = profileData.data
              this.form.firstName = data.firstName
              this.form.lastName = data.lastName
              this.form.email = data.email
              
              // Fetch business info
              const businessResponse = await fetch(`http://localhost:8000/api/user-business-info/${userId}/`)
              if (businessResponse.ok) {
                const businessData = await businessResponse.json()
                if (businessData.status === 'success') {
                  this.businessInfo = businessData.data
                }
              }
            }
          }
        }
      } catch (error) {
        console.error('Error loading user data:', error)
        this.error = 'Failed to load user data. Please try again.'
      } finally {
        this.loading = false
      }
    },

    async savePersonalInfo() {
      this.loading = true
      this.error = null
      this.success = null

      try {
        const userData = JSON.parse(localStorage.getItem('user') || '{}')
        
        // Here you would typically send the updated data to your backend
        // For now, we'll just update localStorage
        userData.firstName = this.form.firstName
        userData.lastName = this.form.lastName
        userData.email = this.form.email
        userData.phone = this.form.phone

        localStorage.setItem('user', JSON.stringify(userData))
        localStorage.setItem('user_name', `${this.form.firstName} ${this.form.lastName}`)
        localStorage.setItem('user_email', this.form.email)

        this.success = 'Personal information updated successfully!'
        window.dispatchEvent(new Event('userDataUpdated'))

      } catch (error) {
        console.error('Error saving personal info:', error)
        this.error = 'Failed to save personal info. Please try again.'
      } finally {
        this.loading = false
      }
    },

    async saveBusinessInfo() {

  this.loading = true

  this.error = null

  this.success = null

  try {

    // Here you would typically send the updated data to your backend

    // For now, we'll just update localStorage

    const userData = JSON.parse(localStorage.getItem('user') || '{}')

    userData.departmentName = this.businessInfo.departmentName

    userData.businessUnitName = this.businessInfo.businessUnitName

    userData.entityName = this.businessInfo.entityName

    userData.location = this.businessInfo.location

    userData.departmentHead = this.businessInfo.departmentHead

    localStorage.setItem('user', JSON.stringify(userData))

    localStorage.setItem('user_name', this.form.username)

    localStorage.setItem('user_email', this.form.email)

    this.success = 'Business information updated successfully!'

    // Emit event to update sidebar username

    window.dispatchEvent(new Event('userDataUpdated'))

  } catch (error) {

    console.error('Error saving business info:', error)

    this.error = 'Failed to save business info. Please try again.'

  } finally {

    this.loading = false

  }

},

async updatePassword() {

  this.loading = true

  this.error = null

  this.success = null

      
      try {
        if (this.form.newPassword !== this.form.confirmPassword) {
          this.error = 'Passwords do not match.'
          return
        }
        
        if (this.form.newPassword.length < 6) {
          this.error = 'Password must be at least 6 characters long.'
          return
        }
        
        // Here you would typically send the password update to your backend
        // For now, we'll just show a success message
        this.success = 'Password updated successfully!'
        this.form.newPassword = ''
        this.form.confirmPassword = ''
        this.form.otp = ''
        
      } catch (error) {
        console.error('Error updating password:', error)
        this.error = 'Failed to update password. Please try again.'
      } finally {
        this.loading = false
      }
    },
    
    async saveNotificationSettings() {
      this.loading = true
      this.error = null
      this.success = null
      
      try {
        // Here you would typically send the notification settings to your backend
        // For now, we'll just show a success message
        this.success = 'Notification settings updated successfully!'
        
      } catch (error) {
        console.error('Error saving notification settings:', error)
        this.error = 'Failed to save notification settings. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

.user-profile-container {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  margin: 24px 24px 24px 270px;
  padding: 40px 48px;
  min-height: 70vh;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  max-width: 1100px;
  width: 80vw;
}

.tabs {
  display: flex;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 0;
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 4px;
  width: 100%;
  min-width: 1000px;
}

.tab-btn {
  background: transparent;
  border: none;
  color: #64748b;
  padding: 22px 0;
  font-size: 1.25rem;
  cursor: pointer;
  outline: none;
  border-radius: 16px 0 0 16px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  font-weight: 700;
  position: relative;
  flex: 1 1 0;
  justify-content: center;
  min-width: 220px;
  max-width: 100%;
}

.tab-btn .tab-icon {
  margin-right: 16px;
  font-size: 1.5rem;
  transition: all 0.3s ease;
}

.tab-label {
  white-space: nowrap;
  font-size: 1.18rem;
  font-weight: 700;
}

.tab-btn:hover {
  background: #f8fafc;
  color: #3b82f6;
}

.tab-btn.active {
  background: #3b82f6;
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
}

.tab-content {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px 40px;
  min-height: 400px;
  width: 100%;
  box-sizing: border-box;
}

.profile-form {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 28px;
  gap: 18px;
  flex-wrap: wrap;
  width: 100%;
  justify-content: flex-start;
}

.form-row label {
  min-width: 140px;
  text-align: left;
  font-size: 1rem;
  font-weight: 500;
  color: #475569;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
}

.form-row input[type="text"],
.form-row input[type="email"],
.form-row input[type="password"] {
  width: 220px;
  padding: 12px 16px;
  font-size: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  transition: all 0.3s ease;
  box-sizing: border-box;
  margin-bottom: 0;
}

.form-row input:focus {
  border-color: #3b82f6;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

.form-row.center {
  justify-content: center;
  gap: 0;
  width: 100%;
}

.submit-btn, .verify-btn {
  background: #3b82f6;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 8px 18px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
  min-width: 120px;
  max-width: 220px;
  margin: 0 auto;
}

.submit-btn:hover, .verify-btn:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

/* Smaller Save button for notification section */
.notif-change-form .submit-btn {
  padding: 7px 16px;
  font-size: 0.92rem;
  min-width: 100px;
  max-width: 160px;
  margin: 0 auto;
  box-shadow: 0 1px 4px rgba(59, 130, 246, 0.10);
}

.notification-settings {
  max-width: 500px;
  margin: 0 auto;
  padding-top: 24px;
}

.notification-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 1rem;
  margin-bottom: 12px;
  color: #475569;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.notification-row:hover {
  background: #f1f5f9;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #cbd5e1;
  border-radius: 24px;
  transition: .4s;
}

.switch input:checked + .slider {
  background-color: #3b82f6;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: .4s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.switch input:checked + .slider:before {
  transform: translateX(20px);
}

.password-form {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.password-row {
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 24px;
  gap: 24px;
}

.password-row label {
  min-width: 120px;
  text-align: right;
}

.password-row input[type="password"],
.password-row input[type="text"],
.password-row input[type="email"] {
  width: 260px;
}

.verify-btn {
  margin-left: 24px;
  min-width: 120px;
  justify-content: center;
}

.password-submit-row {
  justify-content: center;
  width: 100%;
  margin-top: 10px;
}

.notif-dropdown-section {
  margin-top: 18px;
  width: 100%;
  margin-left: 0;
  margin-right: 0;
}

.notif-dropdown-toggle {
  background: #f8fafc;
  color: #475569;
  font-size: 1.1rem;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #e2e8f0;
  font-weight: 500;
  transition: all 0.3s ease;
}

.notif-dropdown-toggle:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.notif-dropdown-arrow {
  margin-left: 10px;
  font-size: 1.1rem;
}

.notif-dropdown-content {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 24px;
  margin-top: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.notif-change-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  align-items: flex-start;
}

.notif-form-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 16px;
  width: 100%;
}

.notif-form-row label {
  min-width: 110px;
  font-size: 1rem;
  font-weight: 500;
  color: #222b45;
  text-align: left;
}

.notif-form-row input[type="email"],
.notif-form-row input[type="text"] {
  flex: 1;
  min-width: 0;
  width: 260px;
  padding: 10px 12px;
  font-size: 0.95rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.notif-form-row input:focus {
  border-color: #3b82f6;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

.notif-form-row.center {
  justify-content: center;
  gap: 0;
}

.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.section-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #2563eb;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-helper {
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 24px;
}

/* Notification row and toggle alignment */
.notification-row.notif-dropdown-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 16px;
}

.notification-row .switch {
  margin-left: auto;
}

/* Smaller and centered Save button in notification dropdown */
.notif-change-form .submit-btn {
  padding: 6px 14px !important;
  font-size: 0.90rem !important;
  min-width: 80px !important;
  max-width: 120px !important;
  width: auto !important;
  margin: 16px auto 0 auto !important;
  display: block !important;
  box-shadow: 0 1px 4px rgba(59, 130, 246, 0.10) !important;
}

/* Smaller and centered Update Password button in Change Password tab */
.password-submit-row .submit-btn {
  padding: 8px 20px !important;
  font-size: 0.95rem !important;
  min-width: 120px !important;
  max-width: 180px !important;
  width: auto !important;
  margin: 0 auto !important;
  display: block !important;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15) !important;
}

/* Message styles */
.message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.error-message {
  background-color: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.success-message {
  background-color: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.message i {
  font-size: 1.1rem;
}

/* Disabled state for inputs */
.form-row input:disabled {
  background-color: #f1f5f9;
  color: #64748b;
  cursor: not-allowed;
}

.submit-btn:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.submit-btn:disabled:hover {
  background-color: #94a3b8;
  transform: none;
  box-shadow: none;
}

.account-container {
  display: flex;
  gap: 32px;
  width: 100%;
}

.account-section-left,
.account-section-right {
  flex: 1;
  min-width: 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 1rem;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  transition: all 0.3s ease;
}

.form-group input:disabled {
  background-color: #f1f5f9;
  color: #64748b;
  cursor: not-allowed;
}

.form-group input:focus {
  border-color: #3b82f6;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

@media (max-width: 900px) {
  .form-row {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  .form-row label {
    min-width: 0;
    text-align: left;
    margin-bottom: 2px;
  }
  .form-row input[type="text"],
  .form-row input[type="email"],
  .form-row input[type="password"] {
    width: 100%;
    min-width: 0;
  }
  .account-container {
    flex-direction: column;
  }
}
</style> 