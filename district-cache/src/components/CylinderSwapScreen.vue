<template>
  <div class="swap-screen">
    <HomeHeader />
    <h2>FRV - Cylinder Swap</h2>
    <h3>{{ displayLocationLabel }}</h3>

    <div v-if="isLoading" class="loading">Loading cylinders...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div class="swap-container" v-if="!isLoading && !error">
      <!-- ================= STATION SECTION ================= -->
      <div class="location-section">
        <h3>Station: {{ displayLocationLabel }}</h3>
        <p class="section-subtitle">Select the cylinder to be removed</p>
        
        <!-- Fallback if no slots or cylinders exist -->
        <div v-if="displaySlots.length === 0 && overflowCylinders.length === 0" class="empty-state">
          No cylinder slots or cylinders found for this location.
        </div>

        <!-- Cylinder Slots Grid -->
        <div v-if="displaySlots.length > 0" class="slots-grid">
          <div 
            v-for="item in displaySlots" 
            :key="item.slotId"
            class="slot-rectangle"
            :class="{ 
              empty: !item.cylinder, 
              clickable: item.cylinder,
              selected: selectedCylinderId === item.cylinder?.id 
            }"
            :role="item.cylinder ? 'button' : undefined"
            :tabindex="item.cylinder ? 0 : -1"
            @click="item.cylinder && selectStationCylinder(item.cylinder.id)"
            @keydown.enter="item.cylinder && selectStationCylinder(item.cylinder.id)"
          >
            <template v-if="item.cylinder">
              <!-- NEW: Added Cylinder Type Label -->
              <span class="cylinder-type-label">{{ getCylinderTypeLabel(item.cylinderType) }}</span>
              <span class="cylinder-label">{{ item.cylinder.label }}</span>
              <span class="cylinder-expiry" :class="{ expired: isExpired(item.cylinder.expiry_date) }">
                Exp: {{ item.cylinder.expiry_date ? formatDate(item.cylinder.expiry_date) : 'N/A' }}
              </span>
            </template>
            <template v-else>
              <span class="empty-slot-text">Empty Slot</span>
              <span class="empty-slot-type">{{ getCylinderTypeLabel(item.cylinderType) }}</span>
            </template>
          </div>
        </div>

        <!-- Overflow Cylinders (Cylinders at station that don't fit in defined slots) -->
        <div v-if="overflowCylinders.length > 0" class="overflow-area">
          <h4>Overflow Cylinders ({{ overflowCylinders.length }})</h4>
          <div class="overflow-list">
            <div 
              v-for="cyl in overflowCylinders" 
              :key="'ov-' + cyl.id" 
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
        <p class="section-subtitle">
          <template v-if="selectedSlot">
            Select replacement cylinder for: <strong>{{ getCylinderTypeLabel(selectedSlot.cylinderType) }}</strong>
          </template>
          <template v-else>
            Select a cylinder from the station first
          </template>
        </p>
        
        <div v-if="selectedSlot && burnleyCylindersForType.length > 0" class="overflow-list" style="margin-top: 15px;">
          <div 
            v-for="cyl in burnleyCylindersForType" 
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
        <p v-else-if="selectedSlot" class="empty-text">No available cylinders at Burnley for this type.</p>
        <p v-else class="empty-text">Please select a cylinder from the station to see available replacements.</p>
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
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '@/utils/api'
import HomeHeader from './HomeHeader.vue'

const props = defineProps({
  district: String,
  location_label: String
})

// --- Local State ---
const cylinderTypes = ref([])
const cylinderModels = ref([])
const stationLocation = ref(null)
const burnleyLocation = ref(null)

const slots = ref([])
const stationCylinders = ref([])
const burnleyCylinders = ref([])

const isLoading = ref(false)
const error = ref(null)

// --- Local UI State ---
const isProcessing = ref(false)
const selectedCylinderId = ref(null)
const replacementCylinderId = ref(null)

const showInfoDialog = ref(false)
const infoMessage = ref('')

// --- Helper Functions ---
const getCylinderTypeId = (cylinder) => {
  const model = cylinderModels.value.find(m => m.id === cylinder.cylinder_model)
  return model ? model.cylinder_type : null
}

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

const isExpired = (expiryDate) => {
  if (!expiryDate) return false
  return new Date(expiryDate) < new Date()
}

// --- Computed Properties ---
const displayLocationLabel = computed(() => props.location_label || 'Unknown Location')

const displaySlots = computed(() => {
  const assignedCylIds = new Set()
  const tempSlots = []

  for (const slot of slots.value) {
    const typeId = slot.cylinder_type
    const type = cylinderTypes.value.find(t => t.id === Number(typeId))

    // Find an available cylinder at the station that matches this slot's type
    const availableCyls = stationCylinders.value.filter(c => {
      if (assignedCylIds.has(c.id)) return false
      if (c.status === 'MT') return false
      return getCylinderTypeId(c) === Number(typeId)
    })

    const cyl = availableCyls[0] || null
    if (cyl) assignedCylIds.add(cyl.id)

    tempSlots.push({
      slotId: slot.id,
      cylinderTypeId: typeId,
      cylinderType: type,
      cylinder: cyl
    })
  }
  return tempSlots
})

const overflowCylinders = computed(() => {
  const assignedCylIds = new Set(displaySlots.value.filter(s => s.cylinder).map(s => s.cylinder.id))
  return stationCylinders.value.filter(c => !assignedCylIds.has(c.id))
})

const selectedSlot = computed(() => {
  if (!selectedCylinderId.value) return null
  return displaySlots.value.find(s => s.cylinder?.id === selectedCylinderId.value)
})

const burnleyCylindersForType = computed(() => {
  if (!selectedSlot.value) return []
  const typeId = selectedSlot.value.cylinderTypeId
  return burnleyCylinders.value.filter(c => getCylinderTypeId(c) === Number(typeId))
})

// --- Methods ---
const selectStationCylinder = (id) => {
  selectedCylinderId.value = selectedCylinderId.value === id ? null : id
  replacementCylinderId.value = null // Reset replacement when station selection changes
}

const selectBurnleyCylinder = (id) => {
  replacementCylinderId.value = replacementCylinderId.value === id ? null : id
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

const fetchData = async () => {
  if (!stationLocation.value || !burnleyLocation.value) return
  isLoading.value = true
  error.value = null
  try {
    const [slotsRes, stationCylsRes, burnleyCylsRes, modelsRes, typesRes] = await Promise.all([
      apiFetch(`/locationcylinderslots/?location=${stationLocation.value.id}`),
      apiFetch(`/cylinders/?location=${stationLocation.value.id}&exclude_status=MT`),
      apiFetch(`/cylinders/?location=${burnleyLocation.value.id}&exclude_status=MT`),
      apiFetch('/cylindermodels/'),
      apiFetch('/cylindertypes/')
    ])
    
    slots.value = slotsRes || []
    stationCylinders.value = stationCylsRes || []
    burnleyCylinders.value = burnleyCylsRes || []
    cylinderModels.value = modelsRes || []
    cylinderTypes.value = typesRes || []
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
  fetchData()
}

// --- Lifecycle ---
onMounted(async () => {
  if (props.location_label) {
    await resolveLocations(props.location_label)
    await fetchData()
  }
})
</script>

<style scoped>
/* Slot specific typography */
.cylinder-type-label {
  font-size: 0.65rem;
  font-weight: 500;
  color: #6c757d;
  margin-bottom: 2px;
  line-height: 1.1;
  word-break: break-word;
  text-align: center;
  display: block;
  max-width: 100%;
}
.cylinder-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #2c3e50;
  display: block;
}
.cylinder-expiry {
  font-size: 0.7rem;
  color: #666;
  margin-top: 2px;
  display: block;
}
.cylinder-expiry.expired {
  color: #e74c3c;
  font-weight: 600;
}
.empty-slot-text {
  font-style: italic;
  color: #adb5bd;
  font-size: 0.85rem;
  display: block;
}
.empty-slot-type {
  font-size: 0.65rem;
  color: #888;
  margin-top: 4px;
  display: block;
  text-align: center;
  word-break: break-word;
  line-height: 1.1;
  max-width: 100%;
}
.expiry-info {
  font-size: 0.75rem;
  color: #666;
  margin-left: 6px;
}
</style>