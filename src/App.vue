<template>
  <div class="app">
    <header class="header-fixed">
      <div class="flex justify-between items-center w-full">
        <h1 class="text-2xl font-bold flex items-center gap-2">
          <img src="/pic/FuelDock-1_no_bg_s.png" alt="Logo" class="w-16 h-16" />
          FuelDock Estonia
        </h1>
        <button @click="currentView = 'history'" class="text-6xl leading-none">📋</button>
      </div>
    </header>

    <main class="h-[calc(100vh-80px)]">
      <HistoryScreen v-if="currentView === 'history'"
                     @back="backToMap" />

      <PaymentScreen v-else-if="currentView === 'payment'"
                     :station="paymentStation"
                     @back="backToMap"
                     @complete="completePayment" />

      <StationDetail v-else-if="selectedStation"
                     :station="selectedStation"
                     @back="backToMapFromStation"
                     @pay="showPayment" />

      <MapView v-show="!selectedStation && currentView === 'map'"
               ref="mapViewRef"
               @station-click="showStation" />
    </main>
  </div>

  <div v-if="loading" class="loading-screen">
    <img src="/pic/FuelDock-1_no_bg_s.png" alt="FuelDock" class="loading-logo" />
    <div class="progress-bar">
      <div class="progress-fill" :style="{width: progress + '%'}"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MapView from './components/MapView.vue'
import StationDetail from './components/StationDetail.vue'
import PaymentScreen from './components/PaymentScreen.vue'
import HistoryScreen from './components/HistoryScreen.vue'

const loading = ref(true)
const progress = ref(0)
const currentView = ref('map')
const selectedStation = ref(null)
const paymentStation = ref(null)
const mapViewRef = ref(null)

// Loading animation
onMounted(() => {
  const interval = setInterval(() => {
    progress.value += 5
    if (progress.value >= 100) {
      clearInterval(interval)
      setTimeout(() => {
        loading.value = false
      }, 100)
    }
  }, 100)
})

function showStation(station) {
  if (station.hasStation) {
    selectedStation.value = station
  }
}

function showPayment(station) {
  paymentStation.value = station
  currentView.value = 'payment'
  selectedStation.value = null
}

function backToMap() {
  currentView.value = 'map'
  selectedStation.value = null
  paymentStation.value = null
}

function backToMapFromStation() {
  selectedStation.value = null
  // Restore the map view when returning from station details
  if (mapViewRef.value) {
    // Use nextTick to ensure MapView is visible before restoring
    setTimeout(() => {
      mapViewRef.value.restoreMapView()
    }, 50)
  }
}

function completePayment(data) {
  const history = JSON.parse(localStorage.getItem('fuelHistory') || '[]')
  history.unshift({...data, date: new Date().toISOString()})
  localStorage.setItem('fuelHistory', JSON.stringify(history))
  backToMap()
}
</script>

<style scoped>
.app {
  height: 100vh;
  overflow: hidden;
}

.header-fixed {
  height: 80px;
  background: #1e40af;
  color: white;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
}

/* FIX: Set as a fixed, high-z-index overlay */
.loading-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100vh;

  /* OVERLAY STYLES */
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.7);
}

.loading-logo {
  width: 200px;
  height: auto;
  margin-bottom: 2rem;
}

.progress-bar {
  width: 300px;
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #10b981;
  border-radius: 6px;
  transition: width 0.1s linear;
}
</style>