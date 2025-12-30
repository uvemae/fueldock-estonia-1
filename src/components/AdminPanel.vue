<template>
  <div class="admin-container">
    <header class="admin-header">
      <button @click="$emit('back')" class="back-btn">← Back to Map</button>
      <h2>Admin Panel</h2>
    </header>

    <!-- Tab Navigation -->
    <div class="tabs">
      <button
        :class="{ active: activeTab === 'marinas' }"
        @click="activeTab = 'marinas'"
      >
        Marina Management
      </button>
      <button
        :class="{ active: activeTab === 'users' }"
        @click="activeTab = 'users'"
      >
        User Management
      </button>
    </div>

    <!-- Marina Management Tab -->
    <div v-if="activeTab === 'marinas'" class="tab-content">
      <div class="toolbar">
        <input
          v-model="searchQuery"
          placeholder="🔍 Search marinas..."
          class="search-input"
        />
        <button @click="showAddModal = true" class="add-btn">
          + Add Marina
        </button>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Location</th>
              <th>Provider</th>
              <th>Fuel Level</th>
              <th>Capacity</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="marina in filteredMarinas" :key="marina.id">
              <td>{{ marina.name }}</td>
              <td>{{ marina.location }}</td>
              <td>{{ marina.stationType }}</td>
              <td>
                <div class="fuel-indicator">
                  <div class="fuel-bar">
                    <div
                      class="fuel-fill"
                      :style="{ width: marina.fuelLevel + '%' }"
                      :class="getFuelClass(marina.fuelLevel)"
                    ></div>
                  </div>
                  <span>{{ marina.fuelLevel }}%</span>
                </div>
              </td>
              <td>{{ marina.capacity }}L</td>
              <td>
                <span
                  class="status-badge"
                  :class="marina.hasStation ? 'active' : 'inactive'"
                >
                  {{ marina.hasStation ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button
                    @click="editMarina(marina)"
                    class="edit-btn"
                    title="Edit"
                  >
                    ✏️
                  </button>
                  <button
                    @click="deleteMarina(marina)"
                    class="delete-btn"
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- User Management Tab -->
    <div v-if="activeTab === 'users'" class="tab-content">
      <div class="toolbar">
        <input
          v-model="userSearchQuery"
          placeholder="🔍 Search users..."
          class="search-input"
        />
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Created</th>
              <th>Last Sign In</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td>{{ user.email }}</td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>{{ formatDate(user.last_sign_in_at) }}</td>
              <td>
                <span
                  class="status-badge"
                  :class="user.email_confirmed_at ? 'active' : 'pending'"
                >
                  {{ user.email_confirmed_at ? 'Verified' : 'Pending' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button
                    @click="toggleAdminRole(user)"
                    class="role-btn"
                    :title="isUserAdmin(user) ? 'Remove Admin' : 'Make Admin'"
                  >
                    {{ isUserAdmin(user) ? '👤' : '👑' }}
                  </button>
                  <button
                    @click="deleteUser(user)"
                    class="delete-btn"
                    title="Delete User"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Marina Modal -->
    <div
      v-if="showAddModal || editingMarina"
      class="modal-overlay"
      @mousedown="handleOverlayMouseDown"
    >
      <div class="modal-content" @click.stop @mousedown.stop>
        <h3>{{ editingMarina ? 'Edit Marina' : 'Add New Marina' }}</h3>

        <form @submit.prevent="saveMarina" class="marina-form">
          <div class="form-row">
            <div class="form-group">
              <label>Marina Name *</label>
              <input
                v-model="marinaForm.name"
                type="text"
                required
                placeholder="e.g., DIRHAMI SADAM"
              />
            </div>

            <div class="form-group">
              <label>Location *</label>
              <input
                v-model="marinaForm.location"
                type="text"
                required
                placeholder="e.g., Lääne maakond"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Latitude *</label>
              <input
                v-model.number="marinaForm.coordinates[0]"
                type="number"
                step="any"
                required
              />
            </div>

            <div class="form-group">
              <label>Longitude *</label>
              <input
                v-model.number="marinaForm.coordinates[1]"
                type="number"
                step="any"
                required
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Station Type</label>
              <input
                v-model="marinaForm.stationType"
                type="text"
                placeholder="e.g., Olerex"
              />
            </div>

            <div class="form-group">
              <label>
                <input
                  v-model="marinaForm.hasStation"
                  type="checkbox"
                />
                Has Fuel Station
              </label>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Fuel Level (%)</label>
              <input
                v-model.number="marinaForm.fuelLevel"
                type="number"
                min="0"
                max="100"
              />
            </div>

            <div class="form-group">
              <label>Capacity (L)</label>
              <input
                v-model.number="marinaForm.capacity"
                type="number"
                min="0"
              />
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="cancel-btn">
              Cancel
            </button>
            <button type="submit" class="save-btn">
              {{ editingMarina ? 'Update' : 'Add' }} Marina
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteConfirmModal" class="modal-overlay" @click="deleteConfirmModal = null">
      <div class="login-prompt-modal" @click.stop>
        <div class="modal-icon">⚠️</div>
        <h3>Confirm Delete</h3>
        <p>
          Are you sure you want to delete<br>
          <strong>{{ deleteConfirmModal.item.name || deleteConfirmModal.item.email }}</strong>?
          <br>This action cannot be undone.
        </p>
        <div class="modal-actions">
          <button @click="confirmDelete" class="delete-confirm-btn">
            Delete
          </button>
          <button @click="deleteConfirmModal = null" class="cancel-btn">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
    </div>

    <!-- Notification -->
    <div v-if="notification" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import stationsData from '../data/stations.json'
import { supabase } from '../supabase'

const emit = defineEmits(['back'])

const activeTab = ref('marinas')
const searchQuery = ref('')
const userSearchQuery = ref('')
const showAddModal = ref(false)
const editingMarina = ref(null)
const loading = ref(false)
const notification = ref(null)
const deleteConfirmModal = ref(null)

// Marina data (loaded from JSON for now)
const marinas = ref([...stationsData])

// User data
const users = ref([])

// Marina form
const marinaForm = ref({
  id: '',
  name: '',
  location: '',
  coordinates: [0, 0],
  hasStation: true,
  stationType: '',
  fuelLevel: 0,
  capacity: 0,
  fuels: {
    diesel: { available: true, price: 0 },
    e95: { available: true, price: 0 },
    e98: { available: true, price: 0 }
  },
  payment: ['card'],
  hours: '24/7'
})

// Computed
const filteredMarinas = computed(() => {
  if (!searchQuery.value) return marinas.value

  const query = searchQuery.value.toLowerCase()
  return marinas.value.filter(
    m =>
      m.name.toLowerCase().includes(query) ||
      m.location.toLowerCase().includes(query) ||
      m.stationType?.toLowerCase().includes(query)
  )
})

const filteredUsers = computed(() => {
  if (!userSearchQuery.value) return users.value

  const query = userSearchQuery.value.toLowerCase()
  return users.value.filter(u => u.email.toLowerCase().includes(query))
})

// Watch for tab changes and only load users when users tab is active
watch(activeTab, async (newTab) => {
  if (newTab === 'users' && users.value.length === 0) {
    await loadUsers()
  }
})

// Functions
async function loadUsers() {
  loading.value = true
  try {
    const { data, error } = await supabase.auth.admin.listUsers()

    if (error) throw error

    users.value = data.users || []
  } catch (error) {
    showNotification('Failed to load users: ' + error.message, 'error')
  } finally {
    loading.value = false
  }
}

function editMarina(marina) {
  editingMarina.value = marina
  marinaForm.value = { ...marina }
}

function handleOverlayMouseDown(e) {
  // Only close if clicking directly on the overlay (not on modal content)
  if (e.target.classList.contains('modal-overlay')) {
    closeModal()
  }
}

function closeModal() {
  showAddModal.value = false
  editingMarina.value = null
  deleteConfirmModal.value = null
  resetForm()
}

function resetForm() {
  marinaForm.value = {
    id: '',
    name: '',
    location: '',
    coordinates: [0, 0],
    hasStation: true,
    stationType: '',
    fuelLevel: 0,
    capacity: 0,
    fuels: {
      diesel: { available: true, price: 0 },
      e95: { available: true, price: 0 },
      e98: { available: true, price: 0 }
    },
    payment: ['card'],
    hours: '24/7'
  }
}

async function saveMarina() {
  if (editingMarina.value) {
    // Update existing
    const index = marinas.value.findIndex(m => m.id === editingMarina.value.id)
    if (index !== -1) {
      marinas.value[index] = { ...marinaForm.value }
    }
  } else {
    // Add new
    marinaForm.value.id = `station-${Date.now()}`
    marinas.value.push({ ...marinaForm.value })
  }

  // Save to file via server
  await saveMarinasToServer()

  closeModal()
}

function deleteMarina(marina) {
  deleteConfirmModal.value = { type: 'marina', item: marina }
}

async function confirmDelete() {
  if (!deleteConfirmModal.value) return

  if (deleteConfirmModal.value.type === 'marina') {
    const marina = deleteConfirmModal.value.item
    marinas.value = marinas.value.filter(m => m.id !== marina.id)
    showNotification('Marina deleted successfully', 'success')
    await saveMarinasToServer()
  }

  deleteConfirmModal.value = null
}

async function deleteUser(user) {
  if (!confirm(`Delete user ${user.email}?`)) return

  loading.value = true
  try {
    const { error } = await supabase.auth.admin.deleteUser(user.id)

    if (error) throw error

    users.value = users.value.filter(u => u.id !== user.id)
    showNotification('User deleted successfully', 'success')
  } catch (error) {
    showNotification('Failed to delete user: ' + error.message, 'error')
  } finally {
    loading.value = false
  }
}

async function toggleAdminRole(user) {
  const currentRole = user.user_metadata?.role
  const newRole = currentRole === 'admin' ? 'user' : 'admin'

  loading.value = true
  try {
    const { error } = await supabase.auth.admin.updateUserById(user.id, {
      user_metadata: { role: newRole }
    })

    if (error) throw error

    // Update local data
    const userIndex = users.value.findIndex(u => u.id === user.id)
    if (userIndex !== -1) {
      users.value[userIndex].user_metadata = {
        ...users.value[userIndex].user_metadata,
        role: newRole
      }
    }

    showNotification(
      `User ${newRole === 'admin' ? 'promoted to' : 'removed from'} admin`,
      'success'
    )
  } catch (error) {
    showNotification('Failed to update role: ' + error.message, 'error')
  } finally {
    loading.value = false
  }
}

function isUserAdmin(user) {
  return user.user_metadata?.role === 'admin' || user.email === 'admin@fueldock.ee'
}

async function saveMarinasToServer() {
  loading.value = true
  try {
    const response = await fetch('http://localhost:3001/api/save-stations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(marinas.value)
    })

    // Check if HTTP response is successful (status 200-299)
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`)
    }

    // Try to parse JSON response
    let result
    try {
      result = await response.json()
    } catch (e) {
      // If JSON parsing fails, assume success since HTTP status was OK
      console.log('No JSON response, but HTTP status OK - treating as success')
      showNotification('✅ Marinas saved successfully!', 'success')
      return
    }

    // Check result.success if present, otherwise assume success from HTTP 200
    if (result.success !== false) {
      showNotification('✅ Marinas saved successfully!', 'success')
    } else {
      throw new Error(result.message || 'Save failed')
    }
  } catch (error) {
    console.error('Save error:', error)
    showNotification('❌ Error saving marinas. Is the save server running?', 'error')
  } finally {
    loading.value = false
  }
}

function getFuelClass(level) {
  if (level === 0) return 'empty'
  if (level < 20) return 'low'
  return 'good'
}

function formatDate(dateString) {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function showNotification(message, type = 'success') {
  notification.value = { message, type }
  setTimeout(() => {
    notification.value = null
  }, 3000)
}
</script>

<style scoped>
.admin-container {
  height: 100%;
  background: #f9fafb;
  overflow-y: auto;
}

.admin-header {
  background: white;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.admin-header h2 {
  margin: 0;
  color: #111827;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: #e5e7eb;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #d1d5db;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  background: white;
  border-bottom: 2px solid #e5e7eb;
}

.tabs button {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  color: #6b7280;
}

.tabs button.active {
  background: #3b82f6;
  color: white;
}

.tab-content {
  padding: 1.5rem;
}

.toolbar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
}

.add-btn {
  padding: 0.75rem 1.5rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.add-btn:hover {
  background: #059669;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: #f3f4f6;
}

.data-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.data-table tbody tr:hover {
  background: #f9fafb;
}

.fuel-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.fuel-bar {
  flex: 1;
  height: 20px;
  background: #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
}

.fuel-fill {
  height: 100%;
  transition: width 0.3s;
}

.fuel-fill.good {
  background: #10b981;
}

.fuel-fill.low {
  background: #fbbf24;
}

.fuel-fill.empty {
  background: #ef4444;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.pending {
  background: #fed7aa;
  color: #92400e;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.edit-btn,
.delete-btn,
.role-btn {
  padding: 0.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1.25rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: #dbeafe;
}

.delete-btn:hover {
  background: #fee2e2;
}

.role-btn:hover {
  background: #fef3c7;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin: 0 0 1.5rem 0;
  color: #111827;
}

.marina-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.form-group input[type='text'],
.form-group input[type='number'] {
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
}

.form-group input[type='checkbox'] {
  width: auto;
  margin-right: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.cancel-btn,
.save-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #e5e7eb;
  color: #374151;
}

.cancel-btn:hover {
  background: #d1d5db;
}

.save-btn {
  background: #10b981;
  color: white;
}

.save-btn:hover {
  background: #059669;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  z-index: 4000;
  animation: slideIn 0.3s ease;
}

.notification.success {
  background: #d1fae5;
  color: #065f46;
}

.notification.error {
  background: #fee2e2;
  color: #991b1b;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Delete Confirmation Modal (styled like App.vue login prompt) */
.login-prompt-modal {
  background: white;
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 400px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.login-prompt-modal h3 {
  margin: 0 0 1rem 0;
  color: #111827;
  font-size: 1.5rem;
}

.login-prompt-modal p {
  color: #6b7280;
  margin: 0 0 2rem 0;
  font-size: 1rem;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.delete-confirm-btn {
  padding: 1rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.delete-confirm-btn:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(239, 68, 68, 0.3);
}

.modal-actions .cancel-btn {
  padding: 0.875rem;
  background: white;
  color: #6b7280;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-actions .cancel-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #f0f9ff;
}
</style>
