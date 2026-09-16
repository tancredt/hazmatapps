<template>
  <div class="cylinder-model-details-dialog">
    <div class="dialog-overlay" @click="$emit('close')">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>Cylinder Model Details</h3>
          <button class="close-btn" @click="$emit('close')">&times;</button>
        </div>
        <div class="dialog-body">
          <div v-if="loading" class="loading">Loading cylinder models...</div>
          <div v-else-if="cylinderModels.length === 0" class="no-data">No cylinder models found</div>
          <div v-else class="cylinder-models-list">
            <div v-for="model in cylinderModels" :key="model.id" class="cylinder-model-card">
              <h4>{{ model.part_number }}</h4>
              <div class="summary-row">
                <div class="summary-item"><strong>Supplier:</strong> {{ getSupplierDisplay(model.supplier) }}</div>
                <div class="summary-item"><strong>Volume:</strong> {{ getVolumeDisplay(model.volume) }}</div>
                <div class="summary-item"><strong>Percent Error:</strong> {{ model.percent_error }}</div>
                <div class="summary-item"><strong>Expiry Months:</strong> {{ model.expiry_months }}</div>
              </div>
              
              <div class="gases-section" v-if="getCylinderType(model.cylinder_type)">
                <h5>Gas Configuration (Type {{ getCylinderType(model.cylinder_type).id }})</h5>
                <div class="gas-item">
                  <strong>{{ getGasDisplay(getCylinderType(model.cylinder_type).cylinder_1_gas) }}</strong>: 
                  {{ getCylinderType(model.cylinder_type).cylinder_1_conc }} {{ getUnitDisplay(getCylinderType(model.cylinder_type).cylinder_1_units) }}
                </div>
                <div v-if="getCylinderType(model.cylinder_type).cylinder_2_gas" class="gas-item">
                  <strong>{{ getGasDisplay(getCylinderType(model.cylinder_type).cylinder_2_gas) }}</strong>: 
                  {{ getCylinderType(model.cylinder_type).cylinder_2_conc }} {{ getUnitDisplay(getCylinderType(model.cylinder_type).cylinder_2_units) }}
                </div>
                <div v-if="getCylinderType(model.cylinder_type).cylinder_3_gas" class="gas-item">
                  <strong>{{ getGasDisplay(getCylinderType(model.cylinder_type).cylinder_3_gas) }}</strong>: 
                  {{ getCylinderType(model.cylinder_type).cylinder_3_conc }} {{ getUnitDisplay(getCylinderType(model.cylinder_type).cylinder_3_units) }}
                </div>
                <div v-if="getCylinderType(model.cylinder_type).cylinder_4_gas" class="gas-item">
                  <strong>{{ getGasDisplay(getCylinderType(model.cylinder_type).cylinder_4_gas) }}</strong>: 
                  {{ getCylinderType(model.cylinder_type).cylinder_4_conc }} {{ getUnitDisplay(getCylinderType(model.cylinder_type).cylinder_4_units) }}
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

defineEmits(['close']);

const cylinderModels = ref([]);
const cylinderTypes = ref([]);
const loading = ref(true);

const fetchData = async () => {
  try {
    loading.value = true;
    const [modelsRes, typesRes] = await Promise.all([
      get('/api/inventory/cylindermodels/'),
      get('/api/inventory/cylindertypes/')
    ]);
    if (modelsRes.ok) cylinderModels.value = modelsRes.data;
    if (typesRes.ok) cylinderTypes.value = typesRes.data;
  } catch (error) {
    console.error('Error fetching data:', error);
  } finally {
    loading.value = false;
  }
};

const getCylinderType = (typeId) => cylinderTypes.value.find(t => t.id === typeId);

const getSupplierDisplay = (code) => ({ 'AM': 'AirMet', 'AE': 'AES', 'MS': 'MSA', 'DR': 'Draeger' }[code] || code);
const getVolumeDisplay = (code) => ({ 'L034': '34 L', 'L065': '65 L', 'L103': '103 L', 'L112': '112 L', 'L552': '552 L' }[code] || code);
const getGasDisplay = (code) => ({ 'CO': 'CO', 'HS': 'H2S', 'CH': 'CH4', 'O2': 'O2', 'IB': 'Isobutylene', 'HC': 'HCN', 'N2': 'N2' }[code] || code);
const getUnitDisplay = (code) => ({ 'PM': 'ppm', 'PV': '%v/v', 'PL': '%LEL', 'ML': 'mg/L' }[code] || code);

onMounted(() => { fetchData(); });
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