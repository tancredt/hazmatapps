<template>
  <div class="swap-screen">
    <header class="screen-header">
      <h1>FRV - Detector Swap</h1>
      <h2>{{ displayLocationLabel }}</h2>
      <div class="model-selector">
        <select v-model="swap.selectedModelId" @change="handleModelChange">
          <option v-for="model in swap.models" :key="model.id" :value="model.id">
            {{ model.label }}
          </option>
        </select>
      </div>
    </header>

    <div v-if="swap.isLoading" class="loading-state">Loading equipment...</div>
    <div v-else-if="swap.error" class="error-state">{{ swap.error }}</div>
    
    <template v-else>
      <!-- STATION SECTION -->
      <section class="location-section">
        <h3>Station: {{ displayLocationLabel }}</h3>
        <p class="section-subtitle">Select the detector to be removed</p>
        
        <div class="detectors-grid">
          <div v-if="swap.stationDetectors.length === 0" class="empty-slot">Empty</div>
          <div 
            v-for="det in swap.stationDetectors" 
            :key="det.id" 
            class="detector-item"
            :class="{ selected: selectedStationDetectorId === det.id }"
            @click="selectedStationDetectorId = det.id"
          >
            {{ det.label }}
          </div>
        </div>

        <div v-if="overflowDetectors.length > 0" class="overflow-section">
          <h4>Overflow Detectors</h4>
          <div 
            v-for="det in overflowDetectors" 
            :key="det.id" 
            class="detector-item overflow"
            :class="{ selected: selectedStationDetectorId === det.id }"
            @click="selectedStationDetectorId = det.id"
          >
            {{ det.label }} ✓
          </div>
        </div>
      </section>

      <!-- DISTRICT CACHE SECTION -->
      <section class="location-section">
        <h3>District Cache: {{ swap.districtLocation?.label }}</h3>
        <p class="section-subtitle">Select replacement detector</p>
        
        <div class="detectors-grid">
          <div v-if="swap.districtDetectors.length === 0" class="empty-slot">Empty</div>
          <div 
            v-for="det in swap.districtDetectors" 
            :key="det.id" 
            class="detector-item"
            :class="{ selected: selectedCacheDetectorId === det.id }"
            @click="selectedCacheDetectorId = det.id"
          >
            {{ det.label }}
          </div>
        </div>
      </section>

      <!-- ACTIONS -->
      <div class="actions">
        <button 
          class="btn-primary" 
          :disabled="!canSwap || isProcessing"
          @click="showConfirmDialog = true"
        >
          {{ isProcessing ? 'Processing...' : 'Update' }}
        </button>
      </div>
    </template>

    <!-- CONFIRMATION DIALOG -->
    <div v-if="showConfirmDialog" class="dialog-overlay" @click.self="showConfirmDialog = false">
      <div class="dialog-box">
        <h3>Confirm Action</h3>
        <p>Is the station detector missing?</p>
        <div class="dialog-actions">
          <button @click="executeSwap('MI')" class="btn-danger">Yes</button>
          <button @click="executeSwap('IS')" class="btn-primary">No</button>
          <button @click="showConfirmDialog = false" class="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useSwapStore } from '../stores/swap'

const props = defineProps({
  district: { type: String, required: true },
  location_label: { type: String, required: true }
})

const swap = useSwapStore()

const selectedStationDetectorId = ref(null)
const selectedCacheDetectorId = ref(null)
const isProcessing = ref(false)
const showConfirmDialog = ref(false)

// Fallback to props if route params are slow to bind
const displayLocationLabel = computed(() => props.location_label || 'Unknown Location')

// Identify overflow detectors (if station has more detectors than defined slots)
const overflowDetectors = computed(() => {
  if (swap.stationDetectors.length <= swap.stationSlotCount) return []
  return swap.stationDetectors.slice(swap.stationSlotCount)
})

const canSwap = computed(() => 
  selectedStationDetectorId.value !== null && selectedCacheDetectorId.value !== null
)

onMounted(async () => {
  await swap.fetchModels()
  if (props.district && props.location_label) {
    await swap.resolveLocations(props.district, props.location_label)
    await swap.fetchDetectors()
  } else {
    swap.error = 'Missing district or location label in URL.'
  }
})

// Watch for model changes to refetch detectors
watch(() => swap.selectedModelId, async () => {
  if (swap.stationLocation && swap.districtLocation) {
    await swap.fetchDetectors()
    // Reset selections when model changes
    selectedStationDetectorId.value = null
    selectedCacheDetectorId.value = null
  }
})

const handleModelChange = () => {
  // The watcher above handles the fetch
}

const executeSwap = async (stationStatus) => {
  isProcessing.value = true
  showConfirmDialog.value = false

  try {
    // 1. Move selected cache detector to station (Status: Operational)
    await swap.performSwap(selectedCacheDetectorId.value, swap.stationLocation.id, 'OP')

    // 2. Move selected station detector to Unknown (if missing) or District Cache (if returning)
    const targetLocationId = (stationStatus === 'MI' && swap.unknownLocation) 
      ? swap.unknownLocation.id 
      : swap.districtLocation.id

    await swap.performSwap(selectedStationDetectorId.value, targetLocationId, stationStatus)

    // Refresh data and reset UI
    await swap.fetchDetectors()
    selectedStationDetectorId.value = null
    selectedCacheDetectorId.value = null
  } catch (err) {
    console.error('Swap failed:', err)
    swap.error = 'Failed to perform swap. Please try again.'
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.swap-screen {
  padding: 1rem;
  max-width: 1000px;
  margin: 0 auto;
  font-family: sans-serif;
}
.screen-header {
  text-align: center;
  margin-bottom: 1.5rem;
}
.screen-header h1 { margin: 0; color: #2c3e50; }
.screen-header h2 { margin: 0.25rem 0; color: #42b883; }
.model-selector select {
  padding: 0.5rem;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid #ddd;
}
.loading-state, .error-state {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}
.error-state { color: #e74c3c; }
.location-section {
  background: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}
.location-section h3 { margin-top: 0; color: #2c3e50; }
.section-subtitle { color: #666; margin-bottom: 1rem; }
.detectors-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.detector-item {
  padding: 0.75rem 1.25rem;
  background: white;
  border: 2px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}
.detector-item:hover { border-color: #42b883; }
.detector-item.selected {
  background: #42b883;
  color: white;
  border-color: #36966d;
}
.empty-slot {
  padding: 0.75rem 1.25rem;
  background: #eee;
  color: #999;
  border-radius: 4px;
  font-style: italic;
}
.overflow-section { margin-top: 1rem; border-top: 1px dashed #ccc; padding-top: 1rem; }
.overflow { border-style: dashed; }
.actions { text-align: center; margin: 2rem 0; }
.btn-primary {
  padding: 0.75rem 2rem;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1.1rem;
  cursor: pointer;
}
.btn-primary:disabled { background: #ccc; cursor: not-allowed; }
.btn-danger { background: #e74c3c; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
.btn-secondary { background: #95a5a6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }

.dialog-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}
.dialog-box {
  background: white; padding: 2rem; border-radius: 8px;
  text-align: center; max-width: 400px; width: 90%;
}
.dialog-actions { display: flex; gap: 1rem; justify-content: center; margin-top: 1.5rem; }
</style>