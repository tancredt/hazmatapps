<template>
  <div class="fault-report-edit-page">
    <div class="page-container">
      <h1>{{ isNewFault ? 'Add New Cylinder Fault Report' : 'Edit Cylinder Fault Report' }}</h1>
      <div class="form-container">
        <form @submit.prevent="saveFaultReport" class="fault-report-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="cylinder">Cylinder:</label>
              <input type="text" id="cylinder" :value="cylinderLabel" disabled class="form-control readonly">
            </div>
            <div class="form-group">
              <label for="faultType">Fault Type *:</label>
              <select id="faultType" v-model="faultReport.fault_type" class="form-control" :disabled="isClosed" required>
                <option value="">Select Fault Type</option>
                <option v-for="choice in faultTypeChoices" :key="choice.value" :value="choice.value">
                  {{ choice.label }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="reportDate">Report Date *:</label>
              <input type="date" id="reportDate" v-model="faultReport.report_dt" class="form-control" :disabled="isClosed" required>
            </div>
            <div class="form-group">
              <label for="reportedBy">Reported By:</label>
              <input type="text" id="reportedBy" v-model="faultReport.reported_by" class="form-control" :disabled="isClosed">
            </div>
            <div class="form-group">
              <label for="reportLocation">Report Location *:</label>
              <select id="reportLocation" v-model="faultReport.report_location" class="form-control" :disabled="isClosed" required>
                <option value="">Select Location</option>
                <option v-for="location in locations" :key="location.id" :value="location.id">
                  {{ getLocationLabel(location.id) }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="status">Status *:</label>
              <select id="status" v-model="faultReport.status" class="form-control" :disabled="isClosed" required>
                <option value="OP">Open</option>
                <option value="CL">Closed</option>
              </select>
            </div>
            <div class="form-group full-width">
              <label for="submitNotes">Submit Notes:</label>
              <textarea id="submitNotes" v-model="faultReport.submit_notes" class="form-control" :disabled="isClosed" rows="3"></textarea>
            </div>
            <div class="divider"></div>
            <div class="form-group">
              <label for="resolveDate">Resolve Date:</label>
              <input type="date" id="resolveDate" v-model="faultReport.resolve_dt" class="form-control" :disabled="isClosed">
            </div>
            <div class="form-group">
              <label for="resolvedBy">Resolved By:</label>
              <input type="text" id="resolvedBy" v-model="faultReport.resolved_by" class="form-control" :disabled="isClosed">
            </div>
            <div class="form-group full-width">
              <label for="resolveNotes">Resolve Notes:</label>
              <textarea id="resolveNotes" v-model="faultReport.resolve_notes" class="form-control" :disabled="isClosed" rows="3"></textarea>
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isClosed">{{ isNewFault ? 'Add Fault Report' : 'Update Fault Report' }}</button>
            <router-link :to="returnTo" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3>Success!</h3>
        <p>Cylinder fault report has been {{ isNewFault ? 'added' : 'updated' }} successfully.</p>
        <div class="dialog-actions">
          <button @click="closeDialogAndReturn" class="btn btn-primary">OK</button>
        </div>
      </div>
    </div>

    <!-- Status Change Dialog -->
    <div v-if="showStatusChangeDialog" class="dialog-overlay" @click="handleStatusChangeDialog(false)">
      <div class="dialog-box" @click.stop>
        <h3>Change Status?</h3>
        <p>You've entered a resolve date. Would you like to change the status to Closed?</p>
        <div class="dialog-actions">
          <button @click="handleStatusChangeDialog(true)" class="btn btn-primary">Yes</button>
          <button @click="handleStatusChangeDialog(false)" class="btn btn-secondary">No</button>
        </div>
      </div>
    </div>

    <!-- Missing Resolve Date Warning Dialog -->
    <div v-if="showMissingResolveDateWarning" class="dialog-overlay" @click="closeMissingResolveDateWarning">
      <div class="dialog-box" @click.stop>
        <h3>Missing Resolve Date</h3>
        <p>You have set the status to Closed but have not entered a resolve date. Please enter a resolve date before closing the fault report.</p>
        <div class="dialog-actions">
          <button @click="closeMissingResolveDateWarning" class="btn btn-primary">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { get, post, put } from '@/utils/api';

const router = useRouter();
const route = useRoute();

// State for related data
const locations = ref([]);

// Hardcoded choices for Cylinder Faults (based on CylinderFaultType model)
const faultTypeChoices = ref([
  { value: 'MT', label: 'Empty' },
  { value: 'EX', label: 'Expired' }
]);

// State variables
const cylinderId = ref(route.params.cylinderId);
const cylinderLabel = ref('');
const faultReport = ref({
  report_dt: new Date().toISOString().split('T')[0],
  fault_type: '',
  reported_by: '',
  report_location: '',
  status: 'OP', 
  submit_notes: '',
  resolve_dt: '',
  resolved_by: '',
  resolve_notes: ''
});

const showStatusChangeDialog = ref(false);
const showSuccessDialog = ref(false);
const showMissingResolveDateWarning = ref(false);

const initialStatus = ref('');

const isNewFault = computed(() => !route.params.faultId || route.params.faultId === 'new');

const returnTo = computed(() => {
  if (route.query.from === 'cylinderfaults') {
    return '/cylinderfaults';
  } else {
    return `/cylinders/${cylinderId.value}`;
  }
});

const isClosed = computed(() => {
  return initialStatus.value === 'CL' && faultReport.value.status === 'CL';
});

const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
};

const fetchFaultReport = async () => {
  if (route.params.faultId && route.params.faultId !== 'new') {
    try {
      const result = await get(`/api/inventory/cylinderfaults/${route.params.faultId}/`);
      if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
      const data = result.data;
      faultReport.value = {
        ...data,
        report_dt: data.report_dt ? new Date(data.report_dt).toISOString().split('T')[0] : '',
        resolve_dt: data.resolve_dt ? new Date(data.resolve_dt).toISOString().split('T')[0] : '',
        status: data.status || 'OP'
      };
    } catch (error) {
      console.error('Error fetching fault report:', error);
    }
  }
};

const fetchCylinderDetails = async () => {
  try {
    const result = await get(`/api/inventory/cylinders/${cylinderId.value}/`);
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    cylinderLabel.value = result.data.label;
  } catch (error) {
    console.error('Error fetching cylinder details:', error);
  }
};

const saveFaultReport = async () => {
  try {
    if (!faultReport.value.report_dt) {
      alert('Report Date is required.');
      return;
    }

    if (faultReport.value.status === 'CL' && !faultReport.value.resolve_dt) {
      showMissingResolveDateWarning.value = true;
      return;
    }

    if (faultReport.value.resolve_dt && faultReport.value.report_dt) {
      const resolveDate = new Date(faultReport.value.resolve_dt);
      const reportDate = new Date(faultReport.value.report_dt);
      if (resolveDate < reportDate) {
        alert('Resolve Date must be greater than or equal to Report Date.');
        return;
      }
    }

    const preparePayload = (obj) => {
      const payload = { ...obj };
      if (payload.resolve_dt === '') payload.resolve_dt = null;
      return payload;
    };

    const payload = preparePayload(faultReport.value);
    let result;

    if (isNewFault.value) {
      result = await post('/api/inventory/cylinderfaults/', {
        ...payload,
        cylinder: parseInt(cylinderId.value)
      });
    } else {
      result = await put(`/api/inventory/cylinderfaults/${route.params.faultId}/`, payload);
    }

    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving fault report:', error);
    alert('Error saving fault report: ' + error.message);
  }
};

const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push(returnTo.value);
};

const closeDialog = () => {
  showSuccessDialog.value = false;
};

const closeMissingResolveDateWarning = () => {
  showMissingResolveDateWarning.value = false;
};

watch(() => faultReport.value.resolve_dt, (newVal, oldVal) => {
  if (newVal && faultReport.value.status === 'OP') {
    if (faultReport.value.report_dt) {
      const resolveDate = new Date(newVal);
      const reportDate = new Date(faultReport.value.report_dt);
      if (resolveDate >= reportDate) {
        showStatusChangeDialog.value = true;
      } else {
        alert('Resolve Date must be greater than or equal to Report Date.');
        faultReport.value.resolve_dt = '';
      }
    }
  }
});

const handleStatusChangeDialog = (shouldChange) => {
  if (shouldChange) {
    faultReport.value.status = 'CL';
  }
  showStatusChangeDialog.value = false;
};

const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    locations.value = result.data;
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
};

onMounted(async () => {
  await fetchLocations();
  await fetchCylinderDetails();

  if (!isNewFault.value) {
    await fetchFaultReport();
  }

  initialStatus.value = faultReport.value.status;
});
</script>

<style scoped>
.fault-report-edit-page { min-height: 100vh; display: flex; flex-direction: column; }
.page-container { max-width: 1200px; margin: 1rem auto; padding: 0 2rem; flex: 1; }
h1 { color: #2c3e50; margin-bottom: 1rem; }
.form-container { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.fault-report-form { display: flex; flex-direction: column; }
.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; padding-right: 1rem; }
.form-group { margin-bottom: 0.5rem; min-width: 0; }
.form-group.full-width { grid-column: span 2; }
.divider { grid-column: span 2; height: 1px; background-color: #ccc; margin: 1rem 0; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; }
.form-control { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
.form-control.readonly { background-color: #f8f9fa; cursor: not-allowed; }
.form-control:focus { outline: none; border-color: #42b883; box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2); }
textarea.form-control { resize: vertical; min-height: 80px; }
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
@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; gap: 1rem; }
  .form-group.full-width { grid-column: span 1; }
  .page-container { padding: 0 1rem; margin: 1rem auto; }
  .form-container { padding: 1rem; }
}
</style>