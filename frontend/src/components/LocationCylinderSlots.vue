<template>
  <div class="location-cylinder-slots-page">
    <!-- Filters -->
    <div class="filters-section">
      <button @click="toggleFilters" :aria-expanded="showFilters" class="filter-toggle-btn" :class="{ 'has-active-filters': hasActiveFilters }">
        {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toggle-icon"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </button>
      <div v-show="showFilters" class="search-and-filters-popover">
        <select v-model="filterLocation" class="filter-select">
          <option value="">All Locations</option>
          <option v-for="loc in locations" :key="loc.id" :value="loc.id">{{ loc.label }}</option>
        </select>
        <select v-model="filterDistrict" class="filter-select">
          <option value="">All Districts</option>
          <option v-for="d in districts" :key="d.value" :value="d.value">{{ d.label }}</option>
        </select>        
        <select v-model="filterLocationType" class="filter-select">
          <option value="">All Location Types</option>
          <option v-for="type in locationTypeChoices" :key="type.value" :value="type.value">{{ type.label }}</option>
        </select>
        <select v-model="filterCylinderType" class="filter-select">
          <option value="">All Cylinder Types</option>
          <option v-for="type in cylinderTypes" :key="type.id" :value="type.id">{{ getCylinderTypeLabel(type.id) }}</option>
        </select>
        <div class="reset-btn-wrapper"><button @click="resetFilters" class="reset-btn">Reset Filters</button></div>
      </div>
    </div>

    <div class="page-container">
      <div class="header-actions"><h1>Location Cylinder Slots</h1></div>
      
      <div class="equipment-display">
        <div v-if="loading" class="loading">Loading equipment...</div>
        <div v-else-if="locationGroups.length === 0" class="no-data">{{ emptyMessage }}</div>
        <template v-else>
          <div v-for="locGroup in locationGroups" :key="locGroup.location.id" class="location-block">
            <div class="location-header">
              {{ locGroup.location.label }}
              <span v-if="locGroup.location.district" class="district-tag">{{ getDistrictLabel(locGroup.location.district) }}</span>
            </div>
            
            <div v-if="locGroup.groups.length === 0" class="location-empty">No cylinder slots or equipment at this location.</div>
            
            <div v-else class="model-rows">
              <div v-for="group in locGroup.groups" :key="group.typeId" class="model-row">
                <div class="row-labels">
                  <span class="model-label">{{ getCylinderTypeLabel(group.typeId) }}</span>
                </div>
                
                <div class="slots-and-extras">
                  <div class="slot-boxes" v-if="group.slotCount > 0">
                    <div v-for="(cyl, i) in group.filledBoxes" :key="'filled-' + i" class="slot-box filled">
                      <router-link :to="`/cylinders/${cyl.id}`" class="cylinder-link">{{ cyl.label }}</router-link>
                      <span class="updated-date">{{ formatDate(cyl.receive_date) }}</span>
                    </div>
                    <div v-for="n in group.emptyCount" :key="'empty-' + n" class="slot-box empty">Empty</div>
                  </div>
                  
                  <div v-if="group.overflow.length > 0" class="overflow-area">
                    <span class="overflow-title">Overflow:</span>
                    <div v-for="cyl in group.overflow" :key="cyl.id" class="cylinder-item-container">
                      <router-link :to="`/cylinders/${cyl.id}`" class="overflow-item">{{ cyl.label }}</router-link>
                      <span class="item-date">{{ formatDate(cyl.receive_date) }}</span>
                    </div>
                  </div>
                  
                  <div v-if="group.unslotted.length > 0" class="unslotted-area">
                    <span class="unslotted-title">No Slots Configured (Unslotted):</span>
                    <div v-for="cyl in group.unslotted" :key="cyl.id" class="cylinder-item-container">
                      <router-link :to="`/cylinders/${cyl.id}`" class="unslotted-item">{{ cyl.label }}</router-link>
                      <span class="item-date">{{ formatDate(cyl.receive_date) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { get } from '@/utils/api';

const loading = ref(false);
const locations = ref([]);
const districts = ref([]);
const cylinderTypes = ref([]);
const cylinderModels = ref([]);
const locationTypeChoices = ref([]);
const allSlots = ref([]);
const allCylinders = ref([]);

const showFilters = ref(false);
const filterLocation = ref('');
const filterDistrict = ref('');
const filterLocationType = ref('');
const filterCylinderType = ref('');

const getCylinderTypeLabel = (typeId) => {
  if (!typeId) return 'N/A';
  const type = cylinderTypes.value.find(t => t.id === typeId);
  if (!type) return 'Unknown Type';
  const parts = [];
  if (type.cylinder_1_gas) parts.push(`${type.cylinder_1_gas}(${type.cylinder_1_conc}${type.cylinder_1_units})`);
  if (type.cylinder_2_gas) parts.push(`${type.cylinder_2_gas}(${type.cylinder_2_conc}${type.cylinder_2_units})`);
  if (type.cylinder_3_gas) parts.push(`${type.cylinder_3_gas}(${type.cylinder_3_conc}${type.cylinder_3_units})`);
  if (type.cylinder_4_gas) parts.push(`${type.cylinder_4_gas}(${type.cylinder_4_conc}${type.cylinder_4_units})`);
  return parts.length > 0 ? parts.join('/') : `Balance: ${type.balance_gas}`;
};

const getDistrictLabel = (districtCode) => {
  const d = districts.value.find(dist => dist.value === districtCode);
  return d ? d.label : districtCode;
};

const formatDate = (dateStr) => (dateStr ? dateStr.split('T')[0] : 'N/A');
const getLocationType = (loc) => loc.location_type || '';

const toggleFilters = () => { showFilters.value = !showFilters.value; };
const resetFilters = () => {
  filterLocation.value = ''; filterDistrict.value = '';
  filterLocationType.value = ''; filterCylinderType.value = '';
};

const hasActiveFilters = computed(() =>
  filterLocation.value !== '' || filterDistrict.value !== '' ||
  filterLocationType.value !== '' || filterCylinderType.value !== ''
);

const emptyMessage = computed(() =>
  hasActiveFilters.value ? 'No locations match the selected filters.' : 'No locations found.'
);

const saveStateToLocalStorage = () => {
  localStorage.setItem('locationCylinderSlotsFilterState', JSON.stringify({
    filterLocation: filterLocation.value, filterDistrict: filterDistrict.value,
    filterLocationType: filterLocationType.value, filterCylinderType: filterCylinderType.value
  }));
};

const locationGroups = computed(() => {
  const result = [];
  const modelToType = {};
  cylinderModels.value.forEach(m => { modelToType[m.id] = m.cylinder_type; });

  const matchingLocations = locations.value.filter(loc => {
    if (filterLocation.value !== '' && loc.id !== filterLocation.value) return false;
    if (filterDistrict.value !== '' && loc.district !== filterDistrict.value) return false;
    if (filterLocationType.value !== '' && getLocationType(loc) !== filterLocationType.value) return false;
    return true;
  });

  for (const loc of matchingLocations) {
    const slotsByType = {};
    for (const slot of allSlots.value) {
      if (slot.location !== loc.id) continue;
      if (filterCylinderType.value !== '' && slot.cylinder_type !== filterCylinderType.value) continue;
      if (!slotsByType[slot.cylinder_type]) slotsByType[slot.cylinder_type] = [];
      slotsByType[slot.cylinder_type].push(slot); 
    }

    const cylsByType = {};
    for (const cyl of allCylinders.value) {
      if (cyl.location !== loc.id) continue;
      const typeId = modelToType[cyl.cylinder_model];
      if (!typeId) continue;
      if (filterCylinderType.value !== '' && typeId !== filterCylinderType.value) continue;
      if (!cylsByType[typeId]) cylsByType[typeId] = [];
      cylsByType[typeId].push(cyl);
    }

    const typeIds = new Set([...Object.keys(slotsByType).map(Number), ...Object.keys(cylsByType).map(Number)]);
    const groups = [];

    for (const typeId of typeIds) {
      const slotCount = (slotsByType[typeId] || []).length;
      const cylinders = (cylsByType[typeId] || []).slice().sort((a, b) => (a.label || '').localeCompare(b.label || ''));

      let filledBoxes = [], emptyCount = 0, overflow = [], unslotted = [];
      if (slotCount > 0) {
        filledBoxes = cylinders.slice(0, slotCount);
        overflow = cylinders.slice(slotCount);
        emptyCount = Math.max(0, slotCount - filledBoxes.length);
      } else {
        unslotted = cylinders;
      }
      groups.push({ typeId, slotCount, filledBoxes, emptyCount, overflow, unslotted });
    }

    groups.sort((a, b) => {
      const aHasSlots = a.slotCount > 0 ? 0 : 1;
      const bHasSlots = b.slotCount > 0 ? 0 : 1;
      if (aHasSlots !== bHasSlots) return aHasSlots - bHasSlots;
      return getCylinderTypeLabel(a.typeId).localeCompare(getCylinderTypeLabel(b.typeId));
    });

    if (groups.length === 0 && filterCylinderType.value !== '') continue;
    result.push({ location: loc, groups });
  }
  return result;
});

const fetchAllData = async () => {
  loading.value = true;
  try {
    const [locRes, distRes, typesRes, slotsRes, cylsRes, locTypesRes, modelsRes] = await Promise.all([
      get('/api/inventory/locations/'), get('/api/inventory/districts/'),
      get('/api/inventory/cylindertypes/'), get('/api/inventory/locationcylinderslots/'),
      get('/api/inventory/cylinders/'), get('/api/inventory/location-types/'),
      get('/api/inventory/cylindermodels/')
    ]);
    if (![locRes, distRes, typesRes, slotsRes, cylsRes, locTypesRes, modelsRes].every(r => r.ok)) {
      throw new Error('One or more API requests failed');
    }
    locations.value = locRes.data; districts.value = distRes.data;
    cylinderTypes.value = typesRes.data; allSlots.value = slotsRes.data;
    allCylinders.value = cylsRes.data; locationTypeChoices.value = locTypesRes.data;
    cylinderModels.value = modelsRes.data;
  } catch (error) {
    console.error('Error loading data:', error);
  } finally {
    loading.value = false;
  }
};

watch([filterLocation, filterDistrict, filterLocationType, filterCylinderType], () => {
  saveStateToLocalStorage();
});

onMounted(async () => {
  const savedState = localStorage.getItem('locationCylinderSlotsFilterState');
  if (savedState) {
    try {
      const state = JSON.parse(savedState);
      filterLocation.value = state.filterLocation ?? '';
      filterDistrict.value = state.filterDistrict ?? '';
      filterLocationType.value = state.filterLocationType ?? '';
      filterCylinderType.value = state.filterCylinderType ?? '';
    } catch (e) { console.error('Error parsing state', e); }
  }
  await fetchAllData();
});
</script>

<style scoped>
/* Copy the exact <style scoped> block from LocationSlots.vue here */
.location-cylinder-slots-page { min-height: 100vh; display: flex; flex-direction: column; }
.filters-section { margin-bottom: 0.25rem; position: relative; display: inline-block; padding: 0.5rem 1rem 0; }
.filter-toggle-btn { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.75rem; background-color: #42b883; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem; transition: background-color 0.3s ease; }
.filter-toggle-btn:hover { background-color: #36966d; }
.filter-toggle-btn.has-active-filters { background-color: #e67e22; }
.filter-toggle-btn.has-active-filters:hover { background-color: #d35400; }
.toggle-icon { transition: transform 0.3s ease; }
.filter-toggle-btn[aria-expanded="true"] .toggle-icon { transform: rotate(180deg); }
.search-and-filters-popover { position: absolute; top: 100%; left: 1rem; min-width: 300px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 0.5rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); z-index: 1000; display: flex; flex-direction: column; gap: 0.5rem; }
.reset-btn-wrapper { align-self: flex-start; }
.reset-btn { padding: 0.4rem 0.75rem; background-color: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
.reset-btn:hover { background-color: #c82333; }
.filter-select { padding: 0.4rem; border: 1px solid #ddd; border-radius: 4px; min-width: 150px; }
.page-container { max-width: 1400px; margin: 0 auto; padding: 0.5rem 2rem 2rem; width: 100%; box-sizing: border-box; }
h1 { color: #2c3e50; margin-bottom: 0.5rem; font-size: 1.4rem; }
.header-actions { margin-bottom: 0.75rem; }
.equipment-display { display: flex; flex-direction: column; gap: 1.25rem; }
.loading, .no-data { text-align: center; padding: 2rem; font-style: italic; color: #666; }
.location-block { background: white; border-radius: 8px; padding: 1rem 1.25rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); }
.location-header { font-size: 1.1rem; font-weight: 700; color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 0.5rem; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }
.district-tag { font-size: 0.75rem; font-weight: 600; color: #6c757d; background-color: #f1f3f5; border-radius: 12px; padding: 0.15rem 0.6rem; }
.location-empty { font-style: italic; color: #999; padding: 0.5rem 0; font-size: 0.9rem; }
.model-rows { display: flex; flex-direction: column; gap: 0.75rem; }
.model-row { display: flex; align-items: flex-start; gap: 1rem; flex-wrap: wrap; border-top: 1px solid #f1f1f1; padding-top: 0.75rem; }
.model-row:first-child { border-top: none; padding-top: 0; }
.row-labels { display: flex; flex-direction: column; justify-content: center; min-width: 180px; max-width: 200px; }
.model-label { color: #495057; font-size: 0.9rem; font-weight: 600; word-break: break-word; }
.slots-and-extras { flex: 1; display: flex; flex-direction: column; gap: 0.75rem; min-width: 0; }
.slot-boxes { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.slot-box { flex: 0 1 calc((100% - 2.5rem) / 6); min-width: 110px; min-height: 64px; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 0.9rem; font-weight: 600; box-sizing: border-box; padding: 0.5rem; text-align: center; }
.slot-box.filled { background-color: #eafaf2; border: 2px solid #42b883; color: #2c3e50; }
.slot-box.empty { background-color: #fdecea; border: 2px solid #dc3545; color: #dc3545; }
.updated-date { font-size: 0.7rem; font-weight: 400; color: #6c757d; margin-top: 0.25rem; display: block; line-height: 1; }
.cylinder-link { color: #2c3e50; text-decoration: none; }
.cylinder-link:hover { text-decoration: underline; color: #42b883; }
.unslotted-area, .overflow-area { display: flex; flex-wrap: wrap; gap: 0.75rem; width: 100%; padding-top: 0.75rem; border-top: 1px dashed #e9ecef; align-items: flex-start; }
.unslotted-title, .overflow-title { font-size: 0.8rem; font-weight: 700; color: #6c757d; text-transform: uppercase; width: 100%; margin-bottom: -0.25rem; }
.overflow-title { color: #dc3545; }
.cylinder-item-container { display: flex; flex-direction: column; align-items: center; gap: 0.15rem; }
.item-date { font-size: 0.7rem; font-weight: 400; color: #6c757d; }
.unslotted-item { background-color: #f8f9fa; border: 2px solid #6c757d; color: #495057; border-radius: 6px; padding: 0.35rem 0.6rem; font-size: 0.85rem; font-weight: 600; text-decoration: none; }
.unslotted-item:hover { background-color: #e9ecef; color: #007bff; }
.overflow-item { background-color: #fdecea; border: 2px solid #dc3545; color: #dc3545; border-radius: 6px; padding: 0.35rem 0.6rem; font-size: 0.85rem; font-weight: 600; text-decoration: none; }
.overflow-item:hover { background-color: #f8d7da; }
@media (max-width: 768px) {
  .page-container { padding: 0.5rem 1rem 2rem; }
  .model-row { flex-direction: column; align-items: flex-start; }
  .row-labels { max-width: 100%; }
}
</style>