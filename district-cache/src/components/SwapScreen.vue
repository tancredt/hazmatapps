<template>
<div class="swap-screen">
<h2>FRV - Detector Swap</h2>
<h3>{{ displayLocationLabel }}</h3>
<div class="model-selector">
   <label>Detector Model:</label>
   <select v-model="swap.selectedModelId" @change="swap.fetchDetectors()">
     <option v-for="model in swap.models" :key="model.id" :value="model.id">
       {{ model.label }}
     </option>
   </select>
 </div>
 <div v-if="swap.isLoading" class="loading">Loading equipment...</div>
 <div v-if="swap.error" class="error">{{ swap.error }}</div>
 <div class="swap-container" v-if="!swap.isLoading && !swap.error">
   <!-- ================= STATION SECTION ================= -->
   <div class="location-section">
     <h3>Station: {{ displayLocationLabel }}</h3>
     <p class="section-subtitle">Select the detector to be removed</p>
     <!-- Slot Rectangles -->
     <div class="slots-grid">
       <div 
         v-for="i in swap.stationSlotCount" 
         :key="'st-slot-' + i" 
         class="slot-rectangle"
         :class="{ 
           selected: selectedDetectorId === stationSlottedDetectors[i-1]?.id,
           empty: !stationSlottedDetectors[i-1]
         }"
         @click="stationSlottedDetectors[i-1] && selectStationDetector($event, stationSlottedDetectors[i-1].id)"
       >
         <template v-if="stationSlottedDetectors[i-1]">
           {{ stationSlottedDetectors[i-1].label }}
         </template>
         <template v-else>
           Empty
         </template>
       </div>
     </div>
     <!-- Overflow Area (No Rectangles) -->
     <div v-if="stationOverflowDetectors.length > 0" class="overflow-area">
       <h4>Overflow Detectors ({{ stationOverflowDetectors.length }})</h4>
       <div class="overflow-list">
         <div 
           v-for="det in stationOverflowDetectors" 
           :key="'st-ov-' + det.id" 
           class="overflow-item"
           :class="{ selected: selectedDetectorId === det.id }"
           @click="selectStationDetector($event, det.id)"
         >
           {{ det.label }}
         </div>
       </div>
     </div>
   </div>
   <!-- ================= DISTRICT CACHE SECTION ================= -->
   <div class="location-section">
     <h3>District Cache: {{ swap.districtLocation?.label }}</h3>
     <p class="section-subtitle">Select replacement detector</p>
     <!-- Slot Rectangles -->
     <div class="slots-grid">
       <div 
         v-for="i in swap.districtSlotCount" 
         :key="'dc-slot-' + i" 
         class="slot-rectangle"
         :class="{ 
           selected: replacementDetectorId === districtSlottedDetectors[i-1]?.id,
           empty: !districtSlottedDetectors[i-1]
         }"
         @click="districtSlottedDetectors[i-1] && selectDistrictDetector($event, districtSlottedDetectors[i-1].id)"
       >
         <template v-if="districtSlottedDetectors[i-1]">
           {{ districtSlottedDetectors[i-1].label }}
         </template>
         <template v-else>
           Empty
         </template>
       </div>
     </div>
     <!-- Overflow Area (No Rectangles) -->
     <div v-if="districtOverflowDetectors.length > 0" class="overflow-area">
       <h4>Overflow Detectors ({{ districtOverflowDetectors.length }})</h4>
       <div class="overflow-list">
         <div 
           v-for="det in districtOverflowDetectors" 
           :key="'dc-ov-' + det.id" 
           class="overflow-item"
           :class="{ selected: replacementDetectorId === det.id }"
           @click="selectDistrictDetector($event, det.id)"
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
     @click="showReasonDialog = true"
     :disabled="isProcessing || swap.isLoading || !!swap.error || !selectedDetectorId || !replacementDetectorId"
   >
     {{ isProcessing ? 'Processing...' : 'Update' }}
   </button>
 </div>
 <!-- ================= REASON FOR SWAP DIALOG ================= -->
 <div v-if="showReasonDialog" class="modal-overlay" @click.self="cancelReason">
   <div class="modal-content">
     <h3>Reason for Swap</h3>
     <p>Please select the reason for removing the detector:</p>
     <div class="fault-options">
       <label 
         v-for="ft in faultTypes" 
         :key="ft.value" 
         class="fault-option" 
         :class="{ selected: selectedFaultType === ft.value.trim() }"
       >
         <input 
           type="radio" 
           :value="ft.value.trim()" 
           v-model="selectedFaultType" 
           name="fault-type"
         />
         <span>{{ ft.label }}</span>
       </label>
     </div>
     <div class="modal-actions">
       <button class="btn-cancel" @click="cancelReason" :disabled="isProcessing">Cancel</button>
       <button class="btn-confirm" @click="submitReason" :disabled="isProcessing || !selectedFaultType">
         {{ isProcessing ? 'Processing...' : 'Submit' }}
       </button>
     </div>
   </div>
 </div>
 <!-- ================= INSTRUCTIONS INFO DIALOG ================= -->
 <div v-if="showInfoDialog" class="modal-overlay">
   <div class="modal-content">
     <h3>Instructions</h3>
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
import { useSwapStore } from '../stores/swap'
import { apiFetch } from '@/utils/api'

const props = defineProps({
  district: String,
  location_label: String
})

const swap = useSwapStore()
const isProcessing = ref(false)
const selectedDetectorId = ref(null)
const replacementDetectorId = ref(null)

const showReasonDialog = ref(false)
const showInfoDialog = ref(false)
const infoMessage = ref('')
const faultTypes = ref([])
const selectedFaultType = ref('')

const displayLocationLabel = computed(() => props.location_label || 'Unknown Location')

const stationSlottedDetectors = computed(() => swap.stationDetectors.slice(0, swap.stationSlotCount))
const stationOverflowDetectors = computed(() => swap.stationDetectors.slice(swap.stationSlotCount))

const districtSlottedDetectors = computed(() => swap.districtDetectors.slice(0, swap.districtSlotCount))
const districtOverflowDetectors = computed(() => swap.districtDetectors.slice(swap.districtSlotCount))

const selectStationDetector = (id) => {
  selectedDetectorId.value = selectedDetectorId.value === id ? null : id
}

const selectDistrictDetector = (id) => {
  replacementDetectorId.value = replacementDetectorId.value === id ? null : id
}

const fetchFaultTypes = async () => {
  try {
    const data = await apiFetch('/detector-fault-types/')
    faultTypes.value = data
  } catch (err) {
    console.error('Failed to fetch fault types:', err)
  }
}

const cancelReason = () => {
  showReasonDialog.value = false
  selectedFaultType.value = ''
}

const submitReason = async () => {
  if (!selectedFaultType.value) return

  isProcessing.value = true
  try {
    const ft = selectedFaultType.value.trim()
    let message = ''
    let removedLocId = ''
    let removedStatus = ''

    if (ft === 'MD') {
      if (!swap.unknownLocation) throw new Error('System Error: "Unknown" location (Type: ET, District: AL) not found.')
      message = "Leave the cache detector at the station and ensure a Missing/Damaged equipment form is completed"
      removedLocId = swap.unknownLocation.id
      removedStatus = 'MI'
    } else {
      if (!swap.trLocation) throw new Error(`System Error: "Transit" location (Type: TR, District: ${props.district}) not found.`)

      if (['DD', 'DC'].includes(ft)) {
        message = "Leave the cache detector at the station, ensure a MissingDamaged equipment form is completed and return the faulty detector to Burnley"
      } else {
        message = "Leave the cache detector at the station and return the faulty detector to Burnley"
      }
      removedLocId = swap.trLocation.id
      // 🎯 FIX 1: Changed from 'OF' to 'TR' (In Transit)
      removedStatus = 'TR' 
    }

    const payload = {
      removed_detector_id: selectedDetectorId.value,
      removed_location_id: removedLocId,
      removed_status: removedStatus,
      replacement_detector_id: replacementDetectorId.value,
      replacement_location_id: swap.stationLocation.id,
      replacement_status: 'OP',
      fault_data: {
        detector: selectedDetectorId.value,
        report_dt: new Date().toISOString(),
        reported_by: 'District',
        report_location: swap.stationLocation.id,
        status: 'OP',
        fault_type: selectedFaultType.value
      }
    }

    await apiFetch('/detectors/perform-swap/', {
      method: 'POST',
      body: JSON.stringify(payload)
    })

    infoMessage.value = message
    showReasonDialog.value = false
    showInfoDialog.value = true

    selectedDetectorId.value = null
    replacementDetectorId.value = null
    selectedFaultType.value = ''

  } catch (err) {
    console.error('Swap failed:', err)
    alert(err.message || 'Swap failed. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const closeInfoDialog = () => {
  showInfoDialog.value = false
  swap.fetchDetectors()
}

onMounted(async () => {
  await swap.fetchModels()
  await fetchFaultTypes()
  if (props.district && props.location_label) {
    await swap.resolveLocations(props.district, props.location_label)
    await swap.fetchDetectors()
  }
})

watch(() => swap.selectedModelId, () => {
  if (swap.selectedModelId) {
    swap.fetchDetectors()
  }
})
</script>

<style scoped>
.swap-screen {
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

.swap-container { display: flex; gap: 40px; margin-top: 20px; flex-wrap: wrap; }
.location-section {
  flex: 1; min-width: 320px; background: #f8f9fa; padding: 20px; 
  border-radius: 8px; border: 1px solid #dee2e6;
}
.section-subtitle { color: #666; margin-top: -5px; margin-bottom: 15px; font-size: 0.95rem; }

.slots-grid { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 15px; }
.slot-rectangle {
  width: 110px; height: 70px; border: 2px solid #adb5bd; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; text-align: center;
  font-size: 0.9rem; font-weight: 600; background: #ffffff; color: #333;
  cursor: pointer; transition: all 0.2s ease; padding: 5px; box-sizing: border-box;
  word-break: break-word; 
  -webkit-tap-highlight-color: transparent; 
  user-select: none;
}
.slot-rectangle:hover:not(.empty) { border-color: #42b883; background: #f0fdf4; transform: translateY(-2px); }
.slot-rectangle.selected {
  border-color: #42b883; border-width: 3px; background: #e8f8f2; color: #333;
  box-shadow: 0 4px 6px rgba(66, 184, 131, 0.2); transform: translateY(-2px);
}
.slot-rectangle.empty {
  color: #adb5bd; font-style: italic; font-weight: 400; cursor: default;
  background: #f8f9fa; border-style: dashed;
}

.overflow-area { margin-top: 25px; padding-top: 15px; border-top: 1px dashed #ced4da; }
.overflow-area h4 { margin: 0 0 12px 0; color: #d35400; font-size: 1rem; font-weight: 600; }
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
.btn-cancel:disabled, .btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }

.fault-options {
  display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px;
  max-height: 300px; overflow-y: auto; text-align: left;
}
.fault-option {
  display: flex; align-items: center; gap: 12px; padding: 12px 16px;
  border: 1px solid #dee2e6; border-radius: 6px; cursor: pointer;
  transition: all 0.2s; background: #f8f9fa; user-select: none;
  -webkit-tap-highlight-color: transparent;
}
.fault-option:hover { border-color: #42b883; background: #f0fdf4; }
.fault-option.selected { border-color: #42b883; background: #e8f8f2; font-weight: 600; color: #333; }
.fault-option input[type="radio"] { accent-color: #42b883; width: 18px; height: 18px; margin: 0; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>