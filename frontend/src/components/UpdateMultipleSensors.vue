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

