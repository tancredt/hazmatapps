<template>
  <div class="cylindermodel-form-page">
    <div class="page-container">
      <h1>Add New Cylinder Model</h1>
      <div class="form-container">
        <form @submit.prevent="saveCylinderModel" class="cylindermodel-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="part_number">Part Number *</label>
              <input type="text" id="part_number" v-model="cylinderModel.part_number" required class="form-control" placeholder="Enter part number">
            </div>
            <div class="form-group">
              <label for="cylinder_type">Cylinder Type (Gas Config) *</label>
              <select id="cylinder_type" v-model="cylinderModel.cylinder_type" required class="form-control">
                <option value="">Select Cylinder Type</option>
                <option v-for="type in cylinderTypes" :key="type.id" :value="type.id">
                  Type {{ type.id }} ({{ type.cylinder_1_gas }})
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="supplier">Supplier</label>
              <select id="supplier" v-model="cylinderModel.supplier" class="form-control">
                <option value="">Select Supplier</option>
                <option value="AM">AirMet</option><option value="AE">AES</option>
                <option value="MS">MSA</option><option value="DR">Draeger</option>
              </select>
            </div>
            <div class="form-group">
              <label for="volume">Volume</label>
              <select id="volume" v-model="cylinderModel.volume" class="form-control">
                <option value="L034">34 L</option><option value="L065">65 L</option>
                <option value="L103">103 L</option><option value="L112">112 L</option><option value="L552">552 L</option>
              </select>
            </div>
            <div class="form-group">
              <label for="percent_error">Percent Error</label>
              <input type="number" id="percent_error" v-model.number="cylinderModel.percent_error" class="form-control" step="0.01">
            </div>
            <div class="form-group">
              <label for="expiry_months">Expiry Months</label>
              <input type="number" id="expiry_months" v-model.number="cylinderModel.expiry_months" class="form-control" min="0">
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSaving">Add Cylinder Model</button>
            <router-link to="/cylinders" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>
    <!-- Dialogs omitted for brevity, copy from CylinderTypeForm.vue -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { get, post } from '@/utils/api.js';

const router = useRouter();
const cylinderTypes = ref([]);

const cylinderModel = ref({
  part_number: '',
  cylinder_type: '',
  supplier: 'AM',
  volume: 'L034',
  percent_error: null,
  expiry_months: null
});

const isSaving = ref(false);
const showSuccessDialog = ref(false);
const showErrorDialog = ref(false);
const errorMessages = ref([]);

const fetchCylinderTypes = async () => {
  try {
    const result = await get('/api/inventory/cylindertypes/');
    if (result.ok) cylinderTypes.value = result.data;
  } catch (error) { console.error('Error fetching cylinder types:', error); }
};

const saveCylinderModel = async () => {
  isSaving.value = true;
  try {
    if (!cylinderModel.value.part_number) { alert('Part Number is required.'); return; }
    if (!cylinderModel.value.cylinder_type) { alert('Cylinder Type is required.'); return; }

    const data = {
      ...cylinderModel.value,
      percent_error: cylinderModel.value.percent_error || null,
      expiry_months: cylinderModel.value.expiry_months || null
    };

    const result = await post('/api/inventory/cylindermodels/', data);
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
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving cylinder model:', error);
    alert('Error: ' + error.message);
  } finally { isSaving.value = false; }
};

const closeDialogAndReturn = () => { showSuccessDialog.value = false; router.push('/cylinders'); };
const closeDialog = () => { showSuccessDialog.value = false; };
const closeErrorDialog = () => { showErrorDialog.value = false; errorMessages.value = []; };

onMounted(() => { fetchCylinderTypes(); });
</script>
<style scoped>
.cylindertype-form-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-container {
  max-width: 1400px;
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

.cylindertype-form {
  display: flex;
  flex-direction: column;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 0.5rem;
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

.form-checkbox {
  width: auto;
  margin-left: 0.5rem;
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
@media (max-width: 1024px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr); /* Two columns on medium screens */
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr; /* Single column on mobile */
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