<template>
  <div class="history-page">
    <header class="header">
      <button @click="$emit('back')" class="back-btn">← Back</button>
      <h2>Fuel History</h2>
    </header>

    <div class="content">
      <div v-if="history.length === 0" class="empty">
        <p>No transactions yet</p>
      </div>

      <div v-else class="history-list">
        <div v-for="(item, index) in history" :key="index" class="history-item">
          <div class="item-header">
            <span class="date">{{ formatDate(item.date) }}</span>
            <span class="cost">{{ item.cost.toFixed(2) }}€</span>
          </div>
          <div class="item-details">
            <p><strong>{{ item.station }}</strong></p>
            <p>{{ item.liters }}L {{ item.fuelType }}</p>
          </div>
        </div>
      </div>

      <div v-if="history.length > 0" class="summary">
        <button @click="confirmReset" class="reset-btn">
          🗑️ Clear History
        </button>
        <div class="total-spent">
          <p>Total spent: <strong>{{ totalSpent.toFixed(2) }}€</strong></p>
        </div>
      </div>

      <!-- Confirmation Modal -->
      <div v-if="showConfirmModal" class="modal-overlay" @click="showConfirmModal = false">
        <div class="confirm-modal" @click.stop>
          <div class="modal-icon">⚠️</div>
          <h3>Clear History?</h3>
          <p>This will permanently delete all fuel history records.</p>
          <div class="modal-actions">
            <button @click="showConfirmModal = false" class="cancel-btn">Cancel</button>
            <button @click="resetHistory" class="confirm-btn">Clear All</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

defineEmits(['back'])

// Load history from localStorage
const history = ref([])
const showConfirmModal = ref(false)

onMounted(() => {
  history.value = JSON.parse(localStorage.getItem('fuelHistory') || '[]')
})

// Calculate total spent
const totalSpent = computed(() =>
    history.value.reduce((sum, item) => sum + item.cost, 0)
)

// Format date for display
function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('et-EE', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Show confirmation modal
function confirmReset() {
  showConfirmModal.value = true
}

// Reset history
function resetHistory() {
  localStorage.removeItem('fuelHistory')
  history.value = []
  showConfirmModal.value = false
}
</script>

<style scoped>
.history-page {
  height: 100%;
  overflow-y: auto;
  background: #f3f4f6;
}

.header {
  background: white;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: #e5e7eb;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.content {
  padding: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.empty {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.date {
  color: #6b7280;
  font-size: 0.875rem;
}

.cost {
  font-size: 1.125rem;
  font-weight: 700;
  color: #10b981;
}

.item-details {
  color: #374151;
}

.summary {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.reset-btn {
  flex: 1;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 1rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.reset-btn:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
}

.total-spent {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  font-size: 1.125rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.total-spent p {
  margin: 0;
}

/* Confirmation Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.confirm-modal {
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

.confirm-modal h3 {
  margin: 0 0 1rem 0;
  color: #111827;
  font-size: 1.5rem;
}

.confirm-modal p {
  color: #6b7280;
  margin: 0 0 2rem 0;
  font-size: 1rem;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
}

.cancel-btn {
  flex: 1;
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

.cancel-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #f0f9ff;
}

.confirm-btn {
  flex: 1;
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

.confirm-btn:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(239, 68, 68, 0.3);
}
</style>