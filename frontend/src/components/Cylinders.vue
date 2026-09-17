<template>
  <div class="cylinders-page">
    <div class="filters-section">
      <button @click="toggleFilters" :aria-expanded="showFilters" class="filter-toggle-btn" :class="{ 'has-active-filters': hasActiveFilters }">
        {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toggle-icon"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </button>
      <div v-show="showFilters" class="search-and-filters-popover">
        <input type="text" v-model="searchTerm" placeholder="Search by label/serial..." class="search-input" @input="filterCylinders">
        <select v-model="filterStatus" @change="filterCylinders" class="filter-select">
          <option value="">All Statuses</option>
          <option v-for="choice in cylinderStatusChoices" :key="choice.value" :value="choice.value">{{ choice.label }}</option>
        </select>
        <select v-model="filterDetector" @change="filterCylinders" class="filter-select">
          <option value="">All Detectors</option>
          <option v-for="detector in detectors" :key="detector.id" :value="detector.id">{{ getDetectorLabel(detector.id) }}</option>
        </select>
        <select v-model="filterLocation" @change="filterCylinders" class="filter-select">
          <option value="">All Locations</option>
          <option v-for="location in locations" :key="location.id" :value="location.id">{{ getLocationLabel(location.id) }}</option>
        </select>
        <!-- Cylinder Type Filter -->
        <select v-model="filterCylinderType" @change="filterCylinders" class="filter-select">
          <option value="">All Cylinder Types</option>
          <option v-for="cylinderType in cylinderTypes" :key="cylinderType.id" :value="cylinderType.id">
            {{ getCylinderTypeLabel(cylinderType.id) }}
          </option>
        </select>
        <div class="date-filter-container">
          <label for="expiresBefore" class="date-label">Expires Before:</label>
          <input id="expiresBefore" type="date" v-model="filterExpiresBefore" @change="filterCylinders" class="date-input" />
        </div>
        <div class="checkbox-container">
          <label class="checkbox-label">
            <input type="checkbox" v-model="showEmptyCylinders" @change="filterCylinders" />
            Show Empty Cylinders
          </label>
        </div>
        <div class="reset-btn-wrapper">
          <button @click="resetFilters" class="reset-btn">Reset Filters</button>
        </div>
      </div>
    </div>

    <div class="page-container">
      <div class="header-actions">
        <h1>Cylinders Management</h1>
        <div class="action-buttons">
          <router-link to="/cylinders/new" class="btn btn-primary">Add New Cylinder</router-link>
          <router-link to="/cylinders/add-multiple" class="btn btn-primary">Add Multiple Cylinders</router-link>
          <button @click="openUpdateMultipleCylinders" :disabled="selectedCylinders.length === 0" class="btn btn-primary">Update Multiple</button>
          <button @click="downloadPDF" class="btn btn-primary" title="Download as PDF">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/><path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/></svg>
          </button>
        </div>
      </div>

      <div class="table-container">
        <table class="cylinders-table">
          <thead>
            <tr>
              <th><input type="checkbox" @change="toggleSelectAll" :checked="selectedCylinders.length === filteredCylinders.length && filteredCylinders.length > 0" /></th>
              <th @click="sortBy('label')" class="sortable">Label <span v-if="sortKey === 'label'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('serial')" class="sortable">Serial <span v-if="sortKey === 'serial'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <!-- Added Cylinder Model Column -->
              <th @click="sortBy('cylinder_model')" class="sortable">Cylinder Model <span v-if="sortKey === 'cylinder_model'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <!-- Cylinder Type Column (Calculated) -->
              <th @click="sortBy('cylinder_type')" class="sortable">Cylinder Type <span v-if="sortKey === 'cylinder_type'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('supplier')" class="sortable">Supplier <span v-if="sortKey === 'supplier'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('detector')" class="sortable">Detector <span v-if="sortKey === 'detector'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('location')" class="sortable">Location <span v-if="sortKey === 'location'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('status')" class="sortable">Status <span v-if="sortKey === 'status'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('order_date')" class="sortable">Order Date <span v-if="sortKey === 'order_date'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('receive_date')" class="sortable">Receive Date <span v-if="sortKey === 'receive_date'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
              <th @click="sortBy('expiry_date')" class="sortable">Expiry Date <span v-if="sortKey === 'expiry_date'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cylinder in filteredCylinders" :key="cylinder.id">
              <td><input type="checkbox" :value="cylinder.id" v-model="selectedCylinders" /></td>
              <td><router-link :to="`/cylinders/${cylinder.id}`" class="cylinder-link">{{ cylinder.label }}</router-link></td>
              <td>{{ cylinder.serial || 'N/A' }}</td>
              <!-- Model Part Number -->
              <td>{{ getCylinderModelLabel(cylinder.cylinder_model) || 'N/A' }}</td>
              <!-- Calculated Gas Configuration -->
              <td>{{ getCylinderTypeLabel(getCylinderTypeId(cylinder.cylinder_model)) || 'N/A' }}</td>
              <!-- Supplier from Model -->
              <td>{{ getCylinderModelSupplier(cylinder.cylinder_model) || 'N/A' }}</td>
              <td>{{ getDetectorLabel(cylinder.detector) || 'N/A' }}</td>
              <td>{{ getLocationLabel(cylinder.location) || 'N/A' }}</td>
              <td>{{ getStatusDisplay(cylinder.status) }}</td>
              <td>{{ cylinder.order_date || 'N/A' }}</td>
              <td>{{ cylinder.receive_date || 'N/A' }}</td>
              <td>{{ cylinder.expiry_date || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="loading" class="loading">Loading cylinders...</div>
        <div v-else-if="totalFilteredCylinders === 0" class="no-data">No cylinders found</div>
        
        <div v-if="!loading && totalFilteredCylinders > 0" class="pagination-container">
          <div class="pagination-info">Showing {{ ((currentPage - 1) * cylindersPerPage) + 1 }} to {{ Math.min(currentPage * cylindersPerPage, totalFilteredCylinders) }} of {{ totalFilteredCylinders }} cylinders</div>
          <div class="pagination-controls">
            <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-pagination"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg></button>
            <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-pagination"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg></button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { get } from '@/utils/api';

const router = useRouter();
const cylinders = ref([]);
const loading = ref(true);

const cylinderTypes = ref([]);
const cylinderModels = ref([]); // Added to map Model -> Type
const locations = ref([]);
const detectors = ref([]);
const cylinderStatusChoices = ref([]);

const sortKey = ref('label');
const sortDirection = ref('asc');
const searchTerm = ref('');
const filterStatus = ref('');
const filterLocation = ref('');
const filterCylinderType = ref('');
const filterDetector = ref('');
const filterExpiresBefore = ref('');
const showEmptyCylinders = ref(false);
const showFilters = ref(false);

const currentPage = ref(1);
const cylindersPerPage = ref(50);
const selectedCylinders = ref([]);

const filteredCylindersResult = ref([]);
const totalFilteredCylindersResult = ref(0);
const totalPagesResult = ref(0);

// --- Helper Mapping Functions ---
const getGasDisplay = (gasCode) => {
  if (!gasCode) return '';
  const gases = { 'CO': 'CO', 'HS': 'H2S', 'CH': 'CH4', 'O2': 'O2', 'IB': 'Iso', 'HC': 'HCN', 'N2': 'N2', 'CL': 'Cl2', 'PH': 'PH3', 'SO': 'SO2', 'NO': 'NO2', 'C2': 'CO2', 'NH': 'NH3', 'ET': 'ETO' };
  return gases[gasCode] || gasCode;
};

const getUnitDisplay = (unitCode) => {
  if (!unitCode) return '';
  const units = { 'PM': 'ppm', 'PV': '%v/v', 'PL': '%LEL', 'ML': 'mg/L' };
  return units[unitCode] || unitCode;
};

const getCylinderTypeId = (cylinderModelId) => {
  if (!cylinderModelId) return null;
  const model = cylinderModels.value.find(m => m.id === cylinderModelId);
  return model ? model.cylinder_type : null;
};

const getCylinderTypeLabel = (cylinderTypeId) => {
  if (!cylinderTypeId) return 'N/A';
  const type = cylinderTypes.value.find(t => t.id === cylinderTypeId);
  if (!type) return 'Unknown Type';

  const gasEntries = [];
  const buildEntry = (gas, conc, units) => {
    if (!gas) return null;
    return `${getGasDisplay(gas)} ${conc ?? ''} ${getUnitDisplay(units)}`.trim();
  };

  const entry1 = buildEntry(type.cylinder_1_gas, type.cylinder_1_conc, type.cylinder_1_units);
  const entry2 = buildEntry(type.cylinder_2_gas, type.cylinder_2_conc, type.cylinder_2_units);
  const entry3 = buildEntry(type.cylinder_3_gas, type.cylinder_3_conc, type.cylinder_3_units);
  const entry4 = buildEntry(type.cylinder_4_gas, type.cylinder_4_conc, type.cylinder_4_units);

  if (entry1) gasEntries.push(entry1);
  if (entry2) gasEntries.push(entry2);
  if (entry3) gasEntries.push(entry3);
  if (entry4) gasEntries.push(entry4);

  return gasEntries.length > 0 ? gasEntries.join('; ') : `Balance: ${getGasDisplay(type.balance_gas)}`;
};

const getCylinderModelLabel = (modelId) => {
  if (!modelId) return 'N/A';
  const model = cylinderModels.value.find(m => m.id === modelId);
  return model ? model.part_number : 'Unknown Model';
};

const getCylinderModelSupplier = (modelId) => {
  if (!modelId) return 'N/A';
  const model = cylinderModels.value.find(m => m.id === modelId);
  if (!model) return 'Unknown Model';
  const supplierMap = { 'AM': 'AirMet', 'AE': 'AES', 'MS': 'MSA', 'DR': 'Draeger' };
  return supplierMap[model.supplier] || model.supplier;
};

// --- Standard Helpers ---
onMounted(async () => {
  const savedState = localStorage.getItem('cylindersFilterState');
  if (savedState) {
    const state = JSON.parse(savedState);
    sortKey.value = state.sortKey || 'label';
    sortDirection.value = state.sortDirection || 'asc';
    searchTerm.value = state.searchTerm || '';
    filterStatus.value = state.filterStatus || '';
    filterLocation.value = state.filterLocation || '';
    filterDetector.value = state.filterDetector || '';
    filterCylinderType.value = state.filterCylinderType || '';
    filterExpiresBefore.value = state.filterExpiresBefore || '';
    showEmptyCylinders.value = state.showEmptyCylinders || false;
  }

  await Promise.all([
    fetchCylinderTypes(),
    fetchCylinderModels(), // Fetch models to map to types
    fetchDetectors(),
    fetchLocations(),
    fetchCylinderStatuses()
  ]);
  await fetchCylinders();
});

const saveStateToLocalStorage = () => {
  localStorage.setItem('cylindersFilterState', JSON.stringify({
    sortKey: sortKey.value, sortDirection: sortDirection.value, searchTerm: searchTerm.value,
    filterStatus: filterStatus.value, filterLocation: filterLocation.value, filterDetector: filterDetector.value,
    filterCylinderType: filterCylinderType.value, filterExpiresBefore: filterExpiresBefore.value, showEmptyCylinders: showEmptyCylinders.value
  }));
};

const toggleSelectAll = () => {
  if (selectedCylinders.value.length === filteredCylinders.value.length) selectedCylinders.value = [];
  else selectedCylinders.value = filteredCylinders.value.map(c => c.id);
};

const openUpdateMultipleCylinders = () => {
  router.push({ name: 'UpdateMultipleCylinders', query: { ids: selectedCylinders.value.join(',') } });
};

watch([sortKey, sortDirection, searchTerm, filterStatus, filterLocation, filterDetector, filterCylinderType, filterExpiresBefore, showEmptyCylinders], () => {
  currentPage.value = 1;
  saveStateToLocalStorage();
}, { deep: true });

const fetchCylinderTypes = async () => {
  try { const result = await get('/api/inventory/cylindertypes/'); if (result.ok) cylinderTypes.value = result.data; } 
  catch (error) { console.error('Error fetching cylinder types:', error); }
};

const fetchCylinderModels = async () => {
  try { const result = await get('/api/inventory/cylindermodels/'); if (result.ok) cylinderModels.value = result.data; } 
  catch (error) { console.error('Error fetching cylinder models:', error); }
};

const fetchDetectors = async () => {
  try { const result = await get('/api/inventory/detectors/'); if (result.ok) detectors.value = result.data; } 
  catch (error) { console.error('Error fetching detectors:', error); }
};

const fetchLocations = async () => {
  try { const result = await get('/api/inventory/locations/'); if (result.ok) locations.value = result.data; } 
  catch (error) { console.error('Error fetching locations:', error); }
};

const fetchCylinderStatuses = async () => {
  try { const result = await get('/api/inventory/cylinder-statuses/'); if (result.ok) cylinderStatusChoices.value = result.data; } 
  catch (error) { console.error('Error fetching cylinder statuses:', error); }
};

const fetchCylinders = async () => {
  try {
    loading.value = true;
    const params = new URLSearchParams();
    if (searchTerm.value) params.append('search', searchTerm.value);
    if (filterStatus.value) params.append('status', filterStatus.value);
    if (filterLocation.value) params.append('location', filterLocation.value);
    if (filterDetector.value) params.append('detector', filterDetector.value);
    // Filter by the nested Cylinder Type ID
    if (filterCylinderType.value) params.append('cylinder_model__cylinder_type', filterCylinderType.value);
    if (filterExpiresBefore.value) params.append('expiry_date_lte', filterExpiresBefore.value);
    if (!showEmptyCylinders.value) params.append('exclude_status', 'MT');

    let url = '/api/inventory/cylinders/';
    if (params.toString()) url += '?' + params.toString();

    const result = await get(url);
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    cylinders.value = result.data;
    performSortingAndPagination();
  } catch (error) {
    console.error('Error fetching cylinders:', error);
  } finally { loading.value = false; }
};

const getStatusDisplay = (statusValue) => {
  if (!statusValue) return 'N/A';
  const choice = cylinderStatusChoices.value.find(c => c.value === statusValue);
  return choice ? choice.label : statusValue;
};

const getLocationLabel = (id) => locations.value.find(l => l.id === id)?.label || 'Unknown';
const getDetectorLabel = (id) => detectors.value.find(d => d.id === id)?.label || 'Unknown';

const performSortingAndPagination = () => {
  let result = [...cylinders.value];
  if (sortKey.value) {
    result.sort((a, b) => {
      let valA = a[sortKey.value]; let valB = b[sortKey.value];
      if (sortKey.value === 'location') { valA = getLocationLabel(a.location) || ''; valB = getLocationLabel(b.location) || ''; }
      else if (sortKey.value === 'detector') { valA = getDetectorLabel(a.detector) || ''; valB = getDetectorLabel(b.detector) || ''; }
      else if (sortKey.value === 'cylinder_model') { valA = getCylinderModelLabel(a.cylinder_model) || ''; valB = getCylinderModelLabel(b.cylinder_model) || ''; }
      else if (sortKey.value === 'cylinder_type') { valA = getCylinderTypeLabel(getCylinderTypeId(a.cylinder_model)) || ''; valB = getCylinderTypeLabel(getCylinderTypeId(b.cylinder_model)) || ''; }
      else if (sortKey.value === 'supplier') { valA = getCylinderModelSupplier(a.cylinder_model) || ''; valB = getCylinderModelSupplier(b.cylinder_model) || ''; }
      else if (['receive_date', 'expiry_date', 'order_date'].includes(sortKey.value)) { valA = valA ? new Date(valA) : new Date(0); valB = valB ? new Date(valB) : new Date(0); }
      else { valA = valA || ''; valB = valB || ''; }
      return sortDirection.value === 'asc' ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
    });
  }
  totalFilteredCylindersResult.value = result.length;
  totalPagesResult.value = Math.ceil(result.length / cylindersPerPage.value);
  const startIndex = (currentPage.value - 1) * cylindersPerPage.value;
  filteredCylindersResult.value = result.slice(startIndex, startIndex + cylindersPerPage.value);
};

watch([searchTerm, filterStatus, filterLocation, filterDetector, filterCylinderType, filterExpiresBefore, showEmptyCylinders], () => {
  currentPage.value = 1;
  fetchCylinders();
}, { deep: true });

watch([sortKey, sortDirection, currentPage], () => { performSortingAndPagination(); }, { deep: true });

const filteredCylinders = computed(() => filteredCylindersResult.value);
const totalPages = computed(() => totalPagesResult.value);
const totalFilteredCylinders = computed(() => totalFilteredCylindersResult.value);
const hasActiveFilters = computed(() => searchTerm.value !== '' || filterStatus.value !== '' || filterLocation.value !== '' || filterDetector.value !== '' || filterCylinderType.value !== '' || filterExpiresBefore.value !== '' || showEmptyCylinders.value === true);

const sortBy = (key) => {
  if (sortKey.value === key) sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  else { sortKey.value = key; sortDirection.value = 'asc'; }
};

const filterCylinders = () => { currentPage.value = 1; };
const toggleFilters = () => { showFilters.value = !showFilters.value; };

const resetFilters = () => {
  searchTerm.value = ''; filterStatus.value = ''; filterLocation.value = ''; filterDetector.value = '';
  filterCylinderType.value = ''; filterExpiresBefore.value = ''; showEmptyCylinders.value = false;
  sortKey.value = 'label'; sortDirection.value = 'asc'; currentPage.value = 1;
  localStorage.removeItem('cylindersFilterState');
};

const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };

const downloadPDF = () => {
  const params = new URLSearchParams();
  if (searchTerm.value) params.append('search', searchTerm.value);
  if (filterStatus.value) params.append('status', filterStatus.value);
  if (filterCylinderType.value) params.append('cylinder_model__cylinder_type', filterCylinderType.value);
  if (filterLocation.value) params.append('location', filterLocation.value);
  if (filterExpiresBefore.value) params.append('expiry_date_lte', filterExpiresBefore.value);
  if (showEmptyCylinders.value) params.append('show_empty', 'true');
  if (sortKey.value) params.append('sort_key', sortKey.value);
  if (sortDirection.value) params.append('sort_direction', sortDirection.value);
  params.append('_t', Date.now().toString());

  const queryString = params.toString();
  const url = `/api/inventory/pdf/cylinders/${queryString ? `?${queryString}` : ''}`;
  window.open(url, '_blank');
};
</script>

<style scoped>
/* ... Keep all your existing styles ... */

/* Update table column widths to accommodate the new column */
.cylinders-table th:nth-child(1), .cylinders-table td:nth-child(1) { width: 3%; }
.cylinders-table th:nth-child(2), .cylinders-table td:nth-child(2) { width: 8%; }
.cylinders-table th:nth-child(3), .cylinders-table td:nth-child(3) { width: 8%; }
.cylinders-table th:nth-child(4), .cylinders-table td:nth-child(4) { width: 9%; } /* Model */
.cylinders-table th:nth-child(5), .cylinders-table td:nth-child(5) { width: 16%; } /* Type (Gas Config) */
.cylinders-table th:nth-child(6), .cylinders-table td:nth-child(6) { width: 7%; } /* Supplier */
.cylinders-table th:nth-child(7), .cylinders-table td:nth-child(7) { width: 8%; }
.cylinders-table th:nth-child(8), .cylinders-table td:nth-child(8) { width: 9%; }
.cylinders-table th:nth-child(9), .cylinders-table td:nth-child(9) { width: 6%; }
.cylinders-table th:nth-child(10), .cylinders-table td:nth-child(10) { width: 8%; }
.cylinders-table th:nth-child(11), .cylinders-table td:nth-child(11) { width: 8%; }
.cylinders-table th:nth-child(12), .cylinders-table td:nth-child(12) { width: 8%; }
</style>