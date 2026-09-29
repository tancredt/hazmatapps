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
      <!-- ================= BURNLEY SELECTION SECTION ================= -->
      <div v-if="availableSlots > 0" class="location-section" style="margin-top: 20px;">
        <h3>Available at Burnley</h3>
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
const diLocation = ref(null)
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

// --- Methods ---
const fetchModels = async () => {
  try {
    const data = await apiFetch('/detectormodels/')
    models.value = data
    const microRae = data.find(m => m.label === 'MicroRAE')
    selectedModelId.value = microRae?.id || data[0]?.id
  } catch (err) { console.error('Failed to fetch models:', err) }
}

const resolveDistrictAndDI = async (dLabel) => {
  district.value = dLabel
  error.value = null
  try {
    const diResults = await apiFetch(`/locations/?location_type=DI&district=${encodeURIComponent(dLabel)}`)
    diLocation.value = diResults[0] || null
    if (!diLocation.value) error.value = `District Cache not found for district "${dLabel}".`
  } catch (err) {
    error.value = 'Failed to resolve district cache location.'
    console.error(err)
  }
}

const fetchSlotCount = async () => {
  if (!diLocation.value || !selectedModelId.value) return
  try {
    // Filter by location (DI) AND detector_model
    const slots = await apiFetch(`/locationdetectorslots/?location=${diLocation.value.id}&detector_model=${selectedModelId.value}`)
    slotCount.value = slots.length
  } catch (err) { 
    console.error('Failed to fetch slot count:', err)
    slotCount.value = 0 
  }
}

const fetchCacheAndTransit = async () => {
  if (!diLocation.value || !selectedModelId.value || !district.value) return
  isLoading.value = true
  error.value = null
  try {
    const [cacheData, transitData] = await Promise.all([
      // Cache: Filter by DI location AND detector_model
      apiFetch(`/detector-labels/?location=${diLocation.value.id}&detector_model=${selectedModelId.value}`),
      // Transit: Filter by status=TR, detector_model, AND district
      apiFetch(`/detector-labels/?status=TR&detector_model=${selectedModelId.value}&location__district=${encodeURIComponent(district.value)}`)
    ])
    cacheDetectors.value = cacheData
    transitDetectors.value = transitData
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
    // Filter by Burnley location, status=IS, AND detector_model
    const data = await apiFetch(`/detector-labels/?location__label=Burnley&status=IS&detector_model=${selectedModelId.value}`)
    burnleyDetectors.value = data
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
    if (!diLocation.value) throw new Error('District cache location not found')
    const payload = selectedBurnleyIds.value.map(id => ({ 
      detector_id: id, 
      location_id: diLocation.value.id, 
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
  await fetchModels()
  await resolveDistrictAndDI(props.district)
  await fetchSlotCount()
  await fetchCacheAndTransit()
  await fetchBurnleyDetectors()
})
</script>

<style scoped>
.swap-screen { padding: 20px; font-family: system-ui, -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; color: #333; }
.model-selector { margin-bottom: 20px; }
.model-selector select { padding: 8px 12px; font-size: 1rem; border-radius: 4px; border: 1px solid #ccc; }
.section-subtitle { color: #666; margin-top: -5px; margin-bottom: 15px; font-size: 0.95rem; }
.empty-text { color: #adb5bd; font-style: italic; text-align: center; padding: 20px 0; }

.cache-summary {
  background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 12px; padding: 24px; text-align: center;
}
.summary-hero { margin-bottom: 20px; }
.hero-number { display: block; font-size: 4rem; font-weight: 800; color: #42b883; line-height: 1; }
.hero-number.hero-negative { color: #e74c3c; }
.hero-label { display: block; font-size: 1.1rem; color: #666; margin-top: 6px; font-weight: 500; }
.summary-details { display: flex; justify-content: center; gap: 32px; border-top: 1px solid #dee2e6; padding-top: 16px; }
.summary-item { display: flex; flex-direction: column; align-items: center; }
.summary-value { font-size: 1.6rem; font-weight: 700; color: #333; }
.summary-label { font-size: 0.85rem; color: #888; margin-top: 2px; }

.location-section { flex: 1; min-width: 320px; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; }
.overflow-list { display: flex; flex-wrap: wrap; gap: 10px; }
.overflow-item {
  padding: 8px 14px; background: #fff3cd; border: 1px solid #ffeeba; border-radius: 20px;
  cursor: pointer; font-size: 0.9rem; font-weight: 500; color: #333; transition: all 0.2s;
  -webkit-tap-highlight-color: transparent; user-select: none;
}
.overflow-item:hover { background: #ffe69c; transform: translateY(-1px); }
.overflow-item.selected { background: #e8f8f2; color: #333; border-color: #42b883; border-width: 2px; }

.no-space-message {
  background: #fdecea; border: 1px solid #f5c6cb; border-radius: 8px; padding: 20px;
  text-align: center; color: #e74c3c; font-weight: 500;
}

.action-bar { margin-top: 30px; text-align: center; }
.btn-primary {
  padding: 12px 32px; background: #42b883; color: white; border: none; border-radius: 6px;
  font-size: 1.1rem; font-weight: 600; cursor: pointer; transition: background 0.2s;
}
.btn-primary:hover:not(:disabled) { background: #38a373; }
.btn-primary:disabled { background: #ccc; cursor: not-allowed; }

.loading, .error { text-align: center; padding: 20px; font-size: 1.1rem; }
.error { color: #e74c3c; background: #fdecea; border-radius: 6px; }

.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.6);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
  padding: 20px; animation: fadeIn 0.2s ease-out;
}
.modal-content {
  background: white; padding: 24px; border-radius: 12px; width: 100%; max-width: 420px;
  text-align: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2); animation: slideUp 0.2s ease-out;
}
.modal-content h3 { margin: 0 0 12px 0; color: #333; font-size: 1.25rem; }
.modal-content p { color: #666; margin-bottom: 20px; font-size: 1rem; line-height: 1.5; }
.modal-actions { display: flex; gap: 12px; }
.btn-cancel, .btn-confirm {
  flex: 1; padding: 12px; border: none; border-radius: 8px; font-size: 1rem;
  font-weight: 600; cursor: pointer; transition: opacity 0.2s;
}
.btn-cancel { background: #e9ecef; color: #495057; }
.btn-confirm { background: #42b883; color: white; }
.btn-cancel:disabled, .btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }

.warning-modal { border: 2px solid #e74c3c; }
.warning-icon { font-size: 4rem; margin-bottom: 10px; }
.warning-modal h3 { color: #e74c3c; }
.btn-danger {
  flex: 1; padding: 12px; border: none; border-radius: 8px; font-size: 1rem;
  font-weight: 600; cursor: pointer; background: #e74c3c; color: white;
}
.btn-danger:hover { background: #c0392b; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>