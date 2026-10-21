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

