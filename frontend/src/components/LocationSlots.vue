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
      
      <!-- Equipment display (This is now the scrollable container) -->
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
                      <!-- Configuration Label -->
                      <span class="config-label" v-if="getConfigurationLabel(det.configuration)" :title="getConfigurationLabel(det.configuration)">
                        {{ getConfigurationLabel(det.configuration) }}
                      </span>
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
                      <!-- Configuration Label -->
                      <span class="item-config" v-if="getConfigurationLabel(det.configuration)" :title="getConfigurationLabel(det.configuration)">
                        {{ getConfigurationLabel(det.configuration) }}
                      </span>
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
                      <!-- Configuration Label -->
                      <span class="item-config" v-if="getConfigurationLabel(det.configuration)" :title="getConfigurationLabel(det.configuration)">
                        {{ getConfigurationLabel(det.configuration) }}
                      </span>
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
const locationTypeChoices = ref([]);
const allSlots = ref([]);
const allDetectors = ref([]);
const detectorModelConfigurations = ref([]); // State for configurations

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

// Helper to get configuration label
const getConfigurationLabel = (configId) => {
  if (!configId) return '';
  const config = detectorModelConfigurations.value.find(c => c.id === configId);
  return config ? config.label : '';
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  return dateStr.split('T')[0];
};

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

  const matchingLocations = locations.value.filter(loc => {
    if (filterLocation.value !== '' && loc.id !== filterLocation.value) return false;
    if (filterDistrict.value !== '' && loc.district !== filterDistrict.value) return false;
    if (filterLocationType.value !== '' && getLocationType(loc) !== filterLocationType.value) return false;
    return true;
  });

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
        filledBoxes = detectors.slice(0, slotCount);
        overflow = detectors.slice(slotCount);
        emptyCount = Math.max(0, slotCount - filledBoxes.length);
      } else {
        unslotted = detectors;
      }

      groups.push({ modelId, slotCount, filledBoxes, emptyCount, overflow, unslotted });
    }

    groups.sort((a, b) => {
      const aHasSlots = a.slotCount > 0 ? 0 : 1;
      const bHasSlots = b.slotCount > 0 ? 0 : 1;
      if (aHasSlots !== bHasSlots) return aHasSlots - bHasSlots;
      return getModelName(a.modelId).localeCompare(getModelName(b.modelId));
    });

    if (groups.length === 0 && filterModel.value !== '') continue;

    result.push({ location: loc, groups });
  }

  return result;
});

// ----- Data fetching -----
const fetchAllData = async () => {
  loading.value = true;
  try {
    const [
      locationsResult,
      districtsResult,
      modelsResult,
      slotsResult,
      detectorsResult,
      locationTypesResult,
      configsResult
    ] = await Promise.all([
      get('/api/inventory/locations/'),
      get('/api/inventory/districts/'),
      get('/api/inventory/detectormodels/'),
      get('/api/inventory/locationdetectorslots/'),
      get('/api/inventory/detectors/?exclude_status=DC'),
      get('/api/inventory/location-types/'),
      get('/api/inventory/detectormodelconfigurations/')
    ]);

    if (!locationsResult.ok) throw new Error(`HTTP error! status: ${locationsResult.status}`);
    if (!districtsResult.ok) throw new Error(`HTTP error! status: ${districtsResult.status}`);
    if (!modelsResult.ok) throw new Error(`HTTP error! status: ${modelsResult.status}`);
    if (!slotsResult.ok) throw new Error(`HTTP error! status: ${slotsResult.status}`);
    if (!detectorsResult.ok) throw new Error(`HTTP error! status: ${detectorsResult.status}`);
    if (!locationTypesResult.ok) throw new Error(`HTTP error! status: ${locationTypesResult.status}`);
    if (!configsResult.ok) throw new Error(`HTTP error! status: ${configsResult.status}`);

    locations.value = locationsResult.data;
    districts.value = districtsResult.data;
    detectorModels.value = modelsResult.data;
    allSlots.value = slotsResult.data;
    allDetectors.value = detectorsResult.data;
    locationTypeChoices.value = locationTypesResult.data;
    detectorModelConfigurations.value = configsResult.data;
  } catch (error) {
    console.error('Error loading data:', error);
  } finally {
    loading.value = false;
  }
};

watch([filterLocation, filterDistrict, filterLocationType, filterModel], () => {
  saveStateToLocalStorage();
});

onMounted(async () => {
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

  await fetchAllData();
});
</script>

