<template>
  <div class="map-container">
    <div class="search-bar">
      <input v-model="searchQuery" @input="filterMarkers"
             placeholder="🔍 Search marina..."
             class="w-full p-3 rounded-lg border shadow-lg" />
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
import { ref, onMounted } from 'vue'
import L from 'leaflet'
import stationsData from '../data/stations.json'

const emit = defineEmits(['station-click'])
const mapRef = ref(null)
const searchQuery = ref('')
let map = null
let markers = []

onMounted(() => {
  map = L.map(mapRef.value).setView([58.5953, 25.0136], 7)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map)

  addMarkers(stationsData)
})

function addMarkers(stations) {
  // Clear existing markers
  markers.forEach(m => map.removeLayer(m))
  markers = []

  stations.forEach(station => {
    const color = getMarkerColor(station)
    const icon = createColoredIcon(color)

    const marker = L.marker(station.coordinates, { icon })
        .addTo(map)
        .on('click', () => {
          if (station.hasStation) {
            emit('station-click', station)  // Open detail page
          } else {
            marker.bindPopup(`<b>${station.name}</b><br>No fuel station`).openPopup()
          }
        })

    markers.push(marker)
  })
}

function getMarkerColor(station) {
  if (!station.hasStation) return 'red'
  if (station.fuelLevel === 0) return 'gray'
  if (station.fuelLevel < 20) return 'yellow'
  return 'green'
}

function createColoredIcon(color) {
  const colors = {
    green: '#10b981',
    yellow: '#fbbf24',
    gray: '#9ca3af',
    red: '#ef4444'
  }

  const size = color === 'red' ? 10 : 20

  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background: ${colors[color]}; width: ${size}px; height: ${size}px;
           border-radius: 50%; border: 2px solid white;"></div>`,
    iconSize: [size, size]
  })
}

function filterMarkers() {
  const query = searchQuery.value.toLowerCase()
  if (!query) {
    addMarkers(stationsData)
    return
  }

  const filtered = stationsData.filter(s =>
      s.name.toLowerCase().includes(query) ||
      s.location.toLowerCase().includes(query)
  )

  addMarkers(filtered)

  if (filtered.length > 0) {
    map.setView(filtered[0].coordinates, 10)
  }
}
</script>

<style scoped>
.map-container {
  position: relative;
  height: 100%;
}

.search-bar {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: 90%;
  max-width: 400px;
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
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  z-index: 1000;
}

.legend div {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 4px 0;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.green { background: #10b981; }
.dot.yellow { background: #fbbf24; }
.dot.gray { background: #9ca3af; }
.dot.red { background: #ef4444; }
</style>