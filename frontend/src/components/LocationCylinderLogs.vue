<template>
  <div class="logs-page">
    <div class="filters-section">
      <button @click="toggleFilters" :aria-expanded="showFilters" class="filter-toggle-btn" :class="{ 'has-active-filters': hasActiveFilters }">
        {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toggle-icon"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </button>
      <div v-show="showFilters" class="search-and-filters-popover">
        <input type="text" v-model="filterCylinderLabel" placeholder="Cylinder ID (e.g. 123 or CYL123)..." class="search-input" @input="filterLogs">
        <select v-model="filterCylinderType" @change="filterLogs" class="filter-select">
          <option value="">All Cylinder Types</option>
          <option v-for="type in cylinderTypes" :key="type.id" :value="type.id">{{ getCylinderTypeLabel(type.id) }}</option>
        </select>
        <select v-model="filterCylinderModel" @change="filterLogs" class="filter-select">
          <option value="">All Models</option>
          <option v-for="model in cylinderModels" :key="model.id" :value="model.id">{{ model.part_number }}</option>
        </select>
        <select v-model="filterOldLocation" @change="filterLogs" class="filter-select">
          <option value="">All Old Locations</option>
          <option v-for="loc in locations" :key="loc.id" :value="loc.id">{{ loc.label }}</option>
        </select>
        <select v-model="filterNewLocation" @change="filterLogs" class="filter-select">
          <option value="">All New Locations</option>
          <option v-for="loc in locations" :key="loc.id" :value="loc.id">{{ loc.label }}</option>
        </select>
        <div class="date-filter-container">
          <label for="daysFilter" class="date-label">Updated within last (days):</label>
          <input id="daysFilter" type="number" v-model.number="filterDays" min="0" @change="filterLogs" class="date-input" placeholder="e.g. 7">
        </div>
        <div class="reset-btn-wrapper">
          <button @click="resetFilters" class="reset-btn">Reset Filters</button>
        </div>
      </div>
    </div>

    <div class="page-container">
      <div class="header-actions">
        <h1>Cylinder Location Logs</h1>
      </div>
      <div class="table-container">
        <table class="logs-table">
          <thead>
            <tr>
              <th @click="sortBy('cylinder_label')" class="sortable">Cylinder <span v-if="sortKey === 'cylinder_label'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('cylinder_model_label')" class="sortable">Model <span v-if="sortKey === 'cylinder_model_label'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('cylinder_type')" class="sortable">Type <span v-if="sortKey === 'cylinder_type'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('old_location_label')" class="sortable">Old Location <span v-if="sortKey === 'old_location_label'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('new_location_label')" class="sortable">New Location <span v-if="sortKey === 'new_location_label'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('updated')" class="sortable">Updated <span v-if="sortKey === 'updated'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in filteredLogs" :key="log.id">
              <td>
                <router-link :to="`/cylinders/${log.cylinder}`" class="cylinder-link">
                  {{ log.cylinder_label }}
                </router-link>
              </td>
              <td>{{ log.cylinder_model_label || 'N/A' }}</td>
              <td>{{ getCylinderTypeLabel(log.cylinder_type) || 'N/A' }}</td>
              <td>{{ log.old_location_label || 'N/A (New)' }}</td>
              <td>{{ log.new_location_label || 'N/A' }}</td>
              <td>{{ formatDateTime(log.updated) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="loading" class="loading">Loading logs...</div>
        <div v-else-if="totalFilteredLogs === 0" class="no-data">No logs found</div>
        
        <div v-if="!loading && totalFilteredLogs > 0" class="pagination-container">
          <div class="pagination-info">
            Showing {{ ((currentPage - 1) * logsPerPage) + 1 }} to {{ Math.min(currentPage * logsPerPage, totalFilteredLogs) }} of {{ totalFilteredLogs }} logs
          </div>
          <div class="pagination-controls">
            <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-pagination">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
            </button>
            <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-pagination">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { get } from '@/utils/api';

const logs = ref([]);
const loading = ref(true);
const cylinderTypes = ref([]);
const cylinderModels = ref([]);
const locations = ref([]);

const sortKey = ref('updated');
const sortDirection = ref('desc');
const filterCylinderLabel = ref('');
const filterCylinderType = ref('');
const filterCylinderModel = ref('');
const filterOldLocation = ref('');
const filterNewLocation = ref('');
// Default to 7 days
const filterDays = ref(7);

const showFilters = ref(false);
const currentPage = ref(1);
const logsPerPage = ref(50);

const filteredLogsResult = ref([]);
const totalFilteredLogsResult = ref(0);
const totalPagesResult = ref(0);

onMounted(async () => {
  const savedState = localStorage.getItem('cylinderLogsFilterState');
  if (savedState) {
    const state = JSON.parse(savedState);
    sortKey.value = state.sortKey || 'updated';
    sortDirection.value = state.sortDirection || 'desc';
    filterCylinderLabel.value = state.filterCylinderLabel || '';
    filterCylinderType.value = state.filterCylinderType || '';
    filterCylinderModel.value = state.filterCylinderModel || '';
    filterOldLocation.value = state.filterOldLocation || '';
    filterNewLocation.value = state.filterNewLocation || '';
    // Respect saved state if it exists, otherwise fallback to 7
    filterDays.value = (state.filterDays !== undefined && state.filterDays !== '') ? state.filterDays : 7;
  } else {
    filterDays.value = 7;
  }

  await Promise.all([fetchCylinderTypes(), fetchCylinderModels(), fetchLocations()]);
  await fetchLogs();
});

const saveStateToLocalStorage = () => {
  localStorage.setItem('cylinderLogsFilterState', JSON.stringify({
    sortKey: sortKey.value, sortDirection: sortDirection.value,
    filterCylinderLabel: filterCylinderLabel.value, filterCylinderType: filterCylinderType.value,
    filterCylinderModel: filterCylinderModel.value, filterOldLocation: filterOldLocation.value,
    filterNewLocation: filterNewLocation.value, filterDays: filterDays.value
  }));
};

watch([sortKey, sortDirection, filterCylinderLabel, filterCylinderType, filterCylinderModel, filterOldLocation, filterNewLocation, filterDays], () => {
  currentPage.value = 1;
  saveStateToLocalStorage();
}, { deep: true });

const fetchCylinderTypes = async () => {
  try {
    const result = await get('/api/inventory/cylindertypes/');
    if (result.ok) cylinderTypes.value = result.data;
  } catch (error) { console.error('Error fetching types:', error); }
};

const fetchCylinderModels = async () => {
  try {
    const result = await get('/api/inventory/cylindermodels/');
    if (result.ok) cylinderModels.value = result.data;
  } catch (error) { console.error('Error fetching models:', error); }
};

const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');
    if (result.ok) locations.value = result.data;
  } catch (error) { console.error('Error fetching locations:', error); }
};

const getCylinderTypeLabel = (typeId) => {
  if (!typeId) return 'N/A';
  const type = cylinderTypes.value.find(t => t.id === typeId);
  if (!type) return 'Unknown Type';
  // Simplified label for table display
  const gases = [];
  if (type.cylinder_1_gas) gases.push(`${type.cylinder_1_gas} ${type.cylinder_1_conc || ''} ${type.cylinder_1_units || ''}`.trim());
  if (type.cylinder_2_gas) gases.push(`${type.cylinder_2_gas} ${type.cylinder_2_conc || ''} ${type.cylinder_2_units || ''}`.trim());
  return gases.length > 0 ? gases.join('; ') : `Balance: ${type.balance_gas}`;
};

const fetchLogs = async () => {
  try {
    loading.value = true;
    const params = new URLSearchParams();

    if (filterCylinderLabel.value) params.append('cylinder_label', filterCylinderLabel.value);
    if (filterCylinderType.value) params.append('cylinder__cylinder_model__cylinder_type', filterCylinderType.value);
    if (filterCylinderModel.value) params.append('cylinder__cylinder_model', filterCylinderModel.value);
    if (filterOldLocation.value) params.append('old_location', filterOldLocation.value);
    if (filterNewLocation.value) params.append('new_location', filterNewLocation.value);
    
    if (filterDays.value) {
      const date = new Date();
      date.setDate(date.getDate() - parseInt(filterDays.value));
      params.append('updated_gte', date.toISOString().split('T')[0]);
    }

    let url = '/api/inventory/locationcylinderlogs/';
    if (params.toString()) url += '?' + params.toString();

    const result = await get(url);
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    
    logs.value = result.data;
    performSortingAndPagination();
  } catch (error) {
    console.error('Error fetching logs:', error);
  } finally {
    loading.value = false;
  }
};

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString();
};

const performSortingAndPagination = () => {
  let result = [...logs.value];

  if (sortKey.value) {
    result.sort((a, b) => {
      let valA = a[sortKey.value] || '';
      let valB = b[sortKey.value] || '';

      if (sortKey.value === 'updated') {
        valA = valA ? new Date(valA) : new Date(0);
        valB = valB ? new Date(valB) : new Date(0);
      } else if (sortKey.value === 'cylinder_type') {
        valA = getCylinderTypeLabel(a.cylinder_type) || '';
        valB = getCylinderTypeLabel(b.cylinder_type) || '';
      }

      if (sortDirection.value === 'asc') return valA > valB ? 1 : -1;
      return valA < valB ? 1 : -1;
    });
  }

  totalFilteredLogsResult.value = result.length;
  totalPagesResult.value = Math.ceil(result.length / logsPerPage.value);
  
  const startIndex = (currentPage.value - 1) * logsPerPage.value;
  filteredLogsResult.value = result.slice(startIndex, startIndex + logsPerPage.value);
};

watch([filterCylinderLabel, filterCylinderType, filterCylinderModel, filterOldLocation, filterNewLocation, filterDays], () => {
  currentPage.value = 1;
  fetchLogs();
}, { deep: true });

watch([sortKey, sortDirection, currentPage], () => {
  performSortingAndPagination();
}, { deep: true });

const filteredLogs = computed(() => filteredLogsResult.value);
const totalPages = computed(() => totalPagesResult.value);
const totalFilteredLogs = computed(() => totalFilteredLogsResult.value);

const hasActiveFilters = computed(() => {
  return filterCylinderLabel.value !== '' || filterCylinderType.value !== '' || 
         filterCylinderModel.value !== '' || filterOldLocation.value !== '' || 
         filterNewLocation.value !== '' || filterDays.value !== '';
});

const sortBy = (key) => {
  if (sortKey.value === key) sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  else { sortKey.value = key; sortDirection.value = 'asc'; }
};

const filterLogs = () => { currentPage.value = 1; };
const toggleFilters = () => { showFilters.value = !showFilters.value; };

const resetFilters = () => {
  filterCylinderLabel.value = ''; filterCylinderType.value = '';
  filterCylinderModel.value = ''; filterOldLocation.value = ''; 
  filterNewLocation.value = ''; 
  // Reset back to default 7 days
  filterDays.value = 7; 
  sortKey.value = 'updated'; sortDirection.value = 'desc';
  currentPage.value = 1;
  localStorage.removeItem('cylinderLogsFilterState');
};

const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };
</script>

<style scoped>
/* Copy styles from Faults.vue or Cylinders.vue for consistency */
.logs-page { min-height: 100vh; display: flex; flex-direction: column; }
.filters-section { margin-bottom: 0.5rem; position: relative; display: inline-block; }
.filter-toggle-btn { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background-color: #42b883; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-bottom: 1rem; transition: background-color 0.3s ease; }
.filter-toggle-btn:hover { background-color: #36966d; }
.filter-toggle-btn.has-active-filters { background-color: #e67e22; }
.filter-toggle-btn.has-active-filters:hover { background-color: #d35400; }
.toggle-icon { transition: transform 0.3s ease; }
.filter-toggle-btn[aria-expanded="true"] .toggle-icon { transform: rotate(180deg); }
.search-and-filters-popover { position: absolute; top: 100%; left: 0; width: 20%; min-width: 300px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 1rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); z-index: 1000; display: flex; flex-direction: column; gap: 1rem; }
.reset-btn-wrapper { align-self: flex-start; }
.search-input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; width: 200px; }
.filter-select { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; min-width: 150px; }
.reset-btn { padding: 0.5rem 1rem; background-color: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem; }
.reset-btn:hover { background-color: #c82333; }
.page-container { max-width: 1200px; margin: 0 auto; padding: 1rem 2rem; height: calc(100vh - 70px); overflow: hidden; display: flex; flex-direction: column; }
h1 { color: #2c3e50; margin-bottom: 0.5rem; flex-shrink: 0; }
.header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-shrink: 0; }
.table-container { display: flex; flex-direction: column; flex: 1; overflow: hidden; min-height: 0; }
.logs-table { width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; table-layout: fixed; margin-bottom: 0; }
.logs-table thead th { position: sticky; top: 0; background-color: #f8f9fa; font-weight: 600; word-wrap: break-word; z-index: 10; border-bottom: 1px solid #ddd; }
.logs-table tbody { display: block; max-height: calc(100vh - 280px); overflow-y: auto; }
.logs-table thead, .logs-table tbody tr { display: table; width: 100%; table-layout: fixed; }
.logs-table th, .logs-table td { padding: 0.5rem; text-align: left; border-bottom: 1px solid #ddd; word-wrap: break-word; }
.logs-table th:nth-child(1), .logs-table td:nth-child(1) { width: 16%; }
.logs-table th:nth-child(2), .logs-table td:nth-child(2) { width: 16%; }
.logs-table th:nth-child(3), .logs-table td:nth-child(3) { width: 16%; }
.logs-table th:nth-child(4), .logs-table td:nth-child(4) { width: 16%; }
.logs-table th:nth-child(5), .logs-table td:nth-child(5) { width: 16%; }
.logs-table th:nth-child(6), .logs-table td:nth-child(6) { width: 20%; }
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { background-color: #e9ecef; }
.logs-table tbody tr:hover { background-color: #f8f9fa; }
.cylinder-link { color: #42b883; text-decoration: none; font-weight: 500; }
.cylinder-link:hover { text-decoration: underline; }
.loading, .no-data { text-align: center; padding: 2rem; font-style: italic; color: #666; }
.date-filter-container { display: flex; flex-direction: column; gap: 0.25rem; }
.date-label { font-size: 0.875rem; font-weight: 500; color: #495057; }
.date-input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.875rem; }
.pagination-container { display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; padding: 0.5rem 0; }
.pagination-info { color: #666; font-size: 0.9rem; }
.pagination-controls { display: flex; align-items: center; gap: 1rem; }
.pagination-controls .page-info { color: #666; font-size: 0.9rem; min-width: 120px; text-align: center; }
.btn-pagination { background-color: #6c757d; color: white; border: none; border-radius: 4px; padding: 0.25rem 0.5rem; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background-color 0.3s; }
.btn-pagination:hover:not(:disabled) { background-color: #5a6268; }
.btn-pagination:disabled { background-color: #adb5bd; cursor: not-allowed; opacity: 0.6; }
</style>