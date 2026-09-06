<template>
  <div class="location-slots-page">
    <!-- Filters -->
    <div class="filters-section">
      <button
        @click="toggleFilters"
        :aria-expanded="showFilters"
        class="filter-toggle-btn"
        :class="{ 'has-active-filters': hasActiveFilters }"
      >
        {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="toggle-icon">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>
      <div v-show="showFilters" class="search-and-filters-popover">
        <select v-model="filterLocation" class="filter-select">
          <option value="">All Locations</option>
          <option v-for="loc in locations" :key="loc.id" :value="loc.id">
            {{ loc.label }}
          </option>
        </select>
        <select v-model="filterDistrict" class="filter-select">
          <option value="">All Districts</option>
          <option v-for="d in districts" :key="d.id" :value="d.id">
            {{ d.label }}
          </option>
        </select>        
        
        <!-- UPDATED: Location Type Filter using string representations -->
        <select v-model="filterLocationType" class="filter-select">
          <option value="">All Location Types</option>
          <option v-for="type in locationTypeChoices" :key="type.value" :value="type.value">
            {{ type.label }}
          </option>
        </select>

        <select v-model="filterModel" class="filter-select">
          <option value="">All Models</option>
          <option v-for="model in detectorModels" :key="model.id" :value="model.id">
            {{ model.label }}
          </option>
        </select>
        <div class="reset-btn-wrapper">
          <button @click="resetFilters" class="reset-btn">Reset Filters</button>
        </div>
      </div>
    </div>

    <div class="page-container">
      <div class="header-actions">
        <h1>Location Slots</h1>
      </div>

      <!-- Equipment display -->
      <div class="equipment-display">
        <div v-if="loading" class="loading">Loading equipment...</div>
        <div v-else-if="locationGroups.length === 0" class="no-data">
          {{ emptyMessage }}
        </div>
        <template v-else>
          <div
            v-for="locGroup in locationGroups"
            :key="locGroup.location.id"
            class="location-block"
          >
            <div class="location-header">
              {{ locGroup.location.label }}
              <span v-if="locGroup.location.district_label" class="district-tag">
                {{ locGroup.location.district_label }}
              </span>
            </div>

            <!-- Location with no slots/equipment -->
            <div v-if="locGroup.groups.length === 0" class="location-empty">
              No detector slots or equipment at this location.
            </div>

            <div v-else class="model-rows">
              <div
                v-for="group in locGroup.groups"
                :key="group.modelId"
                class="model-row"
              >
                <!-- Left: model label only -->
                <div class="row-labels">
                  <span class="model-label">{{ getModelName(group.modelId) }}</span>
                </div>

                <!-- Right: slots, overflow, and unslotted -->
                <div class="slots-and-extras">
                  <!-- Slot boxes (only if slots are configured) -->
                  <div class="slot-boxes" v-if="group.slotCount > 0">
                    <div
                      v-for="(det, i) in group.filledBoxes"
                      :key="'filled-' + i"
                      class="slot-box filled"
                    >
                      <router-link :to="`/detectors/${det.id}`" class="detector-link">
                        {{ det.label }}
                      </router-link>
                      <span class="updated-date">{{ formatDate(det.location_updated) }}</span>
                    </div>
                    <div
                      v-for="n in group.emptyCount"
                      :key="'empty-' + n"
                      class="slot-box empty"
                    >
                      Empty
                    </div>
                  </div>

                  <!-- Overflow detectors (only if slots exist but are exceeded) -->
                  <div v-if="group.overflow.length > 0" class="overflow-area">
                    <span class="overflow-title">Overflow:</span>
                    <div v-for="det in group.overflow" :key="det.id" class="detector-item-container">
                      <router-link :to="`/detectors/${det.id}`" class="overflow-item">
                        {{ det.label }}
                      </router-link>
                      <span class="item-date">{{ formatDate(det.location_updated) }}</span>
                    </div>
                  </div>

                  <!-- Unslotted detectors (only if NO slots are configured for this model) -->
                  <div v-if="group.unslotted.length > 0" class="unslotted-area">
                    <span class="unslotted-title">No Slots Configured (Unslotted):</span>
                    <div v-for="det in group.unslotted" :key="det.id" class="detector-item-container">
                      <router-link :to="`/detectors/${det.id}`" class="unslotted-item">
                        {{ det.label }}
                      </router-link>
                      <span class="item-date">{{ formatDate(det.location_updated) }}</span>
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

// ----- State -----
const loading = ref(false);

const locations = ref([]);
const districts = ref([]);
const detectorModels = ref([]);
const locationTypeChoices = ref([]); // Stores the {value, label} choices from the API
const allSlots = ref([]);
const allDetectors = ref([]);

// Filters (all client-side)
const showFilters = ref(false);
const filterLocation = ref('');
const filterDistrict = ref('');
const filterLocationType = ref('');
const filterModel = ref('');

// ----- Helpers -----
const getModelName = (modelId) => {
  if (!modelId) return 'N/A';
  const model = detectorModels.value.find(m => m.id === modelId);
  return model ? model.label : 'Unknown Model';
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  return dateStr.split('T')[0];
};

// Gets the raw location type code (e.g., 'ST', 'AP') from the location object
const getLocationType = (loc) => loc.location_type || '';

const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};

const resetFilters = () => {
  filterLocation.value = '';
  filterDistrict.value = '';
  filterLocationType.value = '';
  filterModel.value = '';
};

const hasActiveFilters = computed(() =>
  filterLocation.value !== '' ||
  filterDistrict.value !== '' ||
  filterLocationType.value !== '' ||
  filterModel.value !== ''
);

const emptyMessage = computed(() =>
  hasActiveFilters.value
    ? 'No locations match the selected filters.'
    : 'No locations found.'
);

// ----- LocalStorage Persistence -----
const saveStateToLocalStorage = () => {
  const state = {
    filterLocation: filterLocation.value,
    filterDistrict: filterDistrict.value,
    filterLocationType: filterLocationType.value,
    filterModel: filterModel.value
  };
  localStorage.setItem('locationSlotsFilterState', JSON.stringify(state));
};

// ----- Core computed: all locations grouped, with slots/detectors per model -----
const locationGroups = computed(() => {
  const result = [];

  // 1. Narrow down which locations to show based on location/district/type filters
  const matchingLocations = locations.value.filter(loc => {
    if (filterLocation.value !== '' && loc.id !== filterLocation.value) return false;
    if (filterDistrict.value !== '' && loc.district !== filterDistrict.value) return false;
    // Compare the raw location type code against the selected choice value
    if (filterLocationType.value !== '' && getLocationType(loc) !== filterLocationType.value) return false;
    return true;
  });

  // 2. Build slot/detector groups for each location
  for (const loc of matchingLocations) {
    const slotsByModel = {};
    for (const slot of allSlots.value) {
      if (slot.location !== loc.id) continue;
      if (filterModel.value !== '' && slot.detector_model !== filterModel.value) continue;
      if (!slotsByModel[slot.detector_model]) slotsByModel[slot.detector_model] = [];
      slotsByModel[slot.detector_model].push(slot);
    }

    const detsByModel = {};
    for (const det of allDetectors.value) {
      if (det.location !== loc.id) continue;
      if (filterModel.value !== '' && det.detector_model !== filterModel.value) continue;
      if (!detsByModel[det.detector_model]) detsByModel[det.detector_model] = [];
      detsByModel[det.detector_model].push(det);
    }

    const modelIds = new Set([
      ...Object.keys(slotsByModel).map(Number),
      ...Object.keys(detsByModel).map(Number)
    ]);

    const groups = [];
    for (const modelId of modelIds) {
      const slotCount = (slotsByModel[modelId] || []).length;
      const detectors = (detsByModel[modelId] || [])
        .slice()
        .sort((a, b) => (a.label || '').localeCompare(b.label || ''));

      let filledBoxes = [];
      let emptyCount = 0;
      let overflow = [];
      let unslotted = [];

      if (slotCount > 0) {
        // Slots exist: fill them, put the rest in overflow
        filledBoxes = detectors.slice(0, slotCount);
        overflow = detectors.slice(slotCount);
        emptyCount = Math.max(0, slotCount - filledBoxes.length);
      } else {
        // No slots exist: all detectors are unslotted
        unslotted = detectors;
      }

      groups.push({ modelId, slotCount, filledBoxes, emptyCount, overflow, unslotted });
    }

    // Models with configured slots appear first; unslotted models at the bottom
    groups.sort((a, b) => {
      const aHasSlots = a.slotCount > 0 ? 0 : 1;
      const bHasSlots = b.slotCount > 0 ? 0 : 1;
      if (aHasSlots !== bHasSlots) return aHasSlots - bHasSlots;
      return getModelName(a.modelId).localeCompare(getModelName(b.modelId));
    });

    // When a model filter is active, hide locations with nothing matching that model
    if (groups.length === 0 && filterModel.value !== '') continue;

    result.push({ location: loc, groups });
  }

  return result;
});

// ----- Data fetching (everything once; filtering is client-side) -----
const fetchAllData = async () => {
  loading.value = true;
  try {
    const [
      locationsResult,
      districtsResult,
      modelsResult,
      slotsResult,
      detectorsResult,
      locationTypesResult // Fetching the choice representations
    ] = await Promise.all([
      get('/api/inventory/locations/'),
      get('/api/inventory/districts/'),
      get('/api/inventory/detectormodels/'),
      get('/api/inventory/locationdetectorslots/'),
      get('/api/inventory/detectors/?exclude_status=DC'),
      get('/api/inventory/location-types/') // Endpoint returning {value, label}
    ]);

    if (!locationsResult.ok) throw new Error(`HTTP error! status: ${locationsResult.status}`);
    if (!districtsResult.ok) throw new Error(`HTTP error! status: ${districtsResult.status}`);
    if (!modelsResult.ok) throw new Error(`HTTP error! status: ${modelsResult.status}`);
    if (!slotsResult.ok) throw new Error(`HTTP error! status: ${slotsResult.status}`);
    if (!detectorsResult.ok) throw new Error(`HTTP error! status: ${detectorsResult.status}`);
    if (!locationTypesResult.ok) throw new Error(`HTTP error! status: ${locationTypesResult.status}`);

    locations.value = locationsResult.data;
    districts.value = districtsResult.data;
    detectorModels.value = modelsResult.data;
    allSlots.value = slotsResult.data;
    allDetectors.value = detectorsResult.data;
    locationTypeChoices.value = locationTypesResult.data;
  } catch (error) {
    console.error('Error loading data:', error);
  } finally {
    loading.value = false;
  }
};

// Save filter state whenever it changes
watch([filterLocation, filterDistrict, filterLocationType, filterModel], () => {
  saveStateToLocalStorage();
});

onMounted(async () => {
  // 1. Restore saved filter state
  const savedState = localStorage.getItem('locationSlotsFilterState');
  if (savedState) {
    try {
      const state = JSON.parse(savedState);
      filterLocation.value = state.filterLocation ?? '';
      filterDistrict.value = state.filterDistrict ?? '';
      filterLocationType.value = state.filterLocationType ?? '';
      filterModel.value = state.filterModel ?? '';
    } catch (e) {
      console.error('Error parsing locationSlotsFilterState', e);
    }
  }

  // 2. Fetch all data
  await fetchAllData();
});
</script>

<style scoped>
.location-slots-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.filters-section {
  margin-bottom: 0.25rem;
  position: relative;
  display: inline-block;
  padding: 0.5rem 1rem 0;
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
  left: 1rem;
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

.filter-select {
  padding: 0.4rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0.5rem 2rem 2rem;
  width: 100%;
  box-sizing: border-box;
}

h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.4rem;
}

.header-actions {
  margin-bottom: 0.75rem;
}

.equipment-display {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.loading,
.no-data {
  text-align: center;
  padding: 2rem;
  font-style: italic;
  color: #666;
}

.location-block {
  background: white;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.location-header {
  font-size: 1.1rem;
  font-weight: 700;
  color: #007bff;
  border-bottom: 2px solid #007bff;
  padding-bottom: 0.5rem;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.district-tag {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6c757d;
  background-color: #f1f3f5;
  border-radius: 12px;
  padding: 0.15rem 0.6rem;
}

.location-empty {
  font-style: italic;
  color: #999;
  padding: 0.5rem 0;
  font-size: 0.9rem;
}

.model-rows {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.model-row {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
  border-top: 1px solid #f1f1f1;
  padding-top: 0.75rem;
}

.model-row:first-child {
  border-top: none;
  padding-top: 0;
}

.row-labels {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 180px;
  max-width: 200px;
}

.model-label {
  color: #495057;
  font-size: 0.9rem;
  font-weight: 600;
}

/* Wrapper for the right side content */
.slots-and-extras {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
}

.slot-boxes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.slot-box {
  flex: 0 1 calc((100% - 2.5rem) / 6);
  min-width: 110px;
  min-height: 64px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 600;
  box-sizing: border-box;
  padding: 0.5rem;
  text-align: center;
}

.slot-box.filled {
  background-color: #eafaf2;
  border: 2px solid #42b883;
  color: #2c3e50;
}

.slot-box.empty {
  background-color: #fdecea;
  border: 2px solid #dc3545;
  color: #dc3545;
}

.updated-date {
  font-size: 0.7rem;
  font-weight: 400;
  color: #6c757d;
  margin-top: 0.25rem;
  display: block;
  line-height: 1;
}

.detector-link {
  color: #2c3e50;
  text-decoration: none;
}

.detector-link:hover {
  text-decoration: underline;
  color: #42b883;
}

/* Overflow & Unslotted Areas */
.unslotted-area,
.overflow-area {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  width: 100%;
  padding-top: 0.75rem;
  border-top: 1px dashed #e9ecef;
  align-items: flex-start;
}

.unslotted-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #6c757d;
  text-transform: uppercase;
  width: 100%;
  margin-bottom: -0.25rem;
}

.overflow-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #dc3545;
  text-transform: uppercase;
  width: 100%;
  margin-bottom: -0.25rem;
}

.detector-item-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
}

.item-date {
  font-size: 0.7rem;
  font-weight: 400;
  color: #6c757d;
}

.unslotted-item {
  background-color: #f8f9fa;
  border: 2px solid #6c757d;
  color: #495057;
  border-radius: 6px;
  padding: 0.35rem 0.6rem;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
}

.unslotted-item:hover {
  background-color: #e9ecef;
  color: #007bff;
}

.overflow-item {
  background-color: #fdecea;
  border: 2px solid #dc3545;
  color: #dc3545;
  border-radius: 6px;
  padding: 0.35rem 0.6rem;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
}

.overflow-item:hover {
  background-color: #f8d7da;
}

@media (max-width: 768px) {
  .page-container {
    padding: 0.5rem 1rem 2rem;
  }

  .model-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .row-labels {
    max-width: 100%;
  }
}
</style>