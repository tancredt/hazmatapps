<template>
  <div class="update-multiple-sensors-page">
    <div class="page-container">
      <h1>Update Multiple Sensors</h1>

      <div class="info-message">
        <p>Updating {{ selectedSensorIds.length }} sensor(s)</p>
      </div>

      <div class="form-container">
        <form @submit.prevent="updateMultipleSensors" class="sensor-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="order_date">Ordered</label>
              <input
                type="date"
                id="order_date"
                v-model="formData.order_date"
                class="form-control"
              >
              <small class="form-hint">Leave blank to keep existing value</small>
            </div>

            <div class="form-group">
              <label for="receive_date">Received</label>
              <input
                type="date"
                id="receive_date"
                v-model="formData.receive_date"
                class="form-control"
              >
              <small class="form-hint">Leave blank to keep existing value</small>
            </div>

            <div class="form-group">
              <label for="warranty_date">Warranty</label>
              <input
                type="date"
                id="warranty_date"
                v-model="formData.warranty_date"
                class="form-control"
              >
              <small class="form-hint">Leave blank to keep existing value</small>
            </div>

            <div class="form-group">
              <label for="expiry_date">Expiry</label>
              <input
                type="date"
                id="expiry_date"
                v-model="formData.expiry_date"
                class="form-control"
              >
              <small class="form-hint">Leave blank to keep existing value</small>
            </div>

            <div class="form-group">
              <label for="install_date">Install Date</label>
              <input
                type="date"
                id="install_date"
                v-model="formData.install_date"
                class="form-control"
              >
              <small class="form-hint">Leave blank to keep existing value</small>
            </div>

            <div class="form-group">
              <label for="remove_date">Remove Date</label>
              <input
                type="date"
                id="remove_date"
                v-model="formData.remove_date"
                class="form-control"
              >
              <small class="form-hint">Leave blank to keep existing value</small>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Updating Sensors...' : 'Update Sensors' }}
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
import { useRouter, useRoute } from 'vue-router';
import { get, patch } from '@/utils/api';

const router = useRouter();
const route = useRoute();

// State for form data
const formData = ref({
  order_date: '',
  receive_date: '',
  warranty_date: '',
  expiry_date: '',
  install_date: '',
  remove_date: ''
});

// State for selected sensors
const selectedSensorIds = ref([]);

// State for submission
const isSubmitting = ref(false);
const showSuccessDialog = ref(false);
const showErrorDialog = ref(false);
const errorMessages = ref([]);
const successMessage = ref('');

// Initialize component
onMounted(() => {
  // Get selected sensor IDs from route query
  if (route.query.ids) {
    selectedSensorIds.value = route.query.ids.split(',').map(id => parseInt(id));
  }
});

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

// Update multiple sensors
const updateMultipleSensors = async () => {
  isSubmitting.value = true;
  errorMessages.value = [];

  // Check if at least one date field is filled
  if (!formData.value.order_date && 
      !formData.value.receive_date && 
      !formData.value.warranty_date && 
      !formData.value.expiry_date &&
      !formData.value.install_date &&
      !formData.value.remove_date) {
    errorMessages.value.push('At least one date field must be filled.');
    showErrorDialog.value = true;
    isSubmitting.value = false;
    return;
  }

  try {
    // Process requests sequentially to avoid database locking issues with SQLite
    const results = [];
    
    for (const sensorId of selectedSensorIds.value) {
      // Prepare the update data with only the fields that have values
      const updateData = {};
      
      if (formData.value.order_date) {
        updateData.order_date = formData.value.order_date;
      }
      if (formData.value.receive_date) {
        updateData.receive_date = formData.value.receive_date;
      }
      if (formData.value.warranty_date) {
        updateData.warranty_date = formData.value.warranty_date;
      }
      if (formData.value.expiry_date) {
        updateData.expiry_date = formData.value.expiry_date;
      }
      if (formData.value.install_date) {
        updateData.install_date = formData.value.install_date;
      }
      if (formData.value.remove_date) {
        updateData.remove_date = formData.value.remove_date;
      }

      // Skip if no fields to update
      if (Object.keys(updateData).length === 0) {
        continue;
      }

      // Send request and wait for response before proceeding to next
      const result = await patch(`/api/inventory/sensors/${sensorId}/`, updateData);

      results.push({ id: sensorId, response: result });
    }

    // Check if any of the requests failed
    const failedRequests = results.filter(result => !result.response.ok);

    if (failedRequests.length > 0) {
      // Handle errors
      for (const { id, response } of results) {
        if (!response.ok) {
          const errorData = response.data;
          for (const [field, errors] of Object.entries(errorData)) {
            errorMessages.value.push(`Sensor ${id}: ${field}: ${errors.join(', ')}`);
          }
        }
      }

      showErrorDialog.value = true;
    } else {
      // All sensors updated successfully
      successMessage.value = `${results.length} sensor(s) have been updated successfully.`;
      showSuccessDialog.value = true;
    }
  } catch (error) {
    console.error('Error updating multiple sensors:', error);
    errorMessages.value = [`Error updating sensors: ${error.message}`];
    showErrorDialog.value = true;
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.update-multiple-sensors-page {
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

.info-message {
  margin-bottom: 1.5rem;
  padding: 0.75rem;
  background-color: #e7f3ff;
  border: 1px solid #b8daff;
  border-radius: 4px;
}

.info-message p {
  margin: 0;
  color: #004085;
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

.form-hint {
  display: block;
  margin-top: 0.25rem;
  color: #6c757d;
  font-size: 0.875rem;
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