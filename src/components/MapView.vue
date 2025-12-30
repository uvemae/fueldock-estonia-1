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

    <!-- Active Filters Badge (Top Right) -->
    <div
      v-if="activeFiltersCount > 0"
      class="active-filters-badge"
      :class="{ 'admin-mode': EDIT_MODE && isAdmin && !guestMode }"
      title="Click to open filters"
      @click="emit('open-filters')"
    >
      Filters ({{ activeFiltersCount }})
    </div>

    <!-- Filter Panel (Slide from right) -->
    <div v-if="showFiltersFromParent" class="filter-overlay" @click="emit('close-filters')">
      <div class="filter-panel" @click.stop>
        <div class="filter-header">
          <h3>🎚️ Filters</h3>
          <button @click="emit('close-filters')" class="close-panel-btn">✕</button>
        </div>

        <div class="filter-content">
          <!-- Distance Filter -->
          <div class="filter-section">
            <h4>🎯 Distance</h4>
            <div class="filter-info">
              📍 From: Map Center (Live Updates)
            </div>
            <div class="radio-group">
              <label>
                <input type="radio" v-model="filters.distance" value="any" @change="onDistanceFilterChange" />
                Any distance
              </label>
              <label>
                <input type="radio" v-model="filters.distance" value="25" @change="onDistanceFilterChange" />
                Within 25 km
              </label>
              <label>
                <input type="radio" v-model="filters.distance" value="50" @change="onDistanceFilterChange" />
                Within 50 km
              </label>
              <label>
                <input type="radio" v-model="filters.distance" value="100" @change="onDistanceFilterChange" />
                Within 100 km
              </label>
              <label>
                <input type="radio" v-model="filters.distance" value="250" @change="onDistanceFilterChange" />
                Within 250 km
              </label>
            </div>
            <div class="filter-hint">
              💡 Pan/zoom the map to update the reference point
            </div>
          </div>

          <!-- Fuel Type Filter -->
          <div class="filter-section">
            <h4>⛽ Fuel Type</h4>
            <div class="checkbox-group">
              <label>
                <input type="checkbox" v-model="filters.fuelTypes" value="diesel" />
                Diesel
              </label>
              <label>
                <input type="checkbox" v-model="filters.fuelTypes" value="e95" />
                E95
              </label>
              <label>
                <input type="checkbox" v-model="filters.fuelTypes" value="e98" />
                E98
              </label>
            </div>
          </div>

          <!-- Price Range Filter -->
          <div class="filter-section">
            <h4>💰 Price Range</h4>
            <div class="price-range">
              <input
                type="range"
                v-model="filters.maxPrice"
                min="1.0"
                max="3.0"
                step="0.1"
                class="price-slider"
              />
              <div class="price-display">
                Max: {{ filters.maxPrice }}€/L
              </div>
            </div>
          </div>

          <!-- Fuel Level Filter -->
          <div class="filter-section">
            <h4>📊 Fuel Level</h4>
            <div class="checkbox-group">
              <label>
                <input type="checkbox" v-model="filters.fuelLevels" value="available" />
                Available (>20%)
              </label>
              <label>
                <input type="checkbox" v-model="filters.fuelLevels" value="low" />
                Low (<20%)
              </label>
              <label>
                <input type="checkbox" v-model="filters.fuelLevels" value="empty" />
                Empty (0%)
              </label>
            </div>
          </div>

          <!-- Provider Filter -->
          <div class="filter-section">
            <h4>🏢 Provider</h4>
            <div class="checkbox-group">
              <label>
                <input type="checkbox" v-model="filters.providers" value="Olerex" />
                Olerex
              </label>
              <label>
                <input type="checkbox" v-model="filters.providers" value="Circle K" />
                Circle K
              </label>
              <label>
                <input type="checkbox" v-model="filters.providers" value="Alexela" />
                Alexela
              </label>
              <label>
                <input type="checkbox" v-model="filters.providers" value="Other" />
                Other
              </label>
            </div>
          </div>

          <!-- Has Station Filter -->
          <div class="filter-section">
            <h4>⛽ Station Status</h4>
            <div class="checkbox-group">
              <label>
                <input type="checkbox" v-model="filters.hasStation" />
                Only show active fuel stations
              </label>
            </div>
          </div>
        </div>

        <div class="filter-actions">
          <button @click="clearAllFilters" class="clear-filters-btn">Clear All</button>
          <button @click="applyFilters" class="apply-filters-btn">
            Apply ({{ getFilteredCount() }})
          </button>
        </div>
      </div>
    </div>

    <!-- Map Type Panel (Slide from right) -->
    <div v-if="showMapTypeFromParent" class="filter-overlay" @click="emit('close-map-type')">
      <div class="map-type-panel" @click.stop>
        <div class="filter-header">
          <h3>🗺️ Map Type</h3>
          <button @click="emit('close-map-type')" class="close-panel-btn">✕</button>
        </div>

        <div class="map-type-content">
          <!-- Map Type Options -->
          <div class="map-type-options">
            <div
              @click="switchMapType('street')"
              class="map-type-option"
              :class="{ active: currentMapType === 'street' }"
            >
              <div class="map-type-icon">🛣️</div>
              <div class="map-type-info">
                <h4>Street Map</h4>
                <p>Standard OpenStreetMap view</p>
              </div>
              <div v-if="currentMapType === 'street'" class="active-indicator">✓</div>
            </div>

            <div
              @click="switchMapType('satellite')"
              class="map-type-option"
              :class="{ active: currentMapType === 'satellite' }"
            >
              <div class="map-type-icon">🛰️</div>
              <div class="map-type-info">
                <h4>Satellite</h4>
                <p>Aerial imagery view</p>
              </div>
              <div v-if="currentMapType === 'satellite'" class="active-indicator">✓</div>
            </div>

            <div
              @click="switchMapType('nautical')"
              class="map-type-option"
              :class="{ active: currentMapType === 'nautical' }"
            >
              <div class="map-type-icon">⚓</div>
              <div class="map-type-info">
                <h4>Nautical</h4>
                <p>Light nautical chart with sea marks</p>
              </div>
              <div v-if="currentMapType === 'nautical'" class="active-indicator">✓</div>
            </div>

            <div
              @click="switchMapType('nautical-dark')"
              class="map-type-option"
              :class="{ active: currentMapType === 'nautical-dark' }"
            >
              <div class="map-type-icon">🧭</div>
              <div class="map-type-info">
                <h4>Nautical+</h4>
                <p>Enhanced nautical with better contrast</p>
              </div>
              <div v-if="currentMapType === 'nautical-dark'" class="active-indicator">✓</div>
            </div>

            <div
              @click="switchMapType('terrain')"
              class="map-type-option"
              :class="{ active: currentMapType === 'terrain' }"
            >
              <div class="map-type-icon">⛰️</div>
              <div class="map-type-info">
                <h4>Terrain</h4>
                <p>Topographic map with elevation</p>
              </div>
              <div v-if="currentMapType === 'terrain'" class="active-indicator">✓</div>
            </div>
          </div>

          <!-- Sea Marks Toggle -->
          <div v-if="currentMapType !== 'nautical' && currentMapType !== 'nautical-dark'" class="sea-marks-toggle">
            <label class="toggle-label">
              <input type="checkbox" v-model="showSeaMarks" @change="toggleSeaMarks" />
              <span>Show Nautical Markers</span>
              <small>Overlay sea marks on current map</small>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- EDIT MODE BUTTONS (only visible for admins) -->
    <div v-if="EDIT_MODE && isAdmin && !guestMode" class="edit-buttons">
      <button
          @click="undoLastMove"
          :disabled="undoHistory.length === 0"
          class="undo-btn"
          title="Undo last marker move"
      >
        ↶
      </button>
      <button
          @click="redoLastMove"
          :disabled="redoHistory.length === 0"
          class="redo-btn"
          title="Redo last undone move"
      >
        ↷
      </button>
      <button
          @click="saveCoordinates"
          class="save-coordinates-btn"
          title="Save updated coordinates"
      >
        💾 Save Coordinates
      </button>
    </div>

    <div ref="mapRef" class="map"></div>

    <!-- Fixed Crosshair Overlay -->
    <div class="crosshair-overlay">
      <svg width="80" height="80" xmlns="http://www.w3.org/2000/svg">
        <line x1="40" y1="0" x2="40" y2="30" stroke="#6b7280" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="40" y1="80" x2="40" y2="50" stroke="#6b7280" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="0" y1="40" x2="30" y2="40" stroke="#6b7280" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="80" y1="40" x2="50" y2="40" stroke="#6b7280" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </div>

    <!-- Fixed Distance Circle Overlay -->
    <div v-if="filters.distance !== 'any' && circleRadiusPx > 0" class="circle-overlay">
      <svg :width="circleRadiusPx * 2" :height="circleRadiusPx * 2" xmlns="http://www.w3.org/2000/svg">
        <circle
          :cx="circleRadiusPx"
          :cy="circleRadiusPx"
          :r="circleRadiusPx"
          fill="#d1d5db"
          fill-opacity="0.15"
          stroke="#9ca3af"
          stroke-width="2"
          stroke-opacity="0.5"
        />
      </svg>
    </div>

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
import { useAuth } from '../composables/useAuth'
import { supabase } from '../supabase'

// EDIT MODE TOGGLE - SET TO false FOR PRODUCTION
const EDIT_MODE = true  // Toggle this to enable/disable dragging

const { user } = useAuth()

const props = defineProps({
  guestMode: {
    type: Boolean,
    default: false
  },
  isAdmin: {
    type: Boolean,
    default: false
  },
  showFiltersFromParent: {
    type: Boolean,
    default: false
  },
  showMapTypeFromParent: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['station-click', 'close-filters', 'close-map-type', 'open-filters'])

// Refs
const mapRef = ref(null)
const searchInput = ref(null)
const searchQuery = ref('')
const showDropdown = ref(false)
const selectedMarker = ref(null)
const saveNotification = ref('')
const lastDraggedStation = ref(null)
const userFavorites = ref([])
const circleRadiusPx = ref(0) // Pixel radius for CSS distance circle

// Undo/Redo history
const undoHistory = ref([])
const redoHistory = ref([])

// Filter - All options selected by default
const filters = ref({
  distance: 'any', // Will use map center as reference
  fuelTypes: ['diesel', 'e95', 'e98'], // All fuel types selected
  maxPrice: 3.0, // Max price
  fuelLevels: ['available', 'low', 'empty'], // All fuel levels selected
  providers: ['Olerex', 'Circle K', 'Alexela', 'Other'], // All providers selected
  hasStation: false // Show all stations (including empty ones)
})

// Map type
const currentMapType = ref('street')
const showSeaMarks = ref(false)

// Map related
let map = null
let markers = []
let markerLayerGroup = null
let coordinateDisplay = null
let baseLayers = {}
let currentBaseLayer = null
let seaMarksLayer = null

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

// Get user's current position for distance calculations
const userPosition = ref(null)
const isUsingGPS = ref(false)

// Filter & Sort Computed Properties
const activeFiltersCount = computed(() => {
  let count = 0
  if (filters.value.distance !== 'any') count++
  if (filters.value.fuelTypes.length > 0) count += filters.value.fuelTypes.length
  if (filters.value.maxPrice < 3.0) count++
  if (filters.value.fuelLevels.length > 0) count += filters.value.fuelLevels.length
  if (filters.value.providers.length > 0) count += filters.value.providers.length
  if (filters.value.hasStation) count++
  return count
})

const activeFiltersList = computed(() => {
  const list = []
  if (filters.value.distance !== 'any') {
    list.push({ label: `Distance <${filters.value.distance}km`, type: 'distance', value: 'any' })
  }
  filters.value.fuelTypes.forEach(fuel => {
    list.push({ label: fuel.toUpperCase(), type: 'fuelTypes', value: fuel })
  })
  if (filters.value.maxPrice < 3.0) {
    list.push({ label: `Price ≤${filters.value.maxPrice}€`, type: 'maxPrice', value: 3.0 })
  }
  filters.value.fuelLevels.forEach(level => {
    const labels = { available: 'Available >20%', low: 'Low <20%', empty: 'Empty' }
    list.push({ label: labels[level], type: 'fuelLevels', value: level })
  })
  filters.value.providers.forEach(provider => {
    list.push({ label: provider, type: 'providers', value: provider })
  })
  if (filters.value.hasStation) {
    list.push({ label: 'Active stations only', type: 'hasStation', value: false })
  }
  return list
})

const visibleStationsCount = computed(() => {
  return getFilteredAndSortedStations().length
})

const totalStationsCount = computed(() => {
  return updatedStations.length
})

// Lifecycle
onMounted(async () => {
  initializeMap()
  addAllMarkers()
  getUserLocation()
  await loadUserFavorites()

  // Apply filters initially with all options selected
  // console.log('🎯 Applying initial filters with all options selected')
  updateMarkersVisibility()

  // Add export function to window for console access
  if (EDIT_MODE) {
    window.exportStationCoordinates = () => {
      console.log('=== UPDATED STATION COORDINATES ===')
      console.log(JSON.stringify(updatedStations, null, 2))
      console.log('=== Copy the above JSON to update stations.json ===')
      return updatedStations
    }
    // console.log('%c📍 EDIT MODE ENABLED', 'color: red; font-size: 16px; font-weight: bold')
    // console.log('Drag markers to update positions.')
    // console.log('Click "Save Coordinates" button or run exportStationCoordinates() in console.')
  }
})

// Get user's location for distance calculations
// ALWAYS use map center as reference point for live updates
function getUserLocation() {
  // Force use of map center (not GPS) for live interactive distance filtering
  isUsingGPS.value = false
  updatePositionFromMapCenter()
  // console.log('📍 Distance filter reference: MAP CENTER (updates as you pan)')
}

// Update user position from current map center
function updatePositionFromMapCenter() {
  if (map) {
    const center = map.getCenter()
    userPosition.value = {
      lat: center.lat,
      lng: center.lng
    }
    // console.log('=== MAP CENTER UPDATE ===')
    // console.log('New userPosition:', userPosition.value)
    // console.log('Map zoom:', map.getZoom())
    // console.log('isUsingGPS:', isUsingGPS.value)
    // console.log('Distance filter:', filters.value.distance)
    // console.log('========================')
  } else {
    // If map not initialized yet, use Estonia center
    userPosition.value = { lat: 58.5953, lng: 25.0136 }
    // console.log('Map not initialized, using Estonia center:', userPosition.value)
  }
}

// Load user's favorites from Supabase or localStorage
async function loadUserFavorites() {
  // For guests, load from localStorage
  if (!user.value) {
    const guestFavorites = localStorage.getItem('guestFavorites')
    if (guestFavorites) {
      const favorites = JSON.parse(guestFavorites)
      userFavorites.value = favorites.map(f => f.station_id)
    }
    return
  }

  // For authenticated users, load from Supabase
  try {
    const { data, error } = await supabase
      .from('favorites')
      .select('station_id')
      .eq('user_id', user.value.id)

    if (error) {
      console.error('Error loading favorites:', error)
      return
    }

    userFavorites.value = data.map(f => f.station_id)
  } catch (error) {
    console.error('Error loading favorites:', error)
  }
}

// Check if a station is favorited
function isFavoriteStation(stationId) {
  return userFavorites.value.includes(stationId)
}

// Expose method to restore map view
function restoreMapView() {
  if (map && lastMapView.center && lastMapView.zoom) {
    map.setView(lastMapView.center, lastMapView.zoom, {
      animate: false
    })
  }
}

// Reset map to default view with zoom out
function resetToDefaultView() {
  if (map) {
    map.flyTo([58.5953, 25.0136], 7, {
      duration: 1.5
    })
    // Update saved view
    lastMapView.center = [58.5953, 25.0136]
    lastMapView.zoom = 7
  }
}

// Fix map size after view changes
function invalidateMapSize() {
  if (map) {
    map.invalidateSize()
  }
}

defineExpose({
  restoreMapView,
  invalidateMapSize,
  resetToDefaultView,
  refreshFavorites: async () => {
    await loadUserFavorites()
    addAllMarkers() // Redraw markers with updated favorite status
  }
})

// Map initialization
function initializeMap() {
  // Check if we have a saved view to restore
  const savedView = lastMapView.center && lastMapView.zoom
      ? [lastMapView.center, lastMapView.zoom]
      : [[58.5953, 25.0136], 7]

  map = L.map(mapRef.value).setView(savedView[0], savedView[1])

  // Create base layers
  baseLayers = {
    street: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }),
    satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: '© Esri',
      maxZoom: 19
    }),
    terrain: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenTopoMap',
      maxZoom: 17
    }),
    // CartoDB Voyager - better base for nautical overlay
    cartoVoyager: L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap, © CARTO',
      maxZoom: 19
    })
  }

  // OpenSeaMap overlay for nautical marks (can be toggled on any base layer)
  // Using updated tile server: t1.openseamap.org
  seaMarksLayer = L.tileLayer('https://t1.openseamap.org/seamark/{z}/{x}/{y}.png', {
    attribution: '© OpenSeaMap contributors',
    maxZoom: 18,
    transparent: true
  })

  // Add default layer (street)
  currentBaseLayer = baseLayers.street
  currentBaseLayer.addTo(map)

  markerLayerGroup = L.layerGroup().addTo(map)

  // Add coordinate display for authenticated users (not guests)
  if (!props.guestMode) {
    // Add red border to map container (only for admins in edit mode)
    if (EDIT_MODE && props.isAdmin) {
      mapRef.value.style.border = '4px solid red'
    }

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

  // Create distance circle (initially hidden)
  updateDistanceCircle()

  // Listen to map movement to update distance reference point LIVE
  // Update circle position and markers during panning for smooth fixed-to-center effect
  map.on('move', () => {
    updatePositionFromMapCenter()
    updateDistanceCircle()
    updateMarkersVisibility()
  })

  // Update circle radius during zoom animation for smooth scaling
  map.on('zoom', () => {
    updateDistanceCircle()
  })

  // Update markers after zoom completes
  map.on('zoomend', () => {
    // console.log('🔍 ZOOM END - Updating markers')
    updateMarkersVisibility()
  })
}

// Update distance circle radius in pixels (for CSS overlay)
function updateDistanceCircle() {
  if (!map || !userPosition.value) {
    circleRadiusPx.value = 0
    return
  }

  // If distance filter is active, calculate pixel radius
  if (filters.value.distance !== 'any') {
    const radiusKm = parseFloat(filters.value.distance)
    const radiusMeters = radiusKm * 1000

    // Get center point in container pixels
    const center = map.getCenter()
    const centerPoint = map.latLngToContainerPoint(center)

    // Calculate a point that's the desired distance away (going north for simplicity)
    const earthRadius = 6371000 // meters
    const lat = center.lat
    const lng = center.lng
    const latRadians = lat * Math.PI / 180

    // Calculate new latitude that's radiusMeters away
    const newLat = lat + (radiusMeters / earthRadius) * (180 / Math.PI)
    const edgePoint = map.latLngToContainerPoint([newLat, lng])

    // Distance in pixels
    const pixelRadius = Math.abs(edgePoint.y - centerPoint.y)
    circleRadiusPx.value = pixelRadius
  } else {
    circleRadiusPx.value = 0
  }
}

// Map type switching
function switchMapType(type) {
  if (!map) return

  // ALWAYS remove seamark layer first to prevent ordering issues
  if (map.hasLayer(seaMarksLayer)) {
    map.removeLayer(seaMarksLayer)
  }

  // Remove current base layer
  if (currentBaseLayer) {
    map.removeLayer(currentBaseLayer)
  }

  // For nautical views, use appropriate base map + seamarksLayer
  if (type === 'nautical') {
    // Light nautical - street base + seamark overlay
    currentBaseLayer = baseLayers.street
    currentBaseLayer.addTo(map)
    // Re-add seamark layer on top
    seaMarksLayer.addTo(map)
    showSeaMarks.value = true
  } else if (type === 'nautical-dark') {
    // Dark nautical - Voyager base + seamark overlay (better contrast)
    currentBaseLayer = baseLayers.cartoVoyager
    currentBaseLayer.addTo(map)
    // Re-add seamark layer on top
    seaMarksLayer.addTo(map)
    showSeaMarks.value = true
  } else {
    // For other types, use the selected base layer
    if (!baseLayers[type]) return

    currentBaseLayer = baseLayers[type]
    currentBaseLayer.addTo(map)

    // When switching away from nautical, disable sea marks
    showSeaMarks.value = false
    // Sea marks layer already removed at the top of function
  }

  currentMapType.value = type
  emit('close-map-type')
}

// Toggle sea marks overlay
function toggleSeaMarks() {
  showSeaMarks.value = !showSeaMarks.value

  if (showSeaMarks.value) {
    if (!map.hasLayer(seaMarksLayer)) {
      seaMarksLayer.addTo(map)
    }
  } else {
    if (map.hasLayer(seaMarksLayer)) {
      map.removeLayer(seaMarksLayer)
    }
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
  const isFavorite = isFavoriteStation(station.id)
  const icon = createColoredIcon(color, station === selectedMarker.value, isFavorite)

  const markerOptions = {
    icon,
    draggable: EDIT_MODE && props.isAdmin && !props.guestMode  // Enable dragging only for admins
  }

  // Add hand cursor for draggable markers
  if (EDIT_MODE && props.isAdmin && !props.guestMode) {
    markerOptions.autoPan = true
    markerOptions.autoPanPadding = [50, 50]
  }

  const marker = L.marker(station.coordinates, markerOptions)
      .on('click', () => handleMarkerClick(station))

  // Add drag handlers for edit mode (only for admins)
  if (EDIT_MODE && props.isAdmin && !props.guestMode) {
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
        // Store move in undo history
        const previousCoordinates = [...updatedStations[stationIndex].coordinates]
        const newCoordinates = [latlng.lat, latlng.lng]

        undoHistory.value.push({
          id: station.id,
          name: updatedStations[stationIndex].name,
          previousCoordinates: previousCoordinates,
          newCoordinates: newCoordinates
        })

        // Clear redo history when new action is performed
        redoHistory.value = []

        // Keep for backwards compatibility
        lastDraggedStation.value = {
          id: station.id,
          previousCoordinates: previousCoordinates,
          newCoordinates: newCoordinates
        }

        updatedStations[stationIndex].coordinates = newCoordinates

        // Also update the station reference in markers array
        const markerObj = markers.find(m => m.station.id === station.id)
        if (markerObj) {
          markerObj.station.coordinates = newCoordinates
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
        }, 5000)
      }
    })

    // Change cursor to hand for dragging (admin only)
    marker.on('mouseover', function(e) {
      mapRef.value.style.cursor = 'grab'
    })

    marker.on('mouseout', function(e) {
      mapRef.value.style.cursor = ''
    })
  }

  // Show coordinates on hover for all authenticated users (not guests)
  if (!props.guestMode) {
    marker.on('mouseover', function(e) {
      const latlng = e.target.getLatLng()
      const coordDiv = document.querySelector('.coordinate-display')
      if (coordDiv) {
        const currentStation = updatedStations.find(s => s.id === station.id)
        coordDiv.style.display = 'block'
        coordDiv.style.background = 'rgba(255, 255, 255, 0.95)'
        coordDiv.innerHTML = `
          <strong>${currentStation ? currentStation.name : station.name}</strong><br>
          Lat: ${latlng.lat.toFixed(6)}<br>
          Lng: ${latlng.lng.toFixed(6)}
        `
      }
    })

    marker.on('mouseout', function(e) {
      const coordDiv = document.querySelector('.coordinate-display')
      if (coordDiv) {
        coordDiv.style.display = 'none'
      }
    })
  }

  return marker
}

async function handleMarkerClick(station) {
  // Smooth fly-to animation from current zoom to target zoom over 2 seconds
  map.flyTo(station.coordinates, 14, {
    animate: true,
    duration: 2
  })

  // Wait for zoom animation (2s) + additional delay (0s) = 2s total
  await new Promise(resolve => setTimeout(resolve, 2000))

  // Save map view AFTER zoom animation completes
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

// Undo last marker move
function undoLastMove() {
  if (undoHistory.value.length === 0) return

  const lastMove = undoHistory.value.pop()
  const stationIndex = updatedStations.findIndex(s => s.id === lastMove.id)

  if (stationIndex !== -1) {
    // Store in redo history
    redoHistory.value.push(lastMove)

    // Restore previous coordinates
    updatedStations[stationIndex].coordinates = [...lastMove.previousCoordinates]

    // Update marker position
    const markerObj = markers.find(m => m.station.id === lastMove.id)
    if (markerObj) {
      markerObj.station.coordinates = [...lastMove.previousCoordinates]
      markerObj.marker.setLatLng(lastMove.previousCoordinates)
    }

    // Update lastDraggedStation for backwards compatibility
    if (undoHistory.value.length > 0) {
      lastDraggedStation.value = undoHistory.value[undoHistory.value.length - 1]
    } else {
      lastDraggedStation.value = null
    }

    // Show notification
    saveNotification.value = `↶ Undone: ${lastMove.name}`
    setTimeout(() => {
      saveNotification.value = ''
    }, 2000)
  }
}

// Redo last undone move
function redoLastMove() {
  if (redoHistory.value.length === 0) return

  const lastUndone = redoHistory.value.pop()
  const stationIndex = updatedStations.findIndex(s => s.id === lastUndone.id)

  if (stationIndex !== -1) {
    // Store back in undo history
    undoHistory.value.push(lastUndone)

    // Apply the new coordinates
    updatedStations[stationIndex].coordinates = [...lastUndone.newCoordinates]

    // Update marker position
    const markerObj = markers.find(m => m.station.id === lastUndone.id)
    if (markerObj) {
      markerObj.station.coordinates = [...lastUndone.newCoordinates]
      markerObj.marker.setLatLng(lastUndone.newCoordinates)
    }

    // Update lastDraggedStation
    lastDraggedStation.value = lastUndone

    // Show notification
    saveNotification.value = `↷ Redone: ${lastUndone.name}`
    setTimeout(() => {
      saveNotification.value = ''
    }, 2000)
  }
}

// Save coordinates function
async function saveCoordinates() {
  try {
    const response = await fetch('http://localhost:3001/api/save-stations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedStations)
    })

    const result = await response.json()

    if (result.success) {
      // Show success notification
      saveNotification.value = '✅ Saved! stations.json updated successfully'
      setTimeout(() => {
        saveNotification.value = ''
      }, 4000)

      // DON'T clear undo history after save - allow undo after saving
      // lastDraggedStation.value = null
      // undoHistory and redoHistory remain intact
    } else {
      throw new Error(result.message)
    }
  } catch (error) {
    console.error('Save error:', error)
    saveNotification.value = '❌ Error saving file. Is the save server running?'
    setTimeout(() => {
      saveNotification.value = ''
    }, 5000)
  }
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

async function selectStation(station) {
  searchQuery.value = station.name
  showDropdown.value = false
  selectedMarker.value = station

  // Smooth fly-to animation from current zoom to target zoom over 2 seconds
  map.flyTo(station.coordinates, 14, {
    animate: true,
    duration: 2
  })

  // Highlight selected marker
  updateMarkersVisibility()

  // Wait for zoom animation (2s) + additional delay (1s) = 3s total
  await new Promise(resolve => setTimeout(resolve, 3000))

  // Save map view AFTER zoom animation completes
  lastMapView.center = map.getCenter()
  lastMapView.zoom = map.getZoom()
  lastMapView.focusedStation = station

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
  const filteredStations = getFilteredAndSortedStations()
  const filteredIds = new Set(filteredStations.map(s => s.id))

  const query = searchQuery.value.toLowerCase()

  markers.forEach(({ marker, station }) => {
    // Check in updatedStations for current data
    const currentStation = updatedStations.find(s => s.id === station.id)

    // Check if matches search query
    const matchesSearch = !query ||
        (currentStation && (
            currentStation.name.toLowerCase().includes(query) ||
            currentStation.location.toLowerCase().includes(query)
        ))

    // Check if passes filters
    const passesFilters = filteredIds.has(station.id)

    // Hide filtered-out markers completely (opacity 0, not semi-transparent)
    marker.setOpacity(matchesSearch && passesFilters ? 1 : 0)
  })
}

// Filter & Sort Functions
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371 // Radius of Earth in km
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a =
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return R * c
}

function getFilteredAndSortedStations() {
  let stations = [...updatedStations]

  // Apply filters
  if (filters.value.hasStation) {
    stations = stations.filter(s => s.hasStation)
  }

  // Only apply provider filter if not all providers are selected
  const allProviders = ['Olerex', 'Circle K', 'Alexela', 'Other']
  const allProvidersSelected = allProviders.every(p => filters.value.providers.includes(p))

  if (filters.value.providers.length > 0 && !allProvidersSelected) {
    stations = stations.filter(s => {
      if (!s.stationType) return filters.value.providers.includes('Other')
      return filters.value.providers.includes(s.stationType)
    })
  }

  // Only apply fuel level filter if not all levels are selected
  const allFuelLevels = ['available', 'low', 'empty']
  const allLevelsSelected = allFuelLevels.every(level => filters.value.fuelLevels.includes(level))

  if (filters.value.fuelLevels.length > 0 && !allLevelsSelected) {
    stations = stations.filter(s => {
      if (filters.value.fuelLevels.includes('available') && s.fuelLevel >= 20) return true
      if (filters.value.fuelLevels.includes('low') && s.fuelLevel < 20 && s.fuelLevel > 0) return true
      if (filters.value.fuelLevels.includes('empty') && s.fuelLevel === 0) return true
      return false
    })
  }

  // Only apply fuel type filter if not all types are selected
  const allFuelTypes = ['diesel', 'e95', 'e98']
  const allTypesSelected = allFuelTypes.every(type => filters.value.fuelTypes.includes(type))

  if (filters.value.fuelTypes.length > 0 && !allTypesSelected) {
    stations = stations.filter(s => {
      if (!s.fuels) return false
      return filters.value.fuelTypes.some(type => s.fuels[type]?.available)
    })
  }

  if (filters.value.maxPrice < 3.0) {
    stations = stations.filter(s => {
      if (!s.fuels) return false
      const prices = Object.values(s.fuels).map(f => f.price).filter(p => p > 0)
      return prices.length > 0 && Math.min(...prices) <= filters.value.maxPrice
    })
  }

  if (filters.value.distance !== 'any' && userPosition.value) {
    const maxDist = parseFloat(filters.value.distance)
    // console.log(`📏 Filtering by distance: ${maxDist}km from`, userPosition.value)
    const originalCount = stations.length
    stations = stations.filter(s => {
      const dist = calculateDistance(
        userPosition.value.lat,
        userPosition.value.lng,
        s.coordinates[0],
        s.coordinates[1]
      )
      return dist <= maxDist
    })
    // console.log(`Filtered ${originalCount} stations → ${stations.length} within ${maxDist}km`)
  }

  // Sort by distance by default
  if (userPosition.value) {
    stations.sort((a, b) => {
      const distA = calculateDistance(
        userPosition.value.lat,
        userPosition.value.lng,
        a.coordinates[0],
        a.coordinates[1]
      )
      const distB = calculateDistance(
        userPosition.value.lat,
        userPosition.value.lng,
        b.coordinates[0],
        b.coordinates[1]
      )
      return distA - distB
    })
  }

  return stations
}

function getFilteredCount() {
  return getFilteredAndSortedStations().length
}

function applyFilters() {
  emit('close-filters')
  updateDistanceCircle()
  updateMarkersVisibility()
}

function clearAllFilters() {
  filters.value = {
    distance: 'any',
    fuelTypes: ['diesel', 'e95', 'e98'],
    maxPrice: 3.0,
    fuelLevels: ['available', 'low', 'empty'],
    providers: ['Olerex', 'Circle K', 'Alexela', 'Other'],
    hasStation: false
  }
  updateDistanceCircle()
  updateMarkersVisibility()
}

// Handle instant distance filter change
function onDistanceFilterChange() {
  // console.log('🔄 Distance filter changed to:', filters.value.distance)
  updateDistanceCircle()
  updateMarkersVisibility()
}

function removeFilter(type, value) {
  if (type === 'distance') {
    filters.value.distance = value
    onDistanceFilterChange()
  } else if (type === 'maxPrice') {
    filters.value.maxPrice = value
  } else if (type === 'hasStation') {
    filters.value.hasStation = value
  } else if (Array.isArray(filters.value[type])) {
    const index = filters.value[type].indexOf(value)
    if (index > -1) {
      filters.value[type].splice(index, 1)
    }
  }
  updateMarkersVisibility()
}

// Helper functions
function getMarkerColor(station) {
  // Show actual fuel station colors for all users (guests and authenticated)
  if (!station.hasStation) return 'red'
  if (station.fuelLevel === 0) return 'gray'
  if (station.fuelLevel < 20) return 'yellow'
  return 'green'
}

function createColoredIcon(color, isSelected = false, isFavorite = false) {
  const colors = {
    green: '#10b981',
    yellow: '#fbbf24',
    gray: '#9ca3af',
    red: '#ef4444',
    purple: '#a855f7'
  }

  // Red (no station) markers stay small (10px)
  // For all users: green, yellow, gray markers are bigger (15px)
  const baseSize = (color === 'red' ? 10 : 15)
  const size = isSelected ? baseSize + 40 : baseSize
  const borderWidth = isSelected ? 4 : 2

  // Heart badge for favorites (only show for authenticated non-guest users)
  const heartBadge = isFavorite && !props.guestMode ? `
    <div style="
      position: absolute;
      top: -6px;
      right: -6px;
      background: #ef4444;
      color: white;
      width: ${Math.max(16, size * 0.6)}px;
      height: ${Math.max(16, size * 0.6)}px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: ${Math.max(12, size * 0.5)}px;
      line-height: 1;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.5);
      z-index: 10;
    ">♥</div>
  ` : ''

  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="position: relative; width: ${size}px; height: ${size}px;">
        <div style="
          background: ${colors[color]};
          width: ${size}px;
          height: ${size}px;
          border-radius: 50%;
          border: ${borderWidth}px solid ${isSelected ? '#1e40af' : 'white'};
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        "></div>
        ${heartBadge}
      </div>
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

.crosshair-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 1400;
}

.circle-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 1300;
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

/* Filter Button */
.filter-btn {
  padding: 12px 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  height: 48px;
}

.filter-btn:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.filter-badge {
  background: #3b82f6;
  color: white;
  border-radius: 10px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 700;
}

/* Active Filters Badge (Top Right) */
.active-filters-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 999;
  background: white;
  padding: 8px 16px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  font-size: 14px;
  font-weight: 600;
  color: #1e40af;
  border: 2px solid #1e40af;
  cursor: pointer;
  transition: all 0.2s;
}

.active-filters-badge:hover {
  background: #1e40af;
  color: white;
  transform: scale(1.05);
}

/* Adjust position when admin buttons are visible */
.active-filters-badge.admin-mode {
  top: 70px;
}

.active-filters-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: #eff6ff;
  color: #1e40af;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.chip-remove {
  background: none;
  border: none;
  color: #1e40af;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  margin-left: 2px;
  transition: color 0.2s;
}

.chip-remove:hover {
  color: #ef4444;
}

.clear-all-btn {
  padding: 4px 10px;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-all-btn:hover {
  background: #fecaca;
}

/* Results Counter */
.results-counter {
  position: absolute;
  top: 110px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 998;
  background: #10b981;
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

/* Filter Panel */
.filter-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

.filter-panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  max-width: 400px;
  background: white;
  box-shadow: -4px 0 16px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.filter-header {
  padding: 1.5rem;
  border-bottom: 2px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f9fafb;
}

.filter-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #111827;
}

.close-panel-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.2s;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-panel-btn:hover {
  color: #111827;
}

.filter-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.filter-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.filter-section:last-child {
  border-bottom: none;
}

.filter-section h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #111827;
  font-weight: 600;
}

.filter-info {
  background: #dbeafe;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #1e40af;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.filter-hint {
  background: #fef3c7;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.8rem;
  color: #92400e;
  margin-top: 0.75rem;
  font-weight: 500;
  font-style: italic;
}

.radio-group, .checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-group label, .checkbox-group label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.radio-group input[type="radio"],
.checkbox-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.price-range {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.price-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.price-display {
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: #10b981;
  padding: 8px;
  background: #d1fae5;
  border-radius: 8px;
}

.filter-actions {
  padding: 1rem 1.5rem;
  border-top: 2px solid #e5e7eb;
  display: flex;
  gap: 10px;
  background: #f9fafb;
}

.clear-filters-btn {
  flex: 1;
  padding: 12px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.clear-filters-btn:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}

.apply-filters-btn {
  flex: 2;
  padding: 12px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.apply-filters-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

/* EDIT MODE BUTTONS */
.edit-buttons {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
  display: flex;
  gap: 8px;
  align-items: center;
}

/* UNDO BUTTON */
.undo-btn {
  width: 48px;
  height: 48px;
  padding: 0;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 24px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.undo-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.6);
  transform: translateY(-2px);
}

.undo-btn:disabled {
  background: #d1d5db;
  box-shadow: none;
  cursor: not-allowed;
  opacity: 0.5;
}

/* REDO BUTTON */
.redo-btn {
  width: 48px;
  height: 48px;
  padding: 0;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 24px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.redo-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.6);
  transform: translateY(-2px);
}

.redo-btn:disabled {
  background: #d1d5db;
  box-shadow: none;
  cursor: not-allowed;
  opacity: 0.5;
}

/* SAVE COORDINATES BUTTON */
.save-coordinates-btn {
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
  transform: translateY(-2px);
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
  position: absolute;
  top: 68px;
  right: 10px;
  z-index: 2000;
  padding: 12px 20px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
  animation: slideDown 0.3s ease;
  max-width: 300px;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
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

/* Map Type Button */
.map-type-btn {
  padding: 12px 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  height: 48px;
}

.map-type-btn:hover {
  border-color: #1e40af;
  background: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.15);
}

/* Map Type Panel */
.map-type-panel {
  background: white;
  width: 400px;
  height: 100vh;
  position: fixed;
  right: 0;
  top: 0;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.2);
  animation: slideInRight 0.3s ease;
  display: flex;
  flex-direction: column;
  z-index: 1001;
}

.map-type-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.map-type-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.map-type-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.map-type-option:hover {
  background: #f0f9ff;
  border-color: #3b82f6;
  transform: translateX(-4px);
}

.map-type-option.active {
  background: #dbeafe;
  border-color: #1e40af;
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.15);
}

.map-type-icon {
  font-size: 2.5rem;
  line-height: 1;
}

.map-type-info {
  flex: 1;
}

.map-type-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1.125rem;
  color: #111827;
}

.map-type-info p {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.active-indicator {
  font-size: 1.5rem;
  color: #10b981;
  font-weight: 700;
}

/* Sea Marks Toggle */
.sea-marks-toggle {
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 12px;
  border: 2px solid #e5e7eb;
}

.toggle-label {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  cursor: pointer;
}

.toggle-label input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
  margin-right: 0.5rem;
}

.toggle-label span {
  font-weight: 600;
  color: #111827;
  display: flex;
  align-items: center;
  font-size: 1rem;
}

.toggle-label small {
  color: #6b7280;
  font-size: 0.875rem;
  margin-left: 28px;
}
</style>