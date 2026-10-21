<template>
  <div class="update-multiple-cylinders-page">
    <div class="page-container">
      <h1>Update Multiple Cylinders</h1>

      <div class="info-message">
        <p>Updating {{ selectedCylinderIds.length }} cylinder(s)</p>
      </div>

      <div class="form-container">
        <form @submit.prevent="updateMultipleCylinders" class="cylinder-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="order_date">Order Date</label>
              <input
                type="date"
                id="order_date"
                v-model="formData.order_date"
                class="form-control"
              >
              <small class="form-hint">Leave blank to keep existing value</small>
            </div>

            <div class="form-group">
              <label for="receive_date">Receive Date</label>
              <input
                type="date"
                id="receive_date"
                v-model="formData.receive_date"
                class="form-control"
              >
              <small class="form-hint">Leave blank to keep existing value</small>
            </div>

            <div class="form-group">
              <label for="expiry_date">Expiry Date</label>
              <input
                type="date"
                id="expiry_date"
                v-model="formData.expiry_date"
                class="form-control"
              >
              <small class="form-hint">Leave blank to keep existing value</small>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Updating Cylinders...' : 'Update Cylinders' }}
            </button>
            <router-link to="/cylinders" class="btn btn-secondary">Cancel</router-link>
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
  expiry_date: ''
});

// State for selected cylinders
const selectedCylinderIds = ref([]);

// State for submission
const isSubmitting = ref(false);
const showSuccessDialog = ref(false);
const showErrorDialog = ref(false);
const errorMessages = ref([]);
const successMessage = ref('');

// Initialize component
onMounted(() => {
  // Get selected cylinder IDs from route query
  if (route.query.ids) {
    selectedCylinderIds.value = route.query.ids.split(',').map(id => parseInt(id));
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

// Close dialog and return to cylinders page
const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push('/cylinders');
};

// Update multiple cylinders
const updateMultipleCylinders = async () => {
  isSubmitting.value = true;
  errorMessages.value = [];

  // Check if at least one date field is filled
  if (!formData.value.order_date && !formData.value.receive_date && !formData.value.expiry_date) {
    errorMessages.value.push('At least one date field must be filled.');
    showErrorDialog.value = true;
    isSubmitting.value = false;
    return;
  }

  try {
    // Process requests sequentially to avoid database locking issues with SQLite
    const results = [];
    
    for (const cylinderId of selectedCylinderIds.value) {
      // Prepare the update data with only the fields that have values
      const updateData = {};
      
      if (formData.value.order_date) {
        updateData.order_date = formData.value.order_date;
      }
      if (formData.value.receive_date) {
        updateData.receive_date = formData.value.receive_date;
      }
      if (formData.value.expiry_date) {
        updateData.expiry_date = formData.value.expiry_date;
      }

      // Skip if no fields to update
      if (Object.keys(updateData).length === 0) {
        continue;
      }

      // Send request and wait for response before proceeding to next
      const result = await patch(`/api/inventory/cylinders/${cylinderId}/`, updateData);

      results.push({ id: cylinderId, response: result });
    }

    // Check if any of the requests failed
    const failedRequests = results.filter(result => !result.response.ok);

    if (failedRequests.length > 0) {
      // Handle errors
      for (const { id, response } of results) {
        if (!response.ok) {
          const errorData = response.data;
          for (const [field, errors] of Object.entries(errorData)) {
            errorMessages.value.push(`Cylinder ${id}: ${field}: ${errors.join(', ')}`);
          }
        }
      }

      showErrorDialog.value = true;
    } else {
      // All cylinders updated successfully
      successMessage.value = `${results.length} cylinder(s) have been updated successfully.`;
      showSuccessDialog.value = true;
    }
  } catch (error) {
    console.error('Error updating multiple cylinders:', error);
    errorMessages.value = [`Error updating cylinders: ${error.message}`];
    showErrorDialog.value = true;
  } finally {
    isSubmitting.value = false;
  }
};
</script>

