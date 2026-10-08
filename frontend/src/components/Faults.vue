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
        <h1>Detector Faults Management</h1>
        <div class="action-buttons">
          <button @click="downloadPDF" class="btn btn-primary" title="Download as PDF">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
              <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="table-container">
        <table class="inventory-table inventory-table--faults">
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
                <router-link v-if="fault.detector" :to="`/detectors/${fault.detector}`" class="record-link">
                  {{ getDetectorLabel(fault.detector) }}
                </router-link>
                <span v-else>N/A</span>
              </td>
              <td>
                <router-link :to="`/faultreports/${fault.detector}/${fault.id}?from=faults`" class="record-link">
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
const faultStatusChoices = ref([]); // Now fetched from API

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

  await Promise.all([
    fetchDetectors(),
    fetchLocations(),
    fetchFaultTypes(),
    fetchFaultStatuses() // Fetch statuses from API
  ]);

  await fetchFaults();
});

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

watch([sortKey, sortDirection, filterStatus, filterFaultType, filterDetector, filterReportedBefore, showClosedFaults], () => {
  currentPage.value = 1;
  saveStateToLocalStorage();
}, { deep: true });

const fetchDetectors = async () => {
  try {
    const result = await get('/api/inventory/detectors/');
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    detectors.value = result.data;
  } catch (error) {
    console.error('Error fetching detectors:', error);
  }
};

const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    locations.value = result.data;
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
};

const fetchFaultTypes = async () => {
  try {
    const result = await get('/api/inventory/detector-fault-types/');
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    faultTypeChoices.value = result.data;
  } catch (error) {
    console.error('Error fetching fault types:', error);
  }
};

const fetchFaultStatuses = async () => {
  try {
    const result = await get('/api/inventory/detector-fault-statuses/');
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    faultStatusChoices.value = result.data;
  } catch (error) {
    console.error('Error fetching fault statuses:', error);
  }
};

const fetchFaults = async () => {
  try {
    loading.value = true;
    const params = new URLSearchParams();

    if (filterStatus.value) params.append('status', filterStatus.value);
    if (filterFaultType.value) params.append('fault_type', filterFaultType.value);
    if (filterDetector.value) params.append('detector', filterDetector.value);
    if (filterReportedBefore.value) params.append('report_dt_lte', filterReportedBefore.value);
    if (!showClosedFaults.value) params.append('exclude_status', 'CL');

    let url = '/api/inventory/detectorfaults/';
    if (params.toString()) url += '?' + params.toString();

    const result = await get(url);
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);

    faults.value = result.data;
    performSortingAndPagination();
  } catch (error) {
    console.error('Error fetching faults:', error);
  } finally {
    loading.value = false;
  }
};

const getStatusDisplay = (statusValue) => {
  if (!statusValue) return 'N/A';
  const choice = faultStatusChoices.value.find(c => c.value === statusValue);
  return choice ? choice.label : statusValue;
};

const getFaultTypeDisplay = (faultTypeValue) => {
  if (!faultTypeValue) return 'N/A';
  const choice = faultTypeChoices.value.find(c => c.value === faultTypeValue);
  return choice ? choice.label : faultTypeValue;
};

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

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

const getDateStatus = (reportDate, status) => {
  if (!reportDate) return '';
  if (status === 'CL') return 'date-closed';

  const reportDt = new Date(reportDate);
  const today = new Date();
  const twoDaysAgo = new Date();
  twoDaysAgo.setDate(today.getDate() - 2);

  reportDt.setHours(0, 0, 0, 0);
  twoDaysAgo.setHours(0, 0, 0, 0);

  if (reportDt >= twoDaysAgo) return 'date-recent';
  return 'date-overdue';
};

const performSortingAndPagination = () => {
  let result = [...faults.value];

  if (sortKey.value) {
    result.sort((a, b) => {
      let valA = a[sortKey.value];
      let valB = b[sortKey.value];

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

      if (sortDirection.value === 'asc') return valA > valB ? 1 : -1;
      return valA < valB ? 1 : -1;
    });
  }

  totalFilteredFaultsResult.value = result.length;
  totalPagesResult.value = Math.ceil(result.length / faultsPerPage.value);

  const startIndex = (currentPage.value - 1) * faultsPerPage.value;
  const endIndex = startIndex + faultsPerPage.value;
  filteredFaultsResult.value = result.slice(startIndex, endIndex);
};

watch(
  [filterStatus, filterFaultType, filterDetector, filterReportedBefore, showClosedFaults],
  () => {
    currentPage.value = 1;
    fetchFaults();
  },
  { deep: true }
);

watch(
  [sortKey, sortDirection, currentPage],
  () => {
    performSortingAndPagination();
  },
  { deep: true }
);

const filteredFaults = computed(() => filteredFaultsResult.value);
const totalPages = computed(() => totalPagesResult.value);
const totalFilteredFaults = computed(() => totalFilteredFaultsResult.value);

const hasActiveFilters = computed(() => {
  return filterStatus.value !== '' ||
    filterFaultType.value !== '' ||
    filterDetector.value !== '' ||
    filterReportedBefore.value !== '' ||
    showClosedFaults.value === true;
});

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDirection.value = 'asc';
  }
};

const filterFaults = () => { currentPage.value = 1; };
const toggleFilters = () => { showFilters.value = !showFilters.value; };

const resetFilters = () => {
  filterStatus.value = '';
  filterFaultType.value = '';
  filterDetector.value = '';
  filterReportedBefore.value = '';
  showClosedFaults.value = false;
  sortKey.value = 'report_dt';
  sortDirection.value = 'desc';
  currentPage.value = 1;
  localStorage.removeItem('faultsFilterState');
};

const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };

const downloadPDF = () => {
  const params = new URLSearchParams();
  if (filterStatus.value) params.append('status', filterStatus.value);
  if (filterFaultType.value) params.append('fault_type', filterFaultType.value);
  if (filterDetector.value) params.append('detector', filterDetector.value);
  if (filterReportedBefore.value) params.append('report_dt_lte', filterReportedBefore.value);
  if (showClosedFaults.value) params.append('show_closed', 'true');
  if (sortKey.value) params.append('sort_key', sortKey.value);
  if (sortDirection.value) params.append('sort_direction', sortDirection.value);
  params.append('_t', Date.now().toString());

  const queryString = params.toString();
  const url = `/api/inventory/pdf/faults/${queryString ? `?${queryString}` : ''}`;
  window.open(url, '_blank');
};
</script>

