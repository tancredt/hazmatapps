<template>
  <div class="faults-page">
    <div class="filters-section">
      <button @click="toggleFilters" :aria-expanded="showFilters" class="filter-toggle-btn" :class="{ 'has-active-filters': hasActiveFilters }">
        {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toggle-icon">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>

      <div v-show="showFilters" class="search-and-filters-popover">
        <select v-model="filterStatus" @change="filterFaults" class="filter-select">
          <option value="">All Statuses</option>
          <option v-for="choice in faultStatusChoices" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </option>
        </select>
        <select v-model="filterFaultType" @change="filterFaults" class="filter-select">
          <option value="">All Fault Types</option>
          <option v-for="choice in faultTypeChoices" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </option>
        </select>
        <select v-model="filterDetector" @change="filterFaults" class="filter-select">
          <option value="">All Detectors</option>
          <option v-for="detector in detectors" :key="detector.id" :value="detector.id">
            {{ getDetectorLabel(detector.id) }}
          </option>
        </select>
        <div class="date-filter-container">
          <label for="reportedBefore" class="date-label">Reported Before:</label>
          <input
            id="reportedBefore"
            type="date"
            v-model="filterReportedBefore"
            @change="filterFaults"
            class="date-input"
          />
        </div>
        <div class="checkbox-container">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="showClosedFaults"
              @change="filterFaults"
            />
            Show Closed Faults
          </label>
        </div>
        <div class="reset-btn-wrapper">
          <button @click="resetFilters" class="reset-btn">Reset Filters</button>
        </div>
      </div>
    </div>

    <div class="page-container">
      <div class="header-actions">
        <h1>Faults Management</h1>
        <div class="action-buttons">
          <router-link to="/faults/new" class="btn btn-primary">Add New Fault Report</router-link>
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
        <table class="faults-table">
          <thead>
            <tr>
              <th @click="sortBy('detector')" class="sortable">
                Detector <span v-if="sortKey === 'detector'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('fault_type')" class="sortable">
                Fault Type <span v-if="sortKey === 'fault_type'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('status')" class="sortable">
                Status <span v-if="sortKey === 'status'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('report_dt')" class="sortable">
                Report Date <span v-if="sortKey === 'report_dt'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('report_location')" class="sortable">
                Report Location <span v-if="sortKey === 'report_location'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th @click="sortBy('resolve_dt')" class="sortable">
                Resolve Date <span v-if="sortKey === 'resolve_dt'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="fault in filteredFaults" :key="fault.id">
              <td>
                <router-link v-if="fault.detector" :to="`/detectors/${fault.detector}`" class="detector-link">
                  {{ getDetectorLabel(fault.detector) }}
                </router-link>
                <span v-else>N/A</span>
              </td>
              <td>
                <router-link :to="`/faultreports/${fault.detector}/${fault.id}?from=faults`" class="fault-link">
                  {{ getFaultTypeDisplay(fault.fault_type) }}
                </router-link>
              </td>
              <td>{{ getStatusDisplay(fault.status) }}</td>
              <td :class="getDateStatus(fault.report_dt, fault.status)">{{ formatDate(fault.report_dt) }}</td>
              <td>{{ getLocationLabel(fault.report_location) }}</td>
              <td>{{ formatDate(fault.resolve_dt) }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="loading" class="loading">Loading faults...</div>
        <div v-else-if="totalFilteredFaults === 0" class="no-data">No faults found</div>

        <!-- Pagination Controls -->
        <div v-if="!loading && totalFilteredFaults > 0" class="pagination-container">
          <div class="pagination-info">
            Showing {{ ((currentPage - 1) * faultsPerPage) + 1 }} to
            {{ Math.min(currentPage * faultsPerPage, totalFilteredFaults) }} of
            {{ totalFilteredFaults }} faults
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
import { get } from '@/utils/api';

// State for faults data
const faults = ref([]);
const loading = ref(true);

// State for related data
const detectors = ref([]);
const locations = ref([]);
const faultTypeChoices = ref([]);
const faultStatusChoices = ref([]);

// State for sorting and filtering
const sortKey = ref('report_dt');
const sortDirection = ref('desc');
const filterStatus = ref('');
const filterFaultType = ref('');
const filterDetector = ref('');
const filterReportedBefore = ref('');
const showClosedFaults = ref(false);

// State for filter panel visibility
const showFilters = ref(false);

// State for pagination
const currentPage = ref(1);
const faultsPerPage = ref(50);

// State for filtered results and totals
const filteredFaultsResult = ref([]);
const totalFilteredFaultsResult = ref(0);
const totalPagesResult = ref(0);

// Initialize state from localStorage
onMounted(async () => {
  // Load saved state from localStorage
  const savedState = localStorage.getItem('faultsFilterState');
  if (savedState) {
    const state = JSON.parse(savedState);
    sortKey.value = state.sortKey || 'report_dt';
    sortDirection.value = state.sortDirection || 'desc';
    filterStatus.value = state.filterStatus || '';
    filterFaultType.value = state.filterFaultType || '';
    filterDetector.value = state.filterDetector || '';
    filterReportedBefore.value = state.filterReportedBefore || '';
    showClosedFaults.value = state.showClosedFaults || false;
  }

  // Load detectors, locations, fault types, and statuses first
  await Promise.all([
    fetchDetectors(),
    fetchLocations(),
    fetchFaultTypes(),
    fetchFaultStatuses()
  ]);

  // Then load faults
  await fetchFaults();
});

// Function to save state to localStorage
const saveStateToLocalStorage = () => {
  const state = {
    sortKey: sortKey.value,
    sortDirection: sortDirection.value,
    filterStatus: filterStatus.value,
    filterFaultType: filterFaultType.value,
    filterDetector: filterDetector.value,
    filterReportedBefore: filterReportedBefore.value,
    showClosedFaults: showClosedFaults.value
  };
  localStorage.setItem('faultsFilterState', JSON.stringify(state));
};

// Watch for changes to filter/sort parameters and save to localStorage
watch([sortKey, sortDirection, filterStatus, filterFaultType, filterDetector, filterReportedBefore, showClosedFaults], () => {
  // Reset to first page when filters/sorting changes
  currentPage.value = 1;
  saveStateToLocalStorage();
}, { deep: true });

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

// Fetch fault types from the API
const fetchFaultTypes = async () => {
  try {
    const result = await get('/api/inventory/detector-fault-types/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    faultTypeChoices.value = result.data;
  } catch (error) {
    console.error('Error fetching fault types:', error);
  }
};

// Fetch fault statuses from the API
const fetchFaultStatuses = async () => {
  try {
    const result = await get('/api/inventory/detector-statuses/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    faultStatusChoices.value = result.data;
  } catch (error) {
    console.error('Error fetching fault statuses:', error);
  }
};

// Fetch faults from the API
const fetchFaults = async () => {
  try {
    loading.value = true;

    // Build query parameters based on filters
    const params = new URLSearchParams();

    // Add status filter
    if (filterStatus.value) {
      params.append('status', filterStatus.value);
    }

    // Add fault type filter
    if (filterFaultType.value) {
      params.append('fault_type', filterFaultType.value);
    }

    // Add detector filter
    if (filterDetector.value) {
      params.append('detector', filterDetector.value);
    }

    // Add reported before filter to the API call
    if (filterReportedBefore.value) {
      params.append('report_dt_lte', filterReportedBefore.value);
    }

    // Add exclude closed filter (default behavior when checkbox is not selected)
    if (!showClosedFaults.value) {
      params.append('exclude_status', 'CL');
    }

    // Build the URL with parameters
    let url = '/api/inventory/detectorfaults/';
    if (params.toString()) {
      url += '?' + params.toString();
    }

    // Fetch faults from the Django REST API
    const result = await get(url);

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    faults.value = result.data;

    // Apply sorting and pagination after fetching
    performSortingAndPagination();
  } catch (error) {
    console.error('Error fetching faults:', error);
    // In case of error, we could show a user-friendly message
  } finally {
    loading.value = false;
  }
};

// Get status label from choices
const getStatusDisplay = (statusValue) => {
  if (!statusValue) return 'N/A';
  const choice = faultStatusChoices.value.find(c => c.value === statusValue);
  return choice ? choice.label : statusValue;
};

// Get fault type label from choices
const getFaultTypeDisplay = (faultTypeValue) => {
  if (!faultTypeValue) return 'N/A';
  const choice = faultTypeChoices.value.find(c => c.value === faultTypeValue);
  return choice ? choice.label : faultTypeValue;
};

// Helper functions to get related object labels using local state
const getDetectorLabel = (detectorId) => {
  if (!detectorId) return 'N/A';
  const detector = detectors.value.find(d => d.id === detectorId);
  return detector ? detector.label : 'Unknown Detector';
};

const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
};

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// Function to determine the date status based on status and date
const getDateStatus = (reportDate, status) => {
  if (!reportDate) return ''; // If no report date, return empty string

  if (status === 'CL') {
    // If status is Closed, return 'closed' status (blue)
    return 'date-closed';
  }

  // If status is Open, check if report date was within the last 2 days
  const reportDt = new Date(reportDate);
  const today = new Date();
  const twoDaysAgo = new Date();
  twoDaysAgo.setDate(today.getDate() - 2);

  // Set time to 00:00:00 to compare only dates
  reportDt.setHours(0, 0, 0, 0);
  twoDaysAgo.setHours(0, 0, 0, 0);

  // If report date is within the last 2 days, return 'recent' status (orange)
  if (reportDt >= twoDaysAgo) {
    return 'date-recent';
  }

  // Otherwise, return 'overdue' status (red)
  return 'date-overdue';
};

// Function to perform sorting and pagination
const performSortingAndPagination = () => {
  let result = [...faults.value];

  // Apply sorting
  if (sortKey.value) {
    result.sort((a, b) => {
      let valA = a[sortKey.value];
      let valB = b[sortKey.value];

      // Handle nested properties
      if (sortKey.value === 'detector') {
        valA = getDetectorLabel(a.detector) || '';
        valB = getDetectorLabel(b.detector) || '';
      } else if (sortKey.value === 'report_location') {
        valA = getLocationLabel(a.report_location) || '';
        valB = getLocationLabel(b.report_location) || '';
      } else if (sortKey.value === 'report_dt' || sortKey.value === 'resolve_dt') {
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
  totalFilteredFaultsResult.value = result.length;

  // Calculate total pages
  totalPagesResult.value = Math.ceil(result.length / faultsPerPage.value);

  // Apply pagination
  const startIndex = (currentPage.value - 1) * faultsPerPage.value;
  const endIndex = startIndex + faultsPerPage.value;
  filteredFaultsResult.value = result.slice(startIndex, endIndex);
};

// Watch for changes to filter parameters and re-fetch from API
watch(
  [filterStatus, filterFaultType, filterDetector, filterReportedBefore, showClosedFaults],
  () => {
    // Reset to first page when filters change
    currentPage.value = 1;
    fetchFaults();
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

// Computed property to get filtered and sorted faults
const filteredFaults = computed(() => {
  return filteredFaultsResult.value;
});

// Computed property to get total number of pages
const totalPages = computed(() => {
  return totalPagesResult.value;
});

// Computed property to get the total number of filtered faults (before pagination)
const totalFilteredFaults = computed(() => {
  return totalFilteredFaultsResult.value;
});

// Computed property to check if any filters are active
const hasActiveFilters = computed(() => {
  return filterStatus.value !== '' ||
    filterFaultType.value !== '' ||
    filterDetector.value !== '' ||
    filterReportedBefore.value !== '' ||
    showClosedFaults.value === true;
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

// Function to filter faults (called on input)
const filterFaults = () => {
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
  filterStatus.value = '';
  filterFaultType.value = '';
  filterDetector.value = '';
  filterReportedBefore.value = '';
  showClosedFaults.value = false;
  sortKey.value = 'report_dt';
  sortDirection.value = 'desc';
  currentPage.value = 1; // Reset to first page when filters are reset

  // Clear the saved state in localStorage
  localStorage.removeItem('faultsFilterState');

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
  if (filterFaultType.value) {
    params.append('fault_type', filterFaultType.value);
  }
  if (filterDetector.value) {
    params.append('detector', filterDetector.value);
  }
  if (filterReportedBefore.value) {
    params.append('report_dt_lte', filterReportedBefore.value);
  }
  if (showClosedFaults.value) {
    params.append('show_closed', 'true');
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
  const url = `/api/inventory/pdf/faults/${queryString ? `?${queryString}` : ''}`;

  // Open in new tab or download directly
  window.open(url, '_blank');
};
</script>

<style scoped>
.faults-page {
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

.faults-table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;
  table-layout: fixed;
  margin-bottom: 0; /* Remove bottom margin since pagination is below */
}

.faults-table thead th {
  position: sticky; /* Make headers stick to the top */
  top: 0;
  background-color: #f8f9fa;
  font-weight: 600;
  word-wrap: break-word;
  z-index: 10; /* Ensure headers stay above scrolled content */
  border-bottom: 1px solid #ddd;
}

.faults-table tbody {
  display: block;
  max-height: calc(100vh - 280px); /* Account for navbar, headers, actions, pagination */
  overflow-y: auto;
}

.faults-table thead,
.faults-table tbody tr {
  display: table;
  width: 100%;
  table-layout: fixed;
}

.faults-table th,
.faults-table td {
  padding: 0.5rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
  word-wrap: break-word;
}

.faults-table th:nth-child(1),
.faults-table td:nth-child(1) {
  width: 16%; /* Detector */
}

.faults-table th:nth-child(2),
.faults-table td:nth-child(2) {
  width: 20%; /* Fault Type */
}

.faults-table th:nth-child(3),
.faults-table td:nth-child(3) {
  width: 13%; /* Status */
}

.faults-table th:nth-child(4),
.faults-table td:nth-child(4) {
  width: 16%; /* Report Date */
}

.faults-table th:nth-child(5),
.faults-table td:nth-child(5) {
  width: 18%; /* Report Location */
}

.faults-table th:nth-child(6),
.faults-table td:nth-child(6) {
  width: 9%; /* Resolve Date */
}

.faults-table th {
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

.faults-table tbody tr:hover {
  background-color: #f8f9fa;
}

.fault-link {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

.fault-link:hover {
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

.date-closed {
  color: blue;
  font-weight: bold;
}

.date-recent {
  color: orange;
  font-weight: bold;
}

.date-overdue {
  color: red;
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
