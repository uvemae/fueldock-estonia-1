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

    <!-- SAVE COORDINATES BUTTON (only visible in EDIT_MODE) -->
    <button
        v-if="EDIT_MODE"
        @click="saveCoordinates"
        class="save-coordinates-btn"
        title="Save updated coordinates"
    >
      💾 Save Coordinates
    </button>

    <div ref="mapRef" class="map"></div>

    <div class="legend">
      <div><span class="dot green"></span> Fuel >20%</div>
      <div><span class="dot yellow"></span> Fuel <20%</div>
      <div><span class="dot red"></span> No station</div>
    </div>

    <!-- SAVE NOTIFICATION -->
    <div v-if="saveNotification" class="save-notification">
      {{ saveNotification }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import L from 'leaflet'
import stationsData from '../data/stations.json'

// EDIT MODE TOGGLE - SET TO false FOR PRODUCTION
const EDIT_MODE = true  // Toggle this to enable/disable dragging

const emit = defineEmits(['station-click'])

// Refs
const mapRef = ref(null)
const searchInput = ref(null)
const searchQuery = ref('')
const showDropdown = ref(false)
const selectedMarker = ref(null)
const saveNotification = ref('')

// Map related
let map = null
let markers = []
let markerLayerGroup = null
let coordinateDisplay = null

// Store updated positions
let updatedStations = JSON.parse(JSON.stringify(stationsData))

// Store last map view for persistence
let lastMapView = {
  center: null,
  zoom: null,
  focusedStation: null
}

// Computed
const filteredStations = computed(() => {
  if (!searchQuery.value) return []

  const query = searchQuery.value.toLowerCase()
  // Use updatedStations for search results too
  return updatedStations
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

  // Add export function to window for console access
  if (EDIT_MODE) {
    window.exportStationCoordinates = () => {
      console.log('=== UPDATED STATION COORDINATES ===')
      console.log(JSON.stringify(updatedStations, null, 2))
      console.log('=== Copy the above JSON to update stations.json ===')
      return updatedStations
    }
    console.log('%c📍 EDIT MODE ENABLED', 'color: red; font-size: 16px; font-weight: bold')
    console.log('Drag markers to update positions.')
    console.log('Click "Save Coordinates" button or run exportStationCoordinates() in console.')
  }
})

// Expose method to restore map view
function restoreMapView() {
  if (map && lastMapView.center && lastMapView.zoom) {
    map.setView(lastMapView.center, lastMapView.zoom, {
      animate: false
    })
  }
}

defineExpose({
  restoreMapView
})

// Map initialization
function initializeMap() {
  // Check if we have a saved view to restore
  const savedView = lastMapView.center && lastMapView.zoom
      ? [lastMapView.center, lastMapView.zoom]
      : [[58.5953, 25.0136], 7]

  map = L.map(mapRef.value).setView(savedView[0], savedView[1])

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map)

  markerLayerGroup = L.layerGroup().addTo(map)

  // Add coordinate display for edit mode
  if (EDIT_MODE) {
    // Add red border to map container
    mapRef.value.style.border = '4px solid red'

    // Create coordinate display overlay
    coordinateDisplay = L.control({ position: 'bottomleft' })
    coordinateDisplay.onAdd = function() {
      const div = L.DomUtil.create('div', 'coordinate-display')
      div.style.cssText = `
        background: rgba(255, 255, 255, 0.95);
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-family: monospace;
        font-size: 14px;
        display: none;
      `
      div.innerHTML = 'Drag a marker to see coordinates'
      return div
    }
    coordinateDisplay.addTo(map)
  }
}

// Marker management
function addAllMarkers() {
  clearMarkers()

  // Use updatedStations instead of stationsData to preserve dragged positions
  updatedStations.forEach(station => {
    const marker = createMarker(station)
    markers.push({ marker, station })
    markerLayerGroup.addLayer(marker)
  })
}

function createMarker(station) {
  const color = getMarkerColor(station)
  const icon = createColoredIcon(color, station === selectedMarker.value)

  const markerOptions = {
    icon,
    draggable: EDIT_MODE  // Enable dragging in edit mode
  }

  // Add hand cursor for draggable markers
  if (EDIT_MODE) {
    markerOptions.autoPan = true
    markerOptions.autoPanPadding = [50, 50]
  }

  const marker = L.marker(station.coordinates, markerOptions)
      .on('click', () => handleMarkerClick(station))

  // Add drag handlers for edit mode
  if (EDIT_MODE) {
    marker.on('dragstart', function(e) {
      const coordDiv = document.querySelector('.coordinate-display')
      if (coordDiv) {
        coordDiv.style.display = 'block'
        coordDiv.style.background = 'rgba(255, 255, 100, 0.95)'
        const currentStation = updatedStations.find(s => s.id === station.id)
        coordDiv.innerHTML = `
          <strong>Dragging: ${currentStation ? currentStation.name : station.name}</strong><br>
          Original: [${station.coordinates[0].toFixed(6)}, ${station.coordinates[1].toFixed(6)}]
        `
      }
    })

    marker.on('drag', function(e) {
      const latlng = e.target.getLatLng()
      const coordDiv = document.querySelector('.coordinate-display')
      if (coordDiv) {
        // Find the station in updatedStations to show its name
        const currentStation = updatedStations.find(s => s.id === station.id)
        coordDiv.innerHTML = `
          <strong>${currentStation ? currentStation.name : station.name}</strong><br>
          Lat: ${latlng.lat.toFixed(6)}<br>
          Lng: ${latlng.lng.toFixed(6)}
        `
      }
    })

    marker.on('dragend', function(e) {
      const latlng = e.target.getLatLng()
      // Update the station data in updatedStations
      const stationIndex = updatedStations.findIndex(s => s.id === station.id)
      if (stationIndex !== -1) {
        updatedStations[stationIndex].coordinates = [latlng.lat, latlng.lng]

        // Also update the station reference in markers array
        const markerObj = markers.find(m => m.station.id === station.id)
        if (markerObj) {
          markerObj.station.coordinates = [latlng.lat, latlng.lng]
        }
      }

      const coordDiv = document.querySelector('.coordinate-display')
      if (coordDiv) {
        const currentStation = updatedStations[stationIndex]
        coordDiv.style.background = 'rgba(16, 185, 129, 0.95)'
        coordDiv.innerHTML = `
          <strong>${currentStation ? currentStation.name : station.name}</strong><br>
          ✅ Updated: [${latlng.lat.toFixed(6)}, ${latlng.lng.toFixed(6)}]<br>
          <small>Click "Save Coordinates" button</small>
        `
        setTimeout(() => {
          coordDiv.style.display = 'none'
          coordDiv.style.background = 'rgba(255, 255, 255, 0.95)'
        }, 3000)
      }
    })

    // Change cursor to hand
    marker.on('mouseover', function(e) {
      mapRef.value.style.cursor = 'grab'
    })

    marker.on('mouseout', function(e) {
      mapRef.value.style.cursor = ''
    })
  }

  return marker
}

function handleMarkerClick(station) {
  // Save current map view before opening station details
  lastMapView.center = map.getCenter()
  lastMapView.zoom = map.getZoom()
  lastMapView.focusedStation = station

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

// Save coordinates function
function saveCoordinates() {
  const jsonContent = JSON.stringify(updatedStations, null, 2)
  const blob = new Blob([jsonContent], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'stations.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  // Show notification
  saveNotification.value = '✅ stations.json downloaded! Replace the file in src/data/'
  setTimeout(() => {
    saveNotification.value = ''
  }, 4000)
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

  // Save the view we're about to set
  lastMapView.center = station.coordinates
  lastMapView.zoom = 12
  lastMapView.focusedStation = station

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

  // Don't reset map view if we have a saved focused station
  if (!lastMapView.focusedStation) {
    // Only reset to default view if no station was previously focused
    map.setView([58.5953, 25.0136], 7, {
      animate: true,
      duration: 0.5
    })
  }
}

function updateMarkersVisibility() {
  const query = searchQuery.value.toLowerCase()

  markers.forEach(({ marker, station }) => {
    // Check in updatedStations for current data
    const currentStation = updatedStations.find(s => s.id === station.id)
    const matches = !query ||
        (currentStation && (
            currentStation.name.toLowerCase().includes(query) ||
            currentStation.location.toLowerCase().includes(query)
        ))

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

/* SAVE COORDINATES BUTTON */
.save-coordinates-btn {
  position: absolute;
  top: 70px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  padding: 12px 24px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  transition: all 0.3s;
  animation: pulse-save 2s infinite;
}

.save-coordinates-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.6);
  transform: translateX(-50%) translateY(-2px);
}

@keyframes pulse-save {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  }
  50% {
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.7);
  }
}

/* SAVE NOTIFICATION */
.save-notification {
  position: fixed;
  top: 140px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
  padding: 16px 32px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
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