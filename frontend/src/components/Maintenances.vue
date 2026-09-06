<template>
  <div class="maintenances-page">
    <div class="filters-section">
      <button @click="toggleFilters" :aria-expanded="showFilters" class="filter-toggle-btn" :class="{ 'has-active-filters': hasActiveFilters }">
        {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toggle-icon">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>

      <div v-show="showFilters" class="search-and-filters-popover">
        <select v-model="filterStatus" @change="filterMaintenances" class="filter-select">
          <option value="">All Statuses</option>
          <option v-for="choice in maintenanceStatusChoices" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </option>
        </select>
        <select v-model="filterMaintenanceType" @change="filterMaintenances" class="filter-select">
          <option value="">All Maintenance Types</option>
          <option v-for="choice in maintenanceTypeChoices" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </option>
        </select>
        <select v-model="filterDetectorModel" @change="filterMaintenances" class="filter-select">
          <option value="">All Detector Models</option>
          <option v-for="model in detectorModels" :key="model.id" :value="model.id">
            {{ getDetectorModelLabel(model.id) }}
          </option>
        </select>
        <div class="date-filter-container">
          <label for="dueBefore" class="date-label">Due Before:</label>
          <input
            id="dueBefore"
            type="date"
            v-model="filterDueBefore"
            @change="filterMaintenances"
            class="date-input"
          />
        </div>
        <div class="checkbox-container">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="showCompleteMaintenances"
              @change="filterMaintenances"
            />
            Show Closed Maintenance
          </label>
        </div>
        <div class="reset-btn-wrapper">
          <button @click="resetFilters" class="reset-btn">Reset Filters</button>
        </div>
      </div>
    </div>

    <div class="page-container">
      <div class="header-actions">
        <h1>Maintenance Management</h1>
        <div class="action-buttons">
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
        <table class="maintenances-table">
          <thead>
            <tr>
              <th @click="sortBy('maintenance_type')" class="sortable">
                Type <span v-if="sortKey === 'maintenance_type'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('status')" class="sortable">
                Status <span v-if="sortKey === 'status'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('detector_label')" class="sortable">
                Detector <span v-if="sortKey === 'detector_label'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('detector_model')" class="sortable">
                Detector Model <span v-if="sortKey === 'detector_model'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('date_due')" class="sortable">
                Due Date <span v-if="sortKey === 'date_due'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('date_performed')" class="sortable">
                Performed Date <span v-if="sortKey === 'date_performed'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="maintenance in filteredMaintenances" :key="maintenance.id">
              <td>
                <router-link :to="`/maintenances/${maintenance.detector}/${maintenance.id}?from=maintenances`" class="maintenance-link">
                  {{ getMaintenanceTypeDisplay(maintenance.maintenance_type) }}
                </router-link>
              </td>
              <td>{{ getMaintenanceStatusDisplay(maintenance.status) }}</td>
              <td>
                <router-link v-if="maintenance.detector" :to="`/detectors/${maintenance.detector}`" class="detector-link">
                  {{ maintenance.detector_label || getDetectorLabel(maintenance.detector) }}
                </router-link>
                <span v-else>N/A</span>
              </td>
              <td>{{ getDetectorModelLabel(maintenance.detector_model) }}</td>
              <td :class="getDateDueStatus(maintenance.date_due, maintenance.date_performed)">{{ maintenance.date_due || 'N/A' }}</td>
              <td>{{ maintenance.date_performed || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="loading" class="loading">Loading maintenances...</div>
        <div v-else-if="totalFilteredMaintenances === 0" class="no-data">No maintenances found</div>

        <!-- Pagination Controls -->
        <div v-if="!loading && totalFilteredMaintenances > 0" class="pagination-container">
          <div class="pagination-info">
            Showing {{ ((currentPage - 1) * maintenancesPerPage) + 1 }} to
            {{ Math.min(currentPage * maintenancesPerPage, totalFilteredMaintenances) }} of
            {{ totalFilteredMaintenances }} maintenances
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

// State for maintenances data
const maintenances = ref([]);
const loading = ref(true);

// State for related data
const detectorModels = ref([]);
const maintenanceTypeChoices = ref([]);
const maintenanceStatusChoices = ref([]);

// State for sorting and filtering
const sortKey = ref('date_due');
const sortDirection = ref('asc');
const searchTerm = ref('');
const filterStatus = ref('');
const filterMaintenanceType = ref('');
const filterDetectorModel = ref('');
const filterDueBefore = ref('');
const showCompleteMaintenances = ref(false);

// State for filter panel visibility
const showFilters = ref(false);

// State for pagination
const currentPage = ref(1);
const maintenancesPerPage = ref(50);

// State for filtered results and totals
const filteredMaintenancesResult = ref([]);
const totalFilteredMaintenancesResult = ref(0);
const totalPagesResult = ref(0);

// Initialize state from localStorage
onMounted(async () => {
  // Load saved state from localStorage
  const savedState = localStorage.getItem('maintenancesFilterState');
  if (savedState) {
    const state = JSON.parse(savedState);
    sortKey.value = state.sortKey || 'date_due';
    sortDirection.value = state.sortDirection || 'asc';
    searchTerm.value = state.searchTerm || '';
    filterStatus.value = state.filterStatus || '';
    filterMaintenanceType.value = state.filterMaintenanceType || '';
    filterDetectorModel.value = state.filterDetectorModel || '';
    filterDueBefore.value = state.filterDueBefore || '';
    showCompleteMaintenances.value = state.showCompleteMaintenances || false;
  }

  // Load detector models first
  await fetchDetectorModels();

  // Load maintenance types and statuses
  await Promise.all([
    fetchMaintenanceTypes(),
    fetchMaintenanceStatuses()
  ]);

  // Then load maintenances
  await fetchMaintenances();
});

// Function to save state to localStorage
const saveStateToLocalStorage = () => {
  const state = {
    sortKey: sortKey.value,
    sortDirection: sortDirection.value,
    searchTerm: searchTerm.value,
    filterStatus: filterStatus.value,
    filterMaintenanceType: filterMaintenanceType.value,
    filterDetectorModel: filterDetectorModel.value,
    filterDueBefore: filterDueBefore.value,
    showCompleteMaintenances: showCompleteMaintenances.value
  };
  localStorage.setItem('maintenancesFilterState', JSON.stringify(state));
};


// Watch for changes to filter/sort parameters and save to localStorage
watch([sortKey, sortDirection, searchTerm, filterStatus, filterMaintenanceType, filterDetectorModel, filterDueBefore, showCompleteMaintenances], () => {
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

// Fetch maintenance types from the API
const fetchMaintenanceTypes = async () => {
  try {
    const result = await get('/api/inventory/maintenance-types/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    maintenanceTypeChoices.value = result.data;
  } catch (error) {
    console.error('Error fetching maintenance types:', error);
  }
};

// Fetch maintenance statuses from the API
const fetchMaintenanceStatuses = async () => {
  try {
    const result = await get('/api/inventory/maintenance-statuses/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    maintenanceStatusChoices.value = result.data;
  } catch (error) {
    console.error('Error fetching maintenance statuses:', error);
  }
};

// Fetch maintenances from the API
const fetchMaintenances = async () => {
  try {
    loading.value = true;

    // Build query parameters based on filters
    const params = new URLSearchParams();

    // Add status filter
    if (filterStatus.value) {
      params.append('status', filterStatus.value);
    }

    // Add maintenance type filter
    if (filterMaintenanceType.value) {
      params.append('maintenance_type', filterMaintenanceType.value);
    }

    // Add detector model filter
    if (filterDetectorModel.value) {
      params.append('detector__detector_model', filterDetectorModel.value);
    }

    // Add due before filter to the API call
    if (filterDueBefore.value) {
      params.append('date_due_lte', filterDueBefore.value);
    }

    // Add exclude complete filter (default behavior when checkbox is not selected)
    if (!showCompleteMaintenances.value) {
      params.append('exclude_status', 'CL');
    }

    // Build the URL with parameters
    let url = '/api/inventory/maintenances/';
    if (params.toString()) {
      url += '?' + params.toString();
    }

    // Fetch maintenances from the Django REST API
    const result = await get(url);

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    maintenances.value = result.data;

    // Apply sorting and pagination after fetching
    performSortingAndPagination();
  } catch (error) {
    console.error('Error fetching maintenances:', error);
    // In case of error, we could show a user-friendly message
  } finally {
    loading.value = false;
  }
};

// Get maintenance type label from choices
const getMaintenanceTypeDisplay = (typeValue) => {
  if (!typeValue) return 'N/A';
  const choice = maintenanceTypeChoices.value.find(c => c.value === typeValue);
  return choice ? choice.label : typeValue;
};

// Get maintenance status label from choices
const getMaintenanceStatusDisplay = (statusValue) => {
  if (!statusValue) return 'N/A';
  const choice = maintenanceStatusChoices.value.find(c => c.value === statusValue);
  return choice ? choice.label : statusValue;
};

// Status display mapping (for the PDF function)
const getStatusDisplay = (statusValue) => {
  const statusMap = {
    'SC': 'Scheduled',
    'OP': 'Open',
    'CL': 'Closed'
  };
  return statusMap[statusValue] || statusValue;
};

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// Helper function to get detector labels using local state
const getDetectorLabel = (detectorId) => {
  if (!detectorId) return 'N/A';
  // We no longer fetch detectors list, so return fallback
  return 'Detector ' + detectorId;
};

// Helper function to get detector model labels using local state
const getDetectorModelLabel = (modelId) => {
  if (!modelId) return 'N/A';
  const model = detectorModels.value.find(m => m.id === modelId);
  return model ? model.label : 'Unknown Model';
};

// Function to perform sorting and pagination
const performSortingAndPagination = () => {
  let result = [...maintenances.value];

  // Apply sorting
  if (sortKey.value) {
    result.sort((a, b) => {
      let valA = a[sortKey.value];
      let valB = b[sortKey.value];

      // Handle nested properties
      if (sortKey.value === 'detector_label') {
        valA = a.detector_label || getDetectorLabel(a.detector) || '';
        valB = b.detector_label || getDetectorLabel(b.detector) || '';
      } else if (sortKey.value === 'detector_model') {
        valA = getDetectorModelLabel(a.detector_model) || '';
        valB = getDetectorModelLabel(b.detector_model) || '';
      } else if (sortKey.value === 'date_due' || sortKey.value === 'date_performed') {
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
  totalFilteredMaintenancesResult.value = result.length;

  // Calculate total pages
  totalPagesResult.value = Math.ceil(result.length / maintenancesPerPage.value);

  // Apply pagination
  const startIndex = (currentPage.value - 1) * maintenancesPerPage.value;
  const endIndex = startIndex + maintenancesPerPage.value;
  filteredMaintenancesResult.value = result.slice(startIndex, endIndex);
};

// Watch for changes to filter parameters and re-fetch from API
watch(
  [searchTerm, filterStatus, filterMaintenanceType, filterDetectorModel, filterDueBefore, showCompleteMaintenances],
  () => {
    // Reset to first page when filters change
    currentPage.value = 1;
    fetchMaintenances();
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

// Computed property to get filtered and sorted maintenances
const filteredMaintenances = computed(() => {
  return filteredMaintenancesResult.value;
});

// Computed property to get total number of pages
const totalPages = computed(() => {
  return totalPagesResult.value;
});

// Computed property to get the total number of filtered maintenances (before pagination)
const totalFilteredMaintenances = computed(() => {
  return totalFilteredMaintenancesResult.value;
});

// Computed property to check if any filters are active
const hasActiveFilters = computed(() => {
  return filterStatus.value !== '' ||
    filterMaintenanceType.value !== '' ||
    filterDetectorModel.value !== '' ||
    filterDueBefore.value !== '' ||
    showCompleteMaintenances.value === true;
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

// Function to filter maintenances (called on input)
const filterMaintenances = () => {
  // Reset to first page when filtering
  currentPage.value = 1;
  // Filtering will be handled by the watcher
};

// Function to toggle the filter panel
const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};

// Function to determine the date due status
const getDateDueStatus = (dateDue, datePerformed) => {
  if (!dateDue) return ''; // If no due date, return empty string

  // If date performed is not null/blank, return 'performed' status (blue)
  if (datePerformed) return 'date-performed';

  // Compare due date with today
  const dueDate = new Date(dateDue);
  const today = new Date();

  // Set time to 00:00:00 to compare only dates
  dueDate.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);

  // If date performed is null/blank and due date is today or in the past, return 'overdue' status (red)
  if (dueDate <= today) {
    return 'date-overdue';
  }

  // If date performed is null/blank and due date is in the future, return 'upcoming' status (orange)
  return 'date-upcoming';
};

// Function to reset all filters
const resetFilters = () => {
  searchTerm.value = '';
  filterStatus.value = '';
  filterMaintenanceType.value = '';
  filterDetectorModel.value = '';
  filterDueBefore.value = '';
  showCompleteMaintenances.value = false;
  sortKey.value = 'date_due';
  sortDirection.value = 'asc';
  currentPage.value = 1; // Reset to first page when filters are reset

  // Clear the saved state in localStorage
  localStorage.removeItem('maintenancesFilterState');

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

  if (filterStatus.value) {
    params.append('status', filterStatus.value);
  }
  if (filterMaintenanceType.value) {
    params.append('maintenance_type', filterMaintenanceType.value);
  }
  if (filterDetectorModel.value) {
    params.append('detector__detector_model', filterDetectorModel.value);
  }
  if (filterDueBefore.value) {
    params.append('date_due_lte', filterDueBefore.value);
  }
  if (showCompleteMaintenances.value) {
    params.append('show_complete', 'true');
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
  const url = `/api/inventory/pdf/maintenance/${queryString ? `?${queryString}` : ''}`;

  // Open in new tab or download directly
  window.open(url, '_blank');
};
</script>

<style scoped>
.maintenances-page {
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

.maintenances-table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;
  table-layout: fixed;
  margin-bottom: 0; /* Remove bottom margin since pagination is below */
}

.maintenances-table thead th {
  position: sticky; /* Make headers stick to the top */
  top: 0;
  background-color: #f8f9fa;
  font-weight: 600;
  word-wrap: break-word;
  z-index: 10; /* Ensure headers stay above scrolled content */
  border-bottom: 1px solid #ddd;
}

.maintenances-table tbody {
  display: block;
  max-height: calc(100vh - 280px); /* Account for navbar, headers, actions, pagination */
  overflow-y: auto;
}

.maintenances-table thead,
.maintenances-table tbody tr {
  display: table;
  width: 100%;
  table-layout: fixed;
}

.maintenances-table th,
.maintenances-table td {
  padding: 0.5rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
  word-wrap: break-word;
}

.maintenances-table th:nth-child(1),
.maintenances-table td:nth-child(1) {
  width: 20%; /* Type */
}

.maintenances-table th:nth-child(2),
.maintenances-table td:nth-child(2) {
  width: 16%; /* Status */
}

.maintenances-table th:nth-child(3),
.maintenances-table td:nth-child(3) {
  width: 16%; /* Detector */
}

.maintenances-table th:nth-child(4),
.maintenances-table td:nth-child(4) {
  width: 18%; /* Detector Model */
}

.maintenances-table th:nth-child(5),
.maintenances-table td:nth-child(5) {
  width: 18%; /* Due Date */
}

.maintenances-table th:nth-child(6),
.maintenances-table td:nth-child(6) {
  width: 24%; /* Performed Date */
}

.maintenances-table th {
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

.maintenances-table tbody tr:hover {
  background-color: #f8f9fa;
}

.maintenance-link {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

.maintenance-link:hover {
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

.date-overdue {
  color: red;
  font-weight: bold;
}

.date-performed {
  color: blue;
  font-weight: bold;
}

.date-upcoming {
  color: orange;
  font-weight: bold;
}

.loading, .no-data {
  text-align: center;
  padding: 2rem;
  font-style: italic;
  color: #666;
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

  .filter-select {
    width: 100%;
    margin-bottom: 0.5rem;
  }

  .page-container {
    padding: 0 1rem;
    margin-top: 1rem;
  }
}
</style>