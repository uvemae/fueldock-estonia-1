<template>
  <div class="detail-page">
    <header class="header">
      <button @click="$emit('back')" class="back-btn">← Back</button>
      <h2>{{ station.name }}</h2>
    </header>

    <div class="content">
      <!-- Station info -->
      <div class="info-card">
        <div class="info-row">
          <span class="label">Provider:</span>
          <span class="value">⛽ {{ station.stationType }}</span>
        </div>
        <div class="info-row">
          <span class="label">Location:</span>
          <span class="value">📍 {{ station.location }}</span>
        </div>
        <div class="info-row">
          <span class="label">Status:</span>
          <span class="value" :class="statusClass">{{ statusText }}</span>
        </div>
        <div class="info-row">
          <span class="label">Fuel Level:</span>
          <span class="value">{{ fuelAmount }}L / {{ station.capacity }}L</span>
        </div>
      </div>

      <!-- Fuel prices -->
      <div class="prices-card">
        <h3>Fuel Prices</h3>
        <div v-for="(fuel, type) in station.fuels" :key="type" class="price-row">
          <span class="fuel-type">{{ type.toUpperCase() }}</span>
          <span class="price">{{ fuel.price.toFixed(2) }}€/L</span>
        </div>
      </div>

      <!-- Additional info -->
      <div class="info-card">
        <div class="info-row">
          <span class="label">Hours:</span>
          <span class="value">⏰ {{ station.hours }}</span>
        </div>
        <div class="info-row">
          <span class="label">Payment:</span>
          <span class="value">💳 {{ station.payment.join(', ') }}</span>
        </div>
      </div>

      <!-- Action button -->
      <button @click="$emit('pay', station)" class="fuel-btn">
        START FUELING
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  station: { type: Object, required: true }
})

defineEmits(['back', 'pay'])

// Calculate fuel amount in liters
const fuelAmount = computed(() =>
    Math.round(props.station.capacity * props.station.fuelLevel / 100)
)

// Determine status text and color
const statusText = computed(() => {
  if (props.station.fuelLevel === 0) return '🔴 OUT OF FUEL'
  if (props.station.fuelLevel < 20) return '🟡 LOW FUEL'
  return '🟢 AVAILABLE'
})

const statusClass = computed(() => {
  if (props.station.fuelLevel === 0) return 'text-red-600'
  if (props.station.fuelLevel < 20) return 'text-yellow-600'
  return 'text-green-600'
})
</script>

<style scoped>
.detail-page {
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

.info-card, .prices-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.info-row, .price-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.info-row:last-child, .price-row:last-child {
  border-bottom: none;
}

.label {
  color: #6b7280;
  font-weight: 500;
}

.value {
  font-weight: 600;
}

.fuel-type {
  font-weight: 600;
  color: #1e40af;
}

.price {
  font-size: 1.125rem;
  font-weight: 700;
  color: #10b981;
}

.fuel-btn {
  width: 100%;
  padding: 1rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.125rem;
  font-weight: 700;
  cursor: pointer;
  margin-top: 1rem;
}

.fuel-btn:hover {
  background: #059669;
}
</style>