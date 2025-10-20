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
        <p>Total spent: <strong>{{ totalSpent.toFixed(2) }}€</strong></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

defineEmits(['back'])

// Load history from localStorage
const history = ref([])

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
  background: white;
  border-radius: 12px;
  padding: 1rem;
  margin-top: 1rem;
  text-align: center;
  font-size: 1.125rem;
}
</style>