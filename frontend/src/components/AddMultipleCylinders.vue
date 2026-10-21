<template>
  <div class="add-multiple-cylinders-page">
    <div class="page-container">
      <h1>Add Multiple Cylinders</h1>
      <div class="form-container">
        <form @submit.prevent="addMultipleCylinders" class="cylinder-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="cylinder_model">Cylinder Model *</label>
              <select id="cylinder_model" v-model="formData.cylinder_model" required class="form-control">
                <option value="">Select Cylinder Model</option>
                <option v-for="model in cylinderModels" :key="model.id" :value="model.id">
                  {{ getCylinderModelLabel(model.id) }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="status">Status *</label>
              <select id="status" v-model="formData.status" required class="form-control">
                <option value="">Select Status</option>
                <option value="OP">Operational</option><option value="IS">In Stock</option>
                <option value="OO">On Order</option><option value="MT">Empty</option>
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
              <input type="date" id="order_date" v-model="formData.order_date" class="form-control">
            </div>
            <div class="form-group">
              <label for="number_of_cylinders">Number of Cylinders *</label>
              <input type="number" id="number_of_cylinders" v-model.number="formData.number_of_cylinders" required min="1" class="form-control">
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">{{ isSubmitting ? 'Adding...' : 'Add Multiple Cylinders' }}</button>
            <router-link to="/cylinders" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>
    <!-- Dialogs omitted for brevity -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { get, post } from '@/utils/api';

const router = useRouter();
const cylinderModels = ref([]);
const locations = ref([]);

const formData = ref({
  cylinder_model: '', // Changed
  status: '', location: '', order_date: '', number_of_cylinders: 1
});

const isSubmitting = ref(false);
const showSuccessDialog = ref(false);
const showErrorDialog = ref(false);
const errorMessages = ref([]);
const successMessage = ref('');

const fetchCylinderModels = async () => {
  try {
    const result = await get('/api/inventory/cylindermodels/');
    if (result.ok) cylinderModels.value = result.data;
  } catch (error) { console.error('Error fetching cylinder models:', error); }
};

const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');
    if (result.ok) locations.value = result.data;
  } catch (error) { console.error('Error fetching locations:', error); }
};

const getLocationLabel = (id) => locations.value.find(l => l.id === id)?.label || 'Unknown';
const getCylinderModelLabel = (id) => cylinderModels.value.find(m => m.id === id)?.part_number || 'Unknown';

const closeDialog = () => { showSuccessDialog.value = false; };
const closeErrorDialog = () => { showErrorDialog.value = false; errorMessages.value = []; };
const closeDialogAndReturn = () => { showSuccessDialog.value = false; router.push('/cylinders'); };

const addMultipleCylinders = async () => {
  isSubmitting.value = true;
  errorMessages.value = [];

  if (!formData.value.cylinder_model) errorMessages.value.push('Cylinder Model is required.');
  if (!formData.value.status) errorMessages.value.push('Status is required.');
  if (!formData.value.location) errorMessages.value.push('Location is required.');
  if (!formData.value.number_of_cylinders || formData.value.number_of_cylinders < 1) errorMessages.value.push('Number must be at least 1.');

  if (errorMessages.value.length > 0) { showErrorDialog.value = true; isSubmitting.value = false; return; }

  try {
    const results = [];
    for (let i = 0; i < formData.value.number_of_cylinders; i++) {
      const cylinderData = {
        cylinder_model: parseInt(formData.value.cylinder_model), // Changed
        status: formData.value.status,
        location: parseInt(formData.value.location),
        order_date: formData.value.order_date || null,
        receive_date: null, expiry_date: null, operational_date: null, empty_date: null, serial: null
      };
      const result = await post('/api/inventory/cylinders/', cylinderData);
      results.push({ index: i, response: result });
    }

    const failedRequests = results.filter(r => !r.response.ok);
    if (failedRequests.length > 0) {
      for (const { index, response } of results) {
        if (!response.ok) {
          const errorData = await response.json();
          for (const [field, errors] of Object.entries(errorData)) {
            errorMessages.value.push(`Cylinder ${index + 1}: ${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`);
          }
        }
      }
      showErrorDialog.value = true;
    } else {
      successMessage.value = `${formData.value.number_of_cylinders} cylinder(s) added successfully.`;
      showSuccessDialog.value = true;
    }
  } catch (error) {
    console.error('Error adding multiple cylinders:', error);
    errorMessages.value = [`Error: ${error.message}`];
    showErrorDialog.value = true;
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(async () => {
  await Promise.all([fetchCylinderModels(), fetchLocations()]);
});
</script>

