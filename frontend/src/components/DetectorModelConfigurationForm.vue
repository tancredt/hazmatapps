<template>
  <div class="detectormodelconfiguration-form-page">

    <div class="page-container">
      <h1>Add New Detector Model Configuration</h1>

      <div class="form-container">
        <form @submit.prevent="saveConfiguration" class="detectormodelconfiguration-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="detector_model">Detector Model *</label>
              <select id="detector_model" v-model="configuration.detector_model" required class="form-control">
                <option value="">Select Detector Model</option>
                <option v-for="model in detectorModels" :key="model.id" :value="model.id">
                  {{ getModelName(model.id) }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="label">Label *</label>
              <input
                type="text"
                id="label"
                v-model="configuration.label"
                required
                class="form-control"
                placeholder="Enter configuration label"
              >
            </div>

            <div class="form-group full-width">
              <label for="sensor_gases">Sensor Gases *</label>
              <select
                id="sensor_gases"
                v-model="configuration.sensor_gases"
                required
                multiple
                class="form-control"
                style="min-height: 150px;"
              >
                <option v-for="gas in sensorGasChoices" :key="gas.value" :value="gas.value">
                  {{ gas.label }}
                </option>
              </select>
              <p class="form-help-text">Hold Ctrl/Cmd to select multiple gases. They will be saved as a comma-separated list.</p>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Save Configuration</button>
            <router-link to="/detectors" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3>Success!</h3>
        <p>Detector model configuration has been saved successfully.</p>
        <div class="dialog-actions">
          <button @click="closeDialogAndReturn" class="btn btn-primary">OK</button>
        </div>
      </div>
    </div>

    <!-- Error Dialog -->
    <div v-if="showErrorDialog" class="dialog-overlay" @click="closeErrorDialog">
      <div class="dialog-box" @click.stop>
        <h3>Validation Errors</h3>
        <div class="error-list">
          <p v-for="(error, index) in errorMessages" :key="index" class="error-item">
            {{ error }}
          </p>
        </div>
        <div class="dialog-actions">
          <button @click="closeErrorDialog" class="btn btn-primary">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { post, get } from '@/utils/api.js';

const router = useRouter();

// State for the configuration
const configuration = ref({
  detector_model: null,
  label: '',
  sensor_gases: ''
});

// State for related data
const detectorModels = ref([]);

// Sensor gas choices (matching the SensorGas model choices)
const sensorGasChoices = [
  { value: 'CO', label: 'CO' },
  { value: 'HS', label: 'H2S' },
  { value: 'LE', label: 'LEL' },
  { value: 'O2', label: 'O2' },
  { value: 'VO', label: 'VOC' },
  { value: 'HC', label: 'HCN' },
  { value: 'CL', label: 'Cl2' },
  { value: 'PH', label: 'PH3' },
  { value: 'SO', label: 'SO2' },
  { value: 'NO', label: 'NO2' },
  { value: 'C2', label: 'CO2' },
  { value: 'NH', label: 'NH3' },
  { value: 'ET', label: 'ETO' }
];

// State for success dialog
const showSuccessDialog = ref(false);

// State for error dialog
const showErrorDialog = ref(false);
const errorMessages = ref([]);

// Fetch detector models from the API
const fetchDetectorModels = async () => {
  try {
    const result = await get('/api/inventory/detectormodels/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    detectorModels.value = result.data;
  } catch (error) {
    console.error('Error fetching detector models:', error);
  }
};

// Get model name function
const getModelName = (modelId) => {
  if (!modelId) return 'N/A';
  const model = detectorModels.value.find(m => m.id === modelId);
  return model ? model.label : 'Unknown Model';
};

// Save configuration function
const saveConfiguration = async () => {
  try {
    // Convert the array of selected gases to a comma-separated string
    const payload = {
      ...configuration.value,
      sensor_gases: Array.isArray(configuration.value.sensor_gases) 
        ? configuration.value.sensor_gases.join(',') 
        : configuration.value.sensor_gases
    };

    const result = await post('/api/inventory/detectormodelconfigurations/', payload);

    if (!result.ok) {
      const errorData = result.data;
      errorMessages.value = [];

      for (const [field, errors] of Object.entries(errorData)) {
        errorMessages.value.push(`${field}: ${errors.join(', ')}`);
      }

      showErrorDialog.value = true;
      return;
    }

    // Show success dialog
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving configuration:', error);
    alert('Error saving configuration: ' + error.message);
  }
};

// Close dialog and return to detectors page
const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push('/detectors');
};

// Close dialog functions
const closeDialog = () => {
  showSuccessDialog.value = false;
};

const closeErrorDialog = () => {
  showErrorDialog.value = false;
  errorMessages.value = [];
};

// Initialize component
onMounted(async () => {
  await fetchDetectorModels();
});
</script>

<style scoped>
.detectormodelconfiguration-form-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
  flex: 1;
}

h1 {
  color: #2c3e50;
  margin-bottom: 2rem;
}

.form-container {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.detectormodelconfiguration-form {
  display: flex;
  flex-direction: column;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 0.5rem;
  min-width: 0; /* Allows flex/grid items to shrink below content size */
}

.form-group.full-width {
  grid-column: span 2; /* Span across both columns */
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

.form-control:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

.form-help-text {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #666;
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

.error-list {
  max-height: 200px;
  overflow-y: auto;
  margin: 1rem 0;
  padding: 0.5rem;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.error-item {
  margin: 0.25rem 0;
  color: #721c24;
  font-weight: 500;
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