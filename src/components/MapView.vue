<template>
  <div class="map-container">
    <div class="search-container">
      <div class="search-bar">
        <input
            ref="searchInput"
            v-model="searchQuery"
            @input="handleSearchInput"
            @focus="showDropdown = true"
            @blur="handleSearchBlur"
            placeholder="🔍 Search marina..."
            class="search-input"
        />

        <!-- Live dropdown results -->
        <div v-if="showDropdown && filteredStations.length > 0" class="search-dropdown">
          <div
              v-for="station in filteredStations"
              :key="station.id"
              @mousedown="selectStation(station)"
              class="dropdown-item"
              :class="{ 'has-fuel': station.hasStation }"
          >
            <div class="dropdown-item-content">
              <div class="station-name">{{ station.name }}</div>
              <div class="station-meta">
                <span class="station-location">{{ station.location }}</span>
                <span v-if="station.hasStation" class="fuel-indicator" :class="getFuelStatusClass(station)">
                  {{ getFuelStatusText(station) }}
                </span>
                <span v-else class="no-fuel-indicator">No fuel</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Clear button when search has text -->
      <button
          v-if="searchQuery"
          @click="clearSearch"
          class="clear-button"
          title="Clear search"
      >
        ✕
      </button>
    </div>

    <div ref="mapRef" class="map"></div>

    <div class="legend">
      <div><span class="dot green"></span> Fuel >20%</div>
      <div><span class="dot yellow"></span> Fuel <20%</div>
      <div><span class="dot red"></span> No station</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import L from 'leaflet'
import stationsData from '../data/stations.json'

const emit = defineEmits(['station-click'])

// Refs
const mapRef = ref(null)
const searchInput = ref(null)
const searchQuery = ref('')
const showDropdown = ref(false)
const selectedMarker = ref(null)

// Map related
let map = null
let markers = []
let markerLayerGroup = null

// Computed
const filteredStations = computed(() => {
  if (!searchQuery.value) return []

  const query = searchQuery.value.toLowerCase()
  return stationsData
      .filter(station =>
          station.name.toLowerCase().includes(query) ||
          station.location.toLowerCase().includes(query)
      )
      .slice(0, 8) // Limit dropdown results for better UX
})

// Lifecycle
onMounted(() => {
  initializeMap()
  addAllMarkers()
})

// Map initialization
function initializeMap() {
  map = L.map(mapRef.value).setView([58.5953, 25.0136], 7)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map)

  markerLayerGroup = L.layerGroup().addTo(map)
}

// Marker management
function addAllMarkers() {
  clearMarkers()

  stationsData.forEach(station => {
    const marker = createMarker(station)
    markers.push({ marker, station })
    markerLayerGroup.addLayer(marker)
  })
}

function createMarker(station) {
  const color = getMarkerColor(station)
  const icon = createColoredIcon(color, station === selectedMarker.value)

  return L.marker(station.coordinates, { icon })
      .on('click', () => handleMarkerClick(station))
}

function handleMarkerClick(station) {
  if (station.hasStation) {
    emit('station-click', station)
  } else {
    // Show popup for stations without fuel
    const marker = markers.find(m => m.station.id === station.id)?.marker
    if (marker) {
      marker.bindPopup(`
        <div style="text-align: center;">
          <b>${station.name}</b><br>
          <span style="color: #ef4444;">No fuel station available</span>
        </div>
      `).openPopup()
    }
  }
}

function clearMarkers() {
  if (markerLayerGroup) {
    markerLayerGroup.clearLayers()
  }
  markers = []
}

// Search functionality
function handleSearchInput() {
  showDropdown.value = true

  // Update map markers to highlight search results
  if (searchQuery.value) {
    updateMarkersVisibility()
  } else {
    // Reset all markers to visible when search is cleared
    markers.forEach(({ marker }) => {
      marker.setOpacity(1)
    })
  }
}

function handleSearchBlur() {
  // Delay to allow click on dropdown items
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

function selectStation(station) {
  searchQuery.value = station.name
  showDropdown.value = false
  selectedMarker.value = station

  // Center map on selected station
  map.setView(station.coordinates, 12, {
    animate: true,
    duration: 0.5
  })

  // Highlight selected marker
  updateMarkersVisibility()

  // Find and open popup for selected station
  const markerObj = markers.find(m => m.station.id === station.id)
  if (markerObj) {
    // Create popup content based on station type
    if (station.hasStation) {
      emit('station-click', station)
    } else {
      markerObj.marker.bindPopup(`
        <div style="text-align: center;">
          <b>${station.name}</b><br>
          <span style="color: #ef4444;">No fuel station available</span>
        </div>
      `).openPopup()
    }
  }
}

function clearSearch() {
  searchQuery.value = ''
  selectedMarker.value = null
  showDropdown.value = false

  // Reset all markers
  markers.forEach(({ marker }) => {
    marker.setOpacity(1)
  })

  // Reset map view
  map.setView([58.5953, 25.0136], 7, {
    animate: true,
    duration: 0.5
  })
}

function updateMarkersVisibility() {
  const query = searchQuery.value.toLowerCase()

  markers.forEach(({ marker, station }) => {
    const matches = !query ||
        station.name.toLowerCase().includes(query) ||
        station.location.toLowerCase().includes(query)

    marker.setOpacity(matches ? 1 : 0.3)
  })
}

// Helper functions
function getMarkerColor(station) {
  if (!station.hasStation) return 'red'
  if (station.fuelLevel === 0) return 'gray'
  if (station.fuelLevel < 20) return 'yellow'
  return 'green'
}

function createColoredIcon(color, isSelected = false) {
  const colors = {
    green: '#10b981',
    yellow: '#fbbf24',
    gray: '#9ca3af',
    red: '#ef4444'
  }

  const baseSize = color === 'red' ? 10 : 20
  const size = isSelected ? baseSize + 4 : baseSize
  const borderWidth = isSelected ? 4 : 2

  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        background: ${colors[color]};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        border: ${borderWidth}px solid ${isSelected ? '#1e40af' : 'white'};
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      "></div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2]
  })
}

function getFuelStatusClass(station) {
  if (station.fuelLevel === 0) return 'fuel-empty'
  if (station.fuelLevel < 20) return 'fuel-low'
  return 'fuel-good'
}

function getFuelStatusText(station) {
  if (station.fuelLevel === 0) return 'Empty'
  if (station.fuelLevel < 20) return `${station.fuelLevel}% Low`
  return `${station.fuelLevel}%`
}
</script>

<style scoped>
.map-container {
  position: relative;
  height: 100%;
}

.search-container {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: 90%;
  max-width: 450px;
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.search-bar {
  flex: 1;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.clear-button {
  margin-top: 12px;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: white;
  color: #6b7280;
  font-size: 18px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.2s;
}

.clear-button:hover {
  background: #f3f4f6;
  color: #374151;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
}

.dropdown-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: #f9fafb;
}

.dropdown-item.has-fuel:hover {
  background: #f0f9ff;
}

.dropdown-item-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.station-name {
  font-weight: 600;
  color: #111827;
  font-size: 15px;
}

.station-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.station-location {
  color: #6b7280;
}

.fuel-indicator {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 11px;
}

.fuel-good {
  background: #d1fae5;
  color: #065f46;
}

.fuel-low {
  background: #fed7aa;
  color: #92400e;
}

.fuel-empty {
  background: #fee2e2;
  color: #991b1b;
}

.no-fuel-indicator {
  color: #ef4444;
  font-weight: 500;
}

.map {
  height: 100%;
  width: 100%;
}

.legend {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 1000;
}

.legend div {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 6px 0;
  font-size: 14px;
  color: #374151;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.dot.green { background: #10b981; }
.dot.yellow { background: #fbbf24; }
.dot.red { background: #ef4444; }

/* Custom marker animation */
.custom-marker {
  transition: all 0.3s ease;
}

/* Scrollbar styling for dropdown */
.search-dropdown::-webkit-scrollbar {
  width: 6px;
}

.search-dropdown::-webkit-scrollbar-track {
  background: #f9fafb;
  border-radius: 3px;
}

.search-dropdown::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.search-dropdown::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>