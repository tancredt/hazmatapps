<template>
  <div class="district-status-screen">
    <h2>FRV - District Status</h2>
    <h3>{{ district }}</h3>
    <div class="model-selector">
      <label>Detector Model:</label>
      <select v-model="selectedModelId" @change="handleModelChange">
        <option v-for="model in models" :key="model.id" :value="model.id">{{ model.label }}</option>
      </select>
    </div>
    <div v-if="isLoading" class="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="!isLoading && !error">
      <div class="cache-summary">
        <div class="summary-hero">
          <span class="hero-number" :class="{ 'hero-negative': availableSlots <= 0 }">{{ availableSlots }}</span>
          <span class="hero-label">Slots Available</span>
        </div>
        <div class="summary-details">
          <div class="summary-item"><span class="summary-value">{{ slotCount }}</span><span class="summary-label">Total detector slots</span></div>
          <div class="summary-item"><span class="summary-value">{{ cacheDetectors.length }}</span><span class="summary-label">Detectors in cache</span></div>
          <div class="summary-item"><span class="summary-value">{{ transitDetectors.length }}</span><span class="summary-label">Detectors in transit</span></div>
        </div>
      </div>
      <div class="location-section" style="margin-top: 20px;">
        <h3>District Cache Slots</h3>
        <div class="slots-grid">
          <div v-for="i in slotCount" :key="'slot-' + i" class="slot-rectangle" :class="{ empty: !slottedDetectors[i-1], transit: slottedDetectors[i-1]?.isTransit }">
            <template v-if="slottedDetectors[i-1]">
              <span class="slot-label">{{ slottedDetectors[i-1].label }}</span>
              <span v-if="slottedDetectors[i-1].isTransit" class="transit-badge">In Transit</span>
            </template>
            <template v-else>Empty</template>
          </div>
        </div>
        <div v-if="overflowDetectors.length > 0" class="overflow-area">
          <h4>Overflow ({{ overflowDetectors.length }})</h4>
          <div class="overflow-list">
            <div v-for="det in overflowDetectors" :key="'ov-' + det.id" class="overflow-item" :class="{ 'transit-item': det.isTransit }">
              {{ det.label }}
              <span v-if="det.isTransit" class="transit-badge-small">In Transit</span>
            </div>
          </div>
        </div>
      </div>
      <div class="location-section" style="margin-top: 20px;">
        <h3>Detector Movements (Last 2 Weeks)</h3>
        <div v-if="movementLogs.length > 0" class="table-container">
          <table class="movement-table">
            <thead><tr><th>Detector</th><th>From</th><th>To</th><th>Date</th></tr></thead>
            <tbody>
              <tr v-for="log in movementLogs" :key="log.id">
                <td class="detector-cell">{{ log.detector_label }}</td>
                <td>{{ log.old_location_label || 'N/A' }}</td>
                <td>{{ log.new_location_label }}</td>
                <td>{{ formatDate(log.updated) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty-text">No detector movements in the last two weeks.</p>
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
const diLocation = ref(null)
const slotCount = ref(0)
const cacheDetectors = ref([])
const transitDetectors = ref([])
const movementLogs = ref([])
const isLoading = ref(false)
const error = ref(null)

// --- Computed ---
const totalDetectors = computed(() => cacheDetectors.value.length + transitDetectors.value.length)
const availableSlots = computed(() => slotCount.value - totalDetectors.value)

const allDistrictDetectors = computed(() => {
  const cached = cacheDetectors.value.map(d => ({ ...d, isTransit: false }))
  const transit = transitDetectors.value.map(d => ({ ...d, isTransit: true }))
  return [...cached, ...transit]
})

const slottedDetectors = computed(() => allDistrictDetectors.value.slice(0, slotCount.value))
const overflowDetectors = computed(() => allDistrictDetectors.value.slice(slotCount.value))

// --- Methods ---
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-AU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const fetchModels = async () => {
  try {
    const data = await apiFetch('/detectormodels/')
    models.value = data
    const microRae = data.find(m => m.label === 'MicroRAE')
    selectedModelId.value = microRae?.id || data[0]?.id
  } catch (err) { console.error('Failed to fetch models:', err) }
}

const resolveDistrictAndDI = async (dLabel) => {
  district.value = dLabel; error.value = null
  try {
    const diResults = await apiFetch(`/locations/?location_type=DI&district=${encodeURIComponent(dLabel)}`)
    diLocation.value = diResults[0] || null
    if (!diLocation.value) error.value = `District Cache not found for district "${dLabel}".`
  } catch (err) { error.value = 'Failed to resolve district cache location.'; console.error(err) }
}

const fetchSlotCount = async () => {
  if (!diLocation.value || !selectedModelId.value) return
  try {
    const slots = await apiFetch(`/locationdetectorslots/?location=${diLocation.value.id}&detector_model=${selectedModelId.value}`)
    slotCount.value = slots.length
  } catch (err) { console.error('Failed to fetch slot count:', err); slotCount.value = 0 }
}

const fetchCacheAndTransit = async () => {
  if (!diLocation.value || !selectedModelId.value || !district.value) return
  isLoading.value = true; error.value = null
  try {
    const [cacheData, transitData] = await Promise.all([
      apiFetch(`/detector-labels/?location=${diLocation.value.id}&detector_model=${selectedModelId.value}`),
      apiFetch(`/detector-labels/?status=TR&detector_model=${selectedModelId.value}&location__district=${encodeURIComponent(district.value)}`)
    ])
    cacheDetectors.value = cacheData; transitDetectors.value = transitData
  } catch (err) { error.value = 'Failed to fetch detectors.'; console.error(err) } 
  finally { isLoading.value = false }
}

const fetchMovementLogs = async () => {
  if (!district.value || !selectedModelId.value) return
  try {
    const twoWeeksAgo = new Date(); twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14)
    const gteStr = twoWeeksAgo.toISOString()
    
    const districtDetectors = await apiFetch(`/detectors/?detector_model=${selectedModelId.value}&location__district=${encodeURIComponent(district.value)}`)
    const detectorIdSet = new Set(districtDetectors.map(d => d.id))
    
    const transitDets = await apiFetch(`/detectors/?detector_model=${selectedModelId.value}&status=TR&location__district=${encodeURIComponent(district.value)}`)
    transitDets.forEach(d => detectorIdSet.add(d.id))
    
    const logs = await apiFetch(`/locationdetectorlogs/?district=${encodeURIComponent(district.value)}&updated_gte=${encodeURIComponent(gteStr)}`)
    
    movementLogs.value = logs.filter(l => detectorIdSet.has(l.detector)).sort((a, b) => new Date(b.updated) - new Date(a.updated))
  } catch (err) { console.error('Failed to fetch movement logs:', err); movementLogs.value = [] }
}

const fetchAll = async () => {
  await Promise.all([fetchSlotCount(), fetchCacheAndTransit(), fetchMovementLogs()])
}

const handleModelChange = () => { fetchAll() }

// --- Lifecycle ---
onMounted(async () => {
  await fetchModels()
  await resolveDistrictAndDI(props.district)
  await fetchAll()
})
</script>

<style scoped>
.district-status-screen {
  padding: 20px;
  font-family: system-ui, -apple-system, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  color: #333;
}

.model-selector { margin-bottom: 20px; }
.model-selector select {
  padding: 8px 12px; font-size: 1rem; border-radius: 4px; border: 1px solid #ccc;
}

/* ===== CACHE SUMMARY ===== */
.cache-summary {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
}
.summary-hero { margin-bottom: 20px; }
.hero-number {
  display: block;
  font-size: 4rem;
  font-weight: 800;
  color: #42b883;
  line-height: 1;
}
.hero-number.hero-negative { color: #e74c3c; }
.hero-label {
  display: block;
  font-size: 1.1rem;
  color: #666;
  margin-top: 6px;
  font-weight: 500;
}
.summary-details {
  display: flex;
  justify-content: center;
  gap: 32px;
  border-top: 1px solid #dee2e6;
  padding-top: 16px;
}
.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.summary-value { font-size: 1.6rem; font-weight: 700; color: #333; }
.summary-label { font-size: 0.85rem; color: #888; margin-top: 2px; }

/* ===== SECTIONS ===== */
.location-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.slots-grid { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 15px; }
.slot-rectangle {
  width: 110px; height: 80px; border: 2px solid #adb5bd; border-radius: 6px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; font-size: 0.9rem; font-weight: 600; background: #ffffff; color: #333;
  padding: 5px; box-sizing: border-box; word-break: break-word;
}
.slot-rectangle.empty {
  color: #adb5bd; font-style: italic; font-weight: 400; background: #f8f9fa; border-style: dashed;
}
.slot-rectangle.transit { border-color: #f39c12; background: #fef9e7; }
.slot-label { font-weight: 600; }
.transit-badge {
  font-size: 0.65rem; font-weight: 500; color: #e67e22; background: #fdebd0;
  padding: 2px 6px; border-radius: 8px; margin-top: 3px;
}

.overflow-area { margin-top: 25px; padding-top: 15px; border-top: 1px dashed #ced4da; }
.overflow-area h4 { margin: 0 0 12px 0; color: #d35400; font-size: 1rem; font-weight: 600; }
.overflow-list { display: flex; flex-wrap: wrap; gap: 10px; }
.overflow-item {
  padding: 8px 14px; background: #fff3cd; border: 1px solid #ffeeba; border-radius: 20px;
  font-size: 0.9rem; font-weight: 500; color: #333;
}
.overflow-item.transit-item { background: #fef9e7; border-color: #f39c12; }
.transit-badge-small { font-size: 0.65rem; color: #e67e22; font-weight: 600; margin-left: 4px; }

/* ===== MOVEMENT TABLE ===== */
.table-container { overflow-x: auto; margin-top: 15px; }
.movement-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.movement-table th,
.movement-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}
.movement-table th {
  background: #e9ecef;
  font-weight: 600;
  color: #495057;
}
.movement-table tbody tr:hover { background: #f1f3f5; }
.detector-cell { font-weight: 600; color: #2c3e50; }

.empty-text { color: #adb5bd; font-style: italic; text-align: center; padding: 20px 0; }
.loading, .error { text-align: center; padding: 20px; font-size: 1.1rem; }
.error { color: #e74c3c; background: #fdecea; border-radius: 6px; }
</style>