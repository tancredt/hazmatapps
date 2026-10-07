<template>
 <div class="sensor-details-page">
 <div class="page-container">
 <h1>{{ isNewSensor ? 'Add New Sensor' : 'Edit Sensor' }}</h1>
 <div class="form-container">
 <form @submit.prevent="saveSensor" class="sensor-form">
 <div class="form-grid">
 <div class="form-group">
 <label for="serial">Serial</label>
 <input type="text" id="serial" v-model="sensor.serial" class="form-control" placeholder="Enter sensor serial">
 </div>
 <div class="form-group">
 <label for="sensor_type">Sensor Type *</label>
 <select id="sensor_type" v-model="sensor.sensor_type" required class="form-control">
 <option value="">Select Sensor Type</option>
 <option v-for="type in sensorTypes" :key="type.id" :value="type.id">
{{ getSensorTypeLabel(type.id) }}
 </option>
 </select>
 </div>
     <!-- SEARCHABLE DETECTOR DROPDOWN -->
      <div class="form-group">
        <label>Assigned Detector</label>
        <div class="searchable-select-wrapper">
          <div class="searchable-select" ref="detectorDropdownRef">
            <input
              type="text"
              v-model="detectorSearch"
              @focus="showDetectorDropdown = true"
              placeholder="Search detector..."
              class="form-control"
              autocomplete="off"
            />
            <div v-if="showDetectorDropdown" class="searchable-select-options">
              <!-- NEW: Unassign Option -->
              <div
                @mousedown.prevent="clearDetector"
                class="searchable-select-option clear-detector-option"
              >
                <em>Unassign Detector</em>
              </div>
              
              <div
                v-for="det in filteredDetectorsForSelect"
                :key="det.id"
                @mousedown.prevent="selectDetector(det)"
                class="searchable-select-option"
              >
                {{ det.label }} ({{ det.serial || 'No Serial' }})
              </div>
              <div v-if="filteredDetectorsForSelect.length === 0" class="searchable-select-option no-results">
                No detectors found
              </div>
            </div>
          </div>
          <!-- REMOVED: The red X button is gone -->
        </div>
      </div>
      <div class="form-group">
        <label for="status">Status *</label>
        <select id="status" v-model="sensor.status" required class="form-control">
          <option value="">Select Status</option>
          <option value="OP">Operational</option>
          <option value="IS">In Stock</option>
          <option value="OO">On Order</option>
          <option value="DC">Decommissioned</option>
        </select>
      </div>
      <div class="form-group date-pair">
        <div class="date-row">
          <div class="date-field">
            <label for="order_date">Ordered</label>
            <input type="date" id="order_date" v-model="sensor.order_date" class="form-control">
          </div>
          <div class="date-field">
            <label for="receive_date">Received</label>
            <input type="date" id="receive_date" v-model="sensor.receive_date" class="form-control">
          </div>
        </div>
      </div>
      <div class="empty-grid-cell"></div>
      <div class="form-group date-pair">
        <div class="date-row">
          <div class="date-field">
            <label for="warranty_date">Warranty</label>
            <input type="date" id="warranty_date" v-model="sensor.warranty_date" class="form-control">
          </div>
          <div class="date-field">
            <label for="expiry_date">Expiry</label>
            <input type="date" id="expiry_date" v-model="sensor.expiry_date" class="form-control">
          </div>
        </div>
      </div>
      <div class="empty-grid-cell"></div>
      <div class="form-group date-pair">
        <div class="date-row">
          <div class="date-field">
            <label for="install_date">Install Date</label>
            <input type="date" id="install_date" v-model="sensor.install_date" class="form-control">
          </div>
          <div class="date-field">
            <label for="remove_date">Remove Date</label>
            <input type="date" id="remove_date" v-model="sensor.remove_date" class="form-control">
          </div>
        </div>
      </div>
      <div class="empty-grid-cell"></div>
    </div>
    <div class="form-actions">
      <button type="submit" class="btn btn-primary" :disabled="isSaving">{{ isNewSensor ? 'Add Sensor' : 'Update Sensor' }}</button>
      <router-link to="/sensors" class="btn btn-secondary">Cancel</router-link>
    </div>
  </form>
</div>
 </div>
 <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
 <div class="dialog-box" @click.stop>
 <h3>Success!</h3>
 <p>Sensor has been {{ isNewSensor ? 'added' : 'updated' }} successfully.</p>
 <div class="dialog-actions">
 <button @click="closeDialogAndReturn" class="btn btn-primary">OK</button>
 </div>
 </div>
 </div>
 <div v-if="showErrorDialog" class="dialog-overlay" @click="closeErrorDialog">
 <div class="dialog-box" @click.stop>
 <h3>Validation Errors</h3>
 <div class="error-list">
 <p v-for="(error, index) in errorMessages" :key="index" class="error-item">{{ error }}</p>
 </div>
 <div class="dialog-actions">
 <button @click="closeErrorDialog" class="btn btn-primary">OK</button>
 </div>
 </div>
 </div>
 </div>
 </template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { get, post, put } from '@/utils/api';

const router = useRouter();
const route = useRoute();

const sensorTypes = ref([]);
const detectors = ref([]);

// Searchable Detector State
const detectorSearch = ref('');
const showDetectorDropdown = ref(false);
const detectorDropdownRef = ref(null);

const sensor = ref({
serial: '', sensor_type: '', status: '', detector: null,
order_date: '', receive_date: '', warranty_date: '',
expiry_date: '', install_date: '', remove_date: ''
});

const isDirty = ref(false);
const originalSensor = ref({});
const showSuccessDialog = ref(false);
const showErrorDialog = ref(false);
const errorMessages = ref([]);
const isSaving = ref(false);

const isNewSensor = computed(() => route.params.id === 'new');

const filteredDetectorsForSelect = computed(() => {
if (!detectorSearch.value) return detectors.value;
const term = detectorSearch.value.toLowerCase();
return detectors.value.filter(d => 
d.label.toLowerCase().includes(term) || 
(d.serial && d.serial.toLowerCase().includes(term))
);
});

const selectDetector = (det) => {
sensor.value.detector = det.id;
detectorSearch.value = `${det.label} (${det.serial || 'No Serial'})`;
showDetectorDropdown.value = false;
};

const clearDetector = () => {
sensor.value.detector = null;
detectorSearch.value = '';
showDetectorDropdown.value = false;
};

const handleClickOutside = (event) => {
if (detectorDropdownRef.value && !detectorDropdownRef.value.contains(event.target)) {
showDetectorDropdown.value = false;
}
};

const fetchSensorTypes = async () => {
try {
const result = await get('/api/inventory/sensortypes/');
if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
sensorTypes.value = result.data.results || result.data;
} catch (error) { console.error('Error fetching sensor types:', error); }
};

const fetchDetectors = async () => {
try {
const result = await get('/api/inventory/detectors/');
if (result.ok) detectors.value = result.data.results || result.data;
} catch (error) { console.error('Error fetching detectors:', error); }
};

const fetchSensor = async () => {
try {
const result = await get(`/api/inventory/sensors/${route.params.id}/`);
if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
const data = result.data; 
sensor.value = { ...data, sensor_type: data.sensor_type || null, detector: data.detector || null };

// Sync search input with loaded detector
if (data.detector) {
const det = detectors.value.find(d => d.id === data.detector);
if (det) detectorSearch.value = `${det.label} (${det.serial || 'No Serial'})`;
}

originalSensor.value = { ...sensor.value };
isDirty.value = false;
} catch (error) { console.error('Error fetching sensor:', error); }
};

const sensorGasLabels = {
CO: 'CO', HS: 'H2S', LE: 'LEL', O2: 'O2', VO: 'VOC', HC: 'HCN',
CL: 'Cl2', PH: 'PH3', SO: 'SO2', NO: 'NO2', C2: 'CO2', NH: 'NH3',
ET: 'ETO', CS: 'CO/H2S'
};

const getSensorTypeLabel = (sensorTypeId) => {
if (!sensorTypeId) return 'N/A';
const sensorType = sensorTypes.value.find(st => st.id === sensorTypeId);
if (!sensorType) return 'Unknown Sensor Type';
const parts = [sensorType.part_number];
if (sensorType.sensorgas) parts.push(`(${sensorGasLabels[sensorType.sensorgas] || sensorType.sensorgas})`);
if (sensorType.compatible_detectormodels) parts.push(`[${sensorType.compatible_detectormodels}]`);
return parts.join(' ');
};

const closeDialog = () => { showSuccessDialog.value = false; };
const closeErrorDialog = () => { showErrorDialog.value = false; errorMessages.value = []; };

const saveSensor = async () => {
isSaving.value = true;
try {
if (!sensor.value.sensor_type) { alert('Sensor Type is required.'); isSaving.value = false; return; }
if (!sensor.value.status) { alert('Status is required.'); isSaving.value = false; return; }

// --- NEW VALIDATIONS ---
// 1. Operational sensor must have a detector
if (sensor.value.status === 'OP' && !sensor.value.detector) {
  alert('An Operational sensor must be assigned to a detector.');
  isSaving.value = false;
  return;
}

// 2. Sensor with a detector can only be Operational or Decommissioned
if (sensor.value.detector && !['OP', 'DC'].includes(sensor.value.status)) {
  alert('A sensor assigned to a detector can only be saved as Operational or Decommissioned.');
  isSaving.value = false;
  return;
}
// -----------------------

if (sensor.value.detector && sensor.value.sensor_type && sensor.value.status) {
const selectedType = sensorTypes.value.find(st => st.id === parseInt(sensor.value.sensor_type));
if (selectedType) {
const gas = selectedType.sensorgas;
const result = await get(`/api/inventory/sensors/?detector=${sensor.value.detector}&status=${sensor.value.status}`);
if (result.ok) {
const existingSensors = result.data.results || result.data;
const duplicate = existingSensors.find(s => {
if (route.params.id && s.id === parseInt(route.params.id)) return false;
const sType = sensorTypes.value.find(st => st.id === s.sensor_type);
return sType && sType.sensorgas === gas;
});
if (duplicate) {
errorMessages.value = [`A sensor with gas '${gas}' and status '${sensor.value.status}' is already assigned to this detector.`];
showErrorDialog.value = true;
isSaving.value = false;
return;
}
}
}
}

let sensorData = {
...sensor.value,
sensor_type: sensor.value.sensor_type ? parseInt(sensor.value.sensor_type) : null,
detector: sensor.value.detector ? parseInt(sensor.value.detector) : null,
order_date: sensor.value.order_date || null,
receive_date: sensor.value.receive_date || null,
warranty_date: sensor.value.warranty_date || null,
expiry_date: sensor.value.expiry_date || null,
install_date: sensor.value.install_date || null,
remove_date: sensor.value.remove_date || null
};

let result;
if (isNewSensor.value) {
result = await post('/api/inventory/sensors/', sensorData);
} else {
result = await put(`/api/inventory/sensors/${route.params.id}/`, sensorData);
}

if (!result.ok) {
if (result.status === 400) {
const errorData = result.data;
errorMessages.value = [];
for (const [field, errors] of Object.entries(errorData)) { 
errorMessages.value.push(`${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`);
}
showErrorDialog.value = true;
return;
} else {
throw new Error(`HTTP error! status: ${result.status}`);
}
}

originalSensor.value = { ...sensor.value };
isDirty.value = false;
showSuccessDialog.value = true;
} catch (error) {
console.error('Error saving sensor:', error);
alert('Error saving sensor: ' + error.message);
} finally {
isSaving.value = false;
}
};

const closeDialogAndReturn = () => {
showSuccessDialog.value = false;
router.push('/sensors');
};

onMounted(async () => {
document.addEventListener('click', handleClickOutside);
await Promise.all([fetchSensorTypes(), fetchDetectors()]);

if (!isNewSensor.value) {
await fetchSensor();
}

// If opened from DetectorDetails dialog, pre-fill detector
if (route.query.detectorId) {
const targetDetId = parseInt(route.query.detectorId);
sensor.value.detector = targetDetId;
const det = detectors.value.find(d => d.id === targetDetId);
if (det) {
detectorSearch.value = `${det.label} (${det.serial || 'No Serial'})`;
}
}
});

onUnmounted(() => {
document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.sensor-details-page { min-height: 100vh; display: flex; flex-direction: column; }
.page-container { max-width: 1200px; margin: 1rem auto; padding: 0 2rem; flex: 1; }
h1 { color: #2c3e50; margin-bottom: 1rem; }
.form-container { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.sensor-form { display: flex; flex-direction: column; }
.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.form-group { margin-bottom: 1rem; min-width: 0; }
.date-pair { grid-column: span 2; }
.date-row { display: flex; gap: 1rem; width: 100%; }
.date-field { flex: 1; display: flex; flex-direction: column; }
.date-field label { margin-bottom: 0.5rem; font-weight: 600; color: #333; }
.date-field input { flex: 1; }
.empty-grid-cell { display: none; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; }
.form-control { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
.form-control:focus { outline: none; border-color: #42b883; box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2); }
.form-actions { display: flex; gap: 1rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee; }
.btn { padding: 0.75rem 1.5rem; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; text-decoration: none; display: inline-block; text-align: center; }
.btn-primary { background-color: #42b883; color: white; }
.btn-primary:hover:not(:disabled) { background-color: #36966d; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }
.dialog-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.dialog-box { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); text-align: center; max-width: 400px; width: 90%; z-index: 1001; }
.dialog-box h3 { margin-top: 0; color: #2c3e50; }
.dialog-actions { margin-top: 1.5rem; display: flex; justify-content: center; gap: 1rem; }
.error-list { max-height: 200px; overflow-y: auto; margin: 1rem 0; padding: 0.5rem; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; }
.error-item { margin: 0.25rem 0; color: #721c24; font-weight: 500; }

/* Searchable Select Styles */
.searchable-select-wrapper { display: flex; align-items: center; gap: 0.5rem; }
.searchable-select { flex: 1; position: relative; }
.searchable-select-options { position: absolute; top: 100%; left: 0; right: 0; background: white; border: 1px solid #ddd; border-top: none; border-radius: 0 0 4px 4px; max-height: 200px; overflow-y: auto; z-index: 100; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.searchable-select-option { padding: 0.5rem 0.75rem; cursor: pointer; font-size: 0.9rem; }
.searchable-select-option:hover { background-color: #f0f0f0; }
.searchable-select-option.no-results { color: #888; cursor: default; font-style: italic; }

/* NEW: Styling for the Unassign Option */
.clear-detector-option { 
  color: #dc3545; 
  border-bottom: 1px solid #eee; 
  font-style: italic; 
}
.clear-detector-option:hover {
  background-color: #f8d7da;
}

@media (max-width: 768px) {
.form-grid { grid-template-columns: 1fr; }
.page-container { padding: 0 1rem; }
.form-container { padding: 1rem; }
}
</style>