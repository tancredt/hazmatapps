<template>
  <div class="sensor-details-page">
    <div class="page-container">
      <h1>{{ isNewSensor ? 'Add New Sensor' : 'Edit Sensor' }}</h1>

      <div class="form-container">
        <form @submit.prevent="saveSensor" class="sensor-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="serial">Serial</label>
              <input
                type="text"
                id="serial"
                v-model="sensor.serial"
                class="form-control"
                placeholder="Enter sensor serial"
              >
            </div>

            <div class="form-group">
              <label for="sensor_type">Sensor Type *</label>
              <select id="sensor_type" v-model="sensor.sensor_type" required class="form-control">
                <option value="">Select Sensor Type</option>
                <option v-for="type in sensorTypes" :key="type.id" :value="type.id">
                  {{ getSensorTypeLabel(type.id) }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="status">Status *</label>
              <select id="status" v-model="sensor.status" required class="form-control">
                <option value="">Select Status</option>
                <option value="OP">Operational</option>
                <option value="IS">In Stock</option>
                <option value="OO">On Order</option>
                <option value="DC">Decommissioned</option>
              </select>
            </div>


            <div class="form-group date-pair">
              <div class="date-row">
                <div class="date-field">
                  <label for="order_date">Ordered</label>
                  <input
                    type="date"
                    id="order_date"
                    v-model="sensor.order_date"
                    class="form-control"
                  >
                </div>
                <div class="date-field">
                  <label for="receive_date">Received</label>
                  <input
                    type="date"
                    id="receive_date"
                    v-model="sensor.receive_date"
                    class="form-control"
                  >
                </div>
              </div>
            </div>

            <!-- Empty grid cell to maintain grid alignment -->
            <div class="empty-grid-cell"></div>

            <div class="form-group date-pair">
              <div class="date-row">
                <div class="date-field">
                  <label for="warranty_date">Warranty</label>
                  <input
                    type="date"
                    id="warranty_date"
                    v-model="sensor.warranty_date"
                    class="form-control"
                  >
                </div>
                <div class="date-field">
                  <label for="expiry_date">Expiry</label>
                  <input
                    type="date"
                    id="expiry_date"
                    v-model="sensor.expiry_date"
                    class="form-control"
                  >
                </div>
              </div>
            </div>

            <!-- Empty grid cell to maintain grid alignment -->
            <div class="empty-grid-cell"></div>

            <div class="form-group date-pair">
              <div class="date-row">
                <div class="date-field">
                  <label for="install_date">Install Date</label>
                  <input
                    type="date"
                    id="install_date"
                    v-model="sensor.install_date"
                    class="form-control"
                  >
                </div>
                <div class="date-field">
                  <label for="remove_date">Remove Date</label>
                  <input
                    type="date"
                    id="remove_date"
                    v-model="sensor.remove_date"
                    class="form-control"
                  >
                </div>
              </div>
            </div>

            <!-- Empty grid cell to maintain grid alignment -->
            <div class="empty-grid-cell"></div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSaving">{{ isNewSensor ? 'Add Sensor' : 'Update Sensor' }}</button>
            <router-link to="/sensors" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3>Success!</h3>
        <p>Sensor has been {{ isNewSensor ? 'added' : 'updated' }} successfully.</p>
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
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { get, post, put } from '@/utils/api';

const router = useRouter();
const route = useRoute();

// State for related data
const sensorTypes = ref([]);

// State for the sensor
const sensor = ref({
  serial: '',
  sensor_type: '',
  status: '',
  detector: null,  // Add detector field back but default to null
  order_date: '',
  receive_date: '',
  warranty_date: '',
  expiry_date: '',
  install_date: '',
  remove_date: ''
});

// State for tracking if form has been modified
const isDirty = ref(false);
const originalSensor = ref({});

// State for success dialog
const showSuccessDialog = ref(false);

// State for error dialog
const showErrorDialog = ref(false);
const errorMessages = ref([]);

// State for saving
const isSaving = ref(false);

// Check if we're creating a new sensor or editing an existing one
const isNewSensor = computed(() => route.params.id === 'new');

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


// Fetch sensor data if editing existing sensor
const fetchSensor = async () => {
  try {
    const result = await get(`/api/inventory/sensors/${route.params.id}/`);
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    const data = result.data;
    sensor.value = {
      ...data,
      sensor_type: data.sensor_type || null,
      detector: data.detector || null
    };

    // Store original sensor data for dirty checking
    originalSensor.value = {
      ...data,
      sensor_type: data.sensor_type || null,
      detector: data.detector || null
    };

    // Reset isDirty since we just loaded the data
    isDirty.value = false;
  } catch (error) {
    console.error('Error fetching sensor:', error);
  }
};

// Helper functions to get related object labels using stores
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

// Close dialog function
const closeDialog = () => {
  showSuccessDialog.value = false;
};

// Close error dialog function
const closeErrorDialog = () => {
  showErrorDialog.value = false;
  errorMessages.value = [];
};

// Save sensor function
const saveSensor = async () => {
  isSaving.value = true;

  try {
    // Client-side validation
    if (!sensor.value.sensor_type) {
      alert('Sensor Type is required.');
      return;
    }
    if (!sensor.value.status) {
      alert('Status is required.');
      return;
    }

    let result;
    // Prepare the sensor data with proper data types
    let sensorData = {
      ...sensor.value,
      sensor_type: sensor.value.sensor_type ? parseInt(sensor.value.sensor_type) : null,
      order_date: sensor.value.order_date || null,
      receive_date: sensor.value.receive_date || null,
      warranty_date: sensor.value.warranty_date || null,
      expiry_date: sensor.value.expiry_date || null,
      install_date: sensor.value.install_date || null,
      remove_date: sensor.value.remove_date || null
    };

    if (isNewSensor.value) {
      // When creating a new sensor, explicitly set detector to null
      sensorData.detector = null;

      // Creating a new sensor
      result = await post('/api/inventory/sensors/', sensorData);
    } else {
      // When updating an existing sensor, remove the detector field to leave it unchanged
      delete sensorData.detector;

      // Updating an existing sensor
      result = await put(`/api/inventory/sensors/${route.params.id}/`, sensorData);
    }

    if (!result.ok) {
      // Handle validation errors
      if (result.status === 400) {
        const errorData = result.data;
        errorMessages.value = [];

        for (const [field, errors] of Object.entries(errorData)) {
          errorMessages.value.push(`${field}: ${errors.join(', ')}`);
        }

        showErrorDialog.value = true;
        return; // Don't proceed with success dialog
      } else {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
    }

    // Update original sensor data to match saved data
    originalSensor.value = { ...sensor.value };
    // Reset isDirty flag since changes have been saved
    isDirty.value = false;

    // Show success dialog instead of navigating away
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving sensor:', error);
    alert('Error saving sensor: ' + error.message);
  } finally {
    isSaving.value = false;
  }
};

// Close dialog and return to sensors page
const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push('/sensors');
};

// Initialize component
onMounted(async () => {
  await fetchSensorTypes();

  if (!isNewSensor.value) {
    await fetchSensor();
  }
});
</script>

<style scoped>
.sensor-details-page {
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

.date-pair {
  grid-column: span 2; /* Span across both columns */
}

.date-row {
  display: flex;
  gap: 1rem;
  width: 100%;
}

.date-field {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.date-field label {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.date-field input {
  flex: 1;
}

.empty-grid-cell {
  display: none; /* Hide this cell to maintain grid alignment */
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