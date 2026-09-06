<template>
  <div class="sensortype-form-page">
    <div class="page-container">
      <h1>Add New Sensor Type</h1>

      <div class="form-container">
        <form @submit.prevent="saveSensorType" class="sensortype-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="part_number">Part Number *</label>
              <input
                type="text"
                id="part_number"
                v-model="sensorType.part_number"
                required
                class="form-control"
                placeholder="Enter part number"
              >
            </div>

            <div class="form-group">
              <label for="manufacturer">Manufacturer</label>
              <select id="manufacturer" v-model="sensorType.manufacturer" class="form-control">
                <option value="HW">Honeywell/Rae</option>
                <option value="MS">MSA</option>
                <option value="DR">Draeger</option>
                <option value="PR">Proengin</option>
                <option value="TS">Thermo Scientific</option>
              </select>
            </div>

            <div class="form-group">
              <label for="sensorgas">Gas</label>
              <select id="sensorgas" v-model="sensorType.sensorgas" class="form-control">
                <option value="">Select Gas</option>
                <option value="CO">CO</option>
                <option value="HS">H2S</option>
                <option value="LE">LEL</option>
                <option value="O2">O2</option>
                <option value="VO">VOC</option>
                <option value="HC">HCN</option>
                <option value="CL">Cl2</option>
                <option value="NH">NH3</option>
                <option value="NO">NO2</option>
                <option value="SO">SO2</option>
                <option value="PH">PH3</option>
                <option value="IR">IR</option>
                <option value="EC">EC</option>
                <option value="PID">PID</option>
              </select>
            </div>

            <div class="form-group">
              <label for="compatible_detectormodels">Compatible Detector Models</label>
              <input
                type="text"
                id="compatible_detectormodels"
                v-model="sensorType.compatible_detectormodels"
                class="form-control"
                placeholder="Enter compatible detector models (comma separated IDs)"
              >
              <small class="form-help-text">Comma-delimited list of Detector Model Names</small>
            </div>

            <div class="form-group">
              <label for="warranty_months">Warranty Months</label>
              <input
                type="number"
                id="warranty_months"
                v-model.number="sensorType.warranty_months"
                class="form-control"
                placeholder="Enter warranty months"
                min="0"
              >
            </div>

            <div class="form-group">
              <label for="expiry_months">Expiry Months</label>
              <input
                type="number"
                id="expiry_months"
                v-model.number="sensorType.expiry_months"
                class="form-control"
                placeholder="Enter expiry months"
                min="0"
              >
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSaving">Add Sensor Type</button>
            <router-link to="/sensors" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3>Success!</h3>
        <p>Sensor type has been added successfully.</p>
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
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { post } from '@/utils/api.js';

const router = useRouter();

// State for the sensor type
const sensorType = ref({
  part_number: '',
  manufacturer: 'HW', // Default to Honeywell/Rae
  sensorgas: '',
  compatible_detectormodels: '',
  warranty_months: null,
  expiry_months: null
});

// State for saving
const isSaving = ref(false);

// State for success dialog
const showSuccessDialog = ref(false);

// State for error dialog
const showErrorDialog = ref(false);
const errorMessages = ref([]);

// Save sensor type function
const saveSensorType = async () => {
  isSaving.value = true;

  try {
    // Client-side validation
    if (!sensorType.value.part_number) {
      alert('Part Number is required.');
      return;
    }

    // Prepare the sensor type data
    const sensorTypeData = {
      ...sensorType.value,
      warranty_months: sensorType.value.warranty_months || null,
      expiry_months: sensorType.value.expiry_months || null
    };

    const result = await post('/api/inventory/sensortypes/', sensorTypeData);

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
    console.error('Error saving sensor type:', error);
    alert('Error saving sensor type: ' + error.message);
  } finally {
    isSaving.value = false;
  }
};

// Close dialog and return to sensors page
const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push('/sensors');
};

// Close dialog functions
const closeDialog = () => {
  showSuccessDialog.value = false;
};

const closeErrorDialog = () => {
  showErrorDialog.value = false;
  errorMessages.value = [];
};
</script>

<style scoped>
.sensortype-form-page {
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

.sensortype-form {
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
  display: block;
  margin-top: 0.25rem;
  font-size: 0.8rem;
  color: #6c757d;
}

.form-checkbox {
  width: auto;
  margin-left: 0.5rem;
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
@media (max-width: 1024px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr); /* Two columns on medium screens */
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr; /* Single column on mobile */
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