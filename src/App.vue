<template>
  <div class="app">
    <header class="header-fixed">
      <div class="flex justify-between items-center w-full">
        <h1 class="text-2xl font-bold">FuelDock Estonia</h1>
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
                     @back="selectedStation = null"
                     @pay="showPayment" />

      <MapView v-else @station-click="showStation" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MapView from './components/MapView.vue'
import StationDetail from './components/StationDetail.vue'
import PaymentScreen from './components/PaymentScreen.vue'
import HistoryScreen from './components/HistoryScreen.vue'

const currentView = ref('map')
const selectedStation = ref(null)
const paymentStation = ref(null)

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
</style>