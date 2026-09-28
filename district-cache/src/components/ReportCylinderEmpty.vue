<template>
<div class="report-cylinder-empty-screen">
  <h2>Report Cylinder Empty</h2>
  <h3>{{ location_label }} ({{ district }})</h3>
  
  <div v-if="isLoading" class="loading">Loading cylinders...</div>
  <div v-if="error" class="error">{{ error }}</div>
  
  <div v-if="!isLoading && !error" class="sections-container">
    <!-- Fallback if no slots or cylinders exist -->
    <div v-if="displaySlots.length === 0 && overflowCylinders.length === 0" class="empty-state">
      No cylinder slots or cylinders found for this location.
    </div>

    <!-- Single Unified Slot Grid -->
    <div v-if="displaySlots.length > 0" class="location-section">
      <h3>Cylinder Slots</h3>
      <p class="section-subtitle">Click an operational cylinder to report as empty</p>
      <div class="slots-grid">
        <div 
          v-for="item in displaySlots" 
          :key="item.slotId"
          class="slot-rectangle"
          :class="{ empty: !item.cylinder, clickable: item.cylinder }"
          :role="item.cylinder ? 'button' : undefined"
          :tabindex="item.cylinder ? 0 : -1"
          @click="item.cylinder && openConfirmDialog(item.cylinder)"
          @keydown.enter="item.cylinder && openConfirmDialog(item.cylinder)"
        >
          <template v-if="item.cylinder">
            <span class="cylinder-label">{{ item.cylinder.label }}</span>
            <span class="cylinder-details">{{ getCylinderDetails(item.cylinder).typeLabel }}</span>
            <span class="cylinder-expiry" :class="{ 'expired': isExpired(item.cylinder.expiry_date) }">
              Exp: {{ getCylinderDetails(item.cylinder).expiry }}
            </span>
          </template>
          <template v-else>
            <span class="empty-slot-text">Empty Slot</span>
            <span class="empty-slot-type">{{ getCylinderTypeLabel(item.cylinderType) }}</span>
          </template>
        </div>
      </div>
    </div>

    <!-- Single Unified Overflow Area -->
    <div v-if="overflowCylinders.length > 0" class="location-section overflow-section">
      <h4 class="overflow-title">
        Overflow / Non-Operational ({{ overflowCylinders.length }})
      </h4>
      <div class="overflow-list">
        <div 
          v-for="cyl in overflowCylinders" 
          :key="cyl.id" 
          class="overflow-item"
          role="button"
          tabindex="0"
          @click="openConfirmDialog(cyl)"
          @keydown.enter="openConfirmDialog(cyl)"
        >
          {{ cyl.label }}
          <span v-if="cyl.status !== 'OP'" class="status-badge">({{ cyl.status }})</span>
        </div>
      </div>
    </div>

    <!-- ================= RECENT FAULTS TABLE ================= -->
    <div v-if="recentFaults.length > 0" class="location-section">
      <h3>Recent Cylinder Faults</h3>
      <div class="table-container">
        <table class="faults-table">
          <thead>
            <tr>
              <th>Cylinder</th>
              <th>Reported</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="fault in recentFaults" :key="fault.id">
              <td class="cylinder-cell">{{ getCylinderLabel(fault.cylinder) }}</td>
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

const cylinderModels = ref([]);
const cylinderTypes = ref([]);

const displaySlots = ref([]);
const overflowCylinders = ref([]);
const recentFaults = ref([]);

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

// --- Fault Table Helpers ---
const getCylinderLabel = (cylId) => {
  return `CYL${String(cylId).padStart(5, '0')}`;
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
    // 1. Fetch all required data in parallel
    const [slotsRes, cylsRes, modelsRes, typesRes, faultsRes] = await Promise.all([
      apiFetch(`/locationcylinderslots/?location__label=${encodeURIComponent(props.location_label)}`),
      apiFetch(`/cylinders/?location__label=${encodeURIComponent(props.location_label)}&exclude_status=MT`),
      apiFetch('/cylindermodels/'),
      apiFetch('/cylindertypes/'),
      apiFetch(`/cylinderfaults/?report_location__label=${encodeURIComponent(props.location_label)}`)
    ]);

    cylinderModels.value = modelsRes || [];
    cylinderTypes.value = typesRes || [];

    // 2. Process Slots & Cylinders
    const assignedCylIds = new Set();
    const tempSlots = [];

    for (const slot of (slotsRes || [])) {
      const typeId = slot.cylinder_type;
      const type = cylinderTypes.value.find(t => t.id === Number(typeId));
      
      const availableCyls = (cylsRes || []).filter(c => {
        if (assignedCylIds.has(c.id)) return false;
        if (c.status !== 'OP') return false;
        const model = cylinderModels.value.find(m => m.id === c.cylinder_model);
        return model && model.cylinder_type === typeId;
      });
      
      const cyl = availableCyls[0] || null;
      if (cyl) assignedCylIds.add(cyl.id);
      
      tempSlots.push({
        slotId: slot.id,
        cylinderType: type,
        cylinder: cyl
      });
    }
    displaySlots.value = tempSlots;

    const tempOverflow = (cylsRes || []).filter(cyl => !assignedCylIds.has(cyl.id));
    overflowCylinders.value = tempOverflow;

    // 3. Process Recent Faults (Sort descending by date, limit to 10)
    recentFaults.value = (faultsRes || [])
      .sort((a, b) => new Date(b.report_dt) - new Date(a.report_dt))
      .slice(0, 10);

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
  fetchData();
};

const submitFault = async () => {
  if (!selectedCylinder.value) return;

  isProcessing.value = true;
  try {
    const locations = await apiFetch('/locations/');
    const location = locations.find(loc => loc.label === props.location_label);

    if (!location) {
      throw new Error('Could not determine location ID for fault report.');
    }

    const payload = {
      cylinder: selectedCylinder.value.id,
      report_dt: new Date().toISOString(),
      report_location: location.id,
      fault_type: 'MT',
      status: 'OP',
      reported_by: 'District Cache App'
    };

    await apiFetch('/cylinderfaults/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

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

.empty-slot-type {
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

.cylinder-label { 
  font-size: 1rem; 
  font-weight: 700; 
  color: #2c3e50; 
  margin-bottom: 2px;
  line-height: 1.2;
}
.cylinder-details { 
  font-size: 0.7rem; 
  color: #555; 
  line-height: 1.2;
  margin-bottom: 2px;
}
.cylinder-expiry { 
  font-size: 0.7rem; 
  font-weight: 600; 
  color: #2c3e50; 
}
.cylinder-expiry.expired {
  color: #e74c3c;
  font-weight: 700;
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
.cylinder-cell { font-weight: 600; color: #2c3e50; }

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

/* Modals */
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

.btn-cancel:disabled, .btn-confirm:disabled { 
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
    height: 90px;
  }
}
</style>