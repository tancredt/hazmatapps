<template>
  <div class="add-multiple-detectors-page">
    <div class="page-container">
      <h1>Add Multiple Detectors</h1>

      <div class="form-container">
        <form @submit.prevent="addMultipleDetectors" class="add-multiple-detectors-form">
          <div class="common-fields">
            <h2>Common Fields</h2>
            <div class="form-grid">
              <div class="form-group">
                <label for="model">Model *</label>
                <select id="model" v-model="commonFields.detector_model" required class="form-control">
                  <option value="">Select Model</option>
                  <option v-for="model in detectorModels" :key="model.id" :value="model.id">
                    {{ getModelName(model.id) }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="status">Status *</label>
                <select id="status" v-model="commonFields.status" required class="form-control">
                  <option value="">Select Status</option>
                  <option value="OP">Operational</option>
                  <option value="IS">In Stock</option>
                  <option value="OO">On Order</option>
                  <option value="OF">Offline Repair</option>
                  <option value="DC">Decommissioned</option>
                </select>
              </div>

              <div class="form-group">
                <label for="configuration">Configuration</label>
                <select id="configuration" v-model="commonFields.configuration" class="form-control">
                  <option value="">Select Configuration</option>
                  <option v-for="config in detectorModelConfigurations" :key="config.id" :value="config.id">
                    {{ getConfigurationLabel(config.id) }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="location">Location *</label>
                <select id="location" v-model="commonFields.location" required class="form-control">
                  <option value="">Select Location</option>
                  <option v-for="location in locations" :key="location.id" :value="location.id">
                    {{ getLocationLabel(location.id) }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="purchase_date">Purchase Date</label>
                <input
                  type="date"
                  id="purchase_date"
                  v-model="commonFields.purchase_date"
                  class="form-control"
                >
              </div>

              <div class="form-group">
                <label for="purchase_cost">Purchase Cost ($)</label>
                <input
                  type="number"
                  id="purchase_cost"
                  v-model.number="commonFields.purchase_cost"
                  step="0.01"
                  class="form-control"
                >
              </div>
            </div>
          </div>

          <div class="individual-detectors">
            <h2>Individual Detectors</h2>
            <div class="detector-lines">
              <div v-for="(detector, index) in detectors" :key="index" class="detector-line">
                <div class="detector-form-grid">
                  <div class="form-group">
                    <label :for="`label-${index}`">Label {{ index + 1 }} *</label>
                    <input
                      :id="`label-${index}`"
                      v-model="detector.label"
                      required
                      class="form-control"
                      :placeholder="`Enter label for detector ${index + 1}`"
                    >
                  </div>

                  <div class="form-group serial-with-remove">
                    <label :for="`serial-${index}`">Serial {{ index + 1 }} *</label>
                    <div class="serial-input-container">
                      <input
                        :id="`serial-${index}`"
                        v-model="detector.serial"
                        required
                        class="form-control"
                        :placeholder="`Enter serial for detector ${index + 1}`"
                      >
                      <button type="button" @click="removeDetector(index)" class="remove-btn" title="Remove detector">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <line x1="18" y1="6" x2="6" y2="18"></line>
                          <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="add-detector-button">
              <button type="button" @click="addDetector" class="btn btn-secondary">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                Add Detector
              </button>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">Add Multiple Detectors</button>
            <router-link to="/detectors" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3>Success!</h3>
        <p>{{ successMessage }}</p>
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

    <!-- Progress Dialog -->
    <div v-if="showProgressDialog" class="dialog-overlay">
      <div class="dialog-box" @click.stop>
        <h3>Adding Detectors</h3>
        <p>{{ progressMessage }}</p>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        <p>{{ progressCount }}</p>
        <div class="dialog-actions">
          <button @click="cancelOperation" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { get, post } from '@/utils/api';

const router = useRouter();

// State for related data
const detectorModels = ref([]);
const locations = ref([]);
const detectorModelConfigurations = ref([]);

// State for common fields
const commonFields = ref({
  detector_model: '',
  status: '',
  configuration: '',
  location: '',
  purchase_date: '',
  purchase_cost: null
});

// State for individual detectors
const detectors = ref([{ label: '', serial: '' }]);
const isSubmitting = ref(false);
const showSuccessDialog = ref(false);
const showErrorDialog = ref(false);
const showProgressDialog = ref(false);
const errorMessages = ref([]);
const successMessage = ref('');
const progressMessage = ref('');
const progressPercentage = ref(0);
const progressCount = ref('');
const cancelRequested = ref(false);

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

// Fetch detector model configurations from the API
const fetchDetectorModelConfigurations = async () => {
  try {
    const result = await get('/api/inventory/detectormodelconfigurations/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    detectorModelConfigurations.value = result.data;
  } catch (error) {
    console.error('Error fetching detector model configurations:', error);
  }
};

// Helper functions to get related object labels
const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
};

const getModelName = (modelId) => {
  if (!modelId) return 'N/A';
  const model = detectorModels.value.find(m => m.id === modelId);
  return model ? model.label : 'Unknown Model';
};

const getConfigurationLabel = (configId) => {
  if (!configId) return 'N/A';
  const config = detectorModelConfigurations.value.find(c => c.id === configId);
  if (!config) return 'Unknown Configuration';

  // Get the detector model name using the detector model ID
  const modelName = getModelName(config.detector_model);
  return `${config.label} (${modelName})`;
};

// Add a new detector line
const addDetector = () => {
  detectors.value.push({ label: '', serial: '' });
};

// Remove a detector line
const removeDetector = (index) => {
  if (detectors.value.length > 1) {
    detectors.value.splice(index, 1);
  }
};

// Add multiple detectors function
const addMultipleDetectors = async () => {
  // Validate common fields
  if (!commonFields.value.detector_model) {
    alert('Model is required.');
    return;
  }
  if (!commonFields.value.status) {
    alert('Status is required.');
    return;
  }
  if (!commonFields.value.location) {
    alert('Location is required.');
    return;
  }

  // Validate individual detectors
  for (let i = 0; i < detectors.value.length; i++) {
    const detector = detectors.value[i];
    if (!detector.label.trim()) {
      alert(`Label is required for detector ${i + 1}.`);
      return;
    }
    if (!detector.serial.trim()) {
      alert(`Serial is required for detector ${i + 1}.`);
      return;
    }
  }

  isSubmitting.value = true;
  showProgressDialog.value = true;
  cancelRequested.value = false;
  progressMessage.value = 'Starting to add detectors...';
  progressCount.value = `0 of ${detectors.value.length} completed`;

  try {
    let successfulCount = 0;
    
    for (let i = 0; i < detectors.value.length; i++) {
      if (cancelRequested.value) {
        progressMessage.value = 'Operation cancelled.';
        break;
      }

      const detector = detectors.value[i];
      
      // Prepare the detector data with common fields
      const detectorData = {
        label: detector.label,
        serial: detector.serial,
        status: commonFields.value.status,
        configuration: commonFields.value.configuration || null,
        purchase_date: commonFields.value.purchase_date || null,
        purchase_cost: commonFields.value.purchase_cost ? parseFloat(commonFields.value.purchase_cost) : null,
        location: parseInt(commonFields.value.location),
        detector_model: parseInt(commonFields.value.detector_model)
      };

      progressMessage.value = `Adding detector: ${detector.label} (${detector.serial})`;
      progressPercentage.value = ((i) / detectors.value.length) * 100;
      progressCount.value = `${i} of ${detectors.value.length} completed`;

      try {
        const result = await post('/api/inventory/detectors/', detectorData);

        if (!result.ok) {
          const errorData = result.data;

          // Handle validation errors from the API
          if (result.status === 400) {
            errorMessages.value = [];

            for (const [field, errors] of Object.entries(errorData)) {
              errorMessages.value.push(`${field}: ${errors.join(', ')}`);
            }

            showErrorDialog.value = true;
            showProgressDialog.value = false;
            return; // Stop the process
          } else {
            throw new Error(errorData.detail || `HTTP error! status: ${result.status}`);
          }
        }

        successfulCount++;
      } catch (error) {
        console.error(`Error adding detector ${detector.label}:`, error);
        showProgressDialog.value = false;
        errorMessages.value = [`Failed to add detector "${detector.label}": ${error.message}`];
        showErrorDialog.value = true;
        return; // Stop the process
      }
    }

    if (!cancelRequested.value) {
      progressMessage.value = 'All detectors added successfully!';
      progressPercentage.value = 100;
      progressCount.value = `${successfulCount} of ${detectors.value.length} completed`;
      
      setTimeout(() => {
        showProgressDialog.value = false;
        successMessage.value = `Successfully added ${successfulCount} detector${successfulCount !== 1 ? 's' : ''}.`;
        showSuccessDialog.value = true;
      }, 1000);
    }
  } catch (error) {
    console.error('Error adding multiple detectors:', error);
    showProgressDialog.value = false;
    errorMessage.value = error.message;
    showErrorDialog.value = true;
  } finally {
    isSubmitting.value = false;
  }
};

// Cancel the operation
const cancelOperation = () => {
  cancelRequested.value = true;
  showProgressDialog.value = false;
};

// Close dialogs
const closeDialog = () => {
  showSuccessDialog.value = false;
};

const closeErrorDialog = () => {
  showErrorDialog.value = false;
  errorMessages.value = [];
};

const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push('/detectors');
};

// Initialize component
onMounted(async () => {
  await Promise.all([
    fetchDetectorModels(),
    fetchLocations(),
    fetchDetectorModelConfigurations()
  ]);
});
</script>

