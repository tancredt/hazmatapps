<template>
  <div class="cylindertype-form-page">
    <div class="page-container">
      <h1>Add New Cylinder Type (Gas Configuration)</h1>
      <div class="form-container">
        <form @submit.prevent="saveCylinderType" class="cylindertype-form">
          <div class="form-grid">
            <!-- Balance Gas (Required) -->
            <div class="form-group">
              <label for="balance_gas">Balance Gas *</label>
              <select id="balance_gas" v-model="cylinderType.balance_gas" required class="form-control">
                <option value="CO">CO</option>
                <option value="HS">H2S</option>
                <option value="CH">CH4</option>
                <option value="O2">O2</option>
                <option value="IB">Isobutylene</option>
                <option value="HC">HCN</option>
                <option value="N2">N2</option>
              </select>
            </div>

            <!-- Column 1: Cylinder 1 fields (Now Optional) -->
            <div class="form-group">
              <label for="cylinder_1_gas">Gas 1</label>
              <select id="cylinder_1_gas" v-model="cylinderType.cylinder_1_gas" class="form-control">
                <option value="">Select Gas (optional)</option>
                <option value="CO">CO</option>
                <option value="HS">H2S</option>
                <option value="CH">CH4</option>
                <option value="O2">O2</option>
                <option value="IB">Isobutylene</option>
                <option value="HC">HCN</option>
                <option value="N2">N2</option>
              </select>
            </div>
            <div class="form-group">
              <label for="cylinder_1_conc">Conc 1</label>
              <input
                type="number"
                id="cylinder_1_conc"
                v-model.number="cylinderType.cylinder_1_conc"
                class="form-control"
                placeholder="Enter concentration"
                step="0.01"
              >
            </div>
            <div class="form-group">
              <label for="cylinder_1_units">Units 1</label>
              <select id="cylinder_1_units" v-model="cylinderType.cylinder_1_units" class="form-control">
                <option value="">Select Units</option>
                <option value="PM">ppm</option>
                <option value="PV">%v/v</option>
                <option value="PL">%LEL</option>
                <option value="ML">mg/L</option>
              </select>
            </div>

            <!-- Column 2: Cylinder 2 fields -->
            <div class="form-group">
              <label for="cylinder_2_gas">Gas 2</label>
              <select id="cylinder_2_gas" v-model="cylinderType.cylinder_2_gas" class="form-control">
                <option value="">Select Gas (optional)</option>
                <option value="CO">CO</option>
                <option value="HS">H2S</option>
                <option value="CH">CH4</option>
                <option value="O2">O2</option>
                <option value="IB">Isobutylene</option>
                <option value="HC">HCN</option>
                <option value="N2">N2</option>
              </select>
            </div>
            <div class="form-group">
              <label for="cylinder_2_conc">Conc 2</label>
              <input
                type="number"
                id="cylinder_2_conc"
                v-model.number="cylinderType.cylinder_2_conc"
                class="form-control"
                placeholder="Enter concentration"
                step="0.01"
              >
            </div>
            <div class="form-group">
              <label for="cylinder_2_units">Units 2</label>
              <select id="cylinder_2_units" v-model="cylinderType.cylinder_2_units" class="form-control">
                <option value="">Select Units</option>
                <option value="PM">ppm</option>
                <option value="PV">%v/v</option>
                <option value="PL">%LEL</option>
                <option value="ML">mg/L</option>
              </select>
            </div>

            <!-- Column 3: Cylinder 3 fields -->
            <div class="form-group">
              <label for="cylinder_3_gas">Gas 3</label>
              <select id="cylinder_3_gas" v-model="cylinderType.cylinder_3_gas" class="form-control">
                <option value="">Select Gas (optional)</option>
                <option value="CO">CO</option>
                <option value="HS">H2S</option>
                <option value="CH">CH4</option>
                <option value="O2">O2</option>
                <option value="IB">Isobutylene</option>
                <option value="HC">HCN</option>
                <option value="N2">N2</option>
              </select>
            </div>
            <div class="form-group">
              <label for="cylinder_3_conc">Conc 3</label>
              <input
                type="number"
                id="cylinder_3_conc"
                v-model.number="cylinderType.cylinder_3_conc"
                class="form-control"
                placeholder="Enter concentration"
                step="0.01"
              >
            </div>
            <div class="form-group">
              <label for="cylinder_3_units">Units 3</label>
              <select id="cylinder_3_units" v-model="cylinderType.cylinder_3_units" class="form-control">
                <option value="">Select Units</option>
                <option value="PM">ppm</option>
                <option value="PV">%v/v</option>
                <option value="PL">%LEL</option>
                <option value="ML">mg/L</option>
              </select>
            </div>

            <!-- Column 4: Cylinder 4 fields -->
            <div class="form-group">
              <label for="cylinder_4_gas">Gas 4</label>
              <select id="cylinder_4_gas" v-model="cylinderType.cylinder_4_gas" class="form-control">
                <option value="">Select Gas (optional)</option>
                <option value="CO">CO</option>
                <option value="HS">H2S</option>
                <option value="CH">CH4</option>
                <option value="O2">O2</option>
                <option value="IB">Isobutylene</option>
                <option value="HC">HCN</option>
                <option value="N2">N2</option>
              </select>
            </div>
            <div class="form-group">
              <label for="cylinder_4_conc">Conc 4</label>
              <input
                type="number"
                id="cylinder_4_conc"
                v-model.number="cylinderType.cylinder_4_conc"
                class="form-control"
                placeholder="Enter concentration"
                step="0.01"
              >
            </div>
            <div class="form-group">
              <label for="cylinder_4_units">Units 4</label>
              <select id="cylinder_4_units" v-model="cylinderType.cylinder_4_units" class="form-control">
                <option value="">Select Units</option>
                <option value="PM">ppm</option>
                <option value="PV">%v/v</option>
                <option value="PL">%LEL</option>
                <option value="ML">mg/L</option>
              </select>
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSaving">Add Cylinder Type</button>
            <router-link to="/cylinders" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3>Success!</h3>
        <p>Cylinder type has been added successfully.</p>
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
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { post } from '@/utils/api.js';

const router = useRouter();

// State for the cylinder type (Physical attributes removed, gases are optional)
const cylinderType = ref({
  balance_gas: 'CO', // Default to CO
  cylinder_1_gas: '',
  cylinder_1_conc: null,
  cylinder_1_units: '',
  cylinder_2_gas: '',
  cylinder_2_conc: null,
  cylinder_2_units: '',
  cylinder_3_gas: '',
  cylinder_3_conc: null,
  cylinder_3_units: '',
  cylinder_4_gas: '',
  cylinder_4_conc: null,
  cylinder_4_units: ''
});

// State for saving
const isSaving = ref(false);

// State for success dialog
const showSuccessDialog = ref(false);

// State for error dialog
const showErrorDialog = ref(false);
const errorMessages = ref([]);

// Save cylinder type function
const saveCylinderType = async () => {
  isSaving.value = true;

  try {
    // Client-side validation (Only balance_gas is strictly required)
    if (!cylinderType.value.balance_gas) {
      alert('Balance Gas is required.');
      return;
    }

    // Prepare the cylinder type data (ensure empty concentrations are sent as null)
    const cylinderTypeData = {
      ...cylinderType.value,
      cylinder_1_conc: cylinderType.value.cylinder_1_conc || null,
      cylinder_2_conc: cylinderType.value.cylinder_2_conc || null,
      cylinder_3_conc: cylinderType.value.cylinder_3_conc || null,
      cylinder_4_conc: cylinderType.value.cylinder_4_conc || null
    };

    const result = await post('/api/inventory/cylindertypes/', cylinderTypeData);

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

    // Show success dialog
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving cylinder type:', error);
    alert('Error saving cylinder type: ' + error.message);
  } finally {
    isSaving.value = false;
  }
};

// Close dialog and return to cylinders page
const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push('/cylinders');
};

// Close dialog functions
const closeDialog = () => {
  showSuccessDialog.value = false;
};

const closeErrorDialog = () => {
  showErrorDialog.value = false;
  errorMessages.value = [];
};
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