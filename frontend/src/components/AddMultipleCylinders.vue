<template>
  <div class="add-multiple-cylinders-page">
    <div class="page-container">
      <h1>Add Multiple Cylinders</h1>

      <div class="form-container">
        <form @submit.prevent="addMultipleCylinders" class="cylinder-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="cylinder_type">Cylinder Type *</label>
              <select id="cylinder_type" v-model="formData.cylinder_type" required class="form-control">
                <option value="">Select Cylinder Type</option>
                <option v-for="type in cylinderTypes" :key="type.id" :value="type.id">
                  {{ getCylinderTypeLabel(type.id) }}
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
                <option value="MT">Empty</option>
              </select>
            </div>

            <div class="form-group">
              <label for="location">Location *</label>
              <select id="location" v-model="formData.location" required class="form-control">
                <option value="">Select Location</option>
                <option v-for="location in locations" :key="location.id" :value="location.id">
                  {{ getLocationLabel(location.id) }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="order_date">Order Date</label>
              <input
                type="date"
                id="order_date"
                v-model="formData.order_date"
                class="form-control"
              >
            </div>

            <div class="form-group">
              <label for="number_of_cylinders">Number of Cylinders *</label>
              <input
                type="number"
                id="number_of_cylinders"
                v-model.number="formData.number_of_cylinders"
                required
                min="1"
                class="form-control"
                placeholder="Enter number of cylinders to add"
              >
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Adding Cylinders...' : 'Add Multiple Cylinders' }}
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
import { useRouter } from 'vue-router';
import { get, post } from '@/utils/api';

const router = useRouter();

// State for related data
const cylinderTypes = ref([]);
const locations = ref([]);

// State for form data
const formData = ref({
  cylinder_type: '',
  status: '',
  location: '',
  order_date: '',
  number_of_cylinders: 1
});

// State for submission
const isSubmitting = ref(false);
const showSuccessDialog = ref(false);
const showErrorDialog = ref(false);
const errorMessages = ref([]);
const successMessage = ref('');

// Fetch cylinder types from the API
const fetchCylinderTypes = async () => {
  try {
    const result = await get('/api/inventory/cylindertypes/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    cylinderTypes.value = result.data;
  } catch (error) {
    console.error('Error fetching cylinder types:', error);
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

// Helper functions to get related object labels
const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
};

const getCylinderTypeLabel = (cylinderTypeId) => {
  if (!cylinderTypeId) return 'N/A';
  const cylinderType = cylinderTypes.value.find(ct => ct.id === cylinderTypeId);
  return cylinderType ? cylinderType.part_number : 'Unknown Cylinder Type';
};

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

// Add multiple cylinders
const addMultipleCylinders = async () => {
  isSubmitting.value = true;
  errorMessages.value = [];

  // Client-side validation
  if (!formData.value.cylinder_type) {
    errorMessages.value.push('Cylinder Type is required.');
  }
  if (!formData.value.status) {
    errorMessages.value.push('Status is required.');
  }
  if (!formData.value.location) {
    errorMessages.value.push('Location is required.');
  }
  if (!formData.value.number_of_cylinders || formData.value.number_of_cylinders < 1) {
    errorMessages.value.push('Number of Cylinders must be at least 1.');
  }

  if (errorMessages.value.length > 0) {
    showErrorDialog.value = true;
    isSubmitting.value = false;
    return;
  }

  try {
    // Process requests sequentially to avoid database locking issues with SQLite
    const results = [];

    for (let i = 0; i < formData.value.number_of_cylinders; i++) {
      // Prepare the cylinder data with proper data types
      const cylinderData = {
        cylinder_type: parseInt(formData.value.cylinder_type),
        status: formData.value.status,
        location: parseInt(formData.value.location),
        order_date: formData.value.order_date || null,
        receive_date: null,
        expiry_date: null,
        operational_date: null,
        empty_date: null,
        serial: null  // Serial can be null initially
      };

      // Send request and wait for response before proceeding to next
      const result = await post('/api/inventory/cylinders/', cylinderData);

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
            errorMessages.value.push(`Cylinder ${index + 1}: ${field}: ${errors.join(', ')}`);
          }
        }
      }

      showErrorDialog.value = true;
    } else {
      // All cylinders created successfully
      successMessage.value = `${formData.value.number_of_cylinders} cylinder(s) have been added successfully.`;
      showSuccessDialog.value = true;
    }
  } catch (error) {
    console.error('Error adding multiple cylinders:', error);
    errorMessages.value = [`Error adding cylinders: ${error.message}`];
    showErrorDialog.value = true;
  } finally {
    isSubmitting.value = false;
  }
};

// Initialize component
onMounted(async () => {
  await Promise.all([
    fetchCylinderTypes(),
    fetchLocations()
  ]);
});
</script>

<style scoped>
.add-multiple-cylinders-page {
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

.cylinder-form {
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