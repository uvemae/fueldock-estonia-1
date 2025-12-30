<template>
  <div class="favorites-container">
    <header class="favorites-header">
      <button @click="$emit('back')" class="back-btn">← Back to Map</button>
      <h2>⭐ My Favorites</h2>
    </header>

    <div class="favorites-content">
      <div v-if="favorites.length === 0" class="empty-state">
        <div class="empty-icon">⭐</div>
        <h3>No Favorites Yet</h3>
        <p>Start adding marinas to your favorites from the map!</p>
        <button @click="$emit('back')" class="browse-btn">
          Browse Marinas
        </button>
      </div>

      <div v-else class="favorites-list">
        <div class="favorites-actions">
          <button @click="showAllOnMap" class="show-all-btn">
            📍 Show All on Map
          </button>
          <div class="sort-options">
            <label>Sort by:</label>
            <select v-model="sortBy" class="sort-select">
              <option value="distance">Distance</option>
              <option value="name">Name</option>
              <option value="fuelLevel">Fuel Level</option>
              <option value="dateAdded">Recently Added</option>
            </select>
          </div>
        </div>

        <div class="favorite-cards">
          <div
            v-for="favorite in sortedFavorites"
            :key="favorite.id"
            class="favorite-card"
          >
            <div class="card-header">
              <h3>{{ favorite.name }}</h3>
              <div class="card-badges">
                <span class="fuel-badge" :class="getFuelBadgeClass(favorite)">
                  {{ getFuelBadgeText(favorite) }}
                </span>
              </div>
            </div>

            <div class="card-body">
              <div class="info-row">
                <span class="icon">📍</span>
                <span>{{ favorite.location }}</span>
              </div>
              <div class="info-row">
                <span class="icon">⛽</span>
                <span>{{ favorite.station_type }}</span>
              </div>
              <div class="info-row" v-if="favorite.distance">
                <span class="icon">🗺️</span>
                <span>{{ favorite.distance }} km away</span>
              </div>
              <div class="info-row">
                <span class="icon">💰</span>
                <span>{{ getLowestPrice(favorite) }}</span>
              </div>
            </div>

            <div class="card-notes" v-if="favorite.notes">
              <div class="notes-label">📝 My Notes:</div>
              <div class="notes-text">{{ favorite.notes }}</div>
            </div>

            <div class="card-tags" v-if="favorite.tags && favorite.tags.length > 0">
              <span v-for="tag in favorite.tags" :key="tag" class="tag">
                {{ tag }}
              </span>
            </div>

            <div class="card-actions">
              <button @click="viewStation(favorite)" class="action-btn view-btn">
                👁️ View
              </button>
              <button @click="openEditNotesModal(favorite)" class="action-btn edit-btn">
                ✏️ Edit Notes
              </button>
              <button @click="removeFavorite(favorite)" class="action-btn remove-btn">
                🗑️ Remove
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Notes Modal -->
    <div v-if="editingFavorite" class="modal-overlay" @click="editingFavorite = null">
      <div class="modal-content" @click.stop>
        <h3>✏️ Edit Notes</h3>
        <p class="modal-subtitle">{{ editingFavorite.name }}</p>

        <div class="form-group">
          <label>📝 Personal Notes</label>
          <textarea
            v-model="editNotes"
            placeholder="Add your personal notes about this marina..."
            rows="4"
            class="notes-textarea"
          ></textarea>
        </div>

        <div class="form-group">
          <label>🏷️ Tags</label>
          <div class="tags-input">
            <input
              v-model="newTag"
              @keyup.enter="addTag"
              placeholder="Add a tag and press Enter"
              class="tag-input"
            />
          </div>
          <div class="current-tags" v-if="editTags.length > 0">
            <span v-for="(tag, index) in editTags" :key="index" class="edit-tag">
              {{ tag }}
              <button @click="removeTag(index)" class="remove-tag-btn">✕</button>
            </span>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="editingFavorite = null" class="cancel-btn">Cancel</button>
          <button @click="saveNotes" class="save-btn">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { supabase } from '../supabase'
import { useAuth } from '../composables/useAuth'

const { user } = useAuth()
const emit = defineEmits(['back', 'view-station', 'show-on-map'])

const favorites = ref([])
const sortBy = ref('distance')
const editingFavorite = ref(null)
const editNotes = ref('')
const editTags = ref([])
const newTag = ref('')
const userPosition = ref(null)

onMounted(async () => {
  await loadFavorites()
  getUserLocation()
})

function getUserLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        userPosition.value = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        }
        calculateDistances()
      },
      () => {
        userPosition.value = { lat: 58.9, lng: 25.0136 }
        calculateDistances()
      }
    )
  }
}

function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a =
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return (R * c).toFixed(1)
}

function calculateDistances() {
  if (!userPosition.value) return

  favorites.value.forEach(fav => {
    fav.distance = calculateDistance(
      userPosition.value.lat,
      userPosition.value.lng,
      fav.coordinates[0],
      fav.coordinates[1]
    )
  })
}

async function loadFavorites() {
  // For guests, load from localStorage
  if (!user.value) {
    const guestFavorites = localStorage.getItem('guestFavorites')
    favorites.value = guestFavorites ? JSON.parse(guestFavorites) : []
    return
  }

  // For authenticated users, load from Supabase
  const { data, error } = await supabase
    .from('favorites')
    .select('*')
    .eq('user_id', user.value.id)

  if (error) {
    console.error('Error loading favorites:', error)
  } else {
    favorites.value = data || []
  }
}

const sortedFavorites = computed(() => {
  const sorted = [...favorites.value]

  if (sortBy.value === 'distance') {
    sorted.sort((a, b) => parseFloat(a.distance || 999) - parseFloat(b.distance || 999))
  } else if (sortBy.value === 'name') {
    sorted.sort((a, b) => a.name.localeCompare(b.name))
  } else if (sortBy.value === 'fuelLevel') {
    sorted.sort((a, b) => (b.fuel_level || 0) - (a.fuel_level || 0))
  } else if (sortBy.value === 'dateAdded') {
    sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }

  return sorted
})

function getFuelBadgeClass(favorite) {
  if (favorite.fuel_level === 0) return 'fuel-empty'
  if (favorite.fuel_level < 20) return 'fuel-low'
  return 'fuel-good'
}

function getFuelBadgeText(favorite) {
  if (favorite.fuel_level === 0) return 'Empty'
  if (favorite.fuel_level < 20) return `${favorite.fuel_level}% Low`
  return `${favorite.fuel_level}%`
}

function getLowestPrice(favorite) {
  if (!favorite.fuels) return 'N/A'
  const prices = Object.values(favorite.fuels)
    .map(f => f.price)
    .filter(p => p > 0)
  if (prices.length === 0) return 'N/A'
  return `From ${Math.min(...prices).toFixed(2)}€/L`
}

function viewStation(favorite) {
  emit('view-station', favorite)
}

function showAllOnMap() {
  emit('show-on-map', favorites.value)
}

function openEditNotesModal(favorite) {
  editingFavorite.value = favorite
  editNotes.value = favorite.notes || ''
  editTags.value = favorite.tags || []
}

function addTag() {
  if (newTag.value.trim() && !editTags.value.includes(newTag.value.trim())) {
    editTags.value.push(newTag.value.trim())
    newTag.value = ''
  }
}

function removeTag(index) {
  editTags.value.splice(index, 1)
}

async function saveNotes() {
  const index = favorites.value.findIndex(f => f.id === editingFavorite.value.id)
  if (index !== -1) {
    favorites.value[index].notes = editNotes.value
    favorites.value[index].tags = editTags.value
  }

  // For guests, save to localStorage
  if (!user.value) {
    localStorage.setItem('guestFavorites', JSON.stringify(favorites.value))
    editingFavorite.value = null
    return
  }

  // For authenticated users, save to Supabase
  const { error } = await supabase
    .from('favorites')
    .update({
      notes: editNotes.value,
      tags: editTags.value
    })
    .eq('id', editingFavorite.value.id)
    .eq('user_id', user.value.id)

  if (error) {
    console.error('Error saving notes:', error)
  } else {
    editingFavorite.value = null
  }
}

async function removeFavorite(favorite) {
  if (!confirm(`Remove ${favorite.name} from favorites?`)) return

  favorites.value = favorites.value.filter(f => f.id !== favorite.id)

  // For guests, save to localStorage
  if (!user.value) {
    localStorage.setItem('guestFavorites', JSON.stringify(favorites.value))
    return
  }

  // For authenticated users, delete from Supabase
  const { error } = await supabase
    .from('favorites')
    .delete()
    .eq('id', favorite.id)
    .eq('user_id', user.value.id)

  if (error) {
    console.error('Error removing favorite:', error)
  }
}
</script>

<style scoped>
.favorites-container {
  height: 100%;
  background: #f9fafb;
  overflow-y: auto;
}

.favorites-header {
  background: white;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.favorites-header h2 {
  margin: 0;
  color: #111827;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: #e5e7eb;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #d1d5db;
}

.favorites-content {
  padding: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 2rem;
}

.browse-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.browse-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.favorites-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.show-all-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.show-all-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-options label {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
}

.sort-select {
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.favorite-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.favorite-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  border: 2px solid transparent;
}

.favorite-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: #fbbf24;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-header h3 {
  margin: 0;
  color: #111827;
  font-size: 1.125rem;
}

.card-badges {
  display: flex;
  gap: 0.5rem;
}

.fuel-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
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

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #374151;
}

.info-row .icon {
  font-size: 1rem;
}

.card-notes {
  background: #f9fafb;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.notes-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.notes-text {
  font-size: 0.875rem;
  color: #374151;
  line-height: 1.5;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tag {
  padding: 0.25rem 0.75rem;
  background: #eff6ff;
  color: #1e40af;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn {
  background: #dbeafe;
  color: #1e40af;
}

.view-btn:hover {
  background: #bfdbfe;
}

.edit-btn {
  background: #fef3c7;
  color: #92400e;
}

.edit-btn:hover {
  background: #fde68a;
}

.remove-btn {
  background: #fee2e2;
  color: #dc2626;
}

.remove-btn:hover {
  background: #fecaca;
}

/* Modal Styles */
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
  z-index: 2000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.modal-subtitle {
  margin: 0 0 1.5rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #374151;
}

.notes-textarea,
.tag-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
}

.notes-textarea:focus,
.tag-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.current-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.edit-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: #eff6ff;
  color: #1e40af;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.remove-tag-btn {
  background: none;
  border: none;
  color: #1e40af;
  cursor: pointer;
  font-size: 1rem;
  padding: 0;
}

.remove-tag-btn:hover {
  color: #ef4444;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.cancel-btn,
.save-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #e5e7eb;
  color: #374151;
}

.cancel-btn:hover {
  background: #d1d5db;
}

.save-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}
</style>
