<template>
  <div class="fault-report-edit-page">

    <div class="page-container">
      <h1>{{ isNewFault ? 'Add New Fault Report' : 'Edit Fault Report' }}</h1>

      <div class="form-container">
        <form @submit.prevent="saveFaultReport" class="fault-report-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="detector">Detector:</label>
              <input type="text" id="detector" :value="detectorLabel" disabled class="form-control readonly">
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
        <p>Fault report has been {{ isNewFault ? 'added' : 'updated' }} successfully.</p>
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
const detectorFaultTypes = ref([]);

// State variables
const detectorId = ref(route.params.detectorId);
const detectorLabel = ref('');
const faultReport = ref({
  report_dt: new Date().toISOString().split('T')[0],
  fault_type: '',
  reported_by: '',
  report_location: '',
  status: 'OP', // Default to Open
  submit_notes: '',
  resolve_dt: '',
  resolved_by: '',
  resolve_notes: ''
});

// State for status change dialog
const showStatusChangeDialog = ref(false);
const faultTypeChoices = ref([]);
const showSuccessDialog = ref(false);
const showMissingResolveDateWarning = ref(false);

// Track the initial status when the form loads
const initialStatus = ref('');

// Check if we're creating a new fault report or editing an existing one
const isNewFault = computed(() => !route.params.faultId || route.params.faultId === 'new');

// Determine where to return to based on the referrer
const returnTo = computed(() => {
  // Check if the route has a 'from' parameter indicating where the user came from
  if (route.query.from === 'faults') {
    // If coming from the faults table, return to the faults page
    return '/faults';
  } else {
    // Otherwise, return to the detector details page (default behavior)
    return `/detectors/${detectorId.value}`;
  }
});

// Check if fault report status is Closed ('CL') and form was loaded with Closed status
const isClosed = computed(() => {
  // Disable inputs only if the form was initially loaded with Closed status
  // Allow editing when the user changes the status to Closed from another status
  return initialStatus.value === 'CL' && faultReport.value.status === 'CL';
});

// Get location label
const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
};

// Fetch choice options from the API
const fetchChoices = async () => {
  try {
    // Fetch fault type choices directly
    const result = await get('/api/inventory/detector-fault-types/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    detectorFaultTypes.value = result.data;
    faultTypeChoices.value = detectorFaultTypes.value;
  } catch (error) {
    console.error('Error fetching choice options:', error);
  }
};

// Fetch fault report details if editing existing
const fetchFaultReport = async () => {
  // Only fetch if we're editing an existing fault report (not creating a new one)
  if (route.params.faultId && route.params.faultId !== 'new') {
    try {
      const result = await get(`/api/inventory/detectorfaults/${route.params.faultId}/`);
      if (!result.ok) {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
      const data = result.data;
      faultReport.value = {
        ...data,
        report_dt: data.report_dt ? new Date(data.report_dt).toISOString().split('T')[0] : '',
        resolve_dt: data.resolve_dt ? new Date(data.resolve_dt).toISOString().split('T')[0] : '',
        status: data.status || 'OP' // Ensure status is set, default to Open
      };
    } catch (error) {
      console.error('Error fetching fault report:', error);
    }
  }
};

// Fetch detector details
const fetchDetectorDetails = async () => {
  try {
    const result = await get(`/api/inventory/detectors/${detectorId.value}/`);
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    detectorLabel.value = result.data.label;
  } catch (error) {
    console.error('Error fetching detector details:', error);
  }
};

// Save fault report function
const saveFaultReport = async () => {
  try {
    // Validate that report_dt is not empty
    if (!faultReport.value.report_dt) {
      alert('Report Date is required.');
      return;
    }

    // Check if status is Closed but no resolve date is provided
    if (faultReport.value.status === 'CL' && !faultReport.value.resolve_dt) {
      showMissingResolveDateWarning.value = true;
      return;
    }

    // Validate that resolve_dt is greater than or equal to report_dt (if both are present)
    if (faultReport.value.resolve_dt && faultReport.value.report_dt) {
      const resolveDate = new Date(faultReport.value.resolve_dt);
      const reportDate = new Date(faultReport.value.report_dt);

      if (resolveDate < reportDate) {
        alert('Resolve Date must be greater than or equal to Report Date.');
        return;
      }
    }

    let response;

    // Prepare the payload, converting empty strings to null for date fields
    const preparePayload = (obj) => {
      const payload = { ...obj };
      if (payload.resolve_dt === '') {
        payload.resolve_dt = null;
      }
      // Don't convert report_dt to null since it's mandatory
      return payload;
    };

    const payload = preparePayload(faultReport.value);

    let result;

    if (isNewFault.value) {
      // Creating a new fault report
      result = await post('/api/inventory/detectorfaults/', {
        ...payload,
        detector: parseInt(detectorId.value)  // Convert string ID to integer
      });
    } else {
      // Updating an existing fault report
      result = await put(`/api/inventory/detectorfaults/${route.params.faultId}/`, payload);
    }

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    // Show success dialog
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving fault report:', error);
    alert('Error saving fault report: ' + error.message);
  }
};

// Close dialog and return to appropriate page based on where user came from
const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push(returnTo.value);
};

// Close dialog
const closeDialog = () => {
  showSuccessDialog.value = false;
};

// Close missing resolve date warning dialog
const closeMissingResolveDateWarning = () => {
  showMissingResolveDateWarning.value = false;
};

// Watch for changes to resolve date
watch(() => faultReport.value.resolve_dt, (newVal, oldVal) => {
  // If a resolve date is being set and the status is currently open, validate the date first
  if (newVal && faultReport.value.status === 'OP') {
    // Validate that resolve_dt is greater than or equal to report_dt (if both are present)
    if (faultReport.value.report_dt) {
      const resolveDate = new Date(newVal);
      const reportDate = new Date(faultReport.value.report_dt);

      if (resolveDate >= reportDate) {
        // Date is valid, show the status change dialog
        showStatusChangeDialog.value = true;
      } else {
        // Date is invalid, show an error and clear the resolve date
        alert('Resolve Date must be greater than or equal to Report Date.');
        faultReport.value.resolve_dt = '';
      }
    }
  }
});

// Handle status change dialog response
const handleStatusChangeDialog = (shouldChange) => {
  if (shouldChange) {
    faultReport.value.status = 'CL'; // Change to Closed
  }
  showStatusChangeDialog.value = false;
};

// Initialize component
onMounted(async () => {
  // Load required data
  await Promise.all([
    fetchLocations(),
    fetchChoices()
  ]);

  // Load detector details
  await fetchDetectorDetails();

  // If editing existing fault report, load its details
  if (!isNewFault.value) {
    await fetchFaultReport();
  }

  // Set the initial status after all data is loaded
  initialStatus.value = faultReport.value.status;
});

// Fetch locations from the API
const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    locations.value = result.data;
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
};
</script>

<style scoped>
.fault-report-edit-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-container {
  max-width: 1200px;
  margin: 1rem auto;
  padding: 0 2rem;
  flex: 1;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.form-container {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.fault-report-form {
  display: flex;
  flex-direction: column;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  padding-right: 1rem; /* Add padding to the right side */
}

.form-group {
  margin-bottom: 0.5rem;
  min-width: 0; /* Allows flex/grid items to shrink below content size */
}

.form-group.full-width {
  grid-column: span 2; /* Span across both columns */
}

.divider {
  grid-column: span 2; /* Span across both columns */
  height: 1px;
  background-color: #ccc;
  margin: 1rem 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box; /* Include padding in width calculation */
}

.form-control.readonly {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.form-control:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background-color: #42b883;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #36966d;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-box {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  text-align: center;
  max-width: 400px;
  width: 90%;
  z-index: 1001;
}

.dialog-box h3 {
  margin-top: 0;
  color: #2c3e50;
}

.dialog-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr; /* Single column on smaller screens */
    gap: 1rem;
  }

  .form-group.full-width {
    grid-column: span 1; /* Reset to single column on small screens */
  }

  .page-container {
    padding: 0 1rem;
    margin: 1rem auto;
  }

  .form-container {
    padding: 1rem;
  }
}
</style>