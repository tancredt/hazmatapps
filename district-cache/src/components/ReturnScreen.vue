<template>
  <div class="swap-screen">
    <h2>FRV - Detector Return</h2>
    <h3>{{ district }}</h3>
    <div class="model-selector">
      <label>Detector Model:</label>
      <select v-model="selectedModelId" @change="fetchTRDetectors()">
        <option v-for="model in models" :key="model.id" :value="model.id">{{ model.label }}</option>
      </select>
    </div>
    <div v-if="isLoading" class="loading">Loading detectors...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div class="location-section" v-if="!isLoading && !error">
      <h3>In-Transit Detectors</h3>
      <p class="section-subtitle">Select detectors that have been returned to Burnley</p>
      <div v-if="trDetectors.length > 0" class="overflow-list" style="margin-top: 15px;">
        <div v-for="det in trDetectors" :key="'tr-' + det.id" class="overflow-item" :class="{ selected: selectedIds.includes(det.id) }" @click="toggleSelection(det.id)">
          {{ det.label }}
        </div>
      </div>
      <p v-else class="empty-text">No in-transit detectors found.</p>
    </div>
    <div class="action-bar">
      <button class="btn-primary" @click="showConfirmModal = true" :disabled="isProcessing || isLoading || !!error || selectedIds.length === 0">
        {{ isProcessing ? 'Processing...' : `Return (${selectedIds.length})` }}
      </button>
    </div>
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
      <div class="modal-content">
        <h3>Confirm Return</h3>
        <p>Ensure detectors are placed in the correct return bin at Burnley.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showConfirmModal = false" :disabled="isProcessing">Cancel</button>
          <button class="btn-confirm" @click="executeReturn" :disabled="isProcessing">{{ isProcessing ? 'Returning...' : 'Confirm' }}</button>
        </div>
      </div>
    </div>
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Success</h3>
        <p>Detectors have been successfully returned to Burnley.</p>
        <div class="modal-actions"><button class="btn-confirm" @click="closeSuccessModal">OK</button></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '@/utils/api'

const props = defineProps({ district: String })

// --- State ---
const models = ref([])
const selectedModelId = ref(null)
const district = ref('')
const burnleyLocation = ref(null)
const trDetectors = ref([])
const selectedIds = ref([])
const isLoading = ref(false)
const error = ref(null)

const isProcessing = ref(false)
const showConfirmModal = ref(false)
const showSuccessModal = ref(false)

// --- Computed ---
const selectedCount = computed(() => selectedIds.value.length)

// --- Methods ---
const fetchModels = async () => {
  try {
    const data = await apiFetch('/detectormodels/')
    models.value = data
    const microRae = data.find(m => m.label === 'MicroRAE')
    selectedModelId.value = microRae?.id || data[0]?.id
  } catch (err) { console.error('Failed to fetch models:', err) }
}

const resolveBurnley = async () => {
  error.value = null
  try {
    const burnleyResults = await apiFetch(`/locations/?label=${encodeURIComponent('Burnley')}`)
    burnleyLocation.value = burnleyResults[0] || null
    if (!burnleyLocation.value) error.value = 'Burnley location not found.'
  } catch (err) { error.value = 'Failed to resolve Burnley location.'; console.error(err) }
}

const fetchTRDetectors = async () => {
  if (!district.value || !selectedModelId.value) return
  isLoading.value = true; error.value = null; selectedIds.value = []
  try {
    const data = await apiFetch(`/detector-labels/?status=TR&detector_model=${selectedModelId.value}&location__district=${encodeURIComponent(district.value)}`)
    trDetectors.value = data
  } catch (err) { error.value = 'Failed to fetch in-transit detectors.'; console.error(err) } 
  finally { isLoading.value = false }
}

const toggleSelection = (id) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx > -1) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

const executeReturn = async () => {
  isProcessing.value = true
  try {
    if (!burnleyLocation.value) throw new Error('Burnley location not found')
    const payload = selectedIds.value.map(id => ({ detector_id: id, location_id: burnleyLocation.value.id, status: 'OF' }))
    await apiFetch('/detectors/update-location-status/', { method: 'POST', body: JSON.stringify(payload) })
    showConfirmModal.value = false; showSuccessModal.value = true
  } catch (err) { console.error('Return failed:', err); alert('Failed to return detectors. Please try again.') } 
  finally { isProcessing.value = false }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  fetchTRDetectors()
}

// --- Lifecycle ---
onMounted(async () => {
  await fetchModels()
  await resolveBurnley()
  district.value = props.district
  await fetchTRDetectors()
})
</script>

<style scoped>
/* --- EXACT SAME STYLES AS SWAPSCREEN --- */
.swap-screen { padding: 20px; font-family: system-ui, -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; color: #333; }
.model-selector { margin-bottom: 20px; }
.model-selector select { padding: 8px 12px; font-size: 1rem; border-radius: 4px; border: 1px solid #ccc; }
.location-section { flex: 1; min-width: 320px; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; }
.section-subtitle { color: #666; margin-top: -5px; margin-bottom: 15px; font-size: 0.95rem; }
.empty-text { color: #adb5bd; font-style: italic; text-align: center; padding: 20px 0; }

.overflow-list { display: flex; flex-wrap: wrap; gap: 10px; }
.overflow-item {
  padding: 8px 14px; background: #fff3cd; border: 1px solid #ffeeba; border-radius: 20px;
  cursor: pointer; font-size: 0.9rem; font-weight: 500; color: #333; transition: all 0.2s;
  -webkit-tap-highlight-color: transparent; user-select: none;
}
.overflow-item:hover { background: #ffe69c; transform: translateY(-1px); }
.overflow-item.selected { background: #e8f8f2; color: #333; border-color: #42b883; border-width: 2px; }

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
  background: white; padding: 24px; border-radius: 12px; width: 100%; max-width: 400px;
  text-align: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2); animation: slideUp 0.2s ease-out;
}
.modal-content h3 { margin: 0 0 12px 0; color: #333; font-size: 1.25rem; }
.modal-content p { color: #666; margin-bottom: 20px; font-size: 1rem; line-height: 1.4; }
.modal-actions { display: flex; gap: 12px; }
.btn-cancel, .btn-confirm {
  flex: 1; padding: 12px; border: none; border-radius: 8px; font-size: 1rem;
  font-weight: 600; cursor: pointer; transition: opacity 0.2s;
}
.btn-cancel { background: #e9ecef; color: #495057; }
.btn-confirm { background: #42b883; color: white; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>