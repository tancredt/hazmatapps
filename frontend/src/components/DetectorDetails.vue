<template>
<div class="detector-details-page">
<div class="page-container">
<div class="layout-container">
  <!-- Detector Details Box (Left) -->
  <div class="fixed-box left">
    <h2>Detector Information</h2>
    <div class="form-container">
      <form @submit.prevent="saveDetector" class="detector-form">
        <div class="form-row">
          <div class="form-group">
            <label for="label">Label *</label>
            <input type="text" id="label" v-model="detector.label" required :disabled="!isNewDetector" class="form-control" />
          </div>
          <div class="form-group">
            <label for="serial">Serial *</label>
            <input type="text" id="serial" v-model="detector.serial" required class="form-control" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="detector_model">Model *</label>
            <select id="detector_model" v-model="detector.detector_model" required class="form-control">
              <option value="">Select Model</option>
              <option v-for="model in detectorModels" :key="model.id" :value="model.id">{{ getModelName(model.id) }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="status">Status *</label>
            <select id="status" v-model="detector.status" required class="form-control">
              <option value="">Select Status</option>
              <option value="OP">Operational</option>
              <option value="IS">In Stock</option>
              <option value="OO">On Order</option>
              <option value="OF">Offline Repair</option>
              <option value="DC">Decommissioned</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="configuration">Configuration</label>
            <select id="configuration" v-model="detector.configuration" class="form-control">
              <option value="">Select Configuration</option>
              <option v-for="config in detectorModelConfigurations" :key="config.id" :value="config.id">{{ getConfigurationLabel(config.id) }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="location">Location *</label>
            <select id="location" v-model="detector.location" required class="form-control">
              <option value="">Select Location</option>
              <option v-for="location in locations" :key="location.id" :value="location.id">{{ getLocationLabel(location.id) }}</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="purchase_date">Purchase Date</label>
            <input type="date" id="purchase_date" v-model="detector.purchase_date" class="form-control" />
          </div>
          <div class="form-group">
            <label for="purchase_cost">Purchase Cost ($)</label>
            <input type="number" id="purchase_cost" v-model.number="detector.purchase_cost" step="0.01" class="form-control" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="firmware">Firmware</label>
            <input type="text" id="firmware" v-model="detector.firmware" maxlength="8" class="form-control" />
          </div>
          <div class="form-group">
            <label for="location_updated">Location Last Updated</label>
            <input type="text" id="location_updated" :value="detector.location_updated ? formatDate(detector.location_updated) : 'Never'" readonly class="form-control" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group full-width">
            <label for="notes">Notes</label>
            <textarea id="notes" v-model="detector.notes" rows="4" class="form-control" placeholder="Additional notes about the detector..."></textarea>
          </div>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="!isDirty">Save Detector</button>
          <router-link to="/detectors" class="btn btn-secondary">Cancel</router-link>
        </div>
      </form>
    </div>
  </div>

  <!-- Tables Box (Right) -->
  <div class="fixed-box right">

    <!-- ==================== SENSORS ACCORDION ==================== -->
    <div class="accordion">
      <div class="accordion-header" @click="toggleAccordion('sensors')">
        <h3>Sensors Attached</h3>
        <span class="accordion-icon">{{ accordionStates.sensors ? '−' : '+' }}</span>
      </div>
      <div class="accordion-content" v-show="accordionStates.sensors">

        <!-- GREEN: Configured Slots with Operational Sensors -->
        <div class="sensor-section sensor-section-green">
          <h4 class="sensor-section-title">Configured Sensor Slots</h4>
          <div class="table-container">
            <table class="summary-table sensors-table">
              <thead>
                <tr>
                  <th>Slot Gas</th>
                  <th>Sensor Serial</th>
                  <th>Warranty</th>
                  <th>Expiry</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="slot in matchedSlots" :key="'slot-' + slot.id">
                  <td>
                    <!-- CLICKABLE GAS LINK -->
                    <a href="#" @click.prevent="openSensorSelectDialog(slot.sensorgas)" class="sensor-slot-link">
                      {{ getSensorGasDisplay(slot.sensorgas) }}
                    </a>
                  </td>
                  <td v-if="slot.matchedSensor">
                    <router-link :to="`/sensors/${slot.matchedSensor.id}`" class="sensor-slot-link">
                      {{ slot.matchedSensor.serial || 'N/A' }}
                    </router-link>
                  </td>
                  <td v-else class="no-sensor-cell">No sensor assigned</td>
                  <td :class="getDateStatus(slot.matchedSensor?.warranty_date)">
                    {{ slot.matchedSensor?.warranty_date || 'N/A' }}
                  </td>
                  <td :class="getDateStatus(slot.matchedSensor?.expiry_date)">
                    {{ slot.matchedSensor?.expiry_date || 'N/A' }}
                  </td>
                </tr>
                <tr v-if="matchedSlots.length === 0">
                  <td colspan="4">No sensor slots configured</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ORANGE: Leftover Operational Sensors (no matching slot) -->
        <div class="sensor-section sensor-section-orange" v-if="leftoverOperationalSensors.length > 0">
          <h4 class="sensor-section-title">Unassigned Operational Sensors</h4>
          <div class="table-container">
            <table class="summary-table sensors-table">
              <thead>
                <tr>
                  <th>Gas</th>
                  <th>Sensor Serial</th>
                  <th>Warranty</th>
                  <th>Expiry</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sensor in leftoverOperationalSensors" :key="'leftover-' + sensor.id">
                  <td>{{ getSensorGasDisplay(getSensorGas(sensor.sensor_type)) }}</td>
                  <td>
                    <router-link :to="`/sensors/${sensor.id}`" class="sensor-slot-link">
                      {{ sensor.serial || 'N/A' }}
                    </router-link>
                  </td>
                  <td :class="getDateStatus(sensor.warranty_date)">
                    {{ sensor.warranty_date || 'N/A' }}
                  </td>
                  <td :class="getDateStatus(sensor.expiry_date)">
                    {{ sensor.expiry_date || 'N/A' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- RED: Decommissioned Sensors -->
        <div class="sensor-section sensor-section-red" v-if="decommissionedSensors.length > 0">
          <h4 class="sensor-section-title">Decommissioned Sensors</h4>
          <div class="table-container">
            <table class="summary-table sensors-table">
              <thead>
                <tr>
                  <th>Gas</th>
                  <th>Sensor Serial</th>
                  <th>Warranty</th>
                  <th>Expiry</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sensor in decommissionedSensors" :key="'decom-' + sensor.id">
                  <td>{{ getSensorGasDisplay(getSensorGas(sensor.sensor_type)) }}</td>
                  <td>
                    <router-link :to="`/sensors/${sensor.id}`" class="sensor-slot-link">
                      {{ sensor.serial || 'N/A' }}
                    </router-link>
                  </td>
                  <td :class="getDateStatus(sensor.warranty_date)">
                    {{ sensor.warranty_date || 'N/A' }}
                  </td>
                  <td :class="getDateStatus(sensor.expiry_date)">
                    {{ sensor.expiry_date || 'N/A' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>

    <!-- Fault Reports Accordion -->
    <div class="accordion">
      <div class="accordion-header" @click="toggleAccordion('faults')">
        <h3>Fault Reports</h3>
        <span class="accordion-icon">{{ accordionStates.faults ? '−' : '+' }}</span>
      </div>
      <div class="accordion-content" v-show="accordionStates.faults">
        <div class="table-container">
          <table class="summary-table">
            <thead>
              <tr>
                <th>Date Reported</th>
                <th>Fault Type</th>
                <th>Report Location</th>
                <th>Resolve Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="fault in paginatedFaultReports" :key="fault.id">
                <td>
                  <router-link :to="{ name: 'FaultReportDetails', params: { detectorId: route.params.id, faultId: fault.id } }" class="fault-report-link">
                    {{ formatDateYYYYMMDD(fault.report_dt) }}
                  </router-link>
                </td>
                <td>{{ getFaultTypeDisplay(fault.fault_type) }}</td>
                <td>{{ getLocationLabel(fault.report_location) }}</td>
                <td>{{ fault.resolve_dt ? formatDateYYYYMMDD(fault.resolve_dt) : 'N/A' }}</td>
                <td :class="fault.resolve_dt ? 'status-resolved' : 'status-open'">
                  {{ fault.resolve_dt ? 'Resolved' : 'Open' }}
                </td>
              </tr>
              <tr v-if="detectorFaults.length === 0">
                <td colspan="5">No fault reports</td>
              </tr>
            </tbody>
          </table>
          <div v-if="detectorFaults.length > faultsPerPage" class="pagination-controls">
            <button @click="prevFaultPage" :disabled="faultReportsPage <= 1" class="btn btn-pagination">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
            </button>
            <span class="page-info">Page {{ faultReportsPage }} of {{ Math.ceil(detectorFaults.length / faultsPerPage) }}</span>
            <button @click="nextFaultPage" :disabled="faultReportsPage >= Math.ceil(detectorFaults.length / faultsPerPage)" class="btn btn-pagination">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </div>
          <div class="add-fault-button">
            <router-link :to="{ name: 'FaultReportDetails', params: { detectorId: route.params.id } }" class="btn btn-primary">Add New Fault Report</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Maintenance Accordion -->
    <div class="accordion">
      <div class="accordion-header" @click="toggleAccordion('maintenance')">
        <h3>Maintenance</h3>
        <span class="accordion-icon">{{ accordionStates.maintenance ? '−' : '+' }}</span>
      </div>
      <div class="accordion-content" v-show="accordionStates.maintenance">
        <div class="table-container">
          <table class="summary-table">
            <thead>
              <tr>
                <th>Maintenance Type</th>
                <th>Status</th>
                <th>Date Due</th>
                <th>Date Performed</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="maintenance in paginatedMaintenance" :key="maintenance.id">
                <td>
                  <router-link :to="{ name: 'MaintenanceDetails', params: { detectorId: route.params.id, maintenanceId: maintenance.id } }" class="maintenance-link">
                    {{ getMaintenanceTypeDisplay(maintenance.maintenance_type) }}
                  </router-link>
                </td>
                <td>{{ getMaintenanceStatusDisplay(maintenance.status) }}</td>
                <td :class="getDateDueStatus(maintenance.date_due, maintenance.date_performed)">
                  {{ formatDate(maintenance.date_due) }}
                </td>
                <td>{{ maintenance.date_performed || 'N/A' }}</td>
              </tr>
              <tr v-if="detectorMaintenance.length === 0">
                <td colspan="4">No maintenance records</td>
              </tr>
            </tbody>
          </table>
          <div v-if="detectorMaintenance.length > maintenancePerPage" class="pagination-controls">
            <button @click="prevMaintenancePage" :disabled="maintenancePage <= 1" class="btn btn-pagination">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
            </button>
            <span class="page-info">Page {{ maintenancePage }} of {{ Math.ceil(detectorMaintenance.length / maintenancePerPage) }}</span>
            <button @click="nextMaintenancePage" :disabled="maintenancePage >= Math.ceil(detectorMaintenance.length / maintenancePerPage)" class="btn btn-pagination">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </div>
          <div class="add-maintenance-button">
            <router-link :to="{ name: 'MaintenanceDetails', params: { detectorId: route.params.id } }" class="btn btn-primary">Add New Maintenance</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Location History Accordion -->
    <div class="accordion">
      <div class="accordion-header" @click="toggleAccordion('locationHistory')">
        <h3>Location History</h3>
        <span class="accordion-icon">{{ accordionStates.locationHistory ? '−' : '+' }}</span>
      </div>
      <div class="accordion-content" v-show="accordionStates.locationHistory">
        <div class="table-container">
          <table class="summary-table">
            <thead>
              <tr>
                <th>From</th>
                <th>To</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in paginatedLocationHistory" :key="log.id">
                <td>{{ log.old_location_label || 'N/A' }}</td>
                <td>{{ log.new_location_label }}</td>
                <td>{{ formatDate(log.updated) }}</td>
              </tr>
              <tr v-if="locationHistory.length === 0">
                <td colspan="3">No location history</td>
              </tr>
            </tbody>
          </table>
          <div v-if="locationHistory.length > locationHistoryPerPage" class="pagination-controls">
            <button @click="prevLocationHistoryPage" :disabled="locationHistoryPage <= 1" class="btn btn-pagination">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
            </button>
            <span class="page-info">Page {{ locationHistoryPage }} of {{ Math.ceil(locationHistory.length / locationHistoryPerPage) }}</span>
            <button @click="nextLocationHistoryPage" :disabled="locationHistoryPage >= Math.ceil(locationHistory.length / locationHistoryPerPage)" class="btn btn-pagination">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>
</div>

<!-- Success Dialog -->
<div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
  <div class="dialog-box" @click.stop>
    <h3>Success!</h3>
    <p>Detector details have been saved successfully.</p>
    <div class="dialog-actions">
      <button @click="closeDialog" class="btn btn-primary">OK</button>
    </div>
  </div>
</div>

<!-- Error Dialog -->
<div v-if="showErrorDialog" class="dialog-overlay" @click="closeErrorDialog">
  <div class="dialog-box" @click.stop>
    <h3>Validation Errors</h3>
    <div class="error-list">
      <p v-for="(error, index) in errorMessages" :key="index" class="error-item">{{ error }}</p>
    </div>
    <div class="dialog-actions">
      <button @click="closeErrorDialog" class="btn btn-primary">OK</button>
    </div>
  </div>
</div>

<!-- SENSOR SELECT DIALOG -->
<div v-if="showSensorSelectDialog" class="dialog-overlay" @click="showSensorSelectDialog = false">
  <div class="dialog-box sensor-select-dialog" @click.stop>
    <h3>Select Sensor for {{ getSensorGasDisplay(selectedSlotGas) }}</h3>
    <p class="dialog-subtitle">Choose an In-Stock sensor compatible with this detector.</p>
    <div class="sensor-list-container">
      <div v-if="availableSensorsForSlot.length === 0" class="no-sensors-msg">
        No compatible In-Stock sensors found for this gas.
      </div>
      <div
        v-for="sensor in availableSensorsForSlot"
        :key="sensor.id"
        @click="selectedSensorForSlot = sensor.id"
        class="sensor-option"
        :class="{ selected: selectedSensorForSlot === sensor.id }"
      >
        <div class="sensor-option-serial">{{ sensor.serial || 'No Serial' }}</div>
        <div class="sensor-option-type">{{ getSensorTypeLabelForDialog(sensor.sensor_type) }}</div>
        <div class="sensor-option-dates">
          <span>Exp: {{ sensor.expiry_date || 'N/A' }}</span>
        </div>
      </div>
    </div>
    <div class="dialog-actions">
      <button @click="showSensorSelectDialog = false" class="btn btn-secondary">Cancel</button>
      <button @click="confirmSensorSelection" :disabled="!selectedSensorForSlot" class="btn btn-primary">Select Sensor</button>
    </div>
  </div>
</div>

</div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { post, put, get } from '@/utils/api';

const router = useRouter();
const route = useRoute();

// State for lookup data
const detectorModels = ref([]);
const locations = ref([]);
const sensorTypes = ref([]);
const detectorModelConfigurations = ref([]);

// State for the detector
const detector = ref({
  label: '', serial: '', status: '', configuration: null, location: null,
  detector_model: null, firmware: null, notes: null, purchase_date: '',
  purchase_cost: null, location_updated: null
});

const isDirty = ref(false);
const originalDetector = ref({});
const showSuccessDialog = ref(false);
const showErrorDialog = ref(false);
const errorMessages = ref([]);

// State for related data
const detectorSensors = ref([]);
const detectorSensorSlots = ref([]);
const detectorFaults = ref([]);
const detectorMaintenance = ref([]);
const locationHistory = ref([]);

// Sensor Select Dialog State
const showSensorSelectDialog = ref(false);
const selectedSlotGas = ref('');
const availableSensorsForSlot = ref([]);
const selectedSensorForSlot = ref(null);

// Pagination state
const faultReportsPage = ref(1);
const faultsPerPage = 5;
const maintenancePage = ref(1);
const maintenancePerPage = 5;
const locationHistoryPage = ref(1);
const locationHistoryPerPage = 5;

const isNewDetector = computed(() => route.params.id === 'new');

const paginatedFaultReports = computed(() => {
  const start = (faultReportsPage.value - 1) * faultsPerPage;
  return detectorFaults.value.slice(start, start + faultsPerPage);
});
const paginatedMaintenance = computed(() => {
  const start = (maintenancePage.value - 1) * maintenancePerPage;
  return detectorMaintenance.value.slice(start, start + maintenancePerPage);
});
const paginatedLocationHistory = computed(() => {
  const start = (locationHistoryPage.value - 1) * locationHistoryPerPage;
  return locationHistory.value.slice(start, start + locationHistoryPerPage);
});

// ==================== SENSOR GROUPING LOGIC ====================
const getSensorGas = (sensorTypeId) => {
  if (!sensorTypeId) return '';
  const st = sensorTypes.value.find(s => s.id === sensorTypeId);
  return st ? st.sensorgas : '';
};

const matchedSlots = computed(() => {
  const operationalSensors = detectorSensors.value.filter(s => s.status === 'OP');
  const usedSensorIds = new Set();

  return detectorSensorSlots.value.map(slot => {
    const matchingSensor = operationalSensors.find(s => {
      if (usedSensorIds.has(s.id)) return false;
      return getSensorGas(s.sensor_type) === slot.sensorgas;
    });
    if (matchingSensor) usedSensorIds.add(matchingSensor.id);
    return { ...slot, matchedSensor: matchingSensor || null };
  });
});

const leftoverOperationalSensors = computed(() => {
  const operationalSensors = detectorSensors.value.filter(s => s.status === 'OP');
  const usedSensorIds = new Set();

  for (const slot of detectorSensorSlots.value) {
    const match = operationalSensors.find(s => {
      if (usedSensorIds.has(s.id)) return false;
      return getSensorGas(s.sensor_type) === slot.sensorgas;
    });
    if (match) usedSensorIds.add(match.id);
  }

  return operationalSensors.filter(s => !usedSensorIds.has(s.id));
});

const decommissionedSensors = computed(() => {
  return detectorSensors.value.filter(s => s.status === 'DC');
});
// ==================== END SENSOR GROUPING ====================

const extractList = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString();
};
const formatDateYYYYMMDD = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
};

const getDateDueStatus = (dateDue, datePerformed) => {
  if (!dateDue) return '';
  if (datePerformed) return 'date-performed';
  const dueDate = new Date(dateDue);
  const today = new Date();
  dueDate.setHours(0, 0, 0, 0); today.setHours(0, 0, 0, 0);
  return dueDate <= today ? 'date-overdue' : 'date-upcoming';
};

const getDateStatus = (dateStr) => {
  if (!dateStr || dateStr === 'N/A') return '';
  const date = new Date(dateStr);
  const today = new Date();
  const eightWeeksFromToday = new Date(today);
  eightWeeksFromToday.setDate(today.getDate() + 8 * 7);
  date.setHours(0, 0, 0, 0); today.setHours(0, 0, 0, 0); eightWeeksFromToday.setHours(0, 0, 0, 0);
  if (date <= today) return 'date-overdue';
  if (date <= eightWeeksFromToday) return 'date-warning';
  return 'date-future';
};

const prevFaultPage = () => { if (faultReportsPage.value > 1) faultReportsPage.value--; };
const nextFaultPage = () => { if (faultReportsPage.value < Math.ceil(detectorFaults.value.length / faultsPerPage)) faultReportsPage.value++; };
const prevMaintenancePage = () => { if (maintenancePage.value > 1) maintenancePage.value--; };
const nextMaintenancePage = () => { if (maintenancePage.value < Math.ceil(detectorMaintenance.value.length / maintenancePerPage)) maintenancePage.value++; };
const prevLocationHistoryPage = () => { if (locationHistoryPage.value > 1) locationHistoryPage.value--; };
const nextLocationHistoryPage = () => { if (locationHistoryPage.value < Math.ceil(locationHistory.value.length / locationHistoryPerPage)) locationHistoryPage.value++; };

const getFaultTypeDisplay = (val) => {
  const map = { BF: 'Failed Bump', SF: 'Sensor Fail', CE: 'Calibration Expired', DE: 'Displays Error', WS: 'Will not turn on', MD: 'Detector Missing', DD: 'Damaged Display', DC: 'Damaged Casing', MA: 'Missing Attachment' };
  return map[val] || val;
};
const getMaintenanceTypeDisplay = (val) => {
  const map = { SV: 'Scheduled Service', MS: 'Unscheduled Service', BT: 'Battery Replacement', FC: 'Filter Replacement', DR: 'Dessicant Replacement', CL: 'Clean' };
  return map[val] || val;
};
const getMaintenanceStatusDisplay = (val) => {
  const map = { SC: 'Scheduled', OP: 'Open', CL: 'Closed' };
  return map[val] || val;
};

const getLocationLabel = (id) => {
  if (!id) return 'N/A';
  const loc = locations.value.find(l => l.id === id);
  return loc ? loc.label : 'Unknown Location';
};
const getModelName = (id) => {
  if (!id) return 'N/A';
  const m = detectorModels.value.find(m => m.id === id);
  return m ? m.label : 'Unknown Model';
};
const getConfigurationLabel = (id) => {
  if (!id) return 'N/A';
  const c = detectorModelConfigurations.value.find(c => c.id === id);
  if (!c) return 'Unknown Configuration';
  return `${c.label} (${getModelName(c.detector_model)})`;
};

const getSensorGasDisplay = (sensorgas) => {
  if (!sensorgas) return 'N/A';
  const gasMap = { CO: 'CO', HS: 'H2S', LE: 'LEL', O2: 'O2', VO: 'VOC', HC: 'HCN', CL: 'Cl2', PH: 'PH3', SO: 'SO2', NO: 'NO2', C2: 'CO2', NH: 'NH3', ET: 'ETO', CS: 'CO/H2S' };
  return gasMap[sensorgas] || sensorgas;
};

const getSensorTypeLabelForDialog = (sensorTypeId) => {
  if (!sensorTypeId) return 'Unknown';
  const st = sensorTypes.value.find(s => s.id === sensorTypeId);
  return st ? `${st.part_number} (${getSensorGasDisplay(st.sensorgas)})` : 'Unknown';
};

const closeDialog = () => { showSuccessDialog.value = false; };
const closeErrorDialog = () => { showErrorDialog.value = false; errorMessages.value = []; };

// ==================== SENSOR SELECT DIALOG LOGIC ====================
const openSensorSelectDialog = async (gas) => {
  selectedSlotGas.value = gas;
  selectedSensorForSlot.value = null;
  showSensorSelectDialog.value = true;
  availableSensorsForSlot.value = [];

  try {
    const result = await get('/api/inventory/sensors/?status=IS');
    if (result.ok) {
      const allIS = extractList(result.data);
      const validTypeIds = sensorTypes.value
        .filter(st => st.sensorgas === gas)
        .map(st => st.id);

      const currentModelId = String(detector.value.detector_model);
      const currentModelLabel = getModelName(detector.value.detector_model);

      availableSensorsForSlot.value = allIS.filter(s => {
        if (!validTypeIds.includes(s.sensor_type)) return false;
        const sType = sensorTypes.value.find(st => st.id === s.sensor_type);
        if (!sType) return false;
        
        const compat = sType.compatible_detectormodels || '';
        if (compat === '' || compat.includes(currentModelId) || compat.includes(currentModelLabel)) {
          return true;
        }
        return false;
      });
    }
  } catch (e) {
    console.error('Error fetching sensors for slot:', e);
  }
};

const confirmSensorSelection = () => {
  if (selectedSensorForSlot.value) {
    router.push({
      path: `/sensors/${selectedSensorForSlot.value}`,
      query: { detectorId: route.params.id }
    });
    showSensorSelectDialog.value = false;
  }
};
// ==================== END DIALOG LOGIC ====================

const saveDetector = async () => {
  try {
    if (!detector.value.label.trim()) { alert('Label is required.'); return; }
    if (!detector.value.serial.trim()) { alert('Serial is required.'); return; }
    if (!detector.value.detector_model) { alert('Model is required.'); return; }
    if (!detector.value.status) { alert('Status is required.'); return; }
    if (!detector.value.location) { alert('Location is required.'); return; }

    const detectorData = {
      ...detector.value,
      detector_model: detector.value.detector_model ? parseInt(detector.value.detector_model) : null,
      location: detector.value.location ? parseInt(detector.value.location) : null,
      configuration: detector.value.configuration ? parseInt(detector.value.configuration) : null,
      firmware: detector.value.firmware || null,
      purchase_date: detector.value.purchase_date || null,
      purchase_cost: detector.value.purchase_cost ? parseFloat(detector.value.purchase_cost) : null
    };

    let result;
    if (isNewDetector.value) {
      result = await post('/api/inventory/detectors/', detectorData);
    } else {
      result = await put(`/api/inventory/detectors/${route.params.id}/`, detectorData);
    }

    if (!result.ok) {
      if (result.status === 400) {
        const errorData = result.data;
        errorMessages.value = [];
        for (const [field, errors] of Object.entries(errorData)) {
          errorMessages.value.push(`${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`);
        }
        showErrorDialog.value = true;
        return;
      } else {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
    }

    if (!isNewDetector.value) await fetchRelatedData();
    originalDetector.value = { ...detector.value };
    isDirty.value = false;
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving detector:', error);
    alert('Error saving detector: ' + error.message);
  }
};

const fetchDetector = async () => {
  try {
    const result = await get(`/api/inventory/detectors/${route.params.id}/`);
    if (!result.ok) throw new Error(`HTTP error! status: ${result.status}`);
    const data = result.data;
    detector.value = {
      ...data,
      detector_model: data.detector_model || null,
      location: data.location || null,
      configuration: data.configuration || null,
      firmware: data.firmware || null,
      notes: data.notes || null,
      location_updated: data.location_updated || null
    };
    originalDetector.value = { ...detector.value };
    isDirty.value = false;
  } catch (error) {
    console.error('Error fetching detector:', error);
  }
};

const fetchRelatedData = async () => {
  try {
    if (isNewDetector.value) return;

    const slotsResult = await get(`/api/inventory/sensorslots/?detector=${route.params.id}`);
    if (slotsResult.ok) detectorSensorSlots.value = extractList(slotsResult.data);

    const sensorsResult = await get(`/api/inventory/sensors/?detector=${route.params.id}`);
    if (sensorsResult.ok) detectorSensors.value = extractList(sensorsResult.data);

    const faultsResult = await get(`/api/inventory/detectorfaults/?detector=${route.params.id}`);
    if (faultsResult.ok) detectorFaults.value = extractList(faultsResult.data);

    const maintenanceResult = await get(`/api/inventory/maintenances/?detector=${route.params.id}`);
    if (maintenanceResult.ok) detectorMaintenance.value = extractList(maintenanceResult.data);

    const historyResult = await get(`/api/inventory/locationdetectorlogs/?detector=${route.params.id}`);
    if (historyResult.ok) locationHistory.value = extractList(historyResult.data);
  } catch (error) {
    console.error('Error fetching related data:', error);
  }
};

const accordionStates = ref({ sensors: false, faults: false, maintenance: false, locationHistory: false });
const toggleAccordion = (section) => {
  if (accordionStates.value[section]) {
    accordionStates.value[section] = false;
  } else {
    Object.keys(accordionStates.value).forEach((key) => { accordionStates.value[key] = false; });
    accordionStates.value[section] = true;
  }
};

const initialLoadComplete = ref(false);
const checkIfDirty = () => {
  if (!initialLoadComplete.value) return false;
  return (
    detector.value.label !== originalDetector.value.label ||
    detector.value.serial !== originalDetector.value.serial ||
    detector.value.status !== originalDetector.value.status ||
    detector.value.configuration !== originalDetector.value.configuration ||
    detector.value.location !== originalDetector.value.location ||
    detector.value.detector_model !== originalDetector.value.detector_model ||
    detector.value.firmware !== originalDetector.value.firmware ||
    detector.value.notes !== originalDetector.value.notes ||
    detector.value.purchase_date !== originalDetector.value.purchase_date ||
    detector.value.purchase_cost !== originalDetector.value.purchase_cost ||
    detector.value.location_updated !== originalDetector.value.location_updated
  );
};

watch(detector, () => { isDirty.value = checkIfDirty(); }, { deep: true });

onMounted(async () => {
  await Promise.all([
    fetchDetectorModels(),
    fetchLocations(),
    fetchSensorTypes(),
    fetchDetectorModelConfigurations()
  ]);

  if (!isNewDetector.value) {
    await fetchDetector();
    await fetchRelatedData();
  } else {
    originalDetector.value = { label: '', serial: '', status: '', configuration: null, location: null, detector_model: null, firmware: null, notes: null, purchase_date: '', purchase_cost: null, location_updated: null };
  }

  initialLoadComplete.value = true;
  isDirty.value = checkIfDirty();
});

const fetchDetectorModels = async () => {
  try {
    const result = await get('/api/inventory/detectormodels/');
    if (result.ok) detectorModels.value = extractList(result.data);
  } catch (error) { console.error('Error fetching detector models:', error); }
};
const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');
    if (result.ok) locations.value = extractList(result.data);
  } catch (error) { console.error('Error fetching locations:', error); }
};
const fetchSensorTypes = async () => {
  try {
    const result = await get('/api/inventory/sensortypes/');
    if (result.ok) sensorTypes.value = extractList(result.data);
  } catch (error) { console.error('Error fetching sensor types:', error); }
};
const fetchDetectorModelConfigurations = async () => {
  try {
    const result = await get('/api/inventory/detectormodelconfigurations/');
    if (result.ok) detectorModelConfigurations.value = extractList(result.data);
  } catch (error) { console.error('Error fetching detector model configurations:', error); }
};
</script>

<style scoped>
.detector-details-page { min-height: 100vh; }
.page-container { width: 100%; max-width: 1400px; margin: 2rem auto; padding: 0 2rem; }
h1 { color: #2c3e50; margin-bottom: 2rem; }
.layout-container { display: grid; grid-template-columns: 0.9fr 1fr; gap: 1rem; }
.fixed-box { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); min-width: 0; }
.fixed-box h2 { margin-top: 0; margin-bottom: 1rem; color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; }
.left { grid-column: 1; }
.right { grid-column: 2; display: flex; flex-direction: column; gap: 1rem; }
.form-container { min-width: 0; }
.accordion { border: 1px solid #ddd; border-radius: 4px; overflow: hidden; }
.accordion-header { background-color: #f8f9fa; padding: 1rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.accordion-header h3 { margin: 0; font-size: 1rem; color: #2c3e50; }
.accordion-icon { font-size: 1.2rem; font-weight: bold; }
.accordion-content { padding: 1rem; background-color: white; }
.detector-form { display: flex; flex-direction: column; min-width: 0; }
.form-row { display: flex; gap: 0.25rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.form-group { flex: 1; min-width: 100px; flex-basis: calc(50% - 2rem); padding: 0 0.25rem; box-sizing: border-box; }
.form-group.full-width { flex: 1; min-width: 100%; flex-basis: 100%; padding: 0 0.25rem; box-sizing: border-box; }
@media (max-width: 768px) { .form-group { flex-basis: 100%; } }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; }
.form-control { width: 100%; max-width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
.form-control:focus { outline: none; border-color: #42b883; box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2); }
.form-actions { display: flex; gap: 1rem; margin-top: auto; padding-top: 1rem; border-top: 1px solid #eee; }
.table-container { flex: 1; overflow-y: auto; }
.summary-table { width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden; margin-top: 0.5rem; }
.summary-table th, .summary-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #ddd; font-size: 0.9rem; }
.summary-table th { background-color: #f8f9fa; font-weight: 600; position: sticky; top: 0; }
.sensors-table th:nth-child(1), .sensors-table td:nth-child(1) { width: 20%; }
.sensors-table th:nth-child(2), .sensors-table td:nth-child(2) { width: 30%; }
.sensors-table th:nth-child(3), .sensors-table td:nth-child(3) { width: 25%; }
.sensors-table th:nth-child(4), .sensors-table td:nth-child(4) { width: 25%; }
.summary-table tbody tr:hover { background-color: rgba(0,0,0,0.03); }
.btn { padding: 0.75rem 1.5rem; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; text-decoration: none; display: inline-block; text-align: center; }
.btn-primary { background-color: #42b883; color: white; }
.btn-primary:hover { background-color: #36966d; }
.btn-primary:disabled { background-color: #cccccc; color: #666666; cursor: not-allowed; opacity: 0.6; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }
.dialog-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.dialog-box { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); text-align: center; max-width: 400px; width: 90%; z-index: 1001; }
.dialog-box h3 { margin-top: 0; color: #2c3e50; }
.dialog-actions { margin-top: 1.5rem; display: flex; justify-content: center; gap: 1rem; }
.sensor-slot-link, .fault-report-link, .maintenance-link { color: #42b883; text-decoration: none; font-weight: 500; }
.sensor-slot-link:hover, .fault-report-link:hover, .maintenance-link:hover { text-decoration: underline; }
.add-fault-button, .add-maintenance-button { margin-top: 1rem; text-align: center; }
.pagination-controls { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1rem; }
.pagination-controls .page-info { color: #666; font-size: 0.9rem; }
.btn-pagination { background-color: #6c757d; color: white; border: none; border-radius: 4px; padding: 0.25rem 0.5rem; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background-color 0.3s; }
.btn-pagination:hover:not(:disabled) { background-color: #5a6268; }
.btn-pagination:disabled { background-color: #adb5bd; cursor: not-allowed; opacity: 0.6; }

.sensor-section { border-radius: 6px; padding: 0.75rem; margin-bottom: 0.75rem; }
.sensor-section:last-child { margin-bottom: 0; }
.sensor-section-title { margin: 0 0 0.5rem 0; font-size: 0.9rem; font-weight: 700; }
.sensor-section-green { background-color: #d4edda; border: 1px solid #a3d9a5; }
.sensor-section-green .sensor-section-title { color: #155724; }
.sensor-section-green .summary-table th { background-color: #b7dfb9; }
.sensor-section-orange { background-color: #fff3cd; border: 1px solid #ffc107; }
.sensor-section-orange .sensor-section-title { color: #856404; }
.sensor-section-orange .summary-table th { background-color: #ffe69c; }
.sensor-section-red { background-color: #f8d7da; border: 1px solid #f5c6cb; }
.sensor-section-red .sensor-section-title { color: #721c24; }
.sensor-section-red .summary-table th { background-color: #f1b0b7; }
.no-sensor-cell { color: #888; font-style: italic; }

/* Sensor Select Dialog Styles */
.sensor-select-dialog { max-width: 600px; width: 90%; text-align: left; }
.dialog-subtitle { color: #666; font-size: 0.9rem; margin-bottom: 1rem; }
.sensor-list-container { max-height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 1rem; }
.no-sensors-msg { padding: 1rem; text-align: center; color: #888; font-style: italic; }
.sensor-option { padding: 0.75rem 1rem; border-bottom: 1px solid #eee; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: background 0.2s; }
.sensor-option:last-child { border-bottom: none; }
.sensor-option:hover { background-color: #f8f9fa; }
.sensor-option.selected { background-color: #d4edda; border-left: 4px solid #42b883; }
.sensor-option-serial { font-weight: 600; color: #2c3e50; }
.sensor-option-type { font-size: 0.85rem; color: #555; }
.sensor-option-dates { font-size: 0.8rem; color: #888; }

@media (max-width: 768px) {
  .page-container { padding: 0 1rem; margin-top: 1rem; }
  .layout-container { grid-template-columns: 1fr; grid-template-rows: auto auto; gap: 1rem; height: auto; }
  .left, .right { grid-column: 1; }
  .form-row { flex-direction: column; }
  .form-group { min-width: 100%; }
  .form-actions { flex-direction: column; }
}
.error-list { max-height: 200px; overflow-y: auto; margin: 1rem 0; padding: 0.5rem; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; }
.error-item { margin: 0.25rem 0; color: #721c24; font-weight: 500; }
.status-open { color: red; font-weight: bold; }
.status-resolved { color: blue; font-weight: bold; }
.date-upcoming { color: orange; font-weight: bold; }
.date-performed { color: blue; font-weight: bold; }
.date-overdue { color: red; font-weight: bold; }
.date-warning { color: orange; font-weight: bold; }
.date-future { color: blue; font-weight: bold; }
</style>