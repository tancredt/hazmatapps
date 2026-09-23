<template>
  <div class="report-cylinder-empty-screen">
    <h2>Report Cylinder Empty</h2>
    <h3>{{ location_label }} ({{ district }})</h3>
    
    <div class="model-selector">
      <label>Cylinder Type:</label>
      <select v-model="selectedCylinderTypeId" @change="fetchData">
        <option value="">Select Cylinder Type</option>
        <option v-for="type in cylinderTypes" :key="type.id" :value="type.id">
          {{ getCylinderTypeLabel(type) }}
        </option>
      </select>
    </div>

    <div v-if="isLoading" class="loading">Loading cylinders...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="!isLoading && !error && selectedCylinderTypeId" class="slots-container">
      <!-- Slotted Cylinders -->
      <div class="slots-grid">
        <div 
          v-for="(item, index) in displayItems" 
          :key="'slot-' + index"
          class="slot-rectangle"
          :class="{ 
            empty: !item.cylinder, 
            filled: item.cylinder
          }"
          @click="item.cylinder ? openConfirmDialog(item.cylinder) : null"
        >
          <template v-if="item.cylinder">
            <span class="cylinder-label">{{ item.cylinder.label }}</span>
            <span class="cylinder-details">{{ getCylinderModelLabel(item.cylinder.cylinder_model) }}</span>
          </template>
          <template v-else>
            Empty
          </template>
        </div>
      </div>

      <!-- Overflow Cylinders -->
      <div v-if="overflowCylinders.length > 0" class="overflow-area">
        <h4>Overflow Cylinders ({{ overflowCylinders.length }})</h4>
        <div class="overflow-list">
          <div 
            v-for="cyl in overflowCylinders" 
            :key="'ov-' + cyl.id"
            class="overflow-item"
            @click="openConfirmDialog(cyl)"
          >
            {{ cyl.label }}
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <div v-if="showConfirmDialog" class="modal-overlay" @click.self="closeConfirmDialog">
      <div class="modal-content">
        <h3>Confirm Report</h3>
        <p>Are you sure you want to report <strong>{{ selectedCylinder?.label }}</strong> as empty?</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeConfirmDialog" :disabled="isProcessing">Cancel</button>
          <button class="btn-confirm" @click="submitFault" :disabled="isProcessing">
            {{ isProcessing ? 'Reporting...' : 'Yes, Report Empty' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="modal-overlay">
      <div class="modal-content">
        <h3>Success</h3>
        <p>Fault reported successfully for <strong>{{ selectedCylinder?.label }}</strong>.</p>
        <div class="modal-actions">
          <button class="btn-confirm" @click="closeSuccessDialog">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { apiFetch } from '@/utils/api';

const props = defineProps({
  district: String,
  location_label: String
});

const isLoading = ref(false);
const error = ref('');
const isProcessing = ref(false);

const cylinderTypes = ref([]);
const cylinderModels = ref([]);
const selectedCylinderTypeId = ref('');

const locationSlots = ref([]);
const locationCylinders = ref([]);

const showConfirmDialog = ref(false);
const showSuccessDialog = ref(false);
const selectedCylinder = ref(null);

// --- Helper Functions ---
const getGasDisplay = (gasCode) => {
  if (!gasCode) return '';
  const gases = {
    'CO': 'CO', 'HS': 'H2S', 'CH': 'CH4', 'O2': 'O2',
    'IB': 'Iso', 'HC': 'HCN', 'N2': 'N2', 'CL': 'Cl2',
    'PH': 'PH3', 'SO': 'SO2', 'NO': 'NO2', 'C2': 'CO2',
    'NH': 'NH3', 'ET': 'ETO'
  };
  return gases[gasCode] || gasCode;
};

const getUnitDisplay = (unitCode) => {
  if (!unitCode) return '';
  const units = { 'PM': 'ppm', 'PV': '%v/v', 'PL': '%LEL', 'ML': 'mg/L' };
  return units[unitCode] || unitCode;
};

const getCylinderTypeLabel = (type) => {
  if (!type) return 'N/A';
  const gasEntries = [];
  const buildEntry = (gas, conc, units) => {
    if (!gas) return null;
    return `${getGasDisplay(gas)} ${conc ?? ''} ${getUnitDisplay(units)}`.trim();
  };
  const entry1 = buildEntry(type.cylinder_1_gas, type.cylinder_1_conc, type.cylinder_1_units);
  const entry2 = buildEntry(type.cylinder_2_gas, type.cylinder_2_conc, type.cylinder_2_units);
  const entry3 = buildEntry(type.cylinder_3_gas, type.cylinder_3_conc, type.cylinder_3_units);
  const entry4 = buildEntry(type.cylinder_4_gas, type.cylinder_4_conc, type.cylinder_4_units);
  
  if (entry1) gasEntries.push(entry1);
  if (entry2) gasEntries.push(entry2);
  if (entry3) gasEntries.push(entry3);
  if (entry4) gasEntries.push(entry4);
  
  return gasEntries.length > 0 ? gasEntries.join('; ') : `Balance: ${getGasDisplay(type.balance_gas)}`;
};

const getCylinderModelLabel = (modelId) => {
  const model = cylinderModels.value.find(m => m.id === modelId);
  return model ? model.part_number : `ID: ${modelId}`;
};

// --- Data Fetching ---
const fetchCylinderTypes = async () => {
  try {
    const data = await apiFetch('/cylindertypes/');
    cylinderTypes.value = data || [];
  } catch (err) {
    console.error('Failed to fetch cylinder types:', err);
  }
};

const fetchData = async () => {
  if (!props.location_label || !selectedCylinderTypeId.value) return;
  
  isLoading.value = true;
  error.value = '';
  try {
    const [slotsRes, cylsRes, modelsRes] = await Promise.all([
      apiFetch(`/locationcylinderslots/?location__label=${encodeURIComponent(props.location_label)}&cylinder_type=${selectedCylinderTypeId.value}`),
      // Exclude 'MT' (Empty) cylinders so we only report on active ones
      apiFetch(`/cylinders/?location__label=${encodeURIComponent(props.location_label)}&cylinder_model__cylinder_type=${selectedCylinderTypeId.value}&exclude_status=MT`),
      apiFetch('/cylindermodels/')
    ]);
    
    locationSlots.value = slotsRes || [];
    locationCylinders.value = cylsRes || [];
    cylinderModels.value = modelsRes || [];
  } catch (err) {
    console.error('Failed to fetch data:', err);
    error.value = 'Failed to load cylinder data. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

// --- Computed Layout ---
const displayItems = computed(() => {
  const slotsCount = locationSlots.value.length;
  const items = [];
  for (let i = 0; i < slotsCount; i++) {
    items.push({ cylinder: locationCylinders.value[i] || null });
  }
  return items;
});

const overflowCylinders = computed(() => {
  const slotsCount = locationSlots.value.length;
  return locationCylinders.value.slice(slotsCount);
});

// --- Dialog & Action Handlers ---
const openConfirmDialog = (cylinder) => {
  selectedCylinder.value = cylinder;
  showConfirmDialog.value = true;
};

const closeConfirmDialog = () => {
  showConfirmDialog.value = false;
  selectedCylinder.value = null;
};

const closeSuccessDialog = () => {
  showSuccessDialog.value = false;
  selectedCylinder.value = null;
  fetchData(); // Refresh the grid to reflect the updated status
};

const submitFault = async () => {
  if (!selectedCylinder.value) return;
  
  isProcessing.value = true;
  try {
    // 1. Resolve Location ID (required for the fault report foreign key)
    const locations = await apiFetch('/locations/');
    const location = locations.find(loc => loc.label === props.location_label);
    
    if (!location) {
      throw new Error('Could not determine location ID for fault report.');
    }

    // 2. Build the fault payload
    const payload = {
      cylinder: selectedCylinder.value.id,
      report_dt: new Date().toISOString(),
      report_location: location.id,
      fault_type: 'MT', // MT = Empty (per CylinderFaultType choices)
      status: 'OP',     // Open
      reported_by: 'District Cache App'
    };

    // 3. Submit to API
    await apiFetch('/cylinderfaults/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    // 4. Success flow
    showConfirmDialog.value = false;
    showSuccessDialog.value = true;
  } catch (err) {
    console.error('Failed to report fault:', err);
    alert('Failed to report cylinder as empty. Please check your connection and try again.');
  } finally {
    isProcessing.value = false;
  }
};

onMounted(async () => {
  await fetchCylinderTypes();
});
</script>

<style scoped>
.report-cylinder-empty-screen {
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
  width: 100%;
  max-width: 400px;
}

.slots-container { margin-top: 20px; }

.slots-grid { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 12px; 
  margin-top: 15px; 
}

.slot-rectangle {
  width: 110px; 
  height: 80px; 
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
  padding: 5px; 
  box-sizing: border-box; 
  word-break: break-word;
  transition: all 0.2s ease;
}

.slot-rectangle.filled { 
  border-color: #42b883; 
  background: #e8f8f2; 
  cursor: pointer; 
}
.slot-rectangle.filled:hover { 
  border-color: #36966d; 
  background: #d1f2eb; 
  transform: translateY(-2px); 
}

.slot-rectangle.empty {
  color: #adb5bd; 
  font-style: italic; 
  font-weight: 400; 
  background: #f8f9fa; 
  border-style: dashed; 
  cursor: default;
}

.cylinder-label { 
  font-size: 1rem; 
  font-weight: 700; 
  color: #2c3e50; 
}
.cylinder-details { 
  font-size: 0.7rem; 
  color: #666; 
  margin-top: 4px; 
}

.overflow-area { 
  margin-top: 25px; 
  padding-top: 15px; 
  border-top: 1px dashed #ced4da; 
}
.overflow-area h4 { 
  margin: 0 0 12px 0; 
  color: #d35400; 
  font-size: 1rem; 
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
}
.overflow-item:hover { 
  background: #ffe69c; 
  transform: translateY(-1px); 
}

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
  max-width: 400px;
  text-align: center; 
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2); 
  animation: slideUp 0.2s ease-out;
}
.modal-content h3 { 
  margin: 0 0 12px 0; 
  color: #333; 
  font-size: 1.25rem; 
}
.modal-content p { 
  color: #666; 
  margin-bottom: 20px; 
  font-size: 1rem; 
  line-height: 1.4; 
}
.modal-actions { 
  display: flex; 
  gap: 12px; 
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
.btn-confirm:disabled, .btn-cancel:disabled { 
  opacity: 0.6; 
  cursor: not-allowed; 
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
  .report-cylinder-empty-screen {
    padding: 15px;
  }
  .slot-rectangle {
    width: calc(50% - 6px);
    height: 70px;
  }
}
</style>