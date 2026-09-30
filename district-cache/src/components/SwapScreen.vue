<template>
  <div class="swap-screen">
    <HomeHeader />
    <h2>FRV - Detector Swap</h2>
    <h3>{{ displayLocationLabel }}</h3>
    
    <div class="model-selector">
      <label>Detector Model:</label>
      <select v-model="selectedModelId" @change="fetchDetectors()">
        <option v-for="model in models" :key="model.id" :value="model.id">
          {{ model.label }}
        </option>
      </select>
    </div>

    <div v-if="isLoading" class="loading">Loading equipment...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div class="swap-container" v-if="!isLoading && !error">
      <!-- ================= STATION SECTION ================= -->
      <div class="location-section">
        <h3>Station: {{ displayLocationLabel }}</h3>
        <p class="section-subtitle">Select the detector to be removed</p>
        
        <div class="slots-grid">
          <div 
            v-for="i in stationSlotCount" 
            :key="'st-slot-' + i" 
            class="slot-rectangle"
            :class="{ 
              selected: selectedDetectorId === stationSlottedDetectors[i-1]?.id,
              empty: !stationSlottedDetectors[i-1]
            }"
            @click="stationSlottedDetectors[i-1] && selectStationDetector(stationSlottedDetectors[i-1].id)"
          >
            <template v-if="stationSlottedDetectors[i-1]">
              {{ stationSlottedDetectors[i-1].label }}
            </template>
            <template v-else>Empty</template>
          </div>
        </div>

        <div v-if="stationOverflowDetectors.length > 0" class="overflow-area">
          <h4>Overflow Detectors ({{ stationOverflowDetectors.length }})</h4>
          <div class="overflow-list">
            <div 
              v-for="det in stationOverflowDetectors" 
              :key="'st-ov-' + det.id" 
              class="overflow-item"
              :class="{ selected: selectedDetectorId === det.id }"
              @click="selectStationDetector(det.id)"
            >
              {{ det.label }}
            </div>
          </div>
        </div>
      </div>

      <!-- ================= DISTRICT CACHE SECTION ================= -->
      <div class="location-section">
        <h3>District Cache: {{ districtLocation?.label }}</h3>
        <p class="section-subtitle">Select replacement detector</p>
        
        <div class="slots-grid">
          <div 
            v-for="i in districtSlotCount" 
            :key="'dc-slot-' + i" 
            class="slot-rectangle"
            :class="{ 
              selected: replacementDetectorId === districtSlottedDetectors[i-1]?.id,
              empty: !districtSlottedDetectors[i-1]
            }"
            @click="districtSlottedDetectors[i-1] && selectDistrictDetector(districtSlottedDetectors[i-1].id)"
          >
            <template v-if="districtSlottedDetectors[i-1]">
              {{ districtSlottedDetectors[i-1].label }}
            </template>
            <template v-else>Empty</template>
          </div>
        </div>

        <div v-if="districtOverflowDetectors.length > 0" class="overflow-area">
          <h4>Overflow Detectors ({{ districtOverflowDetectors.length }})</h4>
          <div class="overflow-list">
            <div 
              v-for="det in districtOverflowDetectors" 
              :key="'dc-ov-' + det.id" 
              class="overflow-item"
              :class="{ selected: replacementDetectorId === det.id }"
              @click="selectDistrictDetector(det.id)"
            >
              {{ det.label }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ACTION BUTTON -->
    <div class="action-bar">
      <button
        class="btn-primary"
        @click="executeSwap"
        :disabled="isProcessing || isLoading || !!error || !selectedDetectorId || !replacementDetectorId"
      >
        {{ isProcessing ? 'Processing...' : 'Update' }}
      </button>
    </div>

    <!-- ================= SUCCESS DIALOG ================= -->
    <div v-if="showInfoDialog" class="modal-overlay">
      <div class="modal-content">
        <h3>Swap Successful</h3>
        <p>{{ infoMessage }}</p>
        <div class="modal-actions">
          <button class="btn-confirm" @click="closeInfoDialog">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { apiFetch } from '@/utils/api'
import HomeHeader from './HomeHeader.vue'

const props = defineProps({
  district: String,
  location_label: String
})

// --- Local State ---
const models = ref([])
const selectedModelId = ref(null)
const stationLocation = ref(null)
const districtLocation = ref(null)
const trLocation = ref(null)
const stationDetectors = ref([])
const districtDetectors = ref([])
const stationSlotCount = ref(0)
const districtSlotCount = ref(0)
const isLoading = ref(false)
const error = ref(null)

// --- Local UI State ---
const isProcessing = ref(false)
const selectedDetectorId = ref(null)
const replacementDetectorId = ref(null)

const showInfoDialog = ref(false)
const infoMessage = ref('')

// --- Computed Properties ---
const displayLocationLabel = computed(() => props.location_label || 'Unknown Location')

const stationSlottedDetectors = computed(() => stationDetectors.value.slice(0, stationSlotCount.value))
const stationOverflowDetectors = computed(() => stationDetectors.value.slice(stationSlotCount.value))

const districtSlottedDetectors = computed(() => districtDetectors.value.slice(0, districtSlotCount.value))
const districtOverflowDetectors = computed(() => districtDetectors.value.slice(districtSlotCount.value))

// --- Methods ---
const selectStationDetector = (id) => {
  selectedDetectorId.value = selectedDetectorId.value === id ? null : id
}

const selectDistrictDetector = (id) => {
  replacementDetectorId.value = replacementDetectorId.value === id ? null : id
}

const fetchModels = async () => {
  try {
    const data = await apiFetch('/detectormodels/')
    models.value = data
    const microRae = data.find(m => m.label === 'MicroRAE')
    if (microRae) selectedModelId.value = microRae.id
    else if (data.length > 0 && !selectedModelId.value) selectedModelId.value = data[0].id
  } catch (err) { 
    console.error('Failed to fetch models:', err) 
  }
}

const resolveLocations = async (district, locationLabel) => {
  error.value = null
  try {
    const stationResults = await apiFetch(`/locations/?label=${encodeURIComponent(locationLabel)}&district=${encodeURIComponent(district)}`)
    stationLocation.value = stationResults[0] || null

    const districtResults = await apiFetch(`/locations/?location_type=DI&district=${encodeURIComponent(district)}`)
    districtLocation.value = districtResults[0] || null

    const trResults = await apiFetch(`/locations/?location_type=TR&district=${encodeURIComponent(district)}`)
    trLocation.value = trResults[0] || null

    if (!stationLocation.value) error.value = `Station location "${locationLabel}" not found.`
    if (!districtLocation.value) error.value = `District Cache not found for district "${district}".`
    if (!trLocation.value) error.value = `Transit (TR) location not found for district "${district}".`
  } catch (err) {
    error.value = 'Failed to resolve locations.'
    console.error(err)
  }
}

const fetchSlotCounts = async () => {
  if (!stationLocation.value || !districtLocation.value || !selectedModelId.value) return
  try {
    const [stationSlots, districtSlots] = await Promise.all([
      apiFetch(`/locationdetectorslots/?location=${stationLocation.value.id}&detector_model=${selectedModelId.value}`),
      apiFetch(`/locationdetectorslots/?location=${districtLocation.value.id}&detector_model=${selectedModelId.value}`)
    ])
    stationSlotCount.value = stationSlots.length
    districtSlotCount.value = districtSlots.length
  } catch (err) {
    console.error('Failed to fetch slot counts:', err)
    stationSlotCount.value = 0
    districtSlotCount.value = 0
  }
}

const fetchDetectors = async () => {
  if (!stationLocation.value || !districtLocation.value || !selectedModelId.value) return
  isLoading.value = true
  error.value = null
  try {
    await fetchSlotCounts()
    const [stationData, districtData] = await Promise.all([
      apiFetch(`/detector-labels/?location=${stationLocation.value.id}&detector_model=${selectedModelId.value}`),
      apiFetch(`/detector-labels/?location=${districtLocation.value.id}&detector_model=${selectedModelId.value}`)
    ])
    stationDetectors.value = stationData
    districtDetectors.value = districtData
  } catch (err) {
    error.value = 'Failed to fetch detectors.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const executeSwap = async () => {
  if (!selectedDetectorId.value || !replacementDetectorId.value) return

  isProcessing.value = true
  try {
    if (!trLocation.value) throw new Error(`System Error: "Transit" location not found.`)

    // We no longer send fault_data. The removed detector defaults to Transit (TR).
    const payload = {
      removed_detector_id: selectedDetectorId.value,
      removed_location_id: trLocation.value.id,
      removed_status: 'TR',
      replacement_detector_id: replacementDetectorId.value,
      replacement_location_id: stationLocation.value.id,
      replacement_status: 'OP'
    }

    await apiFetch('/detectors/perform-swap/', {
      method: 'POST',
      body: JSON.stringify(payload)
    })

    infoMessage.value = "Swap successful. Leave the cache detector at the station and return the faulty detector to Burnley."
    showInfoDialog.value = true

    selectedDetectorId.value = null
    replacementDetectorId.value = null

  } catch (err) {
    console.error('Swap failed:', err)
    alert(err.message || 'Swap failed. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const closeInfoDialog = () => {
  showInfoDialog.value = false
  fetchDetectors()
}

// --- Lifecycle ---
onMounted(async () => {
  await fetchModels()
  if (props.district && props.location_label) {
    await resolveLocations(props.district, props.location_label)
    await fetchDetectors()
  }
})

watch(() => selectedModelId.value, () => {
  if (selectedModelId.value) {
    fetchDetectors()
  }
})
</script>

