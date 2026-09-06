<template>
  <div class="add-multiple-sensors-page">
    <div class="page-container">
      <h1>Add Multiple Sensors</h1>

      <div class="form-container">
        <form @submit.prevent="addMultipleSensors" class="sensor-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="sensor_type">Sensor Type *</label>
              <select id="sensor_type" v-model="formData.sensor_type" required class="form-control">
                <option value="">Select Sensor Type</option>
                <option v-for="type in sensorTypes" :key="type.id" :value="type.id">
                  {{ getSensorTypeLabel(type.id) }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="status">Status *</label>
              <select id="status" v-model="formData.status" required class="form-control">
                <option value="">Select Status</option>
                <option value="OP">Operational</option>
                <option value="IS">In Stock</option>
                <option value="OO">On Order</option>
                <option value="DC">Decommissioned</option>
              </select>
            </div>

            <div class="form-group">
              <label for="order_date">Ordered</label>
              <input
                type="date"
                id="order_date"
                v-model="formData.order_date"
                class="form-control"
              >
            </div>

            <div class="form-group">
              <label for="number_of_sensors">Number of Sensors *</label>
              <input
                type="number"
                id="number_of_sensors"
                v-model.number="formData.number_of_sensors"
                required
                min="1"
                class="form-control"
                placeholder="Enter number of sensors to add"
              >
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Adding Sensors...' : 'Add Multiple Sensors' }}
            </button>
            <router-link to="/sensors" class="btn btn-secondary">Cancel</router-link>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { get, post } from '@/utils/api';

const router = useRouter();

// State for related data
const sensorTypes = ref([]);

// State for form data
const formData = ref({
  sensor_type: '',
  status: '',
  order_date: '',
  number_of_sensors: 1
});

// State for submission
const isSubmitting = ref(false);
const showSuccessDialog = ref(false);
const showErrorDialog = ref(false);
const errorMessages = ref([]);
const successMessage = ref('');

// Fetch sensor types from the API
const fetchSensorTypes = async () => {
  try {
    const result = await get('/api/inventory/sensortypes/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    sensorTypes.value = result.data;
  } catch (error) {
    console.error('Error fetching sensor types:', error);
  }
};

// Helper functions to get related object labels
const sensorGasLabels = {
  CO: 'CO', HS: 'H2S', LE: 'LEL', O2: 'O2', VO: 'VOC', HC: 'HCN',
  CL: 'Cl2', PH: 'PH3', SO: 'SO2', NO: 'NO2', C2: 'CO2', NH: 'NH3',
  ET: 'ETO', CS: 'CO/H2S'
};

const getSensorTypeLabel = (sensorTypeId) => {
  if (!sensorTypeId) return 'N/A';
  const sensorType = sensorTypes.value.find(st => st.id === sensorTypeId);
  if (!sensorType) return 'Unknown Sensor Type';
  const parts = [sensorType.part_number];
  if (sensorType.sensorgas) parts.push(`(${sensorGasLabels[sensorType.sensorgas] || sensorType.sensorgas})`);
  if (sensorType.compatible_detectormodels) parts.push(`[${sensorType.compatible_detectormodels}]`);
  return parts.join(' ');
};

// Close dialogs
const closeDialog = () => {
  showSuccessDialog.value = false;
};

const closeErrorDialog = () => {
  showErrorDialog.value = false;
  errorMessages.value = [];
};

// Close dialog and return to sensors page
const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push('/sensors');
};

// Add multiple sensors
const addMultipleSensors = async () => {
  isSubmitting.value = true;
  errorMessages.value = [];

  // Client-side validation
  if (!formData.value.sensor_type) {
    errorMessages.value.push('Sensor Type is required.');
  }
  if (!formData.value.status) {
    errorMessages.value.push('Status is required.');
  }
  if (!formData.value.number_of_sensors || formData.value.number_of_sensors < 1) {
    errorMessages.value.push('Number of Sensors must be at least 1.');
  }

  if (errorMessages.value.length > 0) {
    showErrorDialog.value = true;
    isSubmitting.value = false;
    return;
  }

  try {
    // Process requests sequentially to avoid database locking issues with SQLite
    const results = [];
    
    for (let i = 0; i < formData.value.number_of_sensors; i++) {
      // Prepare the sensor data with proper data types
      const sensorData = {
        sensor_type: parseInt(formData.value.sensor_type),
        status: formData.value.status,
        order_date: formData.value.order_date || null,
        receive_date: null,
        warranty_date: null,
        expiry_date: null,
        install_date: null,
        remove_date: null,
        serial: null,  // Serial can be null initially
        detector: null // Set detector to null as per requirements
      };

      // Send request and wait for response before proceeding to next
      const result = await post('/api/inventory/sensors/', sensorData);

      results.push({ index: i, response: result });
    }

    // Check if any of the requests failed
    const failedRequests = results.filter(result => !result.response.ok);
    
    if (failedRequests.length > 0) {
      // Handle errors
      for (const { index, response } of results) {
        if (!response.ok) {
          const errorData = await response.json();
          for (const [field, errors] of Object.entries(errorData)) {
            errorMessages.value.push(`Sensor ${index + 1}: ${field}: ${errors.join(', ')}`);
          }
        }
      }

      showErrorDialog.value = true;
    } else {
      // All sensors created successfully
      successMessage.value = `${formData.value.number_of_sensors} sensor(s) have been added successfully.`;
      showSuccessDialog.value = true;
    }
  } catch (error) {
    console.error('Error adding multiple sensors:', error);
    errorMessages.value = [`Error adding sensors: ${error.message}`];
    showErrorDialog.value = true;
  } finally {
    isSubmitting.value = false;
  }
};

// Initialize component
onMounted(async () => {
  await fetchSensorTypes();
});
</script>

<style scoped>
.add-multiple-sensors-page {
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

.sensor-form {
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
  margin-bottom: 1rem;
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

  .page-container {
    padding: 0 1rem;
    margin: 1rem auto;
  }

  .form-container {
    padding: 1rem;
  }
}
</style>