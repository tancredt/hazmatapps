<template>
  <div class="cylinders-page">
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
          @input="filterCylinders"
        >
        <select v-model="filterStatus" @change="filterCylinders" class="filter-select">
          <option value="">All Statuses</option>
          <option v-for="choice in cylinderStatusChoices" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </option>
        </select>
        <select v-model="filterDetector" @change="filterCylinders" class="filter-select">
          <option value="">All Detectors</option>
          <option v-for="detector in detectors" :key="detector.id" :value="detector.id">
            {{ getDetectorLabel(detector.id) }}
          </option>
        </select>
        <select v-model="filterLocation" @change="filterCylinders" class="filter-select">
          <option value="">All Locations</option>
          <option v-for="location in locations" :key="location.id" :value="location.id">
            {{ getLocationLabel(location.id) }}
          </option>
        </select>
        <select v-model="filterCylinderType" @change="filterCylinders" class="filter-select">
          <option value="">All Cylinder Types</option>
          <option v-for="cylinderType in cylinderTypes" :key="cylinderType.id" :value="cylinderType.id">
            {{ getCylinderTypeLabel(cylinderType.id) }}
          </option>
        </select>
        <div class="date-filter-container">
          <label for="expiresBefore" class="date-label">Expires Before:</label>
          <input
            id="expiresBefore"
            type="date"
            v-model="filterExpiresBefore"
            @change="filterCylinders"
            class="date-input"
          />
        </div>
        <div class="checkbox-container">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="showEmptyCylinders"
              @change="filterCylinders"
            />
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
          <button
            @click="openUpdateMultipleCylinders"
            :disabled="selectedCylinders.length === 0"
            class="btn btn-primary"
          >
            Update Multiple Cylinders
          </button>
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
        <table class="cylinders-table">
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  @change="toggleSelectAll"
                  :checked="selectedCylinders.length === filteredCylinders.length && filteredCylinders.length > 0"
                />
              </th>
              <th @click="sortBy('label')" class="sortable">
                Label <span v-if="sortKey === 'label'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('serial')" class="sortable">
                Serial <span v-if="sortKey === 'serial'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('cylinder_type')" class="sortable">
                Cylinder Type <span v-if="sortKey === 'cylinder_type'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('supplier')" class="sortable">
                Supplier <span v-if="sortKey === 'supplier'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('detector')" class="sortable">
                Detector <span v-if="sortKey === 'detector'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('location')" class="sortable">
                Location <span v-if="sortKey === 'location'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('status')" class="sortable">
                Status <span v-if="sortKey === 'status'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('order_date')" class="sortable">
                Order Date <span v-if="sortKey === 'order_date'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('receive_date')" class="sortable">
                Receive Date <span v-if="sortKey === 'receive_date'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('expiry_date')" class="sortable">
                Expiry Date <span v-if="sortKey === 'expiry_date'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cylinder in filteredCylinders" :key="cylinder.id">
              <td>
                <input
                  type="checkbox"
                  :value="cylinder.id"
                  v-model="selectedCylinders"
                />
              </td>
              <td>
                <router-link :to="`/cylinders/${cylinder.id}`" class="cylinder-link">
                  {{ cylinder.label }}
                </router-link>
              </td>
              <td>{{ cylinder.serial || 'N/A' }}</td>
              <td>{{ getCylinderTypeLabel(cylinder.cylinder_type) || 'N/A' }}</td>
              <td>{{ getCylinderTypeSupplier(cylinder.cylinder_type) || 'N/A' }}</td>
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

        <!-- Pagination Controls -->
        <div v-if="!loading && totalFilteredCylinders > 0" class="pagination-container">
          <div class="pagination-info">
            Showing {{ ((currentPage - 1) * cylindersPerPage) + 1 }} to
            {{ Math.min(currentPage * cylindersPerPage, totalFilteredCylinders) }} of
            {{ totalFilteredCylinders }} cylinders
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
import { useRouter } from 'vue-router';
import { get } from '@/utils/api';

const router = useRouter();

// State for cylinders data
const cylinders = ref([]);
const loading = ref(true);

// State for related data
const cylinderTypes = ref([]);
const locations = ref([]);
const detectors = ref([]);
const cylinderStatusChoices = ref([]);

// State for sorting and filtering
const sortKey = ref('label');
const sortDirection = ref('asc');
const searchTerm = ref('');
const filterStatus = ref('');
const filterLocation = ref('');
const filterCylinderType = ref('');
const filterDetector = ref('');
const filterExpiresBefore = ref('');
const showEmptyCylinders = ref(false);

// State for filter panel visibility
const showFilters = ref(false);

// State for pagination
const currentPage = ref(1);
const cylindersPerPage = ref(50);

// State for selected cylinders
const selectedCylinders = ref([]);

// State for filtered results and totals
const filteredCylindersResult = ref([]);
const totalFilteredCylindersResult = ref(0);
const totalPagesResult = ref(0);

// Initialize state from localStorage
onMounted(async () => {
  // Load saved state from localStorage
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

  // Load cylinder types, detectors, locations, and statuses first
  await Promise.all([
    fetchCylinderTypes(),
    fetchDetectors(),
    fetchLocations(),
    fetchCylinderStatuses()
  ]);

  // Then load cylinders
  await fetchCylinders();
});

// Function to save state to localStorage
const saveStateToLocalStorage = () => {
  const state = {
    sortKey: sortKey.value,
    sortDirection: sortDirection.value,
    searchTerm: searchTerm.value,
    filterStatus: filterStatus.value,
    filterLocation: filterLocation.value,
    filterDetector: filterDetector.value,
    filterCylinderType: filterCylinderType.value,
    filterExpiresBefore: filterExpiresBefore.value,
    showEmptyCylinders: showEmptyCylinders.value
  };
  localStorage.setItem('cylindersFilterState', JSON.stringify(state));
};

// Toggle select all cylinders
const toggleSelectAll = () => {
  if (selectedCylinders.value.length === filteredCylinders.value.length) {
    // If all are selected, deselect all
    selectedCylinders.value = [];
  } else {
    // Otherwise, select all visible cylinders
    selectedCylinders.value = filteredCylinders.value.map(cylinder => cylinder.id);
  }
};

// Open update multiple cylinders form
const openUpdateMultipleCylinders = () => {
  // Navigate to the update multiple cylinders page with selected cylinder IDs
  router.push({
    name: 'UpdateMultipleCylinders',
    query: { ids: selectedCylinders.value.join(',') }
  });
};

// Watch for changes to filter/sort parameters and save to localStorage
watch([sortKey, sortDirection, searchTerm, filterStatus, filterLocation, filterDetector, filterCylinderType, filterExpiresBefore, showEmptyCylinders], () => {
  // Reset to first page when filters/sorting changes
  currentPage.value = 1;
  saveStateToLocalStorage();
}, { deep: true });

// Fetch cylinder types from the API
const fetchCylinderTypes = async () => {
  try {
    const result = await get('/api/inventory/cylindertypes/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    cylinderTypes.value = result.data;
  } catch (error) {
    console.error('Error fetching cylinder types:', error);
  }
};

// Fetch detectors from the API
const fetchDetectors = async () => {
  try {
    const result = await get('/api/inventory/detectors/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    detectors.value = result.data;
  } catch (error) {
    console.error('Error fetching detectors:', error);
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

// Fetch cylinder statuses from the API
const fetchCylinderStatuses = async () => {
  try {
    const result = await get('/api/inventory/cylinder-statuses/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    cylinderStatusChoices.value = result.data;
  } catch (error) {
    console.error('Error fetching cylinder statuses:', error);
  }
};

// Fetch cylinders from the API
const fetchCylinders = async () => {
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

    // Add detector filter
    if (filterDetector.value) {
      params.append('detector', filterDetector.value);
    }

    // Add cylinder type filter
    if (filterCylinderType.value) {
      params.append('cylinder_type', filterCylinderType.value);
    }

    // Add expires before filter to the API call
    if (filterExpiresBefore.value) {
      params.append('expiry_date_lte', filterExpiresBefore.value);
    }

    // Add exclude decommissioned/empty filter (default behavior when checkbox is not selected)
    if (!showEmptyCylinders.value) {
      params.append('exclude_status', 'MT');
    }

    // Build the URL with parameters
    let url = '/api/inventory/cylinders/';
    if (params.toString()) {
      url += '?' + params.toString();
    }

    // Fetch cylinders from the Django REST API
    const result = await get(url);

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    cylinders.value = result.data;

    // Apply sorting and pagination after fetching
    performSortingAndPagination();
  } catch (error) {
    console.error('Error fetching cylinders:', error);
    // In case of error, we could show a user-friendly message
  } finally {
    loading.value = false;
  }
};

// Get status label from choices
const getStatusDisplay = (statusValue) => {
  if (!statusValue) return 'N/A';
  const choice = cylinderStatusChoices.value.find(c => c.value === statusValue);
  return choice ? choice.label : statusValue;
};

// Helper functions to get related object labels using local state
const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
}

const getDetectorLabel = (detectorId) => {
  if (!detectorId) return 'N/A';
  const detector = detectors.value.find(d => d.id === detectorId);
  return detector ? detector.label : 'Unknown Detector';
};

const getCylinderTypeLabel = (cylinderTypeId) => {
  if (!cylinderTypeId) return 'N/A';
  const cylinderType = cylinderTypes.value.find(ct => ct.id === cylinderTypeId);
  if (!cylinderType) return 'Unknown Cylinder Type';

  return cylinderType.part_number;
};

// Helper function to get supplier from cylinder type
const getCylinderTypeSupplier = (cylinderTypeId) => {
  if (!cylinderTypeId) return 'N/A';
  const cylinderType = cylinderTypes.value.find(ct => ct.id === cylinderTypeId);
  if (!cylinderType) return 'Unknown Cylinder Type';

  // Map supplier codes to their display names
  const supplierMap = {
    'AM': 'AirMet',
    'AE': 'AES',
    'MS': 'MSA',
    'DR': 'Draeger'
  };

  return supplierMap[cylinderType.supplier] || cylinderType.supplier;
};

// Function to perform sorting and pagination
const performSortingAndPagination = () => {
  let result = [...cylinders.value];

  // Apply sorting
  if (sortKey.value) {
    result.sort((a, b) => {
      let valA = a[sortKey.value];
      let valB = b[sortKey.value];

      // Handle nested properties
      if (sortKey.value === 'location') {
        valA = getLocationLabel(a.location) || '';
        valB = getLocationLabel(b.location) || '';
      } else if (sortKey.value === 'cylinder_type') {
        valA = getCylinderTypeLabel(a.cylinder_type) || '';
        valB = getCylinderTypeLabel(b.cylinder_type) || '';
      } else if (sortKey.value === 'supplier') {
        valA = getCylinderTypeSupplier(a.cylinder_type) || '';
        valB = getCylinderTypeSupplier(b.cylinder_type) || '';
      } else if (sortKey.value === 'receive_date' || sortKey.value === 'expiry_date' || sortKey.value === 'order_date') {
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
  totalFilteredCylindersResult.value = result.length;

  // Calculate total pages
  totalPagesResult.value = Math.ceil(result.length / cylindersPerPage.value);

  // Apply pagination
  const startIndex = (currentPage.value - 1) * cylindersPerPage.value;
  const endIndex = startIndex + cylindersPerPage.value;
  filteredCylindersResult.value = result.slice(startIndex, endIndex);
};

// Watch for changes to filter parameters and re-fetch from API
watch(
  [searchTerm, filterStatus, filterLocation, filterDetector, filterCylinderType, filterExpiresBefore, showEmptyCylinders],
  () => {
    // Reset to first page when filters change
    currentPage.value = 1;
    fetchCylinders();
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

// Computed property to get filtered and sorted cylinders
const filteredCylinders = computed(() => {
  return filteredCylindersResult.value;
});

// Computed property to get total number of pages
const totalPages = computed(() => {
  return totalPagesResult.value;
});

// Computed property to get the total number of filtered cylinders (before pagination)
const totalFilteredCylinders = computed(() => {
  return totalFilteredCylindersResult.value;
});

// Computed property to check if any filters are active
const hasActiveFilters = computed(() => {
  return searchTerm.value !== '' ||
    filterStatus.value !== '' ||
    filterLocation.value !== '' ||
    filterDetector.value !== '' ||
    filterCylinderType.value !== '' ||
    filterExpiresBefore.value !== '' ||
    showEmptyCylinders.value === true;
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

// Function to filter cylinders (called on input)
const filterCylinders = () => {
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
  filterDetector.value = '';
  filterCylinderType.value = '';
  filterExpiresBefore.value = '';
  showEmptyCylinders.value = false;
  sortKey.value = 'label';
  sortDirection.value = 'asc';
  currentPage.value = 1; // Reset to first page when filters are reset

  // Clear the saved state in localStorage
  localStorage.removeItem('cylindersFilterState');

  // Filtering will be handled by the watcher
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
  if (filterCylinderType.value) {
    params.append('cylinder_type', filterCylinderType.value);
  }
  if (filterLocation.value) {
    params.append('location', filterLocation.value);
  }
  if (filterExpiresBefore.value) {
    params.append('expiry_date_lte', filterExpiresBefore.value);
  }
  if (showEmptyCylinders.value) {
    params.append('show_empty', 'true');
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
  const url = `/api/inventory/pdf/cylinders/${queryString ? `?${queryString}` : ''}`;

  // Open in new tab or download directly
  window.open(url, '_blank');
};
</script>

<style scoped>
.cylinders-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.filters-section {
  margin-bottom: 0.5rem;
  position: relative;
  display: inline-block;
}

.filter-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  margin-bottom: 1rem;
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
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.reset-btn-wrapper {
  align-self: flex-start;
}

.search-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.reset-btn {
  padding: 0.5rem 1rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.reset-btn:hover {
  background-color: #c82333;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  height: calc(100vh - 70px); /* Full height minus navbar */
  overflow: hidden; /* Prevent page scrolling */
  display: flex;
  flex-direction: column;
}

h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  flex-shrink: 0; /* Don't shrink header */
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-shrink: 0; /* Don't shrink actions */
}

.action-buttons {
  display: flex;
  gap: 1rem;
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

.table-container {
  display: flex;
  flex-direction: column;
  flex: 1; /* Fill remaining space */
  overflow: hidden; /* Prevent overflow */
  min-height: 0; /* Allow flex item to shrink below content size */
}

.cylinders-table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;
  table-layout: fixed;
  margin-bottom: 0; /* Remove bottom margin since pagination is below */
}

.cylinders-table thead th {
  position: sticky; /* Make headers stick to the top */
  top: 0;
  background-color: #f8f9fa;
  font-weight: 600;
  word-wrap: break-word;
  z-index: 10; /* Ensure headers stay above scrolled content */
  border-bottom: 1px solid #ddd;
}

.cylinders-table tbody {
  display: block;
  max-height: calc(100vh - 280px); /* Account for navbar, headers, actions, pagination */
  overflow-y: auto;
}

.cylinders-table thead,
.cylinders-table tbody tr {
  display: table;
  width: 100%;
  table-layout: fixed;
}

.cylinders-table th,
.cylinders-table td {
  padding: 0.5rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
  word-wrap: break-word;
}

.cylinders-table th:nth-child(1),
.cylinders-table td:nth-child(1) {
  width: 4%; /* Checkbox */
}

.cylinders-table th:nth-child(2),
.cylinders-table td:nth-child(2) {
  width: 9%; /* Label */
}

.cylinders-table th:nth-child(3),
.cylinders-table td:nth-child(3) {
  width: 9%; /* Serial */
}

.cylinders-table th:nth-child(4),
.cylinders-table td:nth-child(4) {
  width: 11%; /* Cylinder Type */
}

.cylinders-table th:nth-child(5),
.cylinders-table td:nth-child(5) {
  width: 9%; /* Supplier */
}

.cylinders-table th:nth-child(6),
.cylinders-table td:nth-child(6) {
  width: 9%; /* Detector */
}

.cylinders-table th:nth-child(7),
.cylinders-table td:nth-child(7) {
  width: 9%; /* Location */
}

.cylinders-table th:nth-child(8),
.cylinders-table td:nth-child(8) {
  width: 7%; /* Status */
}

.cylinders-table th:nth-child(9),
.cylinders-table td:nth-child(9) {
  width: 9%; /* Order Date */
}

.cylinders-table th:nth-child(10),
.cylinders-table td:nth-child(10) {
  width: 9%; /* Receive Date */
}

.cylinders-table th:nth-child(11),
.cylinders-table td:nth-child(11) {
  width: 9%; /* Expiry Date */
}

.cylinders-table th {
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

.cylinders-table tbody tr:hover {
  background-color: #f8f9fa;
}

.cylinder-link {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

.cylinder-link:hover {
  text-decoration: underline;
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
  margin-top: 0.5rem;
  padding: 0.5rem 0;
}

.pagination-info {
  color: #666;
  font-size: 0.9rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-controls .page-info {
  color: #666;
  font-size: 0.9rem;
  min-width: 120px;
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

.date-filter-container {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.date-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #495057;
}

.date-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.875rem;
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