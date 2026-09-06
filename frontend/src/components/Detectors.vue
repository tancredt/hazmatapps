<template>
  <div class="detectors-page">
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
        <table class="detectors-table">
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
                <router-link :to="`/detectors/${detector.id}`" class="detector-link">
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

// State for filter panel visibility
const showFilters = ref(false);

// State for pagination
const currentPage = ref(1);
const detectorsPerPage = ref(50);

// State for filtered results and totals
const filteredDetectorsResult = ref([]);
const totalFilteredDetectorsResult = ref(0);
const totalPagesResult = ref(0);

// Initialize state from localStorage
onMounted(async () => {
  // Load saved state from localStorage
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

  // Load detector models, locations, configurations, and statuses first
  await Promise.all([
    fetchDetectorModels(),
    fetchLocations(),
    fetchDistricts(),
    fetchDetectorModelConfigurations(),
    fetchDetectorStatuses()
  ]);

  // Then load detectors
  await fetchDetectors();
});

// Function to save state to localStorage
const saveStateToLocalStorage = () => {
  const state = {
    sortKey: sortKey.value,
    sortDirection: sortDirection.value,
    searchTerm: searchTerm.value,
    filterStatus: filterStatus.value,
    filterLocation: filterLocation.value,
    filterDistrict: filterDistrict.value,
    filterModel: filterModel.value,
    filterConfiguration: filterConfiguration.value,
    showDecommissionedDetectors: showDecommissionedDetectors.value
  };
  localStorage.setItem('detectorsFilterState', JSON.stringify(state));
};

// Watch for changes to filter/sort parameters and save to localStorage
watch([sortKey, sortDirection, searchTerm, filterStatus, filterLocation, filterDistrict, filterModel, filterConfiguration, showDecommissionedDetectors], () => {
  // Reset to first page when filters/sorting changes
  currentPage.value = 1;
  saveStateToLocalStorage();
}, { deep: true });


// Fetch detector models from the API
const fetchDetectorModels = async () => {
  try {
    const result = await get('/api/inventory/detectormodels/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    detectorModels.value = result.data;
  } catch (error) {
    console.error('Error fetching detector models:', error);
  }
};

// Fetch locations from the API
const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    locations.value = result.data;
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
};

// Fetch districts from the API
const fetchDistricts = async () => {
  try {
    const result = await get('/api/inventory/districts/');
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    districts.value = result.data;
  } catch (error) {
    console.error('Error fetching districts:', error);
  }
};

// Fetch detector model configurations from the API
const fetchDetectorModelConfigurations = async () => {
  try {
    const result = await get('/api/inventory/detectormodelconfigurations/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    detectorModelConfigurations.value = result.data;
  } catch (error) {
    console.error('Error fetching detector model configurations:', error);
  }
};

// Fetch detector statuses from the API
const fetchDetectorStatuses = async () => {
  try {
    const result = await get('/api/inventory/detector-statuses/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    detectorStatusChoices.value = result.data;
  } catch (error) {
    console.error('Error fetching detector statuses:', error);
  }
};




// Fetch detectors from the API
const fetchDetectors = async () => {
  try {
    loading.value = true;

    // Build query parameters based on filters
    const params = new URLSearchParams();

    // Add search filter
    if (searchTerm.value) {
      params.append('search', searchTerm.value);
    }

    // Add status filter
    if (filterStatus.value) {
      params.append('status', filterStatus.value);
    }

    // Add location filter
    if (filterLocation.value) {
      params.append('location', filterLocation.value);
    }

    // Add district filter
    if (filterDistrict.value) {
      params.append('location__district', filterDistrict.value);
    }
    // Add model filter
    if (filterModel.value) {
      params.append('detector_model', filterModel.value);
    }

    // Add configuration filter
    if (filterConfiguration.value) {
      params.append('configuration', filterConfiguration.value);
    }

    // Add exclude decommissioned filter (default behavior when checkbox is not selected)
    if (!showDecommissionedDetectors.value) {
      params.append('exclude_status', 'DC');
    }

    // Build the URL with parameters
    let url = '/api/inventory/detectors/';
    if (params.toString()) {
      url += '?' + params.toString();
    }

    // Fetch detectors from the Django REST API
    const result = await get(url);

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    detectors.value = result.data;

    // Apply sorting and pagination after fetching
    performSortingAndPagination();
  } catch (error) {
    console.error('Error fetching detectors:', error);
    // In case of error, we could show a user-friendly message
  } finally {
    loading.value = false;
  }
};

// Get status label from choices
const getStatusDisplay = (statusValue) => {
  if (!statusValue) return 'N/A';
  const choice = detectorStatusChoices.value.find(c => c.value === statusValue);
  return choice ? choice.label : statusValue;
};

// Configuration display mapping
const getConfigurationDisplay = (configValue) => {
  if (!configValue) return 'N/A';
  // If configValue is an object with a label property, use it directly
  if (typeof configValue === 'object' && configValue.label) {
    return configValue.label;
  }
  // Otherwise, treat it as an ID and use local state
  if (typeof configValue === 'string' || typeof configValue === 'number') {
    return getConfigurationLabel(configValue);
  }
  return 'N/A';
};

// Helper functions to get related object labels using local state
const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
}

const getDistrict = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location && location.district ? location.district : 'N/A';
};

const getModelName = (modelId) => {
  if (!modelId) return 'N/A';
  const model = detectorModels.value.find(m => m.id === modelId);
  return model ? model.label : 'Unknown Model';
}

const getConfigurationLabel = (configId) => {
  if (!configId) return 'N/A';
  const config = detectorModelConfigurations.value.find(c => c.id === configId);
  if (!config) return 'Unknown Configuration';

  // Get the detector model name using the detector model ID
  const modelName = getModelName(config.detector_model);
  return `${config.label} (${modelName})`;
};

// Helper function to get manufacturer from detector model
const getDetectorModelManufacturer = (modelId) => {
  if (!modelId) return 'N/A';
  const model = detectorModels.value.find(m => m.id === modelId);
  if (!model) return 'Unknown Manufacturer';

  // Map manufacturer codes to their display names
  const manufacturerMap = {
    'HW': 'Honeywell/Rae',
    'MS': 'MSA',
    'DR': 'Draeger',
    'PR': 'Proengin',
    'TS': 'Thermo Scientific'
  };

  return manufacturerMap[model.manufacturer] || model.manufacturer;
};

// Helper function to format location_updated timestamp
const formatLocationUpdated = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-GB', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

// Function to perform sorting and pagination
const performSortingAndPagination = () => {
  let result = [...detectors.value];

  // Apply sorting
  if (sortKey.value) {
    result.sort((a, b) => {
      let valA = a[sortKey.value];
      let valB = b[sortKey.value];

      // Handle nested properties
      if (sortKey.value === 'location') {
        valA = getLocationLabel(a.location) || '';
        valB = getLocationLabel(b.location) || '';
      } else if (sortKey.value === 'district') {
        valA = getDistrict(a.location) || '';
        valB = getDistrict(b.location) || '';
      } else if (sortKey.value === 'model') {
        valA = getModelName(a.detector_model) || '';
        valB = getModelName(b.detector_model) || '';
      } else if (sortKey.value === 'configuration') {
        valA = getConfigurationDisplay(a.configuration) || '';
        valB = getConfigurationDisplay(b.configuration) || '';
      } else if (sortKey.value === 'purchase_date') {
        valA = valA ? new Date(valA) : new Date(0);
        valB = valB ? new Date(valB) : new Date(0);
      } else if (sortKey.value === 'location_updated') {
        valA = valA ? new Date(valA) : new Date(0);
        valB = valB ? new Date(valB) : new Date(0);
      } else {
        valA = valA || '';
        valB = valB || '';
      }

      if (sortDirection.value === 'asc') {
        return valA > valB ? 1 : -1;
      } else {
        return valA < valB ? 1 : -1;
      }
    });
  }

  // Store the total count
  totalFilteredDetectorsResult.value = result.length;

  // Calculate total pages
  totalPagesResult.value = Math.ceil(result.length / detectorsPerPage.value);

  // Apply pagination
  const startIndex = (currentPage.value - 1) * detectorsPerPage.value;
  const endIndex = startIndex + detectorsPerPage.value;
  filteredDetectorsResult.value = result.slice(startIndex, endIndex);
};

// Watch for changes to filter parameters and re-fetch from API
watch(
  [searchTerm, filterStatus, filterLocation, filterModel, filterConfiguration, showDecommissionedDetectors],
  () => {
    // Reset to first page when filters change
    currentPage.value = 1;
    fetchDetectors();
  },
  { deep: true }
);

// Watch for changes to sort/pagination parameters and re-sort locally
watch(
  [sortKey, sortDirection, currentPage],
  () => {
    performSortingAndPagination();
  },
  { deep: true }
);

// Computed property to get filtered and sorted detectors
const filteredDetectors = computed(() => {
  return filteredDetectorsResult.value;
});

// Computed property to get total number of pages
const totalPages = computed(() => {
  return totalPagesResult.value;
});

// Computed property to get the total number of filtered detectors (before pagination)
const totalFilteredDetectors = computed(() => {
  return totalFilteredDetectorsResult.value;
});

// Computed property to check if any filters are active
const hasActiveFilters = computed(() => {
  return searchTerm.value !== '' ||
    filterStatus.value !== '' ||
    filterLocation.value !== '' ||
    filterModel.value !== '' ||
    filterConfiguration.value !== '' ||
    showDecommissionedDetectors.value === true;
});

// Function to sort the table
const sortBy = (key) => {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDirection.value = 'asc';
  }
};

// Function to filter detectors (called on input)
const filterDetectors = () => {
  // Reset to first page when filtering
  currentPage.value = 1;
  // Filtering will be handled by the watcher
};

// Function to toggle the filter panel
const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};

// Function to reset all filters
const resetFilters = () => {
  searchTerm.value = '';
  filterStatus.value = '';
  filterLocation.value = '';
  filterDistrict.value = '';
  filterModel.value = '';
  filterConfiguration.value = '';
  showDecommissionedDetectors.value = false;
  sortKey.value = 'label';
  sortDirection.value = 'asc';
  currentPage.value = 1; // Reset to first page when filters are reset

  // Clear the saved state in localStorage
  localStorage.removeItem('detectorsFilterState');
};

// Pagination functions
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};

// Function to download the table as PDF from backend
const downloadPDF = () => {
  // Build URL with current filters
  const params = new URLSearchParams();

  if (searchTerm.value) {
    params.append('search', searchTerm.value);
  }
  if (filterStatus.value) {
    params.append('status', filterStatus.value);
  }
  if (filterModel.value) {
    params.append('detector_model', filterModel.value);
  }
  if (filterLocation.value) {
    params.append('location', filterLocation.value);
  }
  if (filterDistrict.value) {
    params.append('location__district', filterDistrict.value);
  }
  if (filterConfiguration.value) {
    params.append('configuration', filterConfiguration.value);
  }
  if (showDecommissionedDetectors.value) {
    params.append('show_decommissioned', 'true');
  }
  
  // Add sort parameters
  if (sortKey.value) {
    params.append('sort_key', sortKey.value);
  }
  if (sortDirection.value) {
    params.append('sort_direction', sortDirection.value);
  }
  
  // Add cache-busting timestamp
  params.append('_t', Date.now().toString());

  const queryString = params.toString();
  const url = `/api/inventory/pdf/detectors/${queryString ? `?${queryString}` : ''}`;

  // Open in new tab or download directly
  window.open(url, '_blank');
};
</script>

<style scoped>
.detectors-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.filters-section {
  margin-bottom: 0.25rem;
  position: relative;
  display: inline-block;
}

.filter-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  transition: background-color 0.3s ease;
}

.filter-toggle-btn:hover {
  background-color: #36966d;
}

.filter-toggle-btn.has-active-filters {
  background-color: #e67e22;
}

.filter-toggle-btn.has-active-filters:hover {
  background-color: #d35400;
}

.toggle-icon {
  transition: transform 0.3s ease;
}

.filter-toggle-btn[aria-expanded="true"] .toggle-icon {
  transform: rotate(180deg);
}

.search-and-filters-popover {
  position: absolute;
  top: 100%;
  left: 0;
  width: 20%;
  min-width: 300px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.reset-btn-wrapper {
  align-self: flex-start;
}

.search-input {
  padding: 0.4rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

.filter-select {
  padding: 0.4rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.reset-btn {
  padding: 0.4rem 0.75rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.reset-btn:hover {
  background-color: #c82333;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.5rem 1rem;
  height: calc(100vh - 50px); /* Full height minus navbar */
  overflow: hidden; /* Prevent page scrolling */
  display: flex;
  flex-direction: column;
}

h1 {
  color: #2c3e50;
  margin-bottom: 0.25rem;
  font-size: 1.4rem;
  flex-shrink: 0; /* Don't shrink header */
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
  flex-shrink: 0; /* Don't shrink actions */
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.4rem 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background-color: #42b883;
  color: white;
}

.btn-primary:hover {
  background-color: #36966d;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.table-container {
  display: flex;
  flex-direction: column;
  flex: 1; /* Fill remaining space */
  overflow: hidden; /* Prevent overflow */
  min-height: 0; /* Allow flex item to shrink below content size */
}

.detectors-table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;
  table-layout: fixed;
  margin-bottom: 0; /* Remove bottom margin since pagination is below */
}

.detectors-table thead th {
  position: sticky; /* Make headers stick to the top */
  top: 0;
  background-color: #f8f9fa;
  font-weight: 600;
  word-wrap: break-word;
  z-index: 10; /* Ensure headers stay above scrolled content */
  border-bottom: 1px solid #ddd;
  padding: 0.4rem;
}

.detectors-table tbody {
  display: block;
  max-height: calc(100vh - 220px); /* Account for navbar, headers, actions, pagination */
  overflow-y: auto;
}

.detectors-table thead,
.detectors-table tbody tr {
  display: table;
  width: 100%;
  table-layout: fixed;
}

.detectors-table th,
.detectors-table td {
  padding: 0.4rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
  word-wrap: break-word;
}

.detectors-table th:nth-child(1),
.detectors-table td:nth-child(1) {
  width: 12%; /* Label */
}

.detectors-table th:nth-child(2),
.detectors-table td:nth-child(2) {
  width: 15%; /* Serial */
}

.detectors-table th:nth-child(3),
.detectors-table td:nth-child(3) {
  width: 16%; /* Model */
}

.detectors-table th:nth-child(4),
.detectors-table td:nth-child(4) {
  width: 12%; /* Location */
}

.detectors-table th:nth-child(5),
.detectors-table td:nth-child(5) {
  width: 12%; /* District */
}


.detectors-table th:nth-child(6),
.detectors-table td:nth-child(6) {
  width: 8%; /* Status */
}

.detectors-table th:nth-child(7),
.detectors-table td:nth-child(7) {
  width: 13%; /* Configuration */
}

.detectors-table th:nth-child(8),
.detectors-table td:nth-child(8) {
  width: 5%; /* Firmware */
}

.detectors-table th:nth-child(9),
.detectors-table td:nth-child(9) {
  width: 10%; /* Purchase Date */
}

.detectors-table th:nth-child(10),
.detectors-table td:nth-child(10) {
  width: 10%; /* Loc. Updated */
}

.detectors-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  position: relative;
  word-wrap: break-word;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: #e9ecef;
}

.detectors-table tbody tr:hover {
  background-color: #f8f9fa;
}

.detector-link {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

.detector-link:hover {
  text-decoration: underline;
}

.loading, .no-data {
  text-align: center;
  padding: 2rem;
  font-style: italic;
  color: #666;
}

@media (max-width: 768px) {
  .filters-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .nav-links {
    order: 3;
    width: 100%;
    justify-content: center;
  }

  .search-and-filters {
    order: 2;
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .search-input, .filter-select {
    width: 100%;
    margin-bottom: 0.5rem;
  }

  .page-container {
    padding: 0 1rem;
    margin-top: 1rem;
  }
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-button {
  background-color: #2c3e50;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  text-align: center;
  font-size: 1rem;
}

.dropdown-button:hover {
  background-color: #34495e;
}

.dropdown-content {
  display: none;
  position: absolute;
  background-color: #f9f9f9;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
  z-index: 1;
  border-radius: 4px;
  top: 100%;
  left: 0;
}

.dropdown-content a {
  color: black;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
}

.dropdown-content a:hover {
  background-color: #f1f1f1;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown:hover .dropdown-button {
  background-color: #34495e;
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
  max-width: 500px;
  width: 90%;
  z-index: 1001;
}

.dialog-box h3 {
  margin-top: 0;
  color: #2c3e50;
  text-align: center;
}

.location-form {
  text-align: left;
  margin-top: 1rem;
}

.location-form .form-group {
  margin-bottom: 1rem;
}

.location-form .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.location-form .form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.location-form .form-control:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
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

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.25rem;
  padding: 0.25rem 0;
}

.pagination-info {
  color: #666;
  font-size: 0.85rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-controls .page-info {
  color: #666;
  font-size: 0.85rem;
  min-width: 100px;
  text-align: center;
}

.btn-pagination {
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}

.btn-pagination:hover:not(:disabled) {
  background-color: #5a6268;
}

.btn-pagination:disabled {
  background-color: #adb5bd;
  cursor: not-allowed;
  opacity: 0.6;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #495057;
}
</style>