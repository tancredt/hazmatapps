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
            <!-- Date fields omitted for brevity, keep them as they were -->
            <div class="form-group date-pair">
              <div class="date-row">
                <div class="date-field"><label for="order_date">Order Date</label><input type="date" id="order_date" v-model="cylinder.order_date" class="form-control"></div>
                <div class="date-field"><label for="receive_date">Receive Date</label><input type="date" id="receive_date" v-model="cylinder.receive_date" class="form-control"></div>
              </div>
            </div>
            <div class="empty-grid-cell"></div>
            <div class="form-group"><label for="expiry_date">Expiry Date</label><input type="date" id="expiry_date" v-model="cylinder.expiry_date" class="form-control"></div>
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
            <button type="button" class="btn btn-secondary" @click="showCylinderModelDetails = true">View Cylinder Models</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Dialogs (Success, Error) omitted for brevity, keep as they were -->

    <CylinderModelDetailsDialog v-if="showCylinderModelDetails" @close="showCylinderModelDetails = false" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { get, post, put } from '@/utils/api';
import CylinderModelDetailsDialog from './CylinderModelDetailsDialog.vue'; // Updated import

const router = useRouter();
const route = useRoute();

const cylinderModels = ref([]); // Changed from cylinderTypes
const locations = ref([]);

const cylinder = ref({
  serial: '',
  cylinder_model: '', // Changed from cylinder_type
  status: '',
  location: '',
  order_date: '', receive_date: '', expiry_date: '', operational_date: '', empty_date: ''
});

const isDirty = ref(false);
const originalCylinder = ref({});
const showSuccessDialog = ref(false);
const showErrorDialog = ref(false);
const errorMessages = ref([]);
const isSaving = ref(false);
const showCylinderModelDetails = ref(false); // Changed from showCylinderTypeDetails

const isNewCylinder = computed(() => route.params.id === 'new');

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

const fetchCylinder = async () => {
  try {
    const result = await get(`/api/inventory/cylinders/${route.params.id}/`);
    if (result.ok) {
      const data = result.data;
      cylinder.value = { ...data, cylinder_model: data.cylinder_model || null, location: data.location || null };
      originalCylinder.value = { ...cylinder.value };
      isDirty.value = false;
    }
  } catch (error) { console.error('Error fetching cylinder:', error); }
};

const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
};

const getCylinderModelLabel = (modelId) => {
  if (!modelId) return 'N/A';
  const model = cylinderModels.value.find(m => m.id === modelId);
  return model ? `${model.part_number} (${getSupplierDisplay(model.supplier)})` : 'Unknown Model';
};

const getSupplierDisplay = (code) => {
  const map = { 'AM': 'AirMet', 'AE': 'AES', 'MS': 'MSA', 'DR': 'Draeger' };
  return map[code] || code;
};

const closeDialog = () => { showSuccessDialog.value = false; };
const closeErrorDialog = () => { showErrorDialog.value = false; errorMessages.value = []; };

const saveCylinder = async () => {
  isSaving.value = true;
  try {
    if (!cylinder.value.cylinder_model) { alert('Cylinder Model is required.'); return; }
    if (!cylinder.value.status) { alert('Status is required.'); return; }
    if (!cylinder.value.location) { alert('Location is required.'); return; }

    const cylinderData = {
      ...cylinder.value,
      cylinder_model: cylinder.value.cylinder_model ? parseInt(cylinder.value.cylinder_model) : null,
      location: cylinder.value.location ? parseInt(cylinder.value.location) : null,
      order_date: cylinder.value.order_date || null, receive_date: cylinder.value.receive_date || null,
      expiry_date: cylinder.value.expiry_date || null, operational_date: cylinder.value.operational_date || null,
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
        errorMessages.value = [];
        for (const [field, errors] of Object.entries(result.data)) {
          errorMessages.value.push(`${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`);
        }
        showErrorDialog.value = true;
        return;
      }
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    originalCylinder.value = { ...cylinder.value };
    isDirty.value = false;
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving cylinder:', error);
    alert('Error saving cylinder: ' + error.message);
  } finally {
    isSaving.value = false;
  }
};

const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push('/cylinders');
};

onMounted(async () => {
  await Promise.all([fetchCylinderModels(), fetchLocations()]);
  if (!isNewCylinder.value) await fetchCylinder();
});
</script>

<style scoped>
.cylinder-details-page {
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
  margin-bottom: 0.5rem;
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
  justify-content: flex-end;
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