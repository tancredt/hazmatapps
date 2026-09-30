<template>
  <div class="report-cylinder-empty-screen">
    <HomeHeader />
    <h2>Report Cylinder Empty</h2>
    <h3>{{ location_label }} ({{ district }})</h3>

    <div v-if="isLoading" class="loading">Loading cylinders...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="!isLoading && !error" class="sections-container">
      <!-- Fallback if no slots or cylinders exist -->
      <div v-if="displaySlots.length === 0 && overflowCylinders.length === 0" class="empty-state">
        No cylinder slots or cylinders found for this location.
      </div>

      <!-- Cylinder Slots Grid -->
      <div v-if="displaySlots.length > 0" class="location-section">
        <h3>Cylinder Slots</h3>
        <p class="section-subtitle">Click an operational cylinder to report it as empty</p>
        <div class="slots-grid">
          <div
            v-for="item in displaySlots"
            :key="item.slotId"
            class="slot-rectangle"
            :class="{ empty: !item.cylinder, clickable: item.cylinder }"
            :role="item.cylinder ? 'button' : undefined"
            :tabindex="item.cylinder ? 0 : -1"
            @click="item.cylinder && openConfirmDialog(item.cylinder)"
            @keydown.enter="item.cylinder && openConfirmDialog(item.cylinder)"
          >
            <template v-if="item.cylinder">
              <span class="cylinder-label">{{ item.cylinder.label }}</span>
              <span class="cylinder-details">{{ getCylinderTypeLabel(item.cylinderType) }}</span>
              <span class="cylinder-expiry" :class="{ expired: isExpired(item.cylinder.expiry_date) }">
                Exp: {{ item.cylinder.expiry_date ? new Date(item.cylinder.expiry_date).toLocaleDateString('en-AU') : 'N/A' }}
              </span>
            </template>
            <template v-else>
              <span class="empty-slot-text">Empty Slot</span>
              <span class="empty-slot-type">{{ getCylinderTypeLabel(item.cylinderType) }}</span>
            </template>
          </div>
        </div>
      </div>

      <!-- Overflow Cylinders -->
      <div v-if="overflowCylinders.length > 0" class="location-section overflow-section">
        <h4 class="overflow-title">
          Overflow Cylinders ({{ overflowCylinders.length }})
        </h4>
        <div class="overflow-list">
          <div
            v-for="cyl in overflowCylinders"
            :key="cyl.id"
            class="overflow-item"
            role="button"
            tabindex="0"
            @click="openConfirmDialog(cyl)"
            @keydown.enter="openConfirmDialog(cyl)"
          >
            {{ cyl.label }}
            <span v-if="isExpired(cyl.expiry_date)" class="expired-badge">Expired</span>
          </div>
        </div>
      </div>

      <!-- Recent Faults Table -->
      <div v-if="recentFaults.length > 0" class="location-section">
        <h3>Recent Cylinder Faults (Last 7 Days)</h3>
        <div class="table-container">
          <table class="faults-table">
            <thead>
              <tr>
                <th>Cylinder</th>
                <th>Fault Type</th>
                <th>Reported</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="fault in recentFaults" :key="fault.id">
                <td class="cylinder-cell">{{ getCylinderLabel(fault.cylinder) }}</td>
                <td>{{ fault.fault_type === 'MT' ? 'Empty' : fault.fault_type }}</td>
                <td>{{ formatDate(fault.report_dt) }}</td>
                <td>
                  <span class="status-pill" :class="fault.status === 'OP' ? 'status-open' : 'status-closed'">
                    {{ getStatusLabel(fault.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <div v-if="showConfirmDialog" class="modal-overlay" @click.self="closeConfirmDialog">
      <div class="modal-content">
        <h3>Report Cylinder Empty</h3>
        <p class="modal-subtitle">
          Reporting for: <strong>{{ selectedCylinder?.label }}</strong><br>
          Type: <strong>{{ getCylinderTypeLabel(getCylinderDetails(selectedCylinder).typeLabel) }}</strong>
        </p>
        <p>Are you sure you want to report this cylinder as empty?</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeConfirmDialog" :disabled="isProcessing">Cancel</button>
          <button class="btn-confirm" @click="submitFault" :disabled="isProcessing">
            {{ isProcessing ? 'Reporting...' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="modal-overlay">
      <div class="modal-content">
        <h3>Success</h3>
        <p>Cylinder <strong>{{ selectedCylinder?.label }}</strong> has been reported as empty.</p>
        <div class="modal-actions">
          <button class="btn-confirm" @click="closeSuccessDialog">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/utils/api'
import HomeHeader from './HomeHeader.vue'

const props = defineProps({
  district: String,
  location_label: String
})

const isLoading = ref(false)
const error = ref('')
const isProcessing = ref(false)

const cylinderModels = ref([])
const cylinderTypes = ref([])

const displaySlots = ref([])
const overflowCylinders = ref([])
const recentFaults = ref([])

const showConfirmDialog = ref(false)
const showSuccessDialog = ref(false)
const selectedCylinder = ref(null)

// --- Helper Functions ---
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

const getCylinderTypeLabel = (type) => {
  if (!type) return 'N/A'
  if (typeof type === 'string') return type // Already a label string
  const gasEntries = []
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

const getCylinderDetails = (cylinder) => {
  if (!cylinder) return { typeLabel: 'N/A', expiry: 'N/A' }
  const model = cylinderModels.value.find(m => m.id === cylinder.cylinder_model)
  const type = cylinderTypes.value.find(t => t.id === model?.cylinder_type)

  const typeLabel = type ? getCylinderTypeLabel(type) : (model?.part_number || 'Unknown Type')
  const expiry = cylinder.expiry_date ? new Date(cylinder.expiry_date).toLocaleDateString('en-AU') : 'No Expiry'

  return { typeLabel, expiry }
}

const isExpired = (expiryDate) => {
  if (!expiryDate) return false
  return new Date(expiryDate) < new Date()
}

const getCylinderLabel = (cylId) => {
  return `CYL${String(cylId).padStart(5, '0')}`
}

const getStatusLabel = (status) => {
  return status === 'OP' ? 'Open' : status === 'CL' ? 'Closed' : status
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-AU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// --- Data Fetching ---
const fetchData = async () => {
  if (!props.location_label) return

  isLoading.value = true
  error.value = ''
  try {
    const oneWeekAgo = new Date()
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
    const gteStr = oneWeekAgo.toISOString().split('T')[0]

    const [slotsRes, cylsRes, modelsRes, typesRes, faultsRes] = await Promise.all([
      apiFetch(`/locationcylinderslots/?location__label=${encodeURIComponent(props.location_label)}`),
      apiFetch(`/cylinders/?location__label=${encodeURIComponent(props.location_label)}&exclude_status=MT`),
      apiFetch('/cylindermodels/'),
      apiFetch('/cylindertypes/'),
      apiFetch(`/cylinderfaults/?report_location__label=${encodeURIComponent(props.location_label)}&report_dt_gte=${gteStr}`)
    ])

    cylinderModels.value = modelsRes || []
    cylinderTypes.value = typesRes || []

    // 1. Process Slots & Cylinders
    const assignedCylIds = new Set()
    const tempSlots = []

    for (const slot of (slotsRes || [])) {
      const typeId = slot.cylinder_type
      const type = cylinderTypes.value.find(t => t.id === Number(typeId))

      const availableCyls = (cylsRes || []).filter(c => {
        if (assignedCylIds.has(c.id)) return false
        if (c.status !== 'OP') return false
        const model = cylinderModels.value.find(m => m.id === c.cylinder_model)
        return model && model.cylinder_type === typeId
      })

      const cyl = availableCyls[0] || null
      if (cyl) assignedCylIds.add(cyl.id)

      tempSlots.push({
        slotId: slot.id,
        cylinderType: type,
        cylinder: cyl
      })
    }
    displaySlots.value = tempSlots

    const tempOverflow = (cylsRes || []).filter(cyl => !assignedCylIds.has(cyl.id))
    overflowCylinders.value = tempOverflow

    // 2. Process Recent Faults
    recentFaults.value = (faultsRes || [])
      .sort((a, b) => new Date(b.report_dt) - new Date(a.report_dt))
      .slice(0, 10)

  } catch (err) {
    console.error('Failed to fetch data:', err)
    error.value = 'Failed to load cylinder data. Please try again.'
  } finally {
    isLoading.value = false
  }
}

// --- Dialog & Action Handlers ---
const openConfirmDialog = (cylinder) => {
  selectedCylinder.value = cylinder
  showConfirmDialog.value = true
}

const closeConfirmDialog = () => {
  showConfirmDialog.value = false
  selectedCylinder.value = null
}

const closeSuccessDialog = () => {
  showSuccessDialog.value = false
  selectedCylinder.value = null
  fetchData()
}

const submitFault = async () => {
  if (!selectedCylinder.value) return

  isProcessing.value = true
  try {
    const locationRes = await apiFetch(`/locations/?label=${encodeURIComponent(props.location_label)}`)
    const locationData = Array.isArray(locationRes) ? locationRes : (locationRes.results || [])
    const location = locationData[0]

    if (!location) {
      throw new Error(`Could not find location "${props.location_label}"`)
    }

    const payload = {
      cylinder: selectedCylinder.value.id,
      report_dt: new Date().toISOString(),
      report_location: location.id,
      fault_type: 'MT',
      status: 'OP',
      reported_by: 'District Cache App'
    }

    await apiFetch('/cylinderfaults/', {
      method: 'POST',
      body: JSON.stringify(payload)
    })

    showConfirmDialog.value = false
    showSuccessDialog.value = true
  } catch (err) {
    console.error('Failed to report fault:', err)
    alert(`Failed to report cylinder as empty: ${err.message}`)
  } finally {
    isProcessing.value = false
  }
}

onMounted(async () => {
  await fetchData()
})
</script>

