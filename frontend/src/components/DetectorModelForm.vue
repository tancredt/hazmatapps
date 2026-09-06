<template>
  <div class="detectormodel-form-page">

    <div class="page-container">
      <h1>Add New Detector Model</h1>

      <div class="form-container">
        <form @submit.prevent="saveDetectorModel" class="detectormodel-form">
          <div class="form-row">
            <div class="form-group">
              <label for="manufacturer">Manufacturer</label>
              <select id="manufacturer" v-model="detectorModel.manufacturer" class="form-control">
                <option value="">Select Manufacturer</option>
                <option v-for="choice in manufacturerChoices" :key="choice.value" :value="choice.value">
                  {{ choice.label }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="detector_type">Detector Type *</label>
              <select id="detector_type" v-model="detectorModel.detector_type" required class="form-control">
                <option value="">Select Detector Type</option>
                <option v-for="choice in detectorTypeChoices" :key="choice.value" :value="choice.value">
                  {{ choice.label }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="supplier">Supplier</label>
              <select id="supplier" v-model="detectorModel.supplier" class="form-control">
                <option value="">Select Supplier</option>
                <option v-for="choice in supplierChoices" :key="choice.value" :value="choice.value">
                  {{ choice.label }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="label">Label *</label>
              <input
                type="text"
                id="label"
                v-model="detectorModel.label"
                required
                class="form-control"
                placeholder="Enter label"
              >
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="part_number">Part Number</label>
              <input
                type="text"
                id="part_number"
                v-model="detectorModel.part_number"
                class="form-control"
                placeholder="Enter part number"
              >
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Save Detector Model</button>
            <router-link to="/detectors" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3>Success!</h3>
        <p>Detector model has been saved successfully.</p>
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
import { get, post } from '@/utils/api.js';

const router = useRouter();

// State for the detector model
const detectorModel = ref({
  manufacturer: '',
  detector_type: '',
  supplier: '',
  label: '',
  part_number: ''
});

// State for success dialog
const showSuccessDialog = ref(false);

// State for error dialog
const showErrorDialog = ref(false);
const errorMessages = ref([]);

// Choices for dropdowns
const manufacturerChoices = ref([]);
const detectorTypeChoices = ref([]);
const supplierChoices = ref([]);

// Fetch choice options from the API
const fetchChoices = async () => {
  try {
    // Fetch manufacturer choices
    const manufacturerResult = await get('/api/inventory/manufacturers/');
    if (manufacturerResult.ok) {
      manufacturerChoices.value = manufacturerResult.data;
    }

    // Fetch detector type choices
    const detectorTypeResult = await get('/api/inventory/detector-types/');
    if (detectorTypeResult.ok) {
      detectorTypeChoices.value = detectorTypeResult.data;
    }

    // Fetch supplier choices
    const supplierResult = await get('/api/inventory/suppliers/');
    if (supplierResult.ok) {
      supplierChoices.value = supplierResult.data;
    }
  } catch (error) {
    console.error('Error fetching choice options:', error);
  }
};

// Save detector model function
const saveDetectorModel = async () => {
  try {
    const result = await post('/api/inventory/detectormodels/', detectorModel.value);

    if (!result.ok) {
      if (result.status === 400) {
        const errorData = result.data;
        errorMessages.value = [];

        for (const [field, errors] of Object.entries(errorData)) {
          if (Array.isArray(errors)) {
            errorMessages.value.push(`${field}: ${errors.join(', ')}`);
          } else {
            // Handle cases where errors is not an array
            errorMessages.value.push(`${field}: ${errors}`);
          }
        }

        showErrorDialog.value = true;
        return; // Don't proceed with success dialog
      } else {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
    }

    // Show success dialog
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving detector model:', error);
    alert('Error saving detector model: ' + error.message);
  }
};

// Close dialog and return to detectors page
const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push('/detectors');
};

// Close dialog function
const closeDialog = () => {
  showSuccessDialog.value = false;
};

// Close error dialog function
const closeErrorDialog = () => {
  showErrorDialog.value = false;
  errorMessages.value = [];
};

// Initialize component
onMounted(async () => {
  await fetchChoices();
});
</script>

<style scoped>
.detectormodel-form-page {
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

.detectormodel-form {
  display: flex;
  flex-direction: column;
}

.form-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 200px;
  flex-basis: calc(50% - 0.75rem); /* Two columns by default */
}

/* On smaller screens, make form groups full width */
@media (max-width: 768px) {
  .form-group {
    flex-basis: 100%;
  }
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
}

.form-control:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
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

.btn-primary:hover {
  background-color: #36966d;
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
</style>