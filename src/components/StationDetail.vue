<template>
  <div class="modal-overlay" @click="$emit('back')">
    <div class="modal-content" @click.stop>
      <header class="header">
        <h2>{{ station.name }}</h2>
        <button @click="$emit('back')" class="close-btn">✕</button>
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
            <span class="label">Coordinates:</span>
            <span class="value coordinates">{{ formatCoordinates }}</span>
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

// Format coordinates for display
const formatCoordinates = computed(() => {
  const [lat, lng] = props.station.coordinates
  return `${lat.toFixed(6)}, ${lng.toFixed(6)}`
})

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
  z-index: 1500;
  padding: 1rem;
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

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

/* Hide scrollbar */
.modal-content::-webkit-scrollbar {
  display: none;
}

.modal-content {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header {
  background: #1e40af;
  color: white;
  padding: 1.5rem;
  border-radius: 16px 16px 0 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.content {
  padding: 1.5rem;
}

.info-card, .prices-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
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

.value.coordinates {
  font-family: 'Courier New', monospace;
  color: #1e40af;
  font-size: 0.9rem;
  background: #dbeafe;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
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