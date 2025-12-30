<template>
  <!-- Show login screen if not authenticated and not in guest mode -->
  <LoginScreen
    v-if="!user && !isGuestMode && !authLoading"
    @guest-mode="enableGuestMode"
  />

  <!-- Main App (shown for authenticated users or guests) -->
  <div v-else class="app">
    <header class="header-fixed">
      <div class="flex justify-between items-center w-full">
        <h1 class="text-2xl font-bold flex items-center gap-2">
          <img
            src="/pic/FuelDock-1_no_bg_s.png"
            alt="Logo"
            class="w-16 h-16 logo-clickable"
            @click="goToMapHome"
            title="Go to Map"
          />
          <span class="app-title">FuelDock Estonia</span>
          <span v-if="isGuestMode" class="guest-badge">Guest</span>
        </h1>

        <!-- Desktop Actions -->
        <div class="header-actions desktop-actions">
          <button
            @click="currentView = 'favorites'"
            class="favorites-btn"
            title="My Favorites"
          >
            ⭐
          </button>
          <button
            @click="currentView = 'history'"
            class="history-btn"
            title="Fuel History"
          >
            📋
          </button>
          <button
            v-if="currentView === 'map'"
            @click="toggleFilters"
            class="filters-btn"
            title="Filters"
          >
            🎚️
          </button>
          <button
            v-if="currentView === 'map'"
            @click="toggleMapType"
            class="map-type-btn-header"
            title="Map Type"
          >
            🗺️
          </button>
          <button
            v-if="isAdmin && !isGuestMode"
            @click="currentView = 'admin'"
            class="admin-btn"
            title="Admin Panel"
          >
            ⚙️
          </button>
          <button
            v-if="isGuestMode"
            @click="goToLogin"
            class="guest-login-btn"
            title="Login"
          >
            🔑 Login
          </button>
          <button
            v-if="user"
            @click="handleLogout"
            class="logout-btn"
            title="Logout"
          >
            ← Logout
          </button>
        </div>

        <!-- Mobile Hamburger Menu -->
        <button @click="showMobileMenu = !showMobileMenu" class="hamburger-btn mobile-only">
          ☰
        </button>
      </div>
    </header>

    <!-- Mobile Menu Slide-out (Outside header to escape stacking context) -->
    <div v-if="showMobileMenu" class="mobile-menu-overlay" @click="showMobileMenu = false">
      <div class="mobile-menu" @click.stop>
        <button
          @click="currentView = 'favorites'; showMobileMenu = false"
          class="mobile-menu-item"
          title="Favorites"
        >
          ⭐
        </button>
        <button
          @click="currentView = 'history'; showMobileMenu = false"
          class="mobile-menu-item"
          title="History"
        >
          📋
        </button>
        <button
          v-if="currentView === 'map'"
          @click="toggleFilters(); showMobileMenu = false"
          class="mobile-menu-item"
          title="Filters"
        >
          🎚️
        </button>
        <button
          v-if="currentView === 'map'"
          @click="toggleMapType(); showMobileMenu = false"
          class="mobile-menu-item"
          title="Map Type"
        >
          🗺️
        </button>
        <button
          v-if="isAdmin && !isGuestMode"
          @click="currentView = 'admin'; showMobileMenu = false"
          class="mobile-menu-item"
          title="Admin"
        >
          ⚙️
        </button>
        <button
          v-if="isGuestMode"
          @click="goToLogin(); showMobileMenu = false"
          class="mobile-menu-item login-item"
          title="Login"
        >
          🔑
        </button>
        <button
          v-if="user"
          @click="handleLogout(); showMobileMenu = false"
          class="mobile-menu-item logout-item"
          title="Logout"
        >
          ←
        </button>
      </div>
    </div>

    <main class="h-[calc(100vh-80px)]">
      <FavoritesScreen
        v-if="currentView === 'favorites'"
        @back="backToMap"
        @view-station="showStation"
        @show-on-map="showFavoritesOnMap"
      />

      <HistoryScreen
        v-else-if="currentView === 'history'"
        @back="backToMap"
      />

      <PaymentScreen
        v-else-if="currentView === 'payment'"
        :station="paymentStation"
        @back="backToMap"
        @complete="completePayment"
      />

      <AdminPanel
        v-else-if="currentView === 'admin'"
        @back="backToMap"
      />

      <MapView
        v-show="currentView === 'map'"
        ref="mapViewRef"
        :guest-mode="isGuestMode"
        :is-admin="isAdmin"
        :show-filters-from-parent="showFiltersPanel"
        :show-map-type-from-parent="showMapTypePanel"
        @station-click="showStation"
        @open-filters="showFiltersPanel = true"
        @close-filters="showFiltersPanel = false"
        @close-map-type="showMapTypePanel = false"
      />
    </main>

    <!-- Station Detail Modal Overlay -->
    <StationDetail
      v-if="selectedStation"
      :station="selectedStation"
      @back="backToMapFromStation"
      @pay="showPayment"
    />
  </div>

  <!-- Guest Login Prompt Modal -->
  <div v-if="showLoginPrompt" class="modal-overlay" @click="showLoginPrompt = false">
    <div class="login-prompt-modal" @click.stop>
      <div class="modal-icon">🔒</div>
      <h3>Login Required</h3>
      <p>Please login to see marina details and fuel information</p>
      <div class="modal-actions">
        <button @click="goToLogin" class="login-btn">
          Login / Sign Up
        </button>
        <button @click="showLoginPrompt = false" class="cancel-btn">
          Continue Browsing
        </button>
      </div>
    </div>
  </div>

  <!-- Initial Auth Loading -->
  <div v-if="authLoading" class="loading-screen">
    <img src="/pic/FuelDock-1_no_bg_s.png" alt="FuelDock" class="loading-logo" />
    <div class="progress-bar">
      <div class="progress-fill" :style="{width: progress + '%'}"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from './composables/useAuth'
import LoginScreen from './components/LoginScreen.vue'
import MapView from './components/MapView.vue'
import StationDetail from './components/StationDetail.vue'
import PaymentScreen from './components/PaymentScreen.vue'
import HistoryScreen from './components/HistoryScreen.vue'
import FavoritesScreen from './components/FavoritesScreen.vue'
import AdminPanel from './components/AdminPanel.vue'

const { user, loading: authLoading, isAdmin, checkUser, signOut, initAuthListener } = useAuth()

const progress = ref(0)
const currentView = ref('map')
const selectedStation = ref(null)
const paymentStation = ref(null)
const mapViewRef = ref(null)
const isGuestMode = ref(false)
const showLoginPrompt = ref(false)
const showFiltersPanel = ref(false)
const showMapTypePanel = ref(false)
const showMobileMenu = ref(false)

// Initialize auth
onMounted(async () => {
  // Start progress bar animation
  const interval = setInterval(() => {
    progress.value += 5
    if (progress.value >= 100) {
      clearInterval(interval)
    }
  }, 100)

  // Check authentication status (with built-in 2-second delay)
  await checkUser()
  initAuthListener()
})

function enableGuestMode() {
  isGuestMode.value = true
}

async function handleLogout() {
  try {
    await signOut()
    isGuestMode.value = false
    currentView.value = 'map'
    selectedStation.value = null
  } catch (error) {
    console.error('Logout error:', error)
  }
}

function showStation(station) {
  // Show station details for both authenticated users and guests
  if (station.hasStation) {
    selectedStation.value = station
  }
}

function goToLogin() {
  isGuestMode.value = false
  showLoginPrompt.value = false
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

  // Fix map rendering after switching views
  if (mapViewRef.value) {
    setTimeout(() => {
      mapViewRef.value.invalidateMapSize()
    }, 50)
  }
}

async function backToMapFromStation() {
  selectedStation.value = null
  // Restore the map view and refresh favorites when returning from station details
  if (mapViewRef.value) {
    setTimeout(async () => {
      mapViewRef.value.restoreMapView()
      await mapViewRef.value.refreshFavorites()
    }, 50)
  }
}

function completePayment(data) {
  const history = JSON.parse(localStorage.getItem('fuelHistory') || '[]')
  history.unshift({...data, date: new Date().toISOString()})
  localStorage.setItem('fuelHistory', JSON.stringify(history))
  backToMap()
}

async function showFavoritesOnMap(favorites) {
  currentView.value = 'map'
  // Wait for map to be visible, then refresh favorites
  if (mapViewRef.value) {
    setTimeout(async () => {
      await mapViewRef.value.refreshFavorites()
    }, 50)
  }
}

function toggleFilters() {
  showFiltersPanel.value = !showFiltersPanel.value
}

function toggleMapType() {
  showMapTypePanel.value = !showMapTypePanel.value
}

function goToMapHome() {
  currentView.value = 'map'
  selectedStation.value = null
  // Wait for map to be visible, then reset to default view with zoom out
  if (mapViewRef.value) {
    setTimeout(() => {
      mapViewRef.value.resetToDefaultView()
    }, 100)
  }
}
</script>

<style scoped>
.app {
  height: 100vh;
  overflow: hidden;
}

.header-fixed {
  position: relative;
  height: 80px;
  background: #1e40af;
  color: white;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  z-index: 100;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-clickable {
  cursor: pointer;
  transition: all 0.2s;
}

.logo-clickable:hover {
  transform: scale(1.1);
  opacity: 0.9;
}

.guest-badge {
  font-size: 0.875rem;
  padding: 0.25rem 0.75rem;
  background: rgba(251, 191, 36, 0.3);
  border: 1px solid rgba(251, 191, 36, 0.5);
  border-radius: 12px;
  font-weight: 600;
}

.favorites-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 2rem;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.favorites-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.history-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 2rem;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.filters-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 2rem;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.filters-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.map-type-btn-header {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 2rem;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-type-btn-header:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.admin-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 2rem;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.admin-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.logout-btn {
  padding: 0.75rem 1.25rem;
  background: rgba(239, 68, 68, 0.9);
  border: none;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 10;
  pointer-events: auto;
}

.logout-btn:hover {
  background: rgba(220, 38, 38, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.guest-login-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.guest-login-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

/* Guest Login Prompt Modal */
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

.login-btn {
  padding: 1rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.login-btn:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
}

.cancel-btn {
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

/* Mobile Responsive Styles */
.hamburger-btn {
  display: none;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 1.75rem;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  align-items: center;
  justify-content: center;
}

.hamburger-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.mobile-menu-overlay {
  position: fixed;
  top: 80px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  animation: fadeIn 0.2s ease;
  pointer-events: auto;
}

.mobile-menu {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(30, 64, 175, 0.98);
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  animation: slideDown 0.3s ease;
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
  pointer-events: auto;
  z-index: 10000;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.mobile-menu-item {
  width: 60px;
  height: 60px;
  padding: 0;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 10px;
  font-size: 2rem;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-menu-item:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.mobile-menu-item.login-item {
  background: rgba(16, 185, 129, 0.8);
  color: white;
}

.mobile-menu-item.login-item:hover {
  background: rgba(5, 150, 105, 0.9);
}

.mobile-menu-item.logout-item {
  background: rgba(239, 68, 68, 0.8);
  color: white;
}

.mobile-menu-item.logout-item:hover {
  background: rgba(220, 38, 38, 0.9);
}

/* Show hamburger and hide desktop actions on mobile */
@media (max-width: 768px) {
  .desktop-actions {
    display: none !important;
  }

  .hamburger-btn {
    display: flex;
  }

  .app-title {
    font-size: 1rem;
  }

  h1 img {
    width: 48px !important;
    height: 48px !important;
  }

  .guest-badge {
    font-size: 0.75rem;
    padding: 0.2rem 0.5rem;
  }
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