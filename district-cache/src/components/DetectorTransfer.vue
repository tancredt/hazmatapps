<template>
  <div class="swap-screen">
    <HomeHeader />
    <h2>Update Detector Location</h2>
    
    <div class="form-container">
      <!-- Detector Label -->
      <div class="form-group">
        <label>Detector Label (e.g. PGM123)</label>
        <input 
          type="text" 
          v-model="detectorLabel" 
          class="form-input"
          placeholder="Enter detector label..."
          :disabled="isProcessing"
        />
      </div>

      <!-- Destination -->
      <div class="form-group">
        <label>Select Destination</label>
        <select v-model="destination" class="form-input" :disabled="isProcessing" @change="onDestinationChange">
          <option value="">-- Select Destination --</option>
          <option value="BURNLEY">Burnley repair/calibration</option>
          <option value="DISTRICT_CACHE">District Cache</option>
          <option value="STATION">Fire Station</option>
        </select>
      </div>

      <!-- District (Conditional) -->
      <div v-if="destination === 'DISTRICT_CACHE' || destination === 'STATION'" class="form-group">
        <label>Select District</label>
        <select v-model="selectedDistrict" class="form-input" :disabled="isProcessing || isLoadingDistricts" @change="onDistrictChange">
          <option value="">-- Select District --</option>
          <option v-for="d in districts" :key="d.value" :value="d.value">{{ d.label }}</option>
        </select>
      </div>

      <!-- Fire Station (Conditional) -->
      <div v-if="destination === 'STATION'" class="form-group">
        <label>Select Fire Station</label>
        <select v-model="selectedStation" class="form-input" :disabled="isProcessing || isLoadingStations || !selectedDistrict">
          <option value="">-- Select Fire Station --</option>
          <option v-for="s in stations" :key="s.id" :value="s.label">{{ s.label }}</option>
        </select>
        <div v-if="isLoadingStations" class="loading-inline">Loading stations...</div>
      </div>

      <!-- Action Buttons -->
      <div class="action-bar">
        <button class="btn-cancel" @click="handleCancel" :disabled="isProcessing">Cancel</button>
        <button class="btn-primary" @click="handleSubmit" :disabled="isSubmitDisabled || isProcessing">
          {{ isProcessing ? 'Processing...' : 'Submit' }}
        </button>
      </div>
    </div>

    <!-- Error Modal -->
    <div v-if="showErrorModal" class="modal-overlay" @click.self="showErrorModal = false">
      <div class="modal-content">
        <h3>Detector Not Found</h3>
        <p>{{ errorMessage }}</p>
        <div class="modal-actions">
          <button class="btn-confirm" @click="showErrorModal = false">OK</button>
        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Success</h3>
        <p>Detector location and status have been updated successfully.</p>
        <div class="modal-actions">
          <button class="btn-confirm" @click="closeSuccessModal">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '@/utils/api'
import HomeHeader from './HomeHeader.vue'

const router = useRouter()

// --- State ---
const detectorLabel = ref('')
const destination = ref('')
const selectedDistrict = ref('')
const selectedStation = ref('')

const districts = ref([])
const stations = ref([])

const isLoadingDistricts = ref(false)
const isLoadingStations = ref(false)
const isProcessing = ref(false)

const showErrorModal = ref(false)
const showSuccessModal = ref(false)
const errorMessage = ref('')

// --- Computed ---
const isSubmitDisabled = computed(() => {
  if (!detectorLabel.value.trim()) return true
  if (!destination.value) return true
  if ((destination.value === 'DISTRICT_CACHE' || destination.value === 'STATION') && !selectedDistrict.value) return true
  if (destination.value === 'STATION' && !selectedStation.value) return true
  return false
})

// --- Methods ---
const fetchDistricts = async () => {
  isLoadingDistricts.value = true
  try {
    const data = await apiFetch('/districts/')
    districts.value = data
  } catch (err) {
    console.error('Failed to fetch districts', err)
  } finally {
    isLoadingDistricts.value = false
  }
}

const fetchStations = async () => {
  if (!selectedDistrict.value) {
    stations.value = []
    return
  }
  isLoadingStations.value = true
  selectedStation.value = '' // Reset station when district changes
  try {
    const data = await apiFetch(`/locations/?location_type=ST&district=${encodeURIComponent(selectedDistrict.value)}`)
    stations.value = data
  } catch (err) {
    console.error('Failed to fetch stations', err)
  } finally {
    isLoadingStations.value = false
  }
}

const onDestinationChange = () => {
  selectedDistrict.value = ''
  selectedStation.value = ''
  stations.value = []
}

const onDistrictChange = () => {
  selectedStation.value = ''
  if (destination.value === 'STATION') {
    fetchStations()
  }
}

const handleCancel = () => {
  router.back()
}

// Helper to safely find exact matches since backend uses icontains
const findExactLocation = (results, matchFn) => {
  return results.find(matchFn) || null
}

const handleSubmit = async () => {
  if (isSubmitDisabled.value) return
  isProcessing.value = true
  errorMessage.value = ''

  try {
    // 1. Check if detector exists (case-insensitive exact match)
    const inputLabel = detectorLabel.value.trim()
    const searchResults = await apiFetch(`/detector-labels/?label=${encodeURIComponent(inputLabel)}`)
    
    // The backend uses icontains, so we filter for exact case-insensitive match on frontend
    const matchedDetector = searchResults.find(d => d.label.toUpperCase() === inputLabel.toUpperCase())

    if (!matchedDetector) {
      errorMessage.value = "No record of this detector exists. Check the spelling and if it still fails, email the Hazmat Unit with the label and destination."
      showErrorModal.value = true
      isProcessing.value = false
      return
    }

    // 2. Resolve Target Location ID & Status
    let targetLocationId = null
    let targetStatus = ''

    if (destination.value === 'BURNLEY') {
      const res = await apiFetch(`/locations/?label=Burnley`)
      const loc = findExactLocation(res, l => l.label.toUpperCase() === 'BURNLEY')
      targetLocationId = loc?.id
      targetStatus = 'OF' // OFFLINE
    } 
    else if (destination.value === 'DISTRICT_CACHE') {
      const res = await apiFetch(`/locations/?location_type=DI&district=${encodeURIComponent(selectedDistrict.value)}`)
      const loc = findExactLocation(res, l => l.location_type === 'DI' && l.district?.toUpperCase() === selectedDistrict.value.toUpperCase())
      targetLocationId = loc?.id
      targetStatus = 'IS' // INSTOCK
    } 
    else if (destination.value === 'STATION') {
      const res = await apiFetch(`/locations/?label=${encodeURIComponent(selectedStation.value)}&location_type=ST`)
      const loc = findExactLocation(res, l => l.label.toUpperCase() === selectedStation.value.toUpperCase() && l.location_type === 'ST')
      targetLocationId = loc?.id
      targetStatus = 'OP' // OPERATIONAL
    }

    if (!targetLocationId) {
      throw new Error("Could not resolve the destination location in the database.")
    }

    // 3. Execute Update
    const payload = [{
      detector_id: matchedDetector.id,
      location_id: targetLocationId,
      status: targetStatus
    }]

    await apiFetch('/detectors/update-location-status/', {
      method: 'POST',
      body: JSON.stringify(payload)
    })

    showSuccessModal.value = true

  } catch (err) {
    console.error('Update failed:', err)
    errorMessage.value = err.message || 'An unexpected error occurred. Please try again.'
    showErrorModal.value = true
  } finally {
    isProcessing.value = false
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  // Reset form for next use
  detectorLabel.value = ''
  destination.value = ''
  selectedDistrict.value = ''
  selectedStation.value = ''
  stations.value = []
}

// --- Lifecycle ---
onMounted(() => {
  fetchDistricts()
})
</script>

<style scoped>
.form-container {
  max-width: 600px;
  margin: 0 auto;
  background: #f8f9fa;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #dee2e6;
  text-align: left;
}
.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  font-size: 0.95rem;
}
.form-input {
  width: 100%;
  padding: 10px 12px;
  font-size: 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #fff;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.form-input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}
.form-input:disabled {
  background: #e9ecef;
  cursor: not-allowed;
}
.loading-inline {
  font-size: 0.85rem;
  color: #666;
  margin-top: 6px;
  font-style: italic;
}
.action-bar {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 30px;
}
.action-bar .btn-cancel, .action-bar .btn-primary {
  flex: 0 1 auto;
  min-width: 120px;
}
</style>