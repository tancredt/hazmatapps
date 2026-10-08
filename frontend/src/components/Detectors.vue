<template>
  <div class="inventory-list-page">
    <div class="filters-section">
      <button @click="toggleFilters" :aria-expanded="showFilters" class="filter-toggle-btn" :class="{ 'has-active-filters': hasActiveFilters }">
        {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toggle-icon">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>

      <div v-show="showFilters" class="search-and-filters-popover">
        <input
          type="text"
          v-model="searchTerm"
          placeholder="Search by label/serial..."
          class="search-input"
          @input="filterDetectors"
        >
        <select v-model="filterStatus" @change="filterDetectors" class="filter-select">
          <option value="">All Statuses</option>
          <option v-for="choice in detectorStatusChoices" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </option>
        </select>
        <select v-model="filterLocation" @change="filterDetectors" class="filter-select">
          <option value="">All Locations</option>
          <option v-for="location in locations" :key="location.id" :value="location.id">
            {{ getLocationLabel(location.id) }}
          </option>
        </select>
	<select v-model="filterDistrict" @change="filterDetectors" class="filter-select">
       	  <option value="">All Districts</option>
          <option v-for="d in districts" :key="d.value" :value="d.value">
            {{ d.label }}
          </option>
        </select>
        <select v-model="filterModel" @change="filterDetectors" class="filter-select">
          <option value="">All Models</option>
          <option v-for="model in detectorModels" :key="model.id" :value="model.id">
            {{ getModelName(model.id) }}
          </option>
        </select>
        <select v-model="filterConfiguration" @change="filterDetectors" class="filter-select">
          <option value="">All Configurations</option>
          <option v-for="config in detectorModelConfigurations" :key="config.id" :value="config.id">
            {{ getConfigurationLabel(config.id) }}
          </option>
        </select>
        <div class="checkbox-container">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="showDecommissionedDetectors"
              @change="filterDetectors"
            />
            Show Decommissioned Detectors
          </label>
        </div>
        <div class="reset-btn-wrapper">
          <button @click="resetFilters" class="reset-btn">Reset Filters</button>
        </div>
      </div>
    </div>

    <div class="page-container">
      <div class="header-actions">
        <h1>Detectors Management</h1>
        <div class="action-buttons">
          <router-link to="/detectors/new" class="btn btn-primary">Add New Detector</router-link>
          <router-link to="/detectors/add-multiple" class="btn btn-primary">Add Multiple Detectors</router-link>
          <button
            @click="downloadPDF"
            class="btn btn-primary"
            title="Download as PDF"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
              <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="table-container">
        <table class="inventory-table inventory-table--detectors">
          <thead>
            <tr>
              <th @click="sortBy('label')" class="sortable">
                Label <span v-if="sortKey === 'label'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('serial')" class="sortable">
                Serial <span v-if="sortKey === 'serial'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('model')" class="sortable">
                Model <span v-if="sortKey === 'model'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('location')" class="sortable">
                Location <span v-if="sortKey === 'location'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('district')" class="sortable">
                District <span v-if="sortKey === 'district'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('status')" class="sortable">
                Status <span v-if="sortKey === 'status'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('configuration')" class="sortable">
                Configuration <span v-if="sortKey === 'configuration'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('firmware')" class="sortable">
                Firmware <span v-if="sortKey === 'firmware'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('purchase_date')" class="sortable">
                Purchase Date <span v-if="sortKey === 'purchase_date'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('location_updated')" class="sortable">
                Loc. Updated <span v-if="sortKey === 'location_updated'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="detector in filteredDetectors" :key="detector.id">
              <td>
                <router-link :to="`/detectors/${detector.id}`" class="record-link">
                  {{ detector.label }}
                </router-link>
              </td>
              <td>{{ detector.serial || 'N/A' }}</td>
              <td>{{ getModelName(detector.detector_model) }}</td>
              <td>{{ getLocationLabel(detector.location) }}</td>
              <td>{{ getDistrict(detector.location) }}</td>
              <td>{{ getStatusDisplay(detector.status) }}</td>
              <td>{{ getConfigurationDisplay(detector.configuration) || 'N/A' }}</td>
              <td>{{ detector.firmware || 'N/A' }}</td>
              <td>{{ detector.purchase_date || 'N/A' }}</td>
              <td>{{ formatLocationUpdated(detector.location_updated) || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="loading" class="loading">Loading detectors...</div>
        <div v-else-if="totalFilteredDetectors === 0" class="no-data">No detectors found</div>

        <!-- Pagination Controls -->
        <div v-if="!loading && totalFilteredDetectors > 0" class="pagination-container">
          <div class="pagination-info">
            Showing {{ ((currentPage - 1) * detectorsPerPage) + 1 }} to
            {{ Math.min(currentPage * detectorsPerPage, totalFilteredDetectors) }} of
            {{ totalFilteredDetectors }} detectors
          </div>
          <div class="pagination-controls">
            <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-pagination">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>

            <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>

            <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-pagination">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { get } from '@/utils/api.js';

// State for detectors data
const detectors = ref([]);
const loading = ref(true);

// State for related data
const detectorModels = ref([]);
const locations = ref([]);
const districts = ref([]);
const detectorModelConfigurations = ref([]);
const detectorStatusChoices = ref([]);
const manufacturers = ref([]); // <--- ADDED: State for manufacturers

// State for sorting and filtering
const sortKey = ref('label');
const sortDirection = ref('asc');
const searchTerm = ref('');
const filterStatus = ref('');
const filterLocation = ref('');
const filterDistrict = ref('');
const filterModel = ref('');
const filterConfiguration = ref('');

const showDecommissionedDetectors = ref(false);
const showFilters = ref(false);

// State for pagination
const currentPage = ref(1);
const detectorsPerPage = ref(50);

const filteredDetectorsResult = ref([]);
const totalFilteredDetectorsResult = ref(0);
const totalPagesResult = ref(0);

// Initialize state from localStorage
onMounted(async () => {
  const savedState = localStorage.getItem('detectorsFilterState');
  if (savedState) {
    const state = JSON.parse(savedState);
    sortKey.value = state.sortKey || 'label';
    sortDirection.value = state.sortDirection || 'asc';
    searchTerm.value = state.searchTerm || '';
    filterStatus.value = state.filterStatus || '';
    filterLocation.value = state.filterLocation || '';
    filterDistrict.value = state.filterDistrict || '';
    filterModel.value = state.filterModel || '';
    filterConfiguration.value = state.filterConfiguration || '';
    showDecommissionedDetectors.value = state.showDecommissionedDetectors || false;
  }

  // Load related data first
  await Promise.all([
    fetchDetectorModels(),
    fetchLocations(),
    fetchDistricts(),
    fetchDetectorModelConfigurations(),
    fetchDetectorStatuses(),
    fetchManufacturers() // <--- ADDED: Fetch manufacturers
  ]);

  // Then load detectors
  await fetchDetectors();
});

// --- Fetch Functions ---
const fetchDetectorModels = async () => {
  try {
    const result = await get('/api/inventory/detectormodels/');
    if (result.ok) detectorModels.value = result.data;
  } catch (error) { console.error('Error fetching detector models:', error); }
};

const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');
    if (result.ok) locations.value = result.data;
  } catch (error) { console.error('Error fetching locations:', error); }
};

const fetchDistricts = async () => {
  try {
    const result = await get('/api/inventory/districts/');
    if (result.ok) districts.value = result.data;
  } catch (error) { console.error('Error fetching districts:', error); }
};

const fetchDetectorModelConfigurations = async () => {
  try {
    const result = await get('/api/inventory/detectormodelconfigurations/');
    if (result.ok) detectorModelConfigurations.value = result.data;
  } catch (error) { console.error('Error fetching detector model configurations:', error); }
};

const fetchDetectorStatuses = async () => {
  try {
    const result = await get('/api/inventory/detector-statuses/');
    if (result.ok) detectorStatusChoices.value = result.data;
  } catch (error) { console.error('Error fetching detector statuses:', error); }
};

// <--- ADDED: Fetch Manufacturers ---
const fetchManufacturers = async () => {
  try {
    const result = await get('/api/inventory/manufacturers/');
    if (result.ok) manufacturers.value = result.data;
  } catch (error) { console.error('Error fetching manufacturers:', error); }
};

const fetchDetectors = async () => {
  try {
    loading.value = true;
    const params = new URLSearchParams();

    if (searchTerm.value) params.append('search', searchTerm.value);
    if (filterStatus.value) params.append('status', filterStatus.value);
    if (filterLocation.value) params.append('location', filterLocation.value);
    if (filterDistrict.value) params.append('location__district', filterDistrict.value);
    if (filterModel.value) params.append('detector_model', filterModel.value);
    if (filterConfiguration.value) params.append('configuration', filterConfiguration.value);
    if (!showDecommissionedDetectors.value) params.append('exclude_status', 'DC');

    let url = '/api/inventory/detectors/';
    if (params.toString()) url += '?' + params.toString();

    const result = await get(url);
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);

    detectors.value = result.data;
    performSortingAndPagination();
  } catch (error) {
    console.error('Error fetching detectors:', error);
  } finally {
    loading.value = false;
  }
};

// --- Helper Functions ---
const getStatusDisplay = (statusValue) => {
  if (!statusValue) return 'N/A';
  const choice = detectorStatusChoices.value.find(c => c.value === statusValue);
  return choice ? choice.label.trim() : statusValue;
};

const getConfigurationDisplay = (configValue) => {
  if (!configValue) return 'N/A';
  if (typeof configValue === 'object' && configValue.label) return configValue.label;
  if (typeof configValue === 'string' || typeof configValue === 'number') return getConfigurationLabel(configValue);
  return 'N/A';
};

const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
};

const getDistrict = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location && location.district ? location.district : 'N/A';
};

const getModelName = (modelId) => {
  if (!modelId) return 'N/A';
  const model = detectorModels.value.find(m => m.id === modelId);
  return model ? model.label : 'Unknown Model';
};

const getConfigurationLabel = (configId) => {
  if (!configId) return 'N/A';
  const config = detectorModelConfigurations.value.find(c => c.id === configId);
  if (!config) return 'Unknown Configuration';
  const modelName = getModelName(config.detector_model);
  return `${config.label} (${modelName})`;
};

// <--- UPDATED: Dynamically map manufacturer codes ---
const getDetectorModelManufacturer = (modelId) => {
  if (!modelId) return 'N/A';
  const model = detectorModels.value.find(m => m.id === modelId);
  if (!model || !model.manufacturer) return 'Unknown Manufacturer';

  const found = manufacturers.value.find(m => m.value === model.manufacturer);
  return found ? found.label.trim() : model.manufacturer;
};

const formatLocationUpdated = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-GB', { year: 'numeric', month: '2-digit', day: '2-digit' });
};

// --- Sorting & Pagination ---
const performSortingAndPagination = () => {
  let result = [...detectors.value];

  if (sortKey.value) {
    result.sort((a, b) => {
      let valA = a[sortKey.value];
      let valB = b[sortKey.value];

      if (sortKey.value === 'location') { valA = getLocationLabel(a.location) || ''; valB = getLocationLabel(b.location) || ''; }
      else if (sortKey.value === 'district') { valA = getDistrict(a.location) || ''; valB = getDistrict(b.location) || ''; }
      else if (sortKey.value === 'model') { valA = getModelName(a.detector_model) || ''; valB = getModelName(b.detector_model) || ''; }
      else if (sortKey.value === 'configuration') { valA = getConfigurationDisplay(a.configuration) || ''; valB = getConfigurationDisplay(b.configuration) || ''; }
      else if (['purchase_date', 'location_updated'].includes(sortKey.value)) { valA = valA ? new Date(valA) : new Date(0); valB = valB ? new Date(valB) : new Date(0); }
      else { valA = valA || ''; valB = valB || ''; }

      return sortDirection.value === 'asc' ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
    });
  }

  totalFilteredDetectorsResult.value = result.length;
  totalPagesResult.value = Math.ceil(result.length / detectorsPerPage.value);

  const startIndex = (currentPage.value - 1) * detectorsPerPage.value;
  const endIndex = startIndex + detectorsPerPage.value;
  filteredDetectorsResult.value = result.slice(startIndex, endIndex);
};

// --- Watchers ---
const saveStateToLocalStorage = () => {
  localStorage.setItem('detectorsFilterState', JSON.stringify({
    sortKey: sortKey.value, sortDirection: sortDirection.value, searchTerm: searchTerm.value,
    filterStatus: filterStatus.value, filterLocation: filterLocation.value, filterDistrict: filterDistrict.value,
    filterModel: filterModel.value, filterConfiguration: filterConfiguration.value,
    showDecommissionedDetectors: showDecommissionedDetectors.value
  }));
};

watch([sortKey, sortDirection, searchTerm, filterStatus, filterLocation, filterDistrict, filterModel, filterConfiguration, showDecommissionedDetectors], () => {
  currentPage.value = 1;
  saveStateToLocalStorage();
}, { deep: true });

watch([searchTerm, filterStatus, filterLocation, filterModel, filterConfiguration, showDecommissionedDetectors], () => {
  currentPage.value = 1;
  fetchDetectors();
}, { deep: true });

watch([sortKey, sortDirection, currentPage], () => { performSortingAndPagination(); }, { deep: true });

// --- Computed Properties ---
const filteredDetectors = computed(() => filteredDetectorsResult.value);
const totalPages = computed(() => totalPagesResult.value);
const totalFilteredDetectors = computed(() => totalFilteredDetectorsResult.value);
const hasActiveFilters = computed(() => searchTerm.value !== '' || filterStatus.value !== '' || filterLocation.value !== '' || filterModel.value !== '' || filterConfiguration.value !== '' || showDecommissionedDetectors.value === true);

// --- UI Actions ---
const sortBy = (key) => {
  if (sortKey.value === key) sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  else { sortKey.value = key; sortDirection.value = 'asc'; }
};

const filterDetectors = () => { currentPage.value = 1; };
const toggleFilters = () => { showFilters.value = !showFilters.value; };

const resetFilters = () => {
  searchTerm.value = ''; filterStatus.value = ''; filterLocation.value = ''; filterDistrict.value = '';
  filterModel.value = ''; filterConfiguration.value = ''; showDecommissionedDetectors.value = false;
  sortKey.value = 'label'; sortDirection.value = 'asc'; currentPage.value = 1;
  localStorage.removeItem('detectorsFilterState');
};

const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };

const downloadPDF = () => {
  const params = new URLSearchParams();
  if (searchTerm.value) params.append('search', searchTerm.value);
  if (filterStatus.value) params.append('status', filterStatus.value);
  if (filterModel.value) params.append('detector_model', filterModel.value);
  if (filterLocation.value) params.append('location', filterLocation.value);
  if (filterDistrict.value) params.append('location__district', filterDistrict.value);
  if (filterConfiguration.value) params.append('configuration', filterConfiguration.value);
  if (showDecommissionedDetectors.value) params.append('show_decommissioned', 'true');
  if (sortKey.value) params.append('sort_key', sortKey.value);
  if (sortDirection.value) params.append('sort_direction', sortDirection.value);
  params.append('_t', Date.now().toString());

  const queryString = params.toString();
  const url = `/api/inventory/pdf/detectors/${queryString ? `?${queryString}` : ''}`;
  window.open(url, '_blank');
};
</script>

