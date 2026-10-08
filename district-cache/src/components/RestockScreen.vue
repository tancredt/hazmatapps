<template>
  <div class="swap-screen">
    <HomeHeader />
    <h2>FRV - District Cache Restock</h2>
    <h3>{{ district }}</h3>
    <div class="model-selector">
      <label>Detector Model:</label>
      <select v-model="selectedModelId" @change="handleModelChange">
        <option v-for="model in models" :key="model.id" :value="model.id">{{ model.label }}</option>
      </select>
    </div>
    <div v-if="isLoading" class="loading">Loading equipment...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="!isLoading && !error">
      <!-- ================= DISTRICT CACHE SUMMARY ================= -->
      <div class="cache-summary">
        <div class="summary-hero">
          <span class="hero-number" :class="{ 'hero-negative': availableSlots <= 0 }">{{ availableSlots }}</span>
          <span class="hero-label">Slots Available</span>
        </div>
        <div class="summary-details">
          <div class="summary-item">
            <span class="summary-value">{{ slotCount }}</span>
            <span class="summary-label">Total detector slots</span>
          </div>
          <div class="summary-item">
            <span class="summary-value">{{ cacheDetectors.length }}</span>
            <span class="summary-label">Detectors in cache</span>
          </div>
          <div class="summary-item">
            <span class="summary-value">{{ transitDetectors.length }}</span>
            <span class="summary-label">Detectors in transit</span>
          </div>
        </div>
      </div>
      
      <!-- ================= SLOT GRID ================= -->
      <div v-if="slotCount > 0" class="location-section" style="margin-top: 20px;">
        <h3>District Cache Slots (Current)</h3>
        <div class="slots-grid">
          <div
            v-for="i in slotCount"
            :key="'slot-' + i"
            class="slot-rectangle"
            :class="{ empty: !slottedDetectors[i-1], transit: slottedDetectors[i-1]?.isTransit }"
          >
            <template v-if="slottedDetectors[i-1]">
              <span class="slot-label">{{ slottedDetectors[i-1].label }}</span>
              <span v-if="slottedDetectors[i-1].isTransit" class="transit-badge">In Transit</span>
            </template>
            <template v-else>
              Empty
            </template>
          </div>
        </div>
        <!-- Overflow -->
        <div v-if="overflowDetectors.length > 0" class="overflow-area">
          <h4>Overflow ({{ overflowDetectors.length }})</h4>
          <div class="overflow-list">
            <div
              v-for="det in overflowDetectors"
              :key="'ov-' + det.id"
              class="overflow-item"
              :class="{ 'transit-item': det.isTransit }"
            >
              {{ det.label }}
              <span v-if="det.isTransit" class="transit-badge-small">In Transit</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= BURNLEY SELECTION SECTION ================= -->
      <div v-if="availableSlots > 0" class="location-section" style="margin-top: 20px;">
        <h3>Available at Burnley <span class="take-info">You can take {{ availableSlots }} detector{{ availableSlots !== 1 ? 's' : '' }}</span></h3>
        <p class="section-subtitle">Select detectors to add to the cache ({{ selectedCount }} selected)</p>
        <div v-if="burnleyDetectors.length > 0" class="overflow-list" style="margin-top: 15px;">
          <div 
            v-for="det in burnleyDetectors" 
            :key="'burnley-' + det.id" 
            class="overflow-item" 
            :class="{ selected: selectedBurnleyIds.includes(det.id) }" 
            @click="toggleBurnleySelection(det.id)"
          >
            {{ det.label }}
          </div>
        </div>
        <p v-else class="empty-text">No available detectors at Burnley.</p>
      </div>

      <div v-if="availableSlots <= 0" class="no-space-message" style="margin-top: 20px;">
        <p>No available slots in this district cache for the selected detector model.</p>
      </div>

      <div v-if="availableSlots > 0" class="action-bar">
        <button 
          class="btn-primary" 
          @click="attemptAddToCache" 
          :disabled="isProcessing || isLoading || !!error || selectedCount === 0"
        >
          {{ isProcessing ? 'Adding...' : `Add to Cache (${selectedCount})` }}
        </button>
      </div>
    </div>

    <!-- Modals -->
    <div v-if="showWarningModal" class="modal-overlay">
      <div class="modal-content warning-modal">
        <div class="warning-icon">⚠️</div>
        <h3>Cache Capacity Exceeded</h3>
        <p>You have selected {{ selectedCount }} detector(s), but adding them would bring the total to {{ totalDetectors + selectedCount }} which exceeds the {{ slotCount }} available slots.</p>
        <div class="modal-actions">
          <button class="btn-danger" @click="showWarningModal = false">OK</button>
        </div>
      </div>
    </div>

    <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
      <div class="modal-content">
        <h3>Confirm Restock</h3>
        <p>You have selected {{ selectedCount }} detector(s) to transfer to the {{ district }} district cache.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showConfirmModal = false" :disabled="isProcessing">Cancel</button>
          <button class="btn-confirm" @click="executeRestock" :disabled="isProcessing">{{ isProcessing ? 'Transferring...' : 'Confirm' }}</button>
        </div>
      </div>
    </div>

    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Success</h3>
        <p>{{ selectedCount }} detector(s) have been transferred to the district cache.</p>
        <div class="modal-actions">
          <button class="btn-confirm" @click="closeSuccessModal">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '@/utils/api'
import HomeHeader from './HomeHeader.vue'

const props = defineProps({ district: String })

// --- State ---
const models = ref([])
const selectedModelId = ref(null)
const district = ref('')
const slotCount = ref(0)
const cacheDetectors = ref([])
const transitDetectors = ref([])
const burnleyDetectors = ref([])
const selectedBurnleyIds = ref([])
const isLoading = ref(false)
const error = ref(null)

const isProcessing = ref(false)
const showWarningModal = ref(false)
const showConfirmModal = ref(false)
const showSuccessModal = ref(false)

// --- Computed ---
const totalDetectors = computed(() => cacheDetectors.value.length + transitDetectors.value.length)
const availableSlots = computed(() => slotCount.value - totalDetectors.value)
const selectedCount = computed(() => selectedBurnleyIds.value.length)
const hasSpace = computed(() => selectedCount.value <= availableSlots.value)

const allDistrictDetectors = computed(() => {
  const cached = cacheDetectors.value.map(d => ({ ...d, isTransit: false }))
  const transit = transitDetectors.value.map(d => ({ ...d, isTransit: true }))
  return [...cached, ...transit]
})

const slottedDetectors = computed(() => allDistrictDetectors.value.slice(0, slotCount.value))
const overflowDetectors = computed(() => allDistrictDetectors.value.slice(slotCount.value))

// --- Methods ---
const fetchModels = async () => {
  try {
    const data = await apiFetch('/detectormodels/')
    models.value = data
    const microRae = data.find(m => m.label === 'MicroRAE')
    selectedModelId.value = microRae?.id || data[0]?.id
  } catch (err) { console.error('Failed to fetch models:', err) }
}

const fetchSlotCount = async () => {
  if (!district.value || !selectedModelId.value) return
  try {
    const diLocations = await apiFetch(`/locations/?location_type=DI&district=${encodeURIComponent(district.value)}`)
    if (!diLocations || diLocations.length === 0) {
      slotCount.value = 0
      return
    }
    const slotPromises = diLocations.map(loc =>
      apiFetch(`/locationdetectorslots/?location=${loc.id}&detector_model=${selectedModelId.value}`)
    )
    const allSlots = await Promise.all(slotPromises)
    slotCount.value = allSlots.reduce((sum, slots) => sum + (slots?.length || 0), 0)
  } catch (err) { 
    console.error('Failed to fetch slot count:', err)
    slotCount.value = 0 
  }
}

const fetchCacheAndTransit = async () => {
  if (!district.value || !selectedModelId.value) return
  isLoading.value = true
  error.value = null
  try {
    const [cacheData, transitData] = await Promise.all([
      apiFetch(`/detector-labels/?location__location_type=DI&location__district=${encodeURIComponent(district.value)}&detector_model=${selectedModelId.value}`),
      apiFetch(`/detector-labels/?status=TR&detector_model=${selectedModelId.value}&location__district=${encodeURIComponent(district.value)}`)
    ])
    cacheDetectors.value = cacheData || []
    transitDetectors.value = transitData || []
  } catch (err) { 
    error.value = 'Failed to fetch detectors.'
    console.error(err) 
  } finally { 
    isLoading.value = false 
  }
}

const fetchBurnleyDetectors = async () => {
  if (!selectedModelId.value) return
  try {
    const data = await apiFetch(`/detector-labels/?location__label=Burnley&status=IS&detector_model=${selectedModelId.value}`)
    burnleyDetectors.value = data || []
  } catch (err) { 
    console.error('Failed to fetch Burnley detectors:', err)
    burnleyDetectors.value = []  
  }
}

const toggleBurnleySelection = (id) => {
  const idx = selectedBurnleyIds.value.indexOf(id)
  if (idx > -1) selectedBurnleyIds.value.splice(idx, 1)
  else selectedBurnleyIds.value.push(id)
}

const clearSelection = () => { selectedBurnleyIds.value = [] }

const handleModelChange = () => {
  clearSelection()
  fetchSlotCount()
  fetchCacheAndTransit()
  fetchBurnleyDetectors()
}

const attemptAddToCache = () => {
  if (selectedCount.value === 0) return
  if (!hasSpace.value) { showWarningModal.value = true; return }
  showConfirmModal.value = true
}

const executeRestock = async () => {
  isProcessing.value = true
  try {
    const diLocations = await apiFetch(`/locations/?location_type=DI&district=${encodeURIComponent(district.value)}`)
    if (!diLocations || diLocations.length === 0) {
      throw new Error('District cache location not found')
    }
    const targetLocation = diLocations[0]
    const payload = selectedBurnleyIds.value.map(id => ({ 
      detector_id: id, 
      location_id: targetLocation.id, 
      status: 'IS' 
    }))
    await apiFetch('/detectors/update-location-status/', { 
      method: 'POST', 
      body: JSON.stringify(payload) 
    })
    showConfirmModal.value = false
    showSuccessModal.value = true
  } catch (err) { 
    console.error('Failed to add to cache:', err)
    alert('Failed to add detectors. Please try again.') 
  } finally { 
    isProcessing.value = false 
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  clearSelection()
  fetchSlotCount()
  fetchCacheAndTransit()
  fetchBurnleyDetectors()
}

// --- Lifecycle ---
onMounted(async () => {
  district.value = props.district
  await fetchModels()
  await fetchSlotCount()
  await fetchCacheAndTransit()
  await fetchBurnleyDetectors()
})
</script>

<style scoped>
.take-info {
  font-size: 0.95rem;
  font-weight: 500;
  color: #42b883;
  margin-left: 8px;
}
</style>