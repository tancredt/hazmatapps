<template>
<div class="report-cylinder-empty-screen">
<h2>Report Cylinder Empty</h2>
<h3>{{ location_label }} ({{ district }})</h3>
<div v-if="isLoading" class="loading">Loading cylinders...</div>
 <div v-if="error" class="error">{{ error }}</div>
 <div v-if="!isLoading && !error" class="slots-container">
   <!-- Fallback if no slots are configured for this location at all -->
   <div v-if="Object.keys(slotsByType).length === 0" class="empty-state">
     No cylinder slots configured for this location.
   </div>

   <!-- Render a section for each CylinderType that has slots -->
   <div v-for="(slotCount, typeId) in slotsByType" :key="'type-' + typeId" class="type-section">
     <h3 class="type-header">
       {{ getCylinderTypeLabel(getCylinderType(typeId)) }} 
       <span class="slot-summary">({{ getCylindersForType(typeId).length }} / {{ slotCount }})</span>
     </h3>
     
     <div class="slots-grid">
       <div 
         v-for="i in slotCount" 
         :key="'slot-' + typeId + '-' + i"
         class="slot-rectangle"
         :class="{ 
           filled: getCylindersForType(typeId)[i-1], 
           empty: !getCylindersForType(typeId)[i-1] 
         }"
         @click="getCylindersForType(typeId)[i-1] && openConfirmDialog(getCylindersForType(typeId)[i-1])"
       >
         <template v-if="getCylindersForType(typeId)[i-1]">
           <span class="cylinder-label">{{ getCylindersForType(typeId)[i-1].label }}</span>
           <span class="cylinder-details">{{ getCylinderDetails(getCylindersForType(typeId)[i-1]).typeLabel }}</span>
           <span class="cylinder-expiry" :class="{ 'expired': isExpired(getCylindersForType(typeId)[i-1].expiry_date) }">
             Exp: {{ getCylinderDetails(getCylindersForType(typeId)[i-1]).expiry }}
           </span>
         </template>
         <template v-else>
           Empty
         </template>
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
import { ref, onMounted } from 'vue';
import { apiFetch } from '@/utils/api';

const props = defineProps({
  district: String,
  location_label: String
});

const isLoading = ref(false);
const error = ref('');
const isProcessing = ref(false);

const currentLocation = ref(null);
const cylinderModels = ref([]);
const cylinderTypes = ref([]);
const locationCylinders = ref([]);
const locationCylinderSlots = ref([]);

// Grouped data structures
const cylindersByType = ref({}); 
const slotsByType = ref({}); 

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

const getCylinderType = (typeId) => {
  return cylinderTypes.value.find(t => t.id === Number(typeId));
};

const getCylindersForType = (typeId) => {
  return cylindersByType.value[typeId] || [];
};

const getCylinderDetails = (cylinder) => {
  const model = cylinderModels.value.find(m => m.id === cylinder.cylinder_model);
  const type = cylinderTypes.value.find(t => t.id === model?.cylinder_type);

  const typeLabel = type ? getCylinderTypeLabel(type) : (model?.part_number || 'Unknown Type');
  const expiry = cylinder.expiry_date ? new Date(cylinder.expiry_date).toLocaleDateString('en-AU') : 'No Expiry';

  return { typeLabel, expiry };
};

const isExpired = (expiryDate) => {
  if (!expiryDate) return false;
  return new Date(expiryDate) < new Date();
};

// --- Data Fetching ---
const fetchData = async () => {
  if (!props.location_label) return;

  isLoading.value = true;
  error.value = '';
  try {
    // 1. Resolve Location ID
    const locations = await apiFetch('/locations/');
    currentLocation.value = locations.find(loc => loc.label === props.location_label);
    if (!currentLocation.value) throw new Error('Location not found');

    // 2. Fetch all required data in parallel
    const [slotsRes, cylsRes, modelsRes, typesRes] = await Promise.all([
      apiFetch(`/locationcylinderslots/?location=${currentLocation.value.id}`),
      apiFetch(`/cylinders/?location__label=${encodeURIComponent(props.location_label)}&exclude_status=MT`),
      apiFetch('/cylindermodels/'),
      apiFetch('/cylindertypes/')
    ]);

    locationCylinderSlots.value = slotsRes || [];
    locationCylinders.value = cylsRes || [];
    cylinderModels.value = modelsRes || [];
    cylinderTypes.value = typesRes || [];

    // 3. Group slots by cylinder_type
    const slotsGrouped = {};
    for (const slot of locationCylinderSlots.value) {
      const typeId = slot.cylinder_type;
      slotsGrouped[typeId] = (slotsGrouped[typeId] || 0) + 1;
    }
    slotsByType.value = slotsGrouped;

    // 4. Group cylinders by cylinder_type
    const cylsGrouped = {};
    for (const cyl of locationCylinders.value) {
      const model = cylinderModels.value.find(m => m.id === cyl.cylinder_model);
      if (model) {
        const typeId = model.cylinder_type;
        if (!cylsGrouped[typeId]) cylsGrouped[typeId] = [];
        cylsGrouped[typeId].push(cyl);
      }
    }
    cylindersByType.value = cylsGrouped;

  } catch (err) {
    console.error('Failed to fetch data:', err);
    error.value = 'Failed to load cylinder data. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

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
    if (!currentLocation.value) {
      throw new Error('Could not determine location ID for fault report.');
    }

    // Build the fault payload
    const payload = {
      cylinder: selectedCylinder.value.id,
      report_dt: new Date().toISOString(),
      report_location: currentLocation.value.id,
      fault_type: 'MT', // MT = Empty
      status: 'OP',     // Open
      reported_by: 'District Cache App'
    };

    // Submit to API
    await apiFetch('/cylinderfaults/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    // Success flow
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
  await fetchData();
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

.slots-container { margin-top: 20px; }

.type-section {
  margin-bottom: 30px;
}
.type-header {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 15px;
  border-bottom: 2px solid #dee2e6;
  padding-bottom: 8px;
}
.slot-summary {
  font-size: 0.9rem;
  color: #666;
  font-weight: normal;
  margin-left: 8px;
}

.slots-grid { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 16px; 
  margin-top: 15px; 
}

.slot-rectangle {
  width: 140px; 
  height: 90px; 
  border-radius: 8px;
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  justify-content: center;
  text-align: center; 
  padding: 8px; 
  box-sizing: border-box; 
  word-break: break-word;
  transition: all 0.2s ease;
}

.slot-rectangle.filled {
  border: 2px solid #42b883;
  background: #e8f8f2;
  color: #333;
  cursor: pointer;
}

.slot-rectangle.filled:hover {
  border-color: #36966d;
  background: #d1f2eb;
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.slot-rectangle.empty {
  border: 2px dashed #adb5bd;
  background: #f8f9fa;
  color: #adb5bd;
  font-style: italic;
  font-weight: 400;
  cursor: default;
}

.cylinder-label { 
  font-size: 1.1rem; 
  font-weight: 700; 
  color: #2c3e50; 
  margin-bottom: 4px;
}

.cylinder-details { 
  font-size: 0.75rem; 
  color: #555; 
  line-height: 1.2;
  margin-bottom: 4px;
}

.cylinder-expiry { 
  font-size: 0.75rem; 
  font-weight: 600; 
  color: #2c3e50; 
}

.cylinder-expiry.expired {
  color: #e74c3c;
  font-weight: 700;
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
    width: calc(50% - 8px);
    height: 85px;
  }
  .cylinder-label {
    font-size: 1rem;
  }
  .cylinder-details, .cylinder-expiry {
    font-size: 0.7rem;
  }
}
</style>