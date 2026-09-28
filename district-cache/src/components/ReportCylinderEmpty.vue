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
    // Calculate the date 7 days ago in YYYY-MM-DD format for the backend filter
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    const gteStr = oneWeekAgo.toISOString().split('T')[0];

    const [slotsRes, cylsRes, modelsRes, typesRes, faultsRes] = await Promise.all([
      apiFetch(`/locationcylinderslots/?location__label=${encodeURIComponent(props.location_label)}`),
      apiFetch(`/cylinders/?location__label=${encodeURIComponent(props.location_label)}&exclude_status=MT`),
      apiFetch('/cylindermodels/'),
      apiFetch('/cylindertypes/'),
      // ✅ UPDATED: Added report_dt_gte to filter faults to the last 7 days on the backend
      apiFetch(`/cylinderfaults/?report_location__label=${encodeURIComponent(props.location_label)}&report_dt_gte=${gteStr}`)
    ]);

    cylinderModels.value = modelsRes || [];
    cylinderTypes.value = typesRes || [];

    // 1. Process Slots & Cylinders
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

    // 2. Process Recent Faults (Sort descending by date, limit to 10)
    // Note: Backend already filtered to last 7 days, we just sort and slice here
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
    const locationRes = await apiFetch(`/locations/?label=${encodeURIComponent(props.location_label)}`);
    const locationData = Array.isArray(locationRes) ? locationRes : (locationRes.results || []);
    const location = locationData[0];

    if (!location) {
      throw new Error(`Could not find location "${props.location_label}"`);
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
    alert(`Failed to report cylinder as empty: ${err.message}`);
  } finally {
    isProcessing.value = false;
  }
};

onMounted(async () => {
  await fetchData();
});
</script>