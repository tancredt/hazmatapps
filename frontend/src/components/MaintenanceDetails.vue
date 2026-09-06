<template>
  <div class="maintenance-edit-page">

    <div class="page-container">
      <h1>{{ isNewMaintenance ? 'Add New Maintenance' : 'Edit Maintenance' }}</h1>

      <div class="form-container">
        <form @submit.prevent="saveMaintenance" class="maintenance-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="detector">Detector:</label>
              <input type="text" id="detector" :value="detectorLabel" disabled class="form-control readonly">
            </div>

            <div class="form-group">
              <label for="maintenanceType">Maintenance Type *:</label>
              <select id="maintenanceType" v-model="maintenance.maintenance_type" class="form-control" :disabled="isComplete" required>
                <option value="">Select Maintenance Type</option>
                <option v-for="choice in maintenanceTypeChoices" :key="choice.value" :value="choice.value">
                  {{ choice.label }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="dateDue">Date Due *:</label>
              <input type="date" id="dateDue" v-model="maintenance.date_due" class="form-control" :disabled="isComplete" required>
            </div>

            <div class="form-group">
              <label for="status">Status *:</label>
              <select id="status" v-model="maintenance.status" class="form-control" :disabled="isComplete" required>
                <option value="">Select Status</option>
                <option v-for="choice in maintenanceStatusChoices" :key="choice.value" :value="choice.value">
                  {{ choice.label }}
                </option>
              </select>
            </div>

            <div class="divider"></div>

            <div class="form-group full-width">
              <label for="maintenanceTasks">Maintenance Tasks:</label>
              <div class="multi-select-dropdown" v-click-outside="closeTaskDropdown">
                <div
                  class="multi-select-input"
                  @click="toggleTaskDropdown"
                  :class="{ 'active': showTaskDropdown }"
                >
                  <span v-if="selectedTaskTypes.length === 0" class="placeholder">Select tasks...</span>
                  <span v-else class="selected-tasks">{{ getSelectedTasksDisplay() }}</span>
                  <svg class="dropdown-arrow" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </div>
                <div v-show="showTaskDropdown" class="multi-select-options">
                  <label v-for="choice in maintenanceTaskTypeChoices" :key="choice.value" class="checkbox-option">
                    <input
                      type="checkbox"
                      :value="choice.value"
                      v-model="selectedTaskTypes"
                      :disabled="isComplete"
                    />
                    <span>{{ choice.label }}</span>
                  </label>
                </div>
              </div>
            </div>

            <div class="form-group full-width">
              <label for="notes">Notes:</label>
              <textarea id="notes" v-model="maintenance.notes" class="form-control" :disabled="isComplete" rows="3"></textarea>
            </div>

            <div class="form-group">
              <label for="datePerformed">Date Performed:</label>
              <input type="date" id="datePerformed" v-model="maintenance.date_performed" class="form-control" :disabled="isComplete">
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isComplete">{{ isNewMaintenance ? 'Add Maintenance' : 'Update Maintenance' }}</button>
            <router-link :to="returnTo" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3>Success!</h3>
        <p>Maintenance record has been {{ isNewMaintenance ? 'added' : 'updated' }} successfully.</p>
        <div class="dialog-actions">
          <button @click="closeDialogAndReturn" class="btn btn-primary">OK</button>
        </div>
      </div>
    </div>

    <!-- Status Change Dialog -->
    <div v-if="showStatusChangeDialog" class="dialog-overlay" @click="handleStatusChangeDialog(false)">
      <div class="dialog-box" @click.stop>
        <h3>Change Status?</h3>
        <p>You've entered a date performed. Would you like to change the status to Closed?</p>
        <div class="dialog-actions">
          <button @click="handleStatusChangeDialog(true)" class="btn btn-primary">Yes</button>
          <button @click="handleStatusChangeDialog(false)" class="btn btn-secondary">No</button>
        </div>
      </div>
    </div>

    <!-- Missing Date Performed Warning Dialog -->
    <div v-if="showMissingDatePerformedWarning" class="dialog-overlay" @click="closeMissingDatePerformedWarning">
      <div class="dialog-box" @click.stop>
        <h3>Missing Date Performed</h3>
        <p>You have set the status to Closed but have not entered a date performed. Please enter a date performed before completing the maintenance.</p>
        <div class="dialog-actions">
          <button @click="closeMissingDatePerformedWarning" class="btn btn-primary">OK</button>
        </div>
      </div>
    </div>

    <!-- Schedule New Maintenance Dialog -->
    <div v-if="showScheduleNewDialog" class="dialog-overlay" @click="closeScheduleNewDialog">
      <div class="dialog-box" @click.stop>
        <h3>Schedule New Maintenance?</h3>
        <p>Do you wish to schedule a new maintenance?</p>
        
        <div class="form-group">
          <label for="schedulePreset">Quick Select:</label>
          <select
            id="schedulePreset"
            v-model="selectedPreset"
            @change="applyPreset"
            class="form-control"
          >
            <option value="">Custom Date</option>
            <option value="7">1 Week</option>
            <option value="30">1 Month</option>
            <option value="90">3 Months</option>
            <option value="180">6 Months</option>
            <option value="365">1 Year</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="scheduledDate">Date Due *</label>
          <input
            id="scheduledDate"
            type="date"
            v-model="scheduledDateDue"
            class="form-control"
            required
          />
        </div>
        
        <div class="dialog-actions">
          <button @click="confirmScheduleNewMaintenance" class="btn btn-primary" :disabled="!scheduledDateDue">Schedule</button>
          <button @click="closeScheduleNewDialog" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { get, post, put, del } from '@/utils/api';

// Custom directive for clicking outside
const vClickOutside = {
  beforeMount(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value();
      }
    };
    document.addEventListener('click', el.clickOutsideEvent);
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent);
  }
};

const router = useRouter();
const route = useRoute();

// State variables
const detectorId = ref(route.params.detectorId);
const maintenanceId = ref(route.params.maintenanceId);
const detectorLabel = ref('');
const maintenance = ref({
  detector: detectorId.value,
  maintenance_type: '',
  status: '',
  date_due: new Date().toISOString().split('T')[0],
  date_performed: '',
  performed_by: '',
  notes: ''
});
const maintenanceTypeChoices = ref([]);
const maintenanceStatusChoices = ref([]);
const maintenanceTaskTypeChoices = ref([]);
const maintenanceTasks = ref([]);
const selectedTaskTypes = ref([]);
const showTaskDropdown = ref(false);
const showSuccessDialog = ref(false);
const showStatusChangeDialog = ref(false);
const showMissingDatePerformedWarning = ref(false);
const showScheduleNewDialog = ref(false);
const scheduledDateDue = ref('');
const selectedPreset = ref('');

// Check if we're creating a new maintenance or editing an existing one
const isNewMaintenance = computed(() => !route.params.maintenanceId || route.params.maintenanceId === 'new');

// Determine where to return to based on the referrer
const returnTo = computed(() => {
  // Check if the route has a 'from' parameter indicating where the user came from
  if (route.query.from === 'maintenances') {
    // If coming from the maintenances table, return to the maintenances page
    return '/maintenances';
  } else {
    // Otherwise, return to the detector details page (default behavior)
    return `/detectors/${detectorId.value}`;
  }
});

// Track the initial status when the form loads
const initialStatus = ref('');

// Check if maintenance status is Closed ('CL') and form was loaded with Closed status
const isComplete = computed(() => {
  // Disable inputs only if the form was initially loaded with Closed status
  // Allow editing when the user changes the status to Closed from another status
  return initialStatus.value === 'CL' && maintenance.value.status === 'CL';
});

// Fetch choice options from the API
const fetchChoices = async () => {
  try {
    // Fetch maintenance type choices
    const maintenanceTypeResult = await get('/api/inventory/maintenance-types/');
    if (maintenanceTypeResult.ok) {
      maintenanceTypeChoices.value = maintenanceTypeResult.data;
    }

    // Fetch maintenance status choices
    const maintenanceStatusResult = await get('/api/inventory/maintenance-statuses/');
    if (maintenanceStatusResult.ok) {
      maintenanceStatusChoices.value = maintenanceStatusResult.data;
    }

    // Fetch maintenance task type choices
    const maintenanceTaskTypeResult = await get('/api/inventory/maintenance-task-types/');
    if (maintenanceTaskTypeResult.ok) {
      maintenanceTaskTypeChoices.value = maintenanceTaskTypeResult.data;
    }
  } catch (error) {
    console.error('Error fetching choice options:', error);
  }
};

// Fetch maintenance details if editing existing
const fetchMaintenance = async () => {
  // Only fetch if we're editing an existing maintenance (not creating a new one)
  if (route.params.maintenanceId && route.params.maintenanceId !== 'new') {
    try {
      const result = await get(`/api/inventory/maintenances/${route.params.maintenanceId}/`);
      if (!result.ok) {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
      const data = result.data;
      maintenance.value = {
        ...data,
        detector: detectorId.value, // Ensure detector is always set to the current detector
        date_due: data.date_due ? new Date(data.date_due).toISOString().split('T')[0] : '',
        date_performed: data.date_performed ? new Date(data.date_performed).toISOString().split('T')[0] : ''
      };
    } catch (error) {
      console.error('Error fetching maintenance:', error);
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

// Get task type label from choices
const getTaskTypeLabel = (taskTypeValue) => {
  const choice = maintenanceTaskTypeChoices.value.find(c => c.value === taskTypeValue);
  return choice ? choice.label : taskTypeValue;
};

// Toggle task dropdown
const toggleTaskDropdown = () => {
  if (!isComplete.value) {
    showTaskDropdown.value = !showTaskDropdown.value;
  }
};

// Close task dropdown
const closeTaskDropdown = () => {
  showTaskDropdown.value = false;
};

// Get display text for selected tasks
const getSelectedTasksDisplay = () => {
  if (selectedTaskTypes.value.length === 0) return '';
  return selectedTaskTypes.value
    .map(taskType => {
      const choice = maintenanceTaskTypeChoices.value.find(c => c.value === taskType);
      return choice ? choice.label : taskType;
    })
    .join(', ');
};

// Sync selectedTaskTypes with maintenanceTasks
const syncSelectedTaskTypes = () => {
  selectedTaskTypes.value = maintenanceTasks.value.map(task => task.task_type);
};

// Save tasks after maintenance is saved - delete all existing and recreate selected
const saveTasks = async (maintenanceId) => {
  try {
    // Delete all existing tasks for this maintenance
    for (const task of maintenanceTasks.value) {
      if (task.id) {
        const result = await del(`/api/inventory/maintenancetasks/${task.id}/`);
        if (!result.ok) {
          console.error('Failed to remove task:', task.task_type);
        }
      }
    }

    // Clear local tasks list
    maintenanceTasks.value = [];

    // Add all currently selected tasks
    for (const taskType of selectedTaskTypes.value) {
      const result = await post('/api/inventory/maintenancetasks/', {
        maintenance: maintenanceId,
        task_type: taskType
      });
      if (result.ok) {
        maintenanceTasks.value.push(result.data);
      } else {
        console.error('Failed to add task:', taskType);
      }
    }
  } catch (error) {
    console.error('Error saving tasks:', error);
  }
};

// Fetch maintenance tasks for the current maintenance
const fetchMaintenanceTasks = async () => {
  // Only fetch if we have a maintenance ID (editing existing maintenance)
  if (route.params.maintenanceId && route.params.maintenanceId !== 'new') {
    try {
      const result = await get(`/api/inventory/maintenancetasks/?maintenance=${route.params.maintenanceId}`);
      if (!result.ok) {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
      maintenanceTasks.value = result.data;
      // Sync selected task types with fetched tasks
      syncSelectedTaskTypes();
    } catch (error) {
      console.error('Error fetching maintenance tasks:', error);
    }
  }
};

// Save maintenance function
const saveMaintenance = async () => {
  try {
    // Validate required fields
    if (!maintenance.value.maintenance_type) {
      alert('Maintenance Type is required.');
      return;
    }

    if (!maintenance.value.date_due) {
      alert('Date Due is required.');
      return;
    }

    if (!maintenance.value.status) {
      alert('Status is required.');
      return;
    }

    // If status is Closed, date performed must be set
    if (maintenance.value.status === 'CL' && !maintenance.value.date_performed) {
      showMissingDatePerformedWarning.value = true;
      return;
    }

    // If date performed is set but status is not Closed, ask if user wants to change status
    if (maintenance.value.date_performed && maintenance.value.status !== 'CL') {
      showStatusChangeDialog.value = true;
      return;
    }

    // If we reach here, all required fields are filled and validated
    // Proceed with saving
    await performSave();
  } catch (error) {
    console.error('Error saving maintenance:', error);
    alert('Error saving maintenance: ' + error.message);
  }
};

// Function to handle the actual saving after dialog confirmation
const performSave = async () => {
  try {

    // Convert empty strings to null for date fields
    if (maintenance.value.date_performed === '') {
      maintenance.value.date_performed = null;
    }

    let result;
    let savedMaintenanceId;
    if (isNewMaintenance.value) {
      // Creating a new maintenance
      result = await post('/api/inventory/maintenances/', maintenance.value);
      if (result.ok) {
        savedMaintenanceId = result.data.id;
      }
    } else {
      // Updating an existing maintenance
      savedMaintenanceId = route.params.maintenanceId;
      result = await put(`/api/inventory/maintenances/${route.params.maintenanceId}/`, maintenance.value);
    }

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    // Save tasks after maintenance is saved
    if (savedMaintenanceId) {
      await saveTasks(savedMaintenanceId);
    }

    // Check if status is Closed and date_performed is not null
    if (maintenance.value.status === 'CL' && maintenance.value.date_performed) {
      // Show dialog asking if user wants to schedule a new maintenance
      showScheduleNewDialog.value = true;
    } else {
      // Show success dialog
      showSuccessDialog.value = true;
    }
  } catch (error) {
    console.error('Error saving maintenance:', error);
    alert('Error saving maintenance: ' + error.message);
  }
};

// Function to handle the status change dialog response
const handleStatusChangeDialog = (shouldChange) => {
  if (shouldChange) {
    // Change status to Closed ('CL') and proceed with saving
    maintenance.value.status = 'CL';
    showStatusChangeDialog.value = false;
    performSave();
  } else {
    // User declined, just close the dialog without saving
    showStatusChangeDialog.value = false;
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

// Close missing date performed warning dialog
const closeMissingDatePerformedWarning = () => {
  showMissingDatePerformedWarning.value = false;
};

// Function to handle the schedule new maintenance dialog response
const handleScheduleNewDialog = (shouldSchedule) => {
  if (shouldSchedule) {
    // Calculate date 6 months after the old date performed
    const oldDatePerformed = new Date(maintenance.value.date_performed);
    const sixMonthsAfterOldDate = new Date(oldDatePerformed);
    sixMonthsAfterOldDate.setMonth(sixMonthsAfterOldDate.getMonth() + 6);
    scheduledDateDue.value = sixMonthsAfterOldDate.toISOString().split('T')[0];
    // Reset preset to custom
    selectedPreset.value = '';
    // Show the dialog with the proposed date
    showScheduleNewDialog.value = true;
  } else {
    // Just show the success dialog
    showSuccessDialog.value = true;
  }
};

// Apply preset date selection
const applyPreset = () => {
  if (!selectedPreset.value) {
    return;
  }
  
  const days = parseInt(selectedPreset.value);
  // Calculate from the date performed, not today
  const baseDate = maintenance.value.date_performed ? new Date(maintenance.value.date_performed) : new Date();
  const futureDate = new Date(baseDate);
  const originalDay = baseDate.getDate();
  
  // For month-based presets, calculate by adding months to preserve day of month
  if (days === 30) {
    // 1 Month - add 1 month
    futureDate.setMonth(baseDate.getMonth() + 1);
  } else if (days === 90) {
    // 3 Months - add 3 months
    futureDate.setMonth(baseDate.getMonth() + 3);
  } else if (days === 180) {
    // 6 Months - add 6 months
    futureDate.setMonth(baseDate.getMonth() + 6);
  } else {
    // For other presets (7 days, 365 days), add days
    futureDate.setDate(baseDate.getDate() + days);
  }
  
  // Check if the day rolled over due to invalid day in target month
  // If so, set to last day of the target month
  if (futureDate.getDate() !== originalDay && days >= 30) {
    // Day rolled over, set to last day of target month
    futureDate.setDate(0); // Setting day to 0 gives last day of previous month
  }
  
  scheduledDateDue.value = futureDate.toISOString().split('T')[0];
};

// Confirm and schedule new maintenance
const confirmScheduleNewMaintenance = async () => {
  showScheduleNewDialog.value = false;

  try {
    // Prepare the new maintenance data
    const newMaintenanceData = {
      detector: maintenance.value.detector,
      maintenance_type: maintenance.value.maintenance_type,
      status: 'SC', // Scheduled
      date_due: scheduledDateDue.value,
      date_performed: null,
      performed_by: '',
      notes: ''
    };

    // Create the new maintenance record
    const result = await post('/api/inventory/maintenances/', newMaintenanceData);

    if (result.ok) {
      // Show success dialog
      showSuccessDialog.value = true;
    } else {
      console.error('Failed to schedule new maintenance:', result.data);
      alert('Error scheduling new maintenance: ' + (result.data.message || 'Unknown error'));
    }
  } catch (error) {
    console.error('Error scheduling new maintenance:', error);
    alert('Error scheduling new maintenance: ' + error.message);
  }
};

// Close schedule new dialog without scheduling
const closeScheduleNewDialog = () => {
  showScheduleNewDialog.value = false;
  showSuccessDialog.value = true;
};

// Initialize component
onMounted(async () => {
  // Load choices
  await fetchChoices();

  // Load detector details
  await fetchDetectorDetails();

  // If editing existing maintenance, load its details and tasks
  if (!isNewMaintenance.value) {
    await fetchMaintenance();
    await fetchMaintenanceTasks();
  } else {
    // If creating new maintenance, check for pre-filled data from query parameters
    const { detector, maintenance_type, status, date_due } = route.query;
    if (detector) maintenance.value.detector = parseInt(detector);
    if (maintenance_type) maintenance.value.maintenance_type = maintenance_type;
    if (status) maintenance.value.status = status;
    if (date_due) maintenance.value.date_due = date_due;
  }

  // Set the initial status after all data is loaded
  initialStatus.value = maintenance.value.status;
});

// Watch for route changes to handle pre-filled data
watch(() => route.query, (newQuery) => {
  if (isNewMaintenance.value) {
    const { detector, maintenance_type, status, date_due } = newQuery;
    if (detector) maintenance.value.detector = parseInt(detector);
    if (maintenance_type) maintenance.value.maintenance_type = maintenance_type;
    if (status) maintenance.value.status = status;
    if (date_due) maintenance.value.date_due = date_due;
  }
});
</script>

<style scoped>
.maintenance-edit-page {
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

.maintenance-form {
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

.form-control:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
  opacity: 0.7;
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

.dialog-box .form-group {
  margin: 1.5rem 0;
  text-align: left;
}

.dialog-box .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.dialog-box .form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.dialog-box .form-control:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

.dialog-box select.form-control {
  cursor: pointer;
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

/* Multi-select Dropdown Styles */
.multi-select-dropdown {
  position: relative;
  width: 100%;
}

.multi-select-input {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  min-height: 44px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.multi-select-input:hover {
  border-color: #42b883;
}

.multi-select-input.active {
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

.multi-select-input .placeholder {
  color: #999;
  font-style: italic;
}

.multi-select-input .selected-tasks {
  color: #333;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  transition: transform 0.2s;
  color: #666;
}

.multi-select-input.active .dropdown-arrow {
  transform: rotate(180deg);
}

.multi-select-options {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 250px;
  overflow-y: auto;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  padding: 0.5rem 0;
}

.checkbox-option {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.checkbox-option:hover {
  background-color: #f5f5f5;
}

.checkbox-option input[type="checkbox"] {
  margin-right: 0.75rem;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-option input[type="checkbox"]:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.checkbox-option span {
  flex: 1;
  color: #333;
}

.checkbox-option:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
