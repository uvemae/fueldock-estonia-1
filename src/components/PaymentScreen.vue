<template>
  <div class="payment-page">
    <header class="header">
      <button @click="handleBack" class="back-btn">← Back</button>
      <h2>{{ getHeaderTitle() }}</h2>
    </header>

    <div class="content">
      <!-- STEP 1: Fuel Selection & Amount -->
      <div v-if="currentStep === 'selection'">
        <!-- Station Info -->
        <div class="card station-info">
          <h3>{{ station.name }}</h3>
          <p class="station-location">{{ station.location }}</p>
        </div>

        <!-- Fuel selection -->
        <div class="card">
          <h3>Select Fuel Type</h3>
          <div class="fuel-options">
            <label
              v-for="(fuel, type) in station.fuels"
              :key="type"
              class="fuel-option"
              :class="{ 'low-stock': getFuelStock(type) < 100 }"
            >
              <input type="radio" :value="type" v-model="selectedFuel" />
              <div class="fuel-details">
                <span class="fuel-name">{{ type.toUpperCase() }}</span>
                <span class="fuel-price">{{ fuel.price.toFixed(2) }}€/L</span>
                <span class="fuel-stock" :class="{ 'warning': getFuelStock(type) < 100 }">
                  {{ getFuelStock(type) }}L available
                </span>
              </div>
            </label>
          </div>
        </div>

        <!-- Amount with presets -->
        <div class="card">
          <h3>Fuel Amount</h3>
          <div class="preset-buttons">
            <button
              v-for="preset in [25, 50, 75, 100]"
              :key="preset"
              @click="liters = preset"
              class="preset-btn"
              :class="{ 'active': liters === preset }"
            >
              {{ preset }}L
            </button>
          </div>
          <input type="number" v-model.number="liters" placeholder="50" class="input" min="1" />
          <div class="price-breakdown">
            <div class="price-row">
              <span>Price per liter:</span>
              <span>{{ currentFuelPrice.toFixed(2) }}€</span>
            </div>
            <div class="price-row total">
              <span>Total Cost:</span>
              <strong>{{ totalCost.toFixed(2) }}€</strong>
            </div>
          </div>
          <div v-if="validationError" class="error-message">
            ⚠️ {{ validationError }}
          </div>
        </div>

        <!-- Payment method -->
        <div class="card">
          <h3>Payment Method</h3>
          <div class="payment-methods">
            <label class="payment-method-card">
              <input type="radio" value="card" v-model="paymentMethod" />
              <div class="method-content">
                <span class="method-icon">💳</span>
                <span class="method-name">Credit Card</span>
              </div>
            </label>
            <label class="payment-method-card">
              <input type="radio" value="mobile" v-model="paymentMethod" />
              <div class="method-content">
                <span class="method-icon">📱</span>
                <span class="method-name">Mobile Pay</span>
              </div>
            </label>
            <label class="payment-method-card">
              <input type="radio" value="qr" v-model="paymentMethod" />
              <div class="method-content">
                <div class="method-icon qr-icon">
                  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    <!-- Top-left corner -->
                    <rect x="5" y="5" width="35" height="35" fill="none" stroke="currentColor" stroke-width="3"/>
                    <rect x="12" y="12" width="21" height="21" fill="currentColor"/>

                    <!-- Top-right corner -->
                    <rect x="60" y="5" width="35" height="35" fill="none" stroke="currentColor" stroke-width="3"/>
                    <rect x="67" y="12" width="21" height="21" fill="currentColor"/>

                    <!-- Bottom-left corner -->
                    <rect x="5" y="60" width="35" height="35" fill="none" stroke="currentColor" stroke-width="3"/>
                    <rect x="12" y="67" width="21" height="21" fill="currentColor"/>

                    <!-- Data pattern -->
                    <rect x="48" y="48" width="7" height="7" fill="currentColor"/>
                    <rect x="60" y="48" width="7" height="7" fill="currentColor"/>
                    <rect x="72" y="48" width="7" height="7" fill="currentColor"/>
                    <rect x="84" y="48" width="7" height="7" fill="currentColor"/>

                    <rect x="48" y="60" width="7" height="7" fill="currentColor"/>
                    <rect x="72" y="60" width="7" height="7" fill="currentColor"/>

                    <rect x="48" y="72" width="7" height="7" fill="currentColor"/>
                    <rect x="60" y="72" width="7" height="7" fill="currentColor"/>
                    <rect x="84" y="72" width="7" height="7" fill="currentColor"/>

                    <rect x="48" y="84" width="7" height="7" fill="currentColor"/>
                    <rect x="72" y="84" width="7" height="7" fill="currentColor"/>
                  </svg>
                </div>
                <span class="method-name">QR Code</span>
              </div>
            </label>
          </div>
        </div>

        <button @click="proceedToPayment" class="confirm-btn">PROCEED TO PAYMENT</button>
      </div>

      <!-- STEP 2: Payment Processing -->
      <div v-if="currentStep === 'processing'" class="processing-screen">
        <div class="processing-animation">
          <div class="spinner"></div>
          <h3>{{ processingMessage }}</h3>
          <p>Please wait...</p>
        </div>
      </div>

      <!-- STEP 3: Refueling Animation -->
      <div v-if="currentStep === 'refueling'" class="refueling-screen">
        <div class="refueling-animation">
          <div class="fuel-pump-icon">⛽</div>
          <h3>Refueling in Progress</h3>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: refuelingProgress + '%' }"></div>
          </div>
          <p class="progress-text">{{ refuelingProgress }}%</p>
          <p class="liters-dispensed">{{ currentLitersDispensed.toFixed(1) }}L / {{ liters }}L</p>
        </div>
      </div>

      <!-- STEP 4: Receipt/Confirmation -->
      <div v-if="currentStep === 'receipt'" class="receipt-screen">
        <div class="success-animation">
          <div class="checkmark">✓</div>
          <h3>Payment Successful!</h3>
        </div>

        <div class="receipt-card">
          <div class="receipt-header">
            <h3>Receipt</h3>
            <p class="transaction-id">Transaction #{{ transactionId }}</p>
            <p class="timestamp">{{ transactionTimestamp }}</p>
          </div>

          <div class="receipt-divider"></div>

          <div class="receipt-details">
            <div class="receipt-row">
              <span>Station:</span>
              <span>{{ station.name }}</span>
            </div>
            <div class="receipt-row">
              <span>Fuel Type:</span>
              <span>{{ selectedFuel.toUpperCase() }}</span>
            </div>
            <div class="receipt-row">
              <span>Amount:</span>
              <span>{{ liters }}L</span>
            </div>
            <div class="receipt-row">
              <span>Price per liter:</span>
              <span>{{ currentFuelPrice.toFixed(2) }}€</span>
            </div>
            <div class="receipt-row">
              <span>Payment Method:</span>
              <span>{{ getPaymentMethodName() }}</span>
            </div>
          </div>

          <div class="receipt-divider"></div>

          <div class="receipt-total">
            <span>Total Paid:</span>
            <strong>{{ totalCost.toFixed(2) }}€</strong>
          </div>
        </div>

        <div class="receipt-actions">
          <button @click="downloadReceipt" class="download-btn">
            📥 Download Receipt
          </button>
          <button @click="finishPayment" class="finish-btn">
            Done
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  station: { type: Object, required: true }
})

const emit = defineEmits(['back', 'complete'])

// Step management
const currentStep = ref('selection') // 'selection', 'processing', 'refueling', 'receipt'

// Selection state
const selectedFuel = ref(Object.keys(props.station.fuels)[0])
const liters = ref(50)
const paymentMethod = ref('card')
const validationError = ref('')

// Mock fuel stock data (in a real app, this would come from the station object)
const fuelStock = ref({})

// Initialize fuel stock with random amounts for demonstration
Object.keys(props.station.fuels).forEach(type => {
  fuelStock.value[type] = Math.floor(Math.random() * 400) + 100 // 100-500L
})

// Processing state
const processingMessage = ref('Connecting to payment gateway...')

// Refueling state
const refuelingProgress = ref(0)
const currentLitersDispensed = ref(0)

// Receipt state
const transactionId = ref('')
const transactionTimestamp = ref('')

// Computed properties
const currentFuelPrice = computed(() => {
  return props.station.fuels[selectedFuel.value]?.price || 0
})

const totalCost = computed(() => {
  return currentFuelPrice.value * liters.value
})

// Helper functions
function getFuelStock(type) {
  return fuelStock.value[type] || 0
}

function getHeaderTitle() {
  switch (currentStep.value) {
    case 'selection': return 'Payment'
    case 'processing': return 'Processing Payment'
    case 'refueling': return 'Refueling'
    case 'receipt': return 'Receipt'
    default: return 'Payment'
  }
}

function getPaymentMethodName() {
  const methods = {
    'card': 'Credit Card',
    'mobile': 'Mobile Pay',
    'qr': 'QR Code'
  }
  return methods[paymentMethod.value] || paymentMethod.value
}

function handleBack() {
  if (currentStep.value === 'selection') {
    emit('back')
  } else if (currentStep.value === 'receipt') {
    finishPayment()
  }
  // Prevent going back during processing/refueling
}

// A. Pre-Payment Flow: Validate before proceeding
function proceedToPayment() {
  validationError.value = ''

  // Validate amount
  if (!liters.value || liters.value <= 0) {
    validationError.value = 'Please enter a valid amount'
    return
  }

  // Check fuel availability
  const availableStock = getFuelStock(selectedFuel.value)
  if (liters.value > availableStock) {
    validationError.value = `Only ${availableStock}L of ${selectedFuel.value.toUpperCase()} available`
    return
  }

  // Check minimum amount (optional)
  if (liters.value < 5) {
    validationError.value = 'Minimum fuel amount is 5L'
    return
  }

  // Proceed to processing
  currentStep.value = 'processing'
  simulatePaymentProcessing()
}

// B. Mock Payment Animation
async function simulatePaymentProcessing() {
  const steps = [
    'Connecting to payment gateway...',
    'Verifying payment method...',
    'Authorizing transaction...',
    'Payment confirmed!'
  ]

  for (let i = 0; i < steps.length; i++) {
    processingMessage.value = steps[i]
    await new Promise(resolve => setTimeout(resolve, 800))
  }

  // Generate transaction details
  transactionId.value = 'FD' + Date.now().toString().slice(-8)
  transactionTimestamp.value = new Date().toLocaleString('et-EE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })

  // Move to refueling animation
  currentStep.value = 'refueling'
  simulateRefueling()
}

// Refueling animation
async function simulateRefueling() {
  const duration = 3000 // 3 seconds
  const steps = 60
  const interval = duration / steps

  for (let i = 0; i <= steps; i++) {
    refuelingProgress.value = Math.round((i / steps) * 100)
    currentLitersDispensed.value = (liters.value * i) / steps
    await new Promise(resolve => setTimeout(resolve, interval))
  }

  // D. Mock Data Updates: Decrease station fuel level
  fuelStock.value[selectedFuel.value] -= liters.value

  // Move to receipt
  currentStep.value = 'receipt'
}

// C. Receipt/Confirmation
function downloadReceipt() {
  const receiptText = `
=================================
      FUELDOCK ESTONIA
=================================

Transaction #${transactionId.value}
${transactionTimestamp.value}

---------------------------------
Station: ${props.station.name}
Fuel Type: ${selectedFuel.value.toUpperCase()}
Amount: ${liters.value}L
Price/L: ${currentFuelPrice.value.toFixed(2)}€
Payment: ${getPaymentMethodName()}
---------------------------------
TOTAL: ${totalCost.value.toFixed(2)}€
=================================

Thank you for using FuelDock!
  `.trim()

  const blob = new Blob([receiptText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `receipt-${transactionId.value}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

function finishPayment() {
  // Emit completion with full transaction details
  emit('complete', {
    station: props.station.name,
    fuelType: selectedFuel.value.toUpperCase(),
    liters: liters.value,
    cost: totalCost.value,
    transactionId: transactionId.value,
    timestamp: transactionTimestamp.value,
    paymentMethod: getPaymentMethodName(),
    date: new Date().toISOString()
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
  transition: all 0.2s;
}

.back-btn:hover {
  background: #d1d5db;
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
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.card h3 {
  margin: 0 0 1rem 0;
  color: #111827;
}

/* Station Info */
.station-info h3 {
  margin-bottom: 0.25rem;
}

.station-location {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

/* Fuel Options */
.fuel-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.fuel-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.fuel-option:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.fuel-option:has(input:checked) {
  border-color: #10b981;
  background: #f0fdf4;
}

.fuel-option.low-stock {
  border-color: #fbbf24;
  background: #fffbeb;
}

.fuel-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.fuel-name {
  font-weight: 600;
  color: #111827;
}

.fuel-price {
  color: #10b981;
  font-weight: 600;
}

.fuel-stock {
  font-size: 0.875rem;
  color: #6b7280;
}

.fuel-stock.warning {
  color: #f59e0b;
  font-weight: 600;
}

/* Preset Buttons */
.preset-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.preset-btn {
  padding: 0.75rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  border-color: #10b981;
  background: #f0fdf4;
}

.preset-btn.active {
  border-color: #10b981;
  background: #10b981;
  color: white;
}

/* Input */
.input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  margin-bottom: 1rem;
}

.input:focus {
  outline: none;
  border-color: #10b981;
}

/* Price Breakdown */
.price-breakdown {
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  color: #6b7280;
}

.price-row.total {
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 2px solid #e5e7eb;
  font-size: 1.125rem;
  color: #111827;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.875rem;
}

/* Payment Methods */
.payment-methods {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.payment-method-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-method-card:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.payment-method-card:has(input:checked) {
  border-color: #10b981;
  background: #f0fdf4;
}

.payment-method-card input {
  display: none;
}

.method-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.method-icon {
  font-size: 2rem;
}

.method-icon.qr-icon {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.method-icon.qr-icon svg {
  width: 100%;
  height: 100%;
  color: #374151;
}

.payment-method-card:has(input:checked) .method-icon.qr-icon svg {
  color: #10b981;
}

.method-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  text-align: center;
}

/* Confirm Button */
.confirm-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.125rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.confirm-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

/* Processing Screen */
.processing-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.processing-animation {
  text-align: center;
}

.spinner {
  width: 80px;
  height: 80px;
  border: 6px solid #e5e7eb;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 2rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.processing-animation h3 {
  color: #111827;
  margin-bottom: 0.5rem;
}

.processing-animation p {
  color: #6b7280;
}

/* Refueling Screen */
.refueling-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.refueling-animation {
  text-align: center;
  width: 100%;
  max-width: 400px;
  padding: 2rem;
}

.fuel-pump-icon {
  font-size: 5rem;
  margin-bottom: 1.5rem;
  animation: pump 1.5s ease-in-out infinite;
}

@keyframes pump {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.refueling-animation h3 {
  color: #111827;
  margin-bottom: 2rem;
}

.progress-bar {
  width: 100%;
  height: 30px;
  background: #e5e7eb;
  border-radius: 15px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
  transition: width 0.05s linear;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: #10b981;
  margin: 0.5rem 0;
}

.liters-dispensed {
  font-size: 1.125rem;
  color: #6b7280;
}

/* Receipt Screen */
.receipt-screen {
  max-width: 500px;
  margin: 0 auto;
}

.success-animation {
  text-align: center;
  margin-bottom: 2rem;
}

.checkmark {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  color: white;
  margin: 0 auto 1rem;
  animation: scaleIn 0.5s ease;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
}

@keyframes scaleIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.success-animation h3 {
  color: #10b981;
  font-size: 1.5rem;
}

.receipt-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.receipt-header {
  text-align: center;
  margin-bottom: 1rem;
}

.receipt-header h3 {
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.transaction-id {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0.25rem 0;
  font-family: monospace;
}

.timestamp {
  font-size: 0.875rem;
  color: #9ca3af;
  margin: 0;
}

.receipt-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 1rem 0;
}

.receipt-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.receipt-row {
  display: flex;
  justify-content: space-between;
  color: #6b7280;
}

.receipt-row span:last-child {
  color: #111827;
  font-weight: 500;
}

.receipt-total {
  display: flex;
  justify-content: space-between;
  font-size: 1.25rem;
  color: #111827;
  padding-top: 0.5rem;
}

.receipt-total strong {
  color: #10b981;
  font-size: 1.5rem;
}

.receipt-actions {
  display: flex;
  gap: 0.75rem;
}

.download-btn, .finish-btn {
  flex: 1;
  padding: 1rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.download-btn {
  background: white;
  color: #10b981;
  border: 2px solid #10b981;
}

.download-btn:hover {
  background: #f0fdf4;
}

.finish-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.finish-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .payment-methods {
    grid-template-columns: 1fr;
  }

  .preset-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>