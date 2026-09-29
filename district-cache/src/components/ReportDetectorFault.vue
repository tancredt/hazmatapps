<template>
<div class="report-detector-fault-screen">
<HomeHeader />
<h2>Report Detector Fault</h2>
<h3>{{ location_label }} ({{ district }})</h3>

<div class="model-selector">
   <label>Detector Model:</label>
   <select v-model="selectedModelId">
     <option v-for="model in detectorModels" :key="model.id" :value="model.id">
       {{ model.label }}
     </option>
   </select>
</div>

<div v-if="isLoading" class="loading">Loading detectors...</div>
<div v-if="error" class="error">{{ error }}</div>

<div v-if="!isLoading && !error" class="sections-container">
 <!-- Fallback if no slots or detectors exist -->
 <div v-if="displaySlots.length === 0 && overflowDetectors.length === 0" class="empty-state">
No detector slots or detectors found for this location and model.
 </div>

<!-- Single Unified Slot Grid -->
 <div v-if="displaySlots.length > 0" class="location-section">
   <h3>Detector Slots</h3>
   <p class="section-subtitle">Click an operational detector to report a fault</p>
   <div class="slots-grid">
     <div 
       v-for="item in displaySlots" 
       :key="item.slotId"
       class="slot-rectangle"
       :class="{ empty: !item.detector, clickable: item.detector }"
       :role="item.detector ? 'button' : undefined"
       :tabindex="item.detector ? 0 : -1"
       @click="item.detector && openFaultDialog(item.detector)"
       @keydown.enter="item.detector && openFaultDialog(item.detector)"
     >
       <template v-if="item.detector">
         <span class="detector-label">{{ item.detector.label }}</span>
         <span class="detector-details">{{ getDetectorModelLabel(item.detector.detector_model) }}</span>
         <span class="detector-serial">{{ item.detector.serial || 'No Serial' }}</span>
       </template>
       <template v-else>
         <span class="empty-slot-text">Empty Slot</span>
         <span class="empty-slot-model">{{ getDetectorModelLabel(item.detectorModelId) }}</span>
       </template>
     </div>
   </div>
 </div>

 <!-- Single Unified Overflow Area -->
 <div v-if="overflowDetectors.length > 0" class="location-section overflow-section">
   <h4 class="overflow-title">
     Overflow / Non-Operational ({{ overflowDetectors.length }})
   </h4>
   <div class="overflow-list">
     <div 
       v-for="det in overflowDetectors" 
       :key="det.id" 
       class="overflow-item"
       role="button"
       tabindex="0"
       @click="openFaultDialog(det)"
       @keydown.enter="openFaultDialog(det)"
     >
       {{ det.label }}
       <span v-if="det.status !== 'OP'" class="status-badge">({{ det.status }})</span>
     </div>
   </div>
 </div>

 <!-- Recent Faults Table -->
 <div v-if="recentFaults.length > 0" class="location-section">
   <h3>Recent Detector Faults</h3>
   <div class="table-container">
     <table class="faults-table">
       <thead>
         <tr>
           <th>Detector</th>
           <th>Fault Type</th>
           <th>Reported</th>
           <th>Status</th>
         </tr>
       </thead>
       <tbody>
         <tr v-for="fault in recentFaults" :key="fault.id">
           <td class="detector-cell">{{ fault.detector_label || `DET-${fault.detector}` }}</td>
           <td>{{ getFaultTypeLabel(fault.fault_type) }}</td>
           <td>{{ formatDate(fault.report_dt) }}</td>
           <td>
             <span class="status-pill" :class="fault.status === 'OP' ? 'status-open' : 'status-closed'">
               {{ getStatusLabel(fault.status) }}
             </span>
           </td>
         </tr>
       </tbody>
     </table>
   </div>
 </div>
</div>

<!-- Fault Type Selection & Confirm Dialog -->
<div v-if="showFaultDialog" class="modal-overlay" @click.self="closeFaultDialog">
 <div class="modal-content">
 <h3>Report Detector Fault</h3>
 <p class="modal-subtitle">
Reporting for: <strong>{{ selectedDetector?.label }}</strong> <br>
Model: <strong>{{ getDetectorModelLabel(selectedDetector?.detector_model) }}</strong>
 </p>
  <div class="fault-options">
     <label 
       v-for="ft in faultTypes" 
       :key="ft.value" 
       class="fault-option" 
       :class="{ selected: selectedFaultType === ft.value }"
     >
       <input 
         type="radio" 
         :value="ft.value" 
         v-model="selectedFaultType" 
         name="fault-type"
       />
       <span>{{ ft.label }}</span>
     </label>
   </div>
   <div class="modal-actions">
     <button class="btn-cancel" @click="closeFaultDialog" :disabled="isProcessing">Cancel</button>
     <button class="btn-confirm" @click="submitFault" :disabled="isProcessing || !selectedFaultType">
       {{ isProcessing ? 'Reporting...' : 'Submit Fault' }}
     </button>
   </div>
 </div>
</div>

<!-- Success Dialog -->
<div v-if="showSuccessDialog" class="modal-overlay">
 <div class="modal-content">
 <h3>Success</h3>
 <p>Fault reported successfully for <strong>{{ selectedDetector?.label }}</strong>.</p>
 <div class="modal-actions">
 <button class="btn-confirm" @click="closeSuccessDialog">OK</button>
 </div>
 </div>
 </div>
 </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { apiFetch } from '@/utils/api';
import HomeHeader from './HomeHeader.vue';

const props = defineProps({
district: String,
location_label: String
});

const isLoading = ref(false);
const error = ref('');
const isProcessing = ref(false);

const detectorModels = ref([]);
const selectedModelId = ref(null);
const faultTypes = ref([]);

const allDetectors = ref([]);
const allSlots = ref([]);
const allFaults = ref([]);

const showFaultDialog = ref(false);
const showSuccessDialog = ref(false);
const selectedDetector = ref(null);
const selectedFaultType = ref('');

// --- Computed Properties (Filtered by selected model) ---
const filteredDetectors = computed(() => {
  if (!selectedModelId.value) return [];
  return allDetectors.value.filter(d => d.detector_model === selectedModelId.value);
});

const filteredSlots = computed(() => {
  if (!selectedModelId.value) return [];
  return allSlots.value.filter(s => s.detector_model === selectedModelId.value);
});

const filteredFaults = computed(() => {
  if (!selectedModelId.value) return [];
  const detectorIds = new Set(filteredDetectors.value.map(d => d.id));
  return allFaults.value.filter(f => detectorIds.has(f.detector));
});

const displaySlots = computed(() => {
  const assignedDetIds = new Set();
  const tempSlots = [];

  for (const slot of filteredSlots.value) {
    const availableDets = filteredDetectors.value.filter(d => {
      if (assignedDetIds.has(d.id)) return false;
      if (d.status !== 'OP') return false;
      return d.detector_model === slot.detector_model;
    });

    const det = availableDets[0] || null;
    if (det) assignedDetIds.add(det.id);

    tempSlots.push({
      slotId: slot.id,
      detectorModelId: slot.detector_model,
      detector: det
    });
  }
  return tempSlots;
});

const overflowDetectors = computed(() => {
  const assignedDetIds = new Set(displaySlots.value.filter(s => s.detector).map(s => s.detector.id));
  return filteredDetectors.value.filter(det => !assignedDetIds.has(det.id));
});

const recentFaults = computed(() => {
  return filteredFaults.value
    .sort((a, b) => new Date(b.report_dt) - new Date(a.report_dt))
    .slice(0, 10);
});

// --- Helper Functions ---
const getDetectorModelLabel = (modelId) => {
  const model = detectorModels.value.find(m => m.id === Number(modelId));
  return model ? model.label : 'Unknown Model';
};

const getFaultTypeLabel = (value) => {
  const ft = faultTypes.value.find(f => f.value === value);
  return ft ? ft.label : value;
};

const getStatusLabel = (status) => {
  return status === 'OP' ? 'Open' : status === 'CL' ? 'Closed' : status;
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('en-AU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// --- Data Fetching ---
const fetchData = async () => {
  if (!props.location_label) return;

  isLoading.value = true;
  error.value = '';
  try {
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    const gteStr = oneWeekAgo.toISOString().split('T')[0];

    const [slotsRes, detsRes, modelsRes, faultTypesRes, faultsRes] = await Promise.all([
      apiFetch(`/locationdetectorslots/?location__label=${encodeURIComponent(props.location_label)}`),
      apiFetch(`/detectors/?location__label=${encodeURIComponent(props.location_label)}`),
      apiFetch('/detectormodels/'),
      apiFetch('/detector-fault-types/'),
      apiFetch(`/detectorfaults/?report_location__label=${encodeURIComponent(props.location_label)}&report_dt_gte=${gteStr}`)
    ]);

    detectorModels.value = modelsRes || [];
    faultTypes.value = faultTypesRes || [];
    allDetectors.value = detsRes || [];
    allSlots.value = slotsRes || [];
    allFaults.value = faultsRes || [];

    // Set default model to MicroRAE if not already set
    if (!selectedModelId.value && detectorModels.value.length > 0) {
      const microRae = detectorModels.value.find(m => m.label === 'MicroRAE');
      selectedModelId.value = microRae ? microRae.id : detectorModels.value[0].id;
    }

  } catch (err) {
    console.error('Failed to fetch data:', err);
    error.value = 'Failed to load detector data. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

// --- Dialog & Action Handlers ---
const openFaultDialog = (detector) => {
  selectedDetector.value = detector;
  selectedFaultType.value = '';
  showFaultDialog.value = true;
};

const closeFaultDialog = () => {
  showFaultDialog.value = false;
  selectedDetector.value = null;
  selectedFaultType.value = '';
};

const closeSuccessDialog = () => {
  showSuccessDialog.value = false;
  selectedDetector.value = null;
  selectedFaultType.value = '';
  fetchData();
};

const submitFault = async () => {
  if (!selectedDetector.value || !selectedFaultType.value) return;

  isProcessing.value = true;
  try {
    const locationRes = await apiFetch(`/locations/?label=${encodeURIComponent(props.location_label)}`);
    const locationData = Array.isArray(locationRes) ? locationRes : (locationRes.results || []);
    const location = locationData[0];

    if (!location) {
      throw new Error(`Could not find location "${props.location_label}"`);
    }

    const payload = {
      detector: selectedDetector.value.id,
      report_dt: new Date().toISOString(),
      report_location: location.id,
      fault_type: selectedFaultType.value,
      status: 'OP',
      reported_by: 'District Cache App'
    };

    await apiFetch('/detectorfaults/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    showFaultDialog.value = false;
    showSuccessDialog.value = true;
  } catch (err) {
    console.error('Failed to report fault:', err);
    alert(`Failed to report detector fault: ${err.message}`);
  } finally {
    isProcessing.value = false;
  }
};

onMounted(async () => {
  await fetchData();
});
</script>

<style scoped>
.report-detector-fault-screen {
padding: 20px;
font-family: system-ui, -apple-system, sans-serif;
max-width: 1200px;
margin: 0 auto;
color: #333;
}

.model-selector {
  margin-bottom: 20px;
}
.model-selector select {
  padding: 8px 12px;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.sections-container {
display: flex;
flex-direction: column;
gap: 24px;
margin-top: 20px;
}

.location-section {
flex: 1;
min-width: 320px;
background: #f8f9fa;
padding: 20px;
border-radius: 8px;
border: 1px solid #dee2e6;
}

.section-subtitle {
color: #666;
margin-top: -5px;
margin-bottom: 15px;
font-size: 0.95rem;
}

.slots-grid {
display: flex;
flex-wrap: wrap;
gap: 12px;
margin-top: 15px;
}

.slot-rectangle {
width: 130px;
height: 90px;
border: 2px solid #adb5bd;
border-radius: 6px;
display: flex;
flex-direction: column;
align-items: center;
justify-content: center;
text-align: center;
font-size: 0.9rem;
font-weight: 600;
background: #ffffff;
color: #333;
transition: all 0.2s ease;
padding: 8px;
box-sizing: border-box;
word-break: break-word;
user-select: none;
}

.slot-rectangle.clickable {
cursor: pointer;
-webkit-tap-highlight-color: transparent;
}

.slot-rectangle.clickable:hover {
border-color: #42b883;
background: #f0fdf4;
transform: translateY(-2px);
}

.slot-rectangle.empty {
color: #adb5bd;
font-style: italic;
font-weight: 400;
cursor: default;
background: #f8f9fa;
border-style: dashed;
}

.empty-slot-text {
font-size: 0.95rem;
font-weight: 500;
color: #868e96;
font-style: normal;
}

.empty-slot-model {
font-size: 0.7rem;
color: #adb5bd;
margin-top: 4px;
text-align: center;
line-height: 1.2;
font-style: normal;
max-width: 100%;
overflow: hidden;
text-overflow: ellipsis;
display: -webkit-box;
-webkit-line-clamp: 2;
-webkit-box-orient: vertical;
}

.detector-label {
font-size: 1rem;
font-weight: 700;
color: #2c3e50;
margin-bottom: 2px;
line-height: 1.2;
}
.detector-details {
font-size: 0.7rem;
color: #555;
line-height: 1.2;
margin-bottom: 2px;
}
.detector-serial {
font-size: 0.65rem;
color: #888;
}

.overflow-section {
margin-top: 20px;
}

.overflow-title {
margin: 0 0 12px 0;
color: #d35400;
font-size: 1.1rem;
font-weight: 600;
}

.overflow-list {
display: flex;
flex-wrap: wrap;
gap: 10px;
}

.overflow-item {
padding: 8px 14px;
background: #fff3cd;
border: 1px solid #ffeeba;
border-radius: 20px;
cursor: pointer;
font-size: 0.9rem;
font-weight: 500;
color: #333;
transition: all 0.2s;
-webkit-tap-highlight-color: transparent;
user-select: none;
}

.overflow-item:hover {
background: #ffe69c;
transform: translateY(-1px);
}

.status-badge {
font-size: 0.75rem;
color: #856404;
margin-left: 4px;
font-weight: 600;
}

.empty-state {
text-align: center;
padding: 40px 20px;
color: #adb5bd;
font-size: 1.1rem;
font-style: italic;
background: #f8f9fa;
border-radius: 8px;
border: 2px dashed #dee2e6;
}

/* ===== FAULTS TABLE ===== */
.table-container { overflow-x: auto; margin-top: 15px; }
.faults-table {
width: 100%;
border-collapse: collapse;
font-size: 0.9rem;
}
.faults-table th,
.faults-table td {
padding: 10px 12px;
text-align: left;
border-bottom: 1px solid #dee2e6;
}
.faults-table th {
background: #e9ecef;
font-weight: 600;
color: #495057;
}
.faults-table tbody tr:hover { background: #f1f3f5; }
.detector-cell { font-weight: 600; color: #2c3e50; }

.status-pill {
display: inline-block;
padding: 4px 10px;
border-radius: 12px;
font-size: 0.75rem;
font-weight: 600;
}
.status-open {
background: #fff3cd;
color: #856404;
}
.status-closed {
background: #d4edda;
color: #155724;
}

/* ===== MODALS ===== */
.modal-overlay {
position: fixed;
top: 0; left: 0; right: 0; bottom: 0;
background: rgba(0, 0, 0, 0.6);
display: flex;
align-items: center;
justify-content: center;
z-index: 1000;
padding: 20px;
animation: fadeIn 0.2s ease-out;
}

.modal-content {
background: white;
padding: 24px;
border-radius: 12px;
width: 100%;
max-width: 420px;
text-align: center;
box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
animation: slideUp 0.2s ease-out;
}

.modal-content h3 {
margin: 0 0 8px 0;
color: #333;
font-size: 1.25rem;
}

.modal-subtitle {
color: #666;
margin-bottom: 20px;
font-size: 0.95rem;
line-height: 1.4;
}

.modal-actions {
display: flex;
gap: 12px;
margin-top: 20px;
}

.btn-cancel, .btn-confirm {
flex: 1;
padding: 12px;
border: none;
border-radius: 8px;
font-size: 1rem;
font-weight: 600;
cursor: pointer;
transition: opacity 0.2s;
}

.btn-cancel {
background: #e9ecef;
color: #495057;
}

.btn-confirm {
background: #42b883;
color: white;
}

.btn-cancel:disabled, .btn-confirm:disabled {
opacity: 0.6;
cursor: not-allowed;
}

.fault-options {
display: flex;
flex-direction: column;
gap: 8px;
max-height: 300px;
overflow-y: auto;
text-align: left;
padding-right: 4px;
}

.fault-option {
display: flex;
align-items: center;
gap: 12px;
padding: 12px 16px;
border: 1px solid #dee2e6;
border-radius: 6px;
cursor: pointer;
transition: all 0.2s;
background: #f8f9fa;
user-select: none;
-webkit-tap-highlight-color: transparent;
}

.fault-option:hover {
border-color: #42b883;
background: #f0fdf4;
}

.fault-option.selected {
border-color: #42b883;
background: #e8f8f2;
font-weight: 600;
color: #333;
}

.fault-option input[type="radio"] {
accent-color: #42b883;
width: 18px;
height: 18px;
margin: 0;
}

.loading, .error {
text-align: center;
padding: 20px;
font-size: 1.1rem;
}

.error {
color: #e74c3c;
background: #fdecea;
border-radius: 6px;
}

@keyframes fadeIn {
from { opacity: 0; }
to { opacity: 1; }
}

@keyframes slideUp {
from { transform: translateY(20px); opacity: 0; }
to { transform: translateY(0); opacity: 1; }
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
.report-detector-fault-screen {
padding: 15px;
}
.slot-rectangle {
width: calc(50% - 6px);
height: 90px;
}
}
</style>