<template>
  <div class="cylinder-details-page">
    <div class="page-container">
      <h1>{{ isNewCylinder ? 'Add New Cylinder' : 'Edit Cylinder' }}</h1>
      <div class="form-container">
        <form @submit.prevent="saveCylinder" class="cylinder-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="serial">Serial</label>
              <input type="text" id="serial" v-model="cylinder.serial" class="form-control" placeholder="Enter cylinder serial">
            </div>
            <div class="form-group">
              <label for="cylinder_model">Cylinder Model *</label>
              <select id="cylinder_model" v-model="cylinder.cylinder_model" required class="form-control">
                <option value="">Select Cylinder Model</option>
                <option v-for="model in cylinderModels" :key="model.id" :value="model.id">
                  {{ getCylinderModelLabel(model.id) }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="status">Status *</label>
              <select id="status" v-model="cylinder.status" required class="form-control">
                <option value="">Select Status</option>
                <option value="OP">Operational</option>
                <option value="IS">In Stock</option>
                <option value="OO">On Order</option>
                <option value="MT">Empty</option>
              </select>
            </div>
            <div class="form-group">
              <label for="location">Location *</label>
              <select id="location" v-model="cylinder.location" required class="form-control">
                <option value="">Select Location</option>
                <option v-for="location in locations" :key="location.id" :value="location.id">
                  {{ getLocationLabel(location.id) }}
                </option>
              </select>
            </div>
            
            <div class="form-group date-pair">
              <div class="date-row">
                <div class="date-field"><label for="order_date">Order Date</label><input type="date" id="order_date" v-model="cylinder.order_date" class="form-control"></div>
                <div class="date-field"><label for="receive_date">Receive Date</label><input type="date" id="receive_date" v-model="cylinder.receive_date" class="form-control"></div>
              </div>
            </div>
            <div class="empty-grid-cell"></div>
            
            <div class="form-group">
              <label for="expiry_date">Expiry Date</label>
              <input type="date" id="expiry_date" v-model="cylinder.expiry_date" class="form-control">
            </div>
            <div class="form-group date-pair">
              <div class="date-row">
                <div class="date-field"><label for="operational_date">Operational Date</label><input type="date" id="operational_date" v-model="cylinder.operational_date" class="form-control"></div>
                <div class="date-field"><label for="empty_date">Empty Date</label><input type="date" id="empty_date" v-model="cylinder.empty_date" class="form-control"></div>
              </div>
            </div>
            <div class="empty-grid-cell"></div>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSaving">{{ isNewCylinder ? 'Add Cylinder' : 'Update Cylinder' }}</button>
            <router-link to="/cylinders" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- SUCCESS DIALOG                             -->
    <!-- ========================================== -->
    <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3>Success!</h3>
        <p>Cylinder has been {{ isNewCylinder ? 'added' : 'updated' }} successfully.</p>
        <div class="dialog-actions">
          <button @click="closeDialogAndReturn" class="btn btn-primary">OK</button>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- ERROR DIALOG                               -->
    <!-- ========================================== -->
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
const cylinderModels = ref([]);
const locations = ref([]);

// State for the cylinder
const cylinder = ref({
  serial: '',
  cylinder_model: '',
  status: '',
  location: '',
  order_date: '',
  receive_date: '',
  expiry_date: '',
  operational_date: '',
  empty_date: ''
});

// State for tracking if form has been modified
const isDirty = ref(false);
const originalCylinder = ref({});

// State for success dialog
const showSuccessDialog = ref(false);

// State for error dialog
const showErrorDialog = ref(false);
const errorMessages = ref([]);

// State for saving
const isSaving = ref(false);

// Check if we're creating a new cylinder or editing an existing one
const isNewCylinder = computed(() => route.params.id === 'new');

// Fetch cylinder models from the API
const fetchCylinderModels = async () => {
  try {
    const result = await get('/api/inventory/cylindermodels/');
    if (result.ok) cylinderModels.value = result.data;
  } catch (error) {
    console.error('Error fetching cylinder models:', error);
  }
};

// Fetch locations from the API
const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');
    if (result.ok) locations.value = result.data;
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
};

// Fetch cylinder data if editing existing cylinder
const fetchCylinder = async () => {
  try {
    const result = await get(`/api/inventory/cylinders/${route.params.id}/`);
    if (result.ok) {
      const data = result.data;
      cylinder.value = {
        ...data,
        cylinder_model: data.cylinder_model || null,
        location: data.location || null
      };
      originalCylinder.value = { ...cylinder.value };
      isDirty.value = false;
    }
  } catch (error) {
    console.error('Error fetching cylinder:', error);
  }
};

// Helper functions
const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
};

const getCylinderModelLabel = (modelId) => {
  if (!modelId) return 'N/A';
  const model = cylinderModels.value.find(m => m.id === modelId);
  return model ? `${model.part_number}` : 'Unknown Model';
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

// Save cylinder function
const saveCylinder = async () => {
  isSaving.value = true;

  try {
    // Client-side validation
    if (!cylinder.value.cylinder_model) { alert('Cylinder Model is required.'); return; }
    if (!cylinder.value.status) { alert('Status is required.'); return; }
    if (!cylinder.value.location) { alert('Location is required.'); return; }

    // Prepare the cylinder data with proper data types
    const cylinderData = {
      ...cylinder.value,
      cylinder_model: cylinder.value.cylinder_model ? parseInt(cylinder.value.cylinder_model) : null,
      location: cylinder.value.location ? parseInt(cylinder.value.location) : null,
      order_date: cylinder.value.order_date || null,
      receive_date: cylinder.value.receive_date || null,
      expiry_date: cylinder.value.expiry_date || null,
      operational_date: cylinder.value.operational_date || null,
      empty_date: cylinder.value.empty_date || null
    };

    let result;
    if (isNewCylinder.value) {
      result = await post('/api/inventory/cylinders/', cylinderData);
    } else {
      result = await put(`/api/inventory/cylinders/${route.params.id}/`, cylinderData);
    }

    if (!result.ok) {
      if (result.status === 400) {
        const errorData = result.data;
        errorMessages.value = [];
        for (const [field, errors] of Object.entries(errorData)) {
          if (Array.isArray(errors)) {
            errorMessages.value.push(`${field}: ${errors.join(', ')}`);
          } else {
            errorMessages.value.push(`${field}: ${errors}`);
          }
        }
        showErrorDialog.value = true;
        return;
      } else {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
    }

    // Update original cylinder data to match saved data
    originalCylinder.value = { ...cylinder.value };
    isDirty.value = false;

    // 🎉 SHOW SUCCESS DIALOG INSTEAD OF NAVIGATING AWAY
    showSuccessDialog.value = true;

  } catch (error) {
    console.error('Error saving cylinder:', error);
    alert('Error saving cylinder: ' + error.message);
  } finally {
    isSaving.value = false;
  }
};

// Close dialog and return to cylinders page
const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push('/cylinders');
};

// Initialize component
onMounted(async () => {
  await Promise.all([
    fetchCylinderModels(),
    fetchLocations()
  ]);

  if (!isNewCylinder.value) {
    await fetchCylinder();
  }
});
</script>

