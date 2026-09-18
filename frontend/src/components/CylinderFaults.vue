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
     <select v-model="filterCylinder" @change="filterFaults" class="filter-select">
       <option value="">All Cylinders</option>
       <option v-for="cylinder in cylinders" :key="cylinder.id" :value="cylinder.id">
         {{ getCylinderLabel(cylinder.id) }}
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
     <h1>Cylinder Faults Management</h1>
   </div>
   <div class="table-container">
     <table class="faults-table">
       <thead>
         <tr>
           <th @click="sortBy('cylinder')" class="sortable">
             Cylinder <span v-if="sortKey === 'cylinder'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
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
             <router-link v-if="fault.cylinder" :to="`/cylinders/${fault.cylinder}`" class="cylinder-link">
               {{ getCylinderLabel(fault.cylinder) }}
             </router-link>
             <span v-else>N/A</span>
           </td>
           <td>
	     <router-link :to="`/cylinderfaultreports/${fault.cylinder}/${fault.id}?from=cylinderfaults`" class="fault-link">
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
const cylinders = ref([]);
const locations = ref([]);

// Hardcoded choices based on CylinderFaultType and CylinderFaultStatus models
const faultTypeChoices = ref([
  { value: 'MT', label: 'Empty' },
  { value: 'EX', label: 'Expired' }
]);
const faultStatusChoices = ref([
  { value: 'OP', label: 'Open' },
  { value: 'CL', label: 'Closed' }
]);

// State for sorting and filtering
const sortKey = ref('report_dt');
const sortDirection = ref('desc');
const filterStatus = ref('');
const filterFaultType = ref('');
const filterCylinder = ref('');
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
const savedState = localStorage.getItem('cylinderFaultsFilterState');
if (savedState) {
const state = JSON.parse(savedState);
sortKey.value = state.sortKey || 'report_dt';
sortDirection.value = state.sortDirection || 'desc';
filterStatus.value = state.filterStatus || '';
filterFaultType.value = state.filterFaultType || '';
filterCylinder.value = state.filterCylinder || '';
filterReportedBefore.value = state.filterReportedBefore || '';
showClosedFaults.value = state.showClosedFaults || false;
}

await Promise.all([
fetchCylinders(),
fetchLocations()
]);

await fetchFaults();
});

const saveStateToLocalStorage = () => {
const state = {
sortKey: sortKey.value,
sortDirection: sortDirection.value,
filterStatus: filterStatus.value,
filterFaultType: filterFaultType.value,
filterCylinder: filterCylinder.value,
filterReportedBefore: filterReportedBefore.value,
showClosedFaults: showClosedFaults.value
};
localStorage.setItem('cylinderFaultsFilterState', JSON.stringify(state));
};

watch([sortKey, sortDirection, filterStatus, filterFaultType, filterCylinder, filterReportedBefore, showClosedFaults], () => {
currentPage.value = 1;
saveStateToLocalStorage();
}, { deep: true });

const fetchCylinders = async () => {
try {
const result = await get('/api/inventory/cylinders/');
if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
cylinders.value = result.data;
} catch (error) {
console.error('Error fetching cylinders:', error);
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

const fetchFaults = async () => {
try {
loading.value = true;
const params = new URLSearchParams();

if (filterStatus.value) params.append('status', filterStatus.value);
if (filterFaultType.value) params.append('fault_type', filterFaultType.value);
if (filterCylinder.value) params.append('cylinder', filterCylinder.value);
if (filterReportedBefore.value) params.append('report_dt_lte', filterReportedBefore.value);
if (!showClosedFaults.value) params.append('exclude_status', 'CL');

let url = '/api/inventory/cylinderfaults/';
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

const getCylinderLabel = (cylinderId) => {
if (!cylinderId) return 'N/A';
const cylinder = cylinders.value.find(c => c.id === cylinderId);
return cylinder ? cylinder.label : 'Unknown Cylinder';
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

if (sortKey.value === 'cylinder') {
valA = getCylinderLabel(a.cylinder) || '';
valB = getCylinderLabel(b.cylinder) || '';
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

totalFilteredFaultsResult.value = result.length;
totalPagesResult.value = Math.ceil(result.length / faultsPerPage.value);

const startIndex = (currentPage.value - 1) * faultsPerPage.value;
const endIndex = startIndex + faultsPerPage.value;
filteredFaultsResult.value = result.slice(startIndex, endIndex);
};

watch(
[filterStatus, filterFaultType, filterCylinder, filterReportedBefore, showClosedFaults],
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
filterCylinder.value !== '' ||
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
filterCylinder.value = '';
filterReportedBefore.value = '';
showClosedFaults.value = false;
sortKey.value = 'report_dt';
sortDirection.value = 'desc';
currentPage.value = 1;
localStorage.removeItem('cylinderFaultsFilterState');
};

const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };
</script>

<style scoped>
/* Styles copied and adapted from Faults.vue */
.faults-page { min-height: 100vh; display: flex; flex-direction: column; }
.filters-section { margin-bottom: 0.5rem; position: relative; display: inline-block; }
.filter-toggle-btn { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background-color: #42b883; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-bottom: 1rem; transition: background-color 0.3s ease; }
.filter-toggle-btn:hover { background-color: #36966d; }
.filter-toggle-btn.has-active-filters { background-color: #e67e22; }
.filter-toggle-btn.has-active-filters:hover { background-color: #d35400; }
.toggle-icon { transition: transform 0.3s ease; }
.filter-toggle-btn[aria-expanded="true"] .toggle-icon { transform: rotate(180deg); }
.search-and-filters-popover { position: absolute; top: 100%; left: 0; width: 20%; min-width: 300px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 1rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); z-index: 1000; display: flex; flex-direction: column; gap: 1rem; }
.reset-btn-wrapper { align-self: flex-start; }
.filter-select { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; min-width: 150px; }
.reset-btn { padding: 0.5rem 1rem; background-color: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem; }
.reset-btn:hover { background-color: #c82333; }
.page-container { max-width: 1200px; margin: 0 auto; padding: 1rem 2rem; height: calc(100vh - 70px); overflow: hidden; display: flex; flex-direction: column; }
h1 { color: #2c3e50; margin-bottom: 0.5rem; flex-shrink: 0; }
.header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-shrink: 0; }
.table-container { display: flex; flex-direction: column; flex: 1; overflow: hidden; min-height: 0; }
.faults-table { width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; table-layout: fixed; margin-bottom: 0; }
.faults-table thead th { position: sticky; top: 0; background-color: #f8f9fa; font-weight: 600; word-wrap: break-word; z-index: 10; border-bottom: 1px solid #ddd; }
.faults-table tbody { display: block; max-height: calc(100vh - 280px); overflow-y: auto; }
.faults-table thead, .faults-table tbody tr { display: table; width: 100%; table-layout: fixed; }
.faults-table th, .faults-table td { padding: 0.5rem; text-align: left; border-bottom: 1px solid #ddd; word-wrap: break-word; }
.faults-table th:nth-child(1), .faults-table td:nth-child(1) { width: 16%; }
.faults-table th:nth-child(2), .faults-table td:nth-child(2) { width: 20%; }
.faults-table th:nth-child(3), .faults-table td:nth-child(3) { width: 13%; }
.faults-table th:nth-child(4), .faults-table td:nth-child(4) { width: 16%; }
.faults-table th:nth-child(5), .faults-table td:nth-child(5) { width: 18%; }
.faults-table th:nth-child(6), .faults-table td:nth-child(6) { width: 9%; }
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { background-color: #e9ecef; }
.faults-table tbody tr:hover { background-color: #f8f9fa; }
.cylinder-link { color: #42b883; text-decoration: none; font-weight: 500; }
.cylinder-link:hover { text-decoration: underline; }
.date-closed { color: blue; font-weight: bold; }
.date-recent { color: orange; font-weight: bold; }
.date-overdue { color: red; font-weight: bold; }
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
.checkbox-container { display: flex; align-items: center; gap: 0.5rem; }
.checkbox-label { display: flex; align-items: center; gap: 0.25rem; font-size: 0.875rem; color: #495057; }
.fault-link {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}
.fault-link:hover {
  text-decoration: underline;
}
</style>