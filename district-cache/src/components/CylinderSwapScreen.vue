<template>
  <div class="swap-screen">
    <HomeHeader />
    <h2>FRV - Cylinder Swap</h2>
    <h3>{{ displayLocationLabel }}</h3>
    
    <div class="type-selector">
      <label>Cylinder Type:</label>
      <select v-model="selectedTypeId" @change="fetchCylinders()">
        <option v-for="type in cylinderTypes" :key="type.id" :value="type.id">
          {{ getCylinderTypeLabel(type) }}
        </option>
      </select>
    </div>

    <div v-if="isLoading" class="loading">Loading cylinders...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div class="swap-container" v-if="!isLoading && !error">
      <!-- ================= STATION SECTION ================= -->
      <div class="location-section">
        <h3>Station: {{ displayLocationLabel }}</h3>
        <p class="section-subtitle">Select the cylinder to be removed</p>
        
        <div class="slots-grid">
          <div 
            v-for="i in stationSlotCount" 
            :key="'st-slot-' + i" 
            class="slot-rectangle"
            :class="{ 
              selected: selectedCylinderId === stationSlottedCylinders[i-1]?.id,
              empty: !stationSlottedCylinders[i-1]
            }"
            @click="stationSlottedCylinders[i-1] && selectStationCylinder(stationSlottedCylinders[i-1].id)"
          >
            <template v-if="stationSlottedCylinders[i-1]">
              {{ stationSlottedCylinders[i-1].label }}
            </template>
            <template v-else>Empty</template>
          </div>
        </div>

        <div v-if="stationOverflowCylinders.length > 0" class="overflow-area">
          <h4>Overflow Cylinders ({{ stationOverflowCylinders.length }})</h4>
          <div class="overflow-list">
            <div 
              v-for="cyl in stationOverflowCylinders" 
              :key="'st-ov-' + cyl.id" 
              class="overflow-item"
              :class="{ selected: selectedCylinderId === cyl.id }"
              @click="selectStationCylinder(cyl.id)"
            >
              {{ cyl.label }}
            </div>
          </div>
        </div>
      </div>

      <!-- ================= BURNLEY CACHE SECTION ================= -->
      <div class="location-section">
        <h3>Burnley Cache</h3>
        <p class="section-subtitle">Select replacement cylinder</p>
        
        <div v-if="burnleyCylinders.length > 0" class="overflow-list" style="margin-top: 15px;">
          <div 
            v-for="cyl in burnleyCylinders" 
            :key="'burnley-' + cyl.id" 
            class="overflow-item"
            :class="{ selected: replacementCylinderId === cyl.id }"
            @click="selectBurnleyCylinder(cyl.id)"
          >
            {{ cyl.label }}
            <span class="expiry-info" v-if="cyl.expiry_date">
              Exp: {{ formatDate(cyl.expiry_date) }}
            </span>
          </div>
        </div>
        <p v-else class="empty-text">No available cylinders at Burnley for this type.</p>
      </div>
    </div>

    <!-- ACTION BUTTON -->
    <div class="action-bar">
      <button
        class="btn-primary"
        @click="executeSwap"
        :disabled="isProcessing || isLoading || !!error || !selectedCylinderId || !replacementCylinderId"
      >
        {{ isProcessing ? 'Processing...' : 'Update' }}
      </button>
    </div>

    <!-- ================= SUCCESS DIALOG ================= -->
    <div v-if="showInfoDialog" class="modal-overlay">
      <div class="modal-content">
        <h3>Swap Successful</h3>
        <p>{{ infoMessage }}</p>
        <div class="modal-actions">
          <button class="btn-confirm" @click="closeInfoDialog">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { apiFetch } from '@/utils/api'
import HomeHeader from './HomeHeader.vue'

const props = defineProps({
  district: String,
  location_label: String
})

// --- Local State ---
const cylinderTypes = ref([])
const selectedTypeId = ref(null)
const stationLocation = ref(null)
const burnleyLocation = ref(null)
const stationCylinders = ref([])
const burnleyCylinders = ref([])
const stationSlotCount = ref(0)
const isLoading = ref(false)
const error = ref(null)

// --- Local UI State ---
const isProcessing = ref(false)
const selectedCylinderId = ref(null)
const replacementCylinderId = ref(null)

const showInfoDialog = ref(false)
const infoMessage = ref('')

// --- Computed Properties ---
const displayLocationLabel = computed(() => props.location_label || 'Unknown Location')

const stationSlottedCylinders = computed(() => stationCylinders.value.slice(0, stationSlotCount.value))
const stationOverflowCylinders = computed(() => stationCylinders.value.slice(stationSlotCount.value))

// --- Helper Functions ---
const getCylinderTypeLabel = (type) => {
  if (!type) return 'N/A'
  const gasEntries = []
  const getGasDisplay = (gasCode) => {
    if (!gasCode) return ''
    const gases = {
      'CO': 'CO', 'HS': 'H2S', 'CH': 'CH4', 'O2': 'O2',
      'IB': 'Iso', 'HC': 'HCN', 'N2': 'N2', 'CL': 'Cl2',
      'PH': 'PH3', 'SO': 'SO2', 'NO': 'NO2', 'C2': 'CO2',
      'NH': 'NH3', 'ET': 'ETO'
    }
    return gases[gasCode] || gasCode
  }
  const getUnitDisplay = (unitCode) => {
    if (!unitCode) return ''
    const units = { 'PM': 'ppm', 'PV': '%v/v', 'PL': '%LEL', 'ML': 'mg/L' }
    return units[unitCode] || unitCode
  }
  const buildEntry = (gas, conc, units) => {
    if (!gas) return null
    return `${getGasDisplay(gas)} ${conc ?? ''} ${getUnitDisplay(units)}`.trim()
  }
  const entry1 = buildEntry(type.cylinder_1_gas, type.cylinder_1_conc, type.cylinder_1_units)
  const entry2 = buildEntry(type.cylinder_2_gas, type.cylinder_2_conc, type.cylinder_2_units)
  const entry3 = buildEntry(type.cylinder_3_gas, type.cylinder_3_conc, type.cylinder_3_units)
  const entry4 = buildEntry(type.cylinder_4_gas, type.cylinder_4_conc, type.cylinder_4_units)
  if (entry1) gasEntries.push(entry1)
  if (entry2) gasEntries.push(entry2)
  if (entry3) gasEntries.push(entry3)
  if (entry4) gasEntries.push(entry4)
  return gasEntries.length > 0 ? gasEntries.join('; ') : `Balance: ${getGasDisplay(type.balance_gas)}`
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-AU')
}

// --- Methods ---
const selectStationCylinder = (id) => {
  selectedCylinderId.value = selectedCylinderId.value === id ? null : id
}

const selectBurnleyCylinder = (id) => {
  replacementCylinderId.value = replacementCylinderId.value === id ? null : id
}

const fetchCylinderTypes = async () => {
  try {
    const data = await apiFetch('/cylindertypes/')
    cylinderTypes.value = data
    if (data.length > 0 && !selectedTypeId.value) {
      selectedTypeId.value = data[0].id
    }
  } catch (err) { 
    console.error('Failed to fetch cylinder types:', err) 
  }
}

const resolveLocations = async (locationLabel) => {
  error.value = null
  try {
    const stationResults = await apiFetch(`/locations/?label=${encodeURIComponent(locationLabel)}`)
    stationLocation.value = stationResults[0] || null

    const burnleyResults = await apiFetch(`/locations/?label=${encodeURIComponent('Burnley')}`)
    burnleyLocation.value = burnleyResults[0] || null

    if (!stationLocation.value) error.value = `Station location "${locationLabel}" not found.`
    if (!burnleyLocation.value) error.value = `Burnley location not found.`
  } catch (err) {
    error.value = 'Failed to resolve locations.'
    console.error(err)
  }
}

const fetchSlotCount = async () => {
  if (!stationLocation.value || !selectedTypeId.value) return
  try {
    const slots = await apiFetch(`/locationcylinderslots/?location=${stationLocation.value.id}&cylinder_type=${selectedTypeId.value}`)
    stationSlotCount.value = slots.length
  } catch (err) {
    console.error('Failed to fetch slot count:', err)
    stationSlotCount.value = 0
  }
}

const fetchCylinders = async () => {
  if (!stationLocation.value || !burnleyLocation.value || !selectedTypeId.value) return
  isLoading.value = true
  error.value = null
  try {
    await fetchSlotCount()
    const [stationData, burnleyData] = await Promise.all([
      apiFetch(`/cylinders/?location=${stationLocation.value.id}&cylinder_model__cylinder_type=${selectedTypeId.value}&exclude_status=MT`),
      apiFetch(`/cylinders/?location=${burnleyLocation.value.id}&status=IS&cylinder_model__cylinder_type=${selectedTypeId.value}`)
    ])
    stationCylinders.value = stationData
    burnleyCylinders.value = burnleyData
  } catch (err) {
    error.value = 'Failed to fetch cylinders.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const executeSwap = async () => {
  if (!selectedCylinderId.value || !replacementCylinderId.value) return

  isProcessing.value = true
  try {
    const payload = {
      removed_cylinder_id: selectedCylinderId.value,
      removed_location_id: burnleyLocation.value.id,
      removed_status: 'MT',
      replacement_cylinder_id: replacementCylinderId.value,
      replacement_location_id: stationLocation.value.id,
      replacement_status: 'OP'
    }

    await apiFetch('/cylinders/perform-swap/', {
      method: 'POST',
      body: JSON.stringify(payload)
    })

    infoMessage.value = "Swap successful. The old cylinder has been marked as empty and returned to Burnley."
    showInfoDialog.value = true

    selectedCylinderId.value = null
    replacementCylinderId.value = null

  } catch (err) {
    console.error('Swap failed:', err)
    alert(err.message || 'Swap failed. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const closeInfoDialog = () => {
  showInfoDialog.value = false
  fetchCylinders()
}

// --- Lifecycle ---
onMounted(async () => {
  await fetchCylinderTypes()
  if (props.location_label) {
    await resolveLocations(props.location_label)
    await fetchCylinders()
  }
})

watch(() => selectedTypeId.value, () => {
  if (selectedTypeId.value) {
    fetchCylinders()
  }
})
</script>

