<template>
  <div class="cylinder-type-details-dialog">
    <div class="dialog-overlay" @click="$emit('close')">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>Cylinder Type Details</h3>
          <button class="close-btn" @click="$emit('close')">&times;</button>
        </div>

        <div class="dialog-body">
          <div v-if="loading" class="loading">Loading cylinder types...</div>

          <div v-else-if="cylinderTypes.length === 0" class="no-data">No cylinder types found</div>

          <div v-else class="cylinder-types-list">
            <div
              v-for="cylinderType in cylinderTypes"
              :key="cylinderType.id"
              class="cylinder-type-card"
            >
              <h4>{{ cylinderType.part_number }}</h4>

              <div class="summary-row">
                <div class="summary-item">
                  <strong>Supplier:</strong> {{ getSupplierDisplay(cylinderType.supplier) }}
                </div>
                <div class="summary-item">
                  <strong>Volume:</strong> {{ getVolumeDisplay(cylinderType.volume) }}
                </div>
                <div class="summary-item">
                  <strong>Active:</strong> {{ cylinderType.active ? 'Yes' : 'No' }}
                </div>
              </div>

              <div class="gases-section">
                <div class="gas-item">
                  <strong>{{ getGasDisplay(cylinderType.cylinder_1_gas) }}</strong>: {{ cylinderType.cylinder_1_conc }} {{ getUnitDisplay(cylinderType.cylinder_1_units) }}
                </div>
                <div v-if="cylinderType.cylinder_2_gas" class="gas-item">
                  <strong>{{ getGasDisplay(cylinderType.cylinder_2_gas) }}</strong>: {{ cylinderType.cylinder_2_conc }} {{ getUnitDisplay(cylinderType.cylinder_2_units) }}
                </div>
                <div v-if="cylinderType.cylinder_3_gas" class="gas-item">
                  <strong>{{ getGasDisplay(cylinderType.cylinder_3_gas) }}</strong>: {{ cylinderType.cylinder_3_conc }} {{ getUnitDisplay(cylinderType.cylinder_3_units) }}
                </div>
                <div v-if="cylinderType.cylinder_4_gas" class="gas-item">
                  <strong>{{ getGasDisplay(cylinderType.cylinder_4_gas) }}</strong>: {{ cylinderType.cylinder_4_conc }} {{ getUnitDisplay(cylinderType.cylinder_4_units) }}
                </div>
              </div>

              <div class="extra-info" v-if="cylinderType.balance_gas || cylinderType.percent_error || cylinderType.expiry_months">
                <div v-if="cylinderType.balance_gas" class="extra-item">
                  <strong>Balance Gas:</strong> {{ getGasDisplay(cylinderType.balance_gas) }}
                </div>
                <div v-if="cylinderType.percent_error" class="extra-item">
                  <strong>Percent Error:</strong> {{ cylinderType.percent_error }}
                </div>
                <div v-if="cylinderType.expiry_months" class="extra-item">
                  <strong>Expiry Months:</strong> {{ cylinderType.expiry_months }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="$emit('close')" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { get } from '@/utils/api';

// Emit event to parent component when dialog is closed
defineEmits(['close']);

// State for cylinder types
const cylinderTypes = ref([]);
const loading = ref(true);

// Fetch cylinder types from the API
const fetchCylinderTypes = async () => {
  try {
    loading.value = true;

    const result = await get('/api/inventory/cylindertypes/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    cylinderTypes.value = result.data;
  } catch (error) {
    console.error('Error fetching cylinder types:', error);
    // In case of error, we could show a user-friendly message
  } finally {
    loading.value = false;
  }
};

// Mapping functions for display values
const getSupplierDisplay = (supplierCode) => {
  const suppliers = {
    'AM': 'AirMet',
    'AE': 'AES',
    'MS': 'MSA',
    'DR': 'Draeger'
  };
  return suppliers[supplierCode] || supplierCode;
};

const getVolumeDisplay = (volumeCode) => {
  const volumes = {
    'L034': '34 L',
    'L065': '65 L',
    'L103': '103 L',
    'L112': '112 L',
    'L552': '552 L'
  };
  return volumes[volumeCode] || volumeCode;
};

const getGasDisplay = (gasCode) => {
  const gases = {
    'CO': 'CO',
    'HS': 'H2S',
    'CH': 'CH4',
    'O2': 'O2',
    'IB': 'Isobutylene',
    'HC': 'HCN',
    'N2': 'N2'
  };
  return gases[gasCode] || gasCode;
};

const getUnitDisplay = (unitCode) => {
  const units = {
    'PM': 'ppm',
    'PV': '%v/v',
    'PL': '%LEL',
    'ML': 'mg/L'
  };
  return units[unitCode] || unitCode;
};

// Initialize component
onMounted(() => {
  fetchCylinderTypes();
});
</script>

<style scoped>
.cylinder-type-details-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
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
}

.dialog-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eee;
  background-color: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.dialog-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #dc3545;
  background: none;
}

.dialog-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.loading, .no-data {
  text-align: center;
  padding: 2rem;
  font-style: italic;
  color: #666;
}

.cylinder-types-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.cylinder-type-card {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 1rem;
  background-color: #f9f9f9;
}

.cylinder-type-card h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.summary-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.summary-item {
  flex: 1;
  min-width: 150px;
  font-size: 0.9rem;
}

.summary-item strong {
  color: #495057;
}

.gases-section {
  margin-bottom: 0.75rem;
}

.gas-item {
  padding: 0.25rem 0;
  font-size: 0.9rem;
}

.gas-item strong {
  color: #2c3e50;
}

.extra-info {
  padding-top: 0.5rem;
  border-top: 1px dashed #eee;
  font-size: 0.85rem;
}

.extra-item {
  padding: 0.25rem 0;
}

.extra-item strong {
  color: #495057;
}

.dialog-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  background-color: #f8f9fa;
  border-radius: 0 0 8px 8px;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .dialog-content {
    width: 95%;
    max-height: 95vh;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
}
</style>