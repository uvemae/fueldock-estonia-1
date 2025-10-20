<template>
  <div class="payment-page">
    <header class="header">
      <button @click="$emit('back')" class="back-btn">← Back</button>
      <h2>Payment</h2>
    </header>

    <div class="content">
      <!-- Fuel selection -->
      <div class="card">
        <h3>Select Fuel Type</h3>
        <div class="fuel-options">
          <label v-for="(fuel, type) in station.fuels" :key="type" class="fuel-option">
            <input type="radio" :value="type" v-model="selectedFuel" />
            <span>{{ type.toUpperCase() }} - {{ fuel.price.toFixed(2) }}€/L</span>
          </label>
        </div>
      </div>

      <!-- Amount -->
      <div class="card">
        <h3>Liters</h3>
        <input type="number" v-model="liters" placeholder="50" class="input" />
        <p class="total">Cost: <strong>{{ totalCost.toFixed(2) }}€</strong></p>
      </div>

      <!-- Payment method -->
      <div class="card">
        <h3>Payment Method</h3>
        <label class="payment-option">
          <input type="radio" value="qr" v-model="paymentMethod" />
          <span>📱 QR Code</span>
        </label>
        <label class="payment-option">
          <input type="radio" value="card" v-model="paymentMethod" />
          <span>💳 Card</span>
        </label>
      </div>

      <!-- QR mockup -->
      <div v-if="paymentMethod === 'qr'" class="qr-box">
        <div class="qr-code">QR</div>
      </div>

      <button @click="confirmPayment" class="confirm-btn">CONFIRM PAYMENT</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  station: { type: Object, required: true }
})

const emit = defineEmits(['back', 'complete'])

const selectedFuel = ref(Object.keys(props.station.fuels)[0])
const liters = ref(50)
const paymentMethod = ref('qr')

const totalCost = computed(() => {
  const price = props.station.fuels[selectedFuel.value]?.price || 0
  return price * liters.value
})

function confirmPayment() {
  emit('complete', {
    station: props.station.name,
    fuelType: selectedFuel.value.toUpperCase(),
    liters: liters.value,
    cost: totalCost.value
  })
}
</script>

<style scoped>
.payment-page {
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

.card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.fuel-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.fuel-option, .payment-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
}

.fuel-option:has(input:checked),
.payment-option:has(input:checked) {
  border-color: #10b981;
  background: #f0fdf4;
}

.input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  margin-top: 0.5rem;
}

.total {
  margin-top: 1rem;
  font-size: 1.125rem;
}

.qr-box {
  text-align: center;
  padding: 2rem;
}

.qr-code {
  width: 200px;
  height: 200px;
  background: white;
  border: 2px solid #333;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: bold;
  margin: 0 auto 1rem;
}

.confirm-btn {
  width: 100%;
  padding: 1rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.125rem;
  font-weight: 700;
  cursor: pointer;
}

.confirm-btn:hover {
  background: #059669;
}
</style>