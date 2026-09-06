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
                  <input
                    type="text"
                    id="label"
                    v-model="detector.label"
                    required
                    :disabled="!isNewDetector"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="serial">Serial *</label>
                  <input
                    type="text"
                    id="serial"
                    v-model="detector.serial"
                    required
                    class="form-control"
                  />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="detector_model">Model *</label>
                  <select
                    id="detector_model"
                    v-model="detector.detector_model"
                    required
                    class="form-control"
                  >
                    <option value="">Select Model</option>
                    <option v-for="model in detectorModels" :key="model.id" :value="model.id">
                      {{ getModelName(model.id) }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="status">Status *</label>
                  <select
                    id="status"
                    v-model="detector.status"
                    required
                    class="form-control"
                  >
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
                  <select
                    id="configuration"
                    v-model="detector.configuration"
                    class="form-control"
                  >
                    <option value="">Select Configuration</option>
                    <option
                      v-for="config in detectorModelConfigurations"
                      :key="config.id"
                      :value="config.id"
                    >
                      {{ getConfigurationLabel(config.id) }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="location">Location *</label>
                  <select
                    id="location"
                    v-model="detector.location"
                    required
                    class="form-control"
                  >
                    <option value="">Select Location</option>
                    <option v-for="location in locations" :key="location.id" :value="location.id">
                      {{ getLocationLabel(location.id) }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="purchase_date">Purchase Date</label>
                  <input
                    type="date"
                    id="purchase_date"
                    v-model="detector.purchase_date"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="purchase_cost">Purchase Cost ($)</label>
                  <input
                    type="number"
                    id="purchase_cost"
                    v-model.number="detector.purchase_cost"
                    step="0.01"
                    class="form-control"
                  />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="firmware">Firmware</label>
                  <input
                    type="text"
                    id="firmware"
                    v-model="detector.firmware"
                    maxlength="8"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="location_updated">Location Last Updated</label>
                  <input
                    type="text"
                    id="location_updated"
                    :value="detector.location_updated ? formatDate(detector.location_updated) : 'Never'"
                    readonly
                    class="form-control"
                  />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group full-width">
                  <label for="notes">Notes</label>
                  <textarea
                    id="notes"
                    v-model="detector.notes"
                    rows="4"
                    class="form-control"
                    placeholder="Additional notes about the detector..."
                  ></textarea>
                </div>
              </div>

              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="!isDirty">
                  Save Detector
                </button>
                <router-link to="/detectors" class="btn btn-secondary">Cancel</router-link>
              </div>
            </form>
          </div>
        </div>

        <!-- Tables Box (Right) -->
        <div class="fixed-box right">
          <!-- Sensors Accordion -->
          <div class="accordion">
            <div class="accordion-header" @click="toggleAccordion('sensors')">
              <h3>Sensors Attached</h3>
              <span class="accordion-icon">{{ accordionStates.sensors ? '−' : '+' }}</span>
            </div>

            <div class="accordion-content" v-show="accordionStates.sensors">
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
                    <tr v-for="slot in detectorSensorSlots" :key="slot.id">
                      <td>
                        <router-link
                          :to="{
                            name: 'SensorSlotEditBySensorGas',
                            params: { detectorId: route.params.id, sensorGas: slot.sensorgas }
                          }"
                          class="sensor-slot-link"
                        >
                          {{ getSensorGasDisplay(slot.sensorgas) }}
                        </router-link>
                      </td>
                      <td>{{ getSensorSerial(slot.sensor) || 'N/A' }}</td>
                      <td :class="getDateStatus(getSensorWarrantyDate(slot.sensor))">
                        {{ getSensorWarrantyDate(slot.sensor) || 'N/A' }}
                      </td>
                      <td :class="getDateStatus(getSensorExpiryDate(slot.sensor))">
                        {{ getSensorExpiryDate(slot.sensor) || 'N/A' }}
                      </td>
                    </tr>
                    <tr v-if="detectorSensorSlots.length === 0">
                      <td colspan="4">No sensor slots configured</td>
                    </tr>
                  </tbody>
                </table>
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
                        <router-link
                          :to="{
                            name: 'FaultReportDetails',
                            params: { detectorId: route.params.id, faultId: fault.id }
                          }"
                          class="fault-report-link"
                        >
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

                <!-- Fault Reports Pagination -->
                <div v-if="detectorFaults.length > faultsPerPage" class="pagination-controls">
                  <button
                    @click="prevFaultPage"
                    :disabled="faultReportsPage <= 1"
                    class="btn btn-pagination"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <polyline points="15 18 9 12 15 6"></polyline>
                    </svg>
                  </button>

                  <span class="page-info">
                    Page {{ faultReportsPage }} of {{ Math.ceil(detectorFaults.length / faultsPerPage) }}
                  </span>

                  <button
                    @click="nextFaultPage"
                    :disabled="faultReportsPage >= Math.ceil(detectorFaults.length / faultsPerPage)"
                    class="btn btn-pagination"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                  </button>
                </div>

                <div class="add-fault-button">
                  <router-link
                    :to="{ name: 'FaultReportDetails', params: { detectorId: route.params.id } }"
                    class="btn btn-primary"
                  >
                    Add New Fault Report
                  </router-link>
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
                        <router-link
                          :to="{
                            name: 'MaintenanceDetails',
                            params: { detectorId: route.params.id, maintenanceId: maintenance.id }
                          }"
                          class="maintenance-link"
                        >
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

                <!-- Maintenance Pagination -->
                <div v-if="detectorMaintenance.length > maintenancePerPage" class="pagination-controls">
                  <button
                    @click="prevMaintenancePage"
                    :disabled="maintenancePage <= 1"
                    class="btn btn-pagination"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <polyline points="15 18 9 12 15 6"></polyline>
                    </svg>
                  </button>

                  <span class="page-info">
                    Page {{ maintenancePage }} of {{ Math.ceil(detectorMaintenance.length / maintenancePerPage) }}
                  </span>

                  <button
                    @click="nextMaintenancePage"
                    :disabled="maintenancePage >= Math.ceil(detectorMaintenance.length / maintenancePerPage)"
                    class="btn btn-pagination"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                  </button>
                </div>

                <div class="add-maintenance-button">
                  <router-link
                    :to="{ name: 'MaintenanceDetails', params: { detectorId: route.params.id } }"
                    class="btn btn-primary"
                  >
                    Add New Maintenance
                  </router-link>
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
                      <th>Location</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="log in paginatedLocationHistory" :key="log.id">
                      <td>{{ log.location_label }}</td>
                      <td>{{ formatDate(log.updated) }}</td>
                    </tr>
                    <tr v-if="locationHistory.length === 0">
                      <td colspan="2">No location history</td>
                    </tr>
                  </tbody>
                </table>

                <!-- Location History Pagination -->
                <div v-if="locationHistory.length > locationHistoryPerPage" class="pagination-controls">
                  <button
                    @click="prevLocationHistoryPage"
                    :disabled="locationHistoryPage <= 1"
                    class="btn btn-pagination"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <polyline points="15 18 9 12 15 6"></polyline>
                    </svg>
                  </button>

                  <span class="page-info">
                    Page {{ locationHistoryPage }} of {{ Math.ceil(locationHistory.length / locationHistoryPerPage) }}
                  </span>

                  <button
                    @click="nextLocationHistoryPage"
                    :disabled="locationHistoryPage >= Math.ceil(locationHistory.length / locationHistoryPerPage)"
                    class="btn btn-pagination"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
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
          <p v-for="(error, index) in errorMessages" :key="index" class="error-item">
            {{ error }}
          </p>
        </div>
        <div class="dialog-actions">
          <button @click="closeErrorDialog" class="btn btn-primary">OK</button>
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
  label: '',
  serial: '',
  status: '',
  configuration: null,
  location: null,
  detector_model: null,
  firmware: null,
  notes: null,
  purchase_date: '',
  purchase_cost: null,
  location_updated: null
});

// State for tracking if form has been modified
const isDirty = ref(false);
const originalDetector = ref({});

// State for success dialog
const showSuccessDialog = ref(false);

// State for error dialog
const showErrorDialog = ref(false);
const errorMessages = ref([]);

// State for related data
const detectorSensors = ref([]);
const detectorSensorSlots = ref([]);
const detectorFaults = ref([]);
const detectorMaintenance = ref([]);
const locationHistory = ref([]);

// Pagination state for fault reports
const faultReportsPage = ref(1);
const faultsPerPage = 5;

// Pagination state for maintenance
const maintenancePage = ref(1);
const maintenancePerPage = 5;

// Pagination state for location history
const locationHistoryPage = ref(1);
const locationHistoryPerPage = 5;

// Check if we're creating a new detector or editing an existing one
const isNewDetector = computed(() => route.params.id === 'new');

// Computed properties for paginated data
const paginatedFaultReports = computed(() => {
  const start = (faultReportsPage.value - 1) * faultsPerPage;
  const end = start + faultsPerPage;
  return detectorFaults.value.slice(start, end);
});

const paginatedMaintenance = computed(() => {
  const start = (maintenancePage.value - 1) * maintenancePerPage;
  const end = start + maintenancePerPage;
  return detectorMaintenance.value.slice(start, end);
});

const paginatedLocationHistory = computed(() => {
  const start = (locationHistoryPage.value - 1) * locationHistoryPerPage;
  const end = start + locationHistoryPerPage;
  return locationHistory.value.slice(start, end);
});

// Helper to normalize list responses
const extractList = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// Format date in YYYY-MM-DD format
const formatDateYYYYMMDD = (dateString) => {
  if (!dateString) return 'N/A';

  const date = new Date(dateString);

  // Adjust for timezone to avoid day shifting
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
};

// Function to determine the date due status
const getDateDueStatus = (dateDue, datePerformed) => {
  if (!dateDue) return '';

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

// Function to determine the date status (for warranty and expiry dates)
const getDateStatus = (dateStr) => {
  if (!dateStr || dateStr === 'N/A') return '';

  const date = new Date(dateStr);
  const today = new Date();

  // Calculate 8 weeks from today
  const eightWeeksFromToday = new Date(today);
  eightWeeksFromToday.setDate(today.getDate() + 8 * 7); // 8 weeks = 56 days

  // Set time to 00:00:00 to compare only dates
  date.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);
  eightWeeksFromToday.setHours(0, 0, 0, 0);

  if (date <= today) {
    // Date is today or before today - red
    return 'date-overdue';
  } else if (date <= eightWeeksFromToday) {
    // Date is after today but within 8 weeks - orange
    return 'date-warning';
  } else {
    // Date is more than 8 weeks in the future - blue
    return 'date-future';
  }
};

// Pagination functions for fault reports
const prevFaultPage = () => {
  if (faultReportsPage.value > 1) {
    faultReportsPage.value--;
  }
};

const nextFaultPage = () => {
  if (faultReportsPage.value < Math.ceil(detectorFaults.value.length / faultsPerPage)) {
    faultReportsPage.value++;
  }
};

// Pagination functions for maintenance
const prevMaintenancePage = () => {
  if (maintenancePage.value > 1) {
    maintenancePage.value--;
  }
};

const nextMaintenancePage = () => {
  if (maintenancePage.value < Math.ceil(detectorMaintenance.value.length / maintenancePerPage)) {
    maintenancePage.value++;
  }
};

// Pagination functions for location history
const prevLocationHistoryPage = () => {
  if (locationHistoryPage.value > 1) {
    locationHistoryPage.value--;
  }
};

const nextLocationHistoryPage = () => {
  if (locationHistoryPage.value < Math.ceil(locationHistory.value.length / locationHistoryPerPage)) {
    locationHistoryPage.value++;
  }
};

// Get status displays
const getSensorStatusDisplay = (statusValue) => {
  const statusMap = {
    OP: 'Operational',
    IS: 'In Stock',
    OO: 'On Order',
    DC: 'Decommissioned'
  };
  return statusMap[statusValue] || statusValue;
};

const getFaultTypeDisplay = (faultTypeValue) => {
  const faultTypeMap = {
    BF: 'Failed Bump',
    SF: 'Sensor Fail',
    CE: 'Calibration Expired',
    DE: 'Displays Error',
    WS: 'Will not turn on',
    DD: 'Damaged Display',
    DC: 'Damaged Casing',
    MA: 'Missing Attachment'
  };
  return faultTypeMap[faultTypeValue] || faultTypeValue;
};

const getMaintenanceTypeDisplay = (maintTypeValue) => {
  const maintTypeMap = {
    SV: 'Scheduled Service',
    MS: 'Unscheduled Service',
    BT: 'Battery Replacement',
    FC: 'Filter Replacement',
    DR: 'Dessicant Replacement',
    CL: 'Clean'
  };
  return maintTypeMap[maintTypeValue] || maintTypeValue;
};

const getMaintenanceStatusDisplay = (statusValue) => {
  const statusMap = {
    SC: 'Scheduled',
    OP: 'Open',
    CL: 'Closed'
  };
  return statusMap[statusValue] || statusValue;
};

// Helper functions to get related object labels
const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find((loc) => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
};

const getModelName = (modelId) => {
  if (!modelId) return 'N/A';
  const model = detectorModels.value.find((m) => m.id === modelId);
  return model ? model.label : 'Unknown Model';
};

const getSensorTypeName = (sensorTypeId) => {
  if (!sensorTypeId) return 'N/A';
  const sensorType = sensorTypes.value.find((st) => st.id === sensorTypeId);
  return sensorType ? sensorType.part_number : 'Unknown Sensor Type';
};

const getSensorGasDisplay = (sensorgas) => {
  if (!sensorgas) return 'N/A';

  // Convert gas code to display name using the choices
  const gasMap = {
    CO: 'CO',
    HS: 'H2S',
    LE: 'LEL',
    O2: 'O2',
    VO: 'VOC',
    HC: 'HCN',
    CL: 'Cl2',
    PH: 'PH3',
    SO: 'SO2',
    NO: 'NO2',
    C2: 'CO2',
    NH: 'NH3',
    ET: 'ETO',
    CS: 'CO/H2S'
  };

  return gasMap[sensorgas] || sensorgas;
};

const getSensorSerial = (sensor) => {
  if (!sensor) return 'N/A';

  // If sensor is an object with serial property, return it
  if (typeof sensor === 'object' && sensor.serial) {
    return sensor.serial;
  }

  // If sensor is an ID, look it up in the local data
  if (typeof sensor === 'string' || typeof sensor === 'number') {
    const sensorObj = detectorSensors.value.find((s) => s.id === sensor);
    return sensorObj ? sensorObj.serial : 'N/A';
  }

  return 'N/A';
};

const getSensorWarrantyDate = (sensor) => {
  if (!sensor) return 'N/A';

  // If sensor is an object with warranty_date property, return it
  if (typeof sensor === 'object' && sensor.warranty_date) {
    return sensor.warranty_date;
  }

  // If sensor is an ID, look it up in the local data
  if (typeof sensor === 'string' || typeof sensor === 'number') {
    const sensorObj = detectorSensors.value.find((s) => s.id === sensor);
    return sensorObj ? sensorObj.warranty_date : 'N/A';
  }

  return 'N/A';
};

const getSensorExpiryDate = (sensor) => {
  if (!sensor) return 'N/A';

  // If sensor is an object with expiry_date property, return it
  if (typeof sensor === 'object' && sensor.expiry_date) {
    return sensor.expiry_date;
  }

  // If sensor is an ID, look it up in the local data
  if (typeof sensor === 'string' || typeof sensor === 'number') {
    const sensorObj = detectorSensors.value.find((s) => s.id === sensor);
    return sensorObj ? sensorObj.expiry_date : 'N/A';
  }

  return 'N/A';
};

const getConfigurationLabel = (configId) => {
  if (!configId) return 'N/A';

  const config = detectorModelConfigurations.value.find((c) => c.id === configId);
  if (!config) return 'Unknown Configuration';

  // Get the detector model name using the detector model ID
  const modelName = getModelName(config.detector_model);
  return `${config.label} (${modelName})`;
};

// Close dialog function
const closeDialog = () => {
  showSuccessDialog.value = false;
};

// Close error dialog function
const closeErrorDialog = () => {
  showErrorDialog.value = false;
  errorMessages.value = [];
};

// Save detector function
const saveDetector = async () => {
  try {
    // Client-side validation
    if (!detector.value.label.trim()) {
      alert('Label is required.');
      return;
    }

    if (!detector.value.serial.trim()) {
      alert('Serial is required.');
      return;
    }

    if (!detector.value.detector_model) {
      alert('Model is required.');
      return;
    }

    if (!detector.value.status) {
      alert('Status is required.');
      return;
    }

    if (!detector.value.location) {
      alert('Location is required.');
      return;
    }

    // If the configuration is being added or changed, block the save
    // while any current sensor slot still has a sensor installed
    if (detector.value.configuration !== originalDetector.value.configuration) {
      const occupiedSlots = detectorSensorSlots.value.filter(
        (slot) => slot.is_current && slot.sensor
      );

      if (occupiedSlots.length > 0) {
        const gasesWithSensors = occupiedSlots
          .map((slot) => getSensorGasDisplay(slot.sensorgas))
          .join(', ');

        errorMessages.value = [
          `Cannot change configuration while sensors are installed in the sensor slots (${gasesWithSensors}). Remove the sensors before changing the detector configuration.`
        ];
        showErrorDialog.value = true;

        // Revert the configuration dropdown to the saved value
        detector.value.configuration = originalDetector.value.configuration;
        return;
      }
    }

    // Prepare the detector data with proper data types
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
      // Creating a new detector
      result = await post('/api/inventory/detectors/', detectorData);
    } else {
      // Updating an existing detector
      result = await put(`/api/inventory/detectors/${route.params.id}/`, detectorData);
    }

    if (!result.ok) {
      // Handle validation errors
      if (result.status === 400) {
        const errorData = result.data;
        errorMessages.value = [];

        for (const [field, errors] of Object.entries(errorData)) {
          if (Array.isArray(errors)) {
            errorMessages.value.push(`${field}: ${errors.join(', ')}`);
          } else {
            // Handle cases where errors is not an array
            errorMessages.value.push(`${field}: ${errors}`);
          }
        }

        showErrorDialog.value = true;
        return; // Don't proceed with success dialog
      } else {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
    }

    // Refresh related data to show any updates
    if (!isNewDetector.value) {
      await fetchRelatedData();
    }

    // Update original detector data to match saved data
    originalDetector.value = { ...detector.value };

    // Reset isDirty flag since changes have been saved
    isDirty.value = false;

    // Show success dialog instead of navigating away
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving detector:', error);
    alert('Error saving detector: ' + error.message);
  }
};

// Fetch detector data if editing existing detector
const fetchDetector = async () => {
  try {
    const result = await get(`/api/inventory/detectors/${route.params.id}/`);

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

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

    // Store original detector data for dirty checking
    originalDetector.value = {
      ...data,
      detector_model: data.detector_model || null,
      location: data.location || null,
      configuration: data.configuration || null,
      firmware: data.firmware || null,
      notes: data.notes || null,
      location_updated: data.location_updated || null
    };

    // Reset isDirty since we just loaded the data
    isDirty.value = false;
  } catch (error) {
    console.error('Error fetching detector:', error);
  }
};

// Fetch related data
const fetchRelatedData = async () => {
  try {
    if (isNewDetector.value) return;

    // Fetch only current sensor slots for this detector
    const slotsResult = await get(
      `/api/inventory/sensorslots/?detector=${route.params.id}&is_current=true`
    );
    if (slotsResult.ok) {
      detectorSensorSlots.value = extractList(slotsResult.data);
    }

    // Fetch sensors for this detector (for detailed sensor info in slots)
    const sensorsResult = await get(`/api/inventory/sensors/?detector=${route.params.id}`);
    if (sensorsResult.ok) {
      detectorSensors.value = extractList(sensorsResult.data);
    }

    // Fetch faults for this detector
    const faultsResult = await get(`/api/inventory/detectorfaults/?detector=${route.params.id}`);
    if (faultsResult.ok) {
      detectorFaults.value = extractList(faultsResult.data);
    }

    // Fetch maintenance for this detector
    const maintenanceResult = await get(`/api/inventory/maintenances/?detector=${route.params.id}`);
    if (maintenanceResult.ok) {
      detectorMaintenance.value = extractList(maintenanceResult.data);
    }

    // Fetch location history for this detector
    const historyResult = await get(
      `/api/inventory/locationdetectorlogs/?detector=${route.params.id}`
    );
    if (historyResult.ok) {
      locationHistory.value = extractList(historyResult.data);
    }
  } catch (error) {
    console.error('Error fetching related data:', error);
  }
};

// Initialize accordion states
const accordionStates = ref({
  sensors: false,
  faults: false,
  maintenance: false,
  locationHistory: false
});

// Function to toggle accordion - only one open at a time
const toggleAccordion = (section) => {
  // If the clicked section is already open, close it
  if (accordionStates.value[section]) {
    accordionStates.value[section] = false;
  } else {
    // Otherwise, close all sections and open the clicked one
    Object.keys(accordionStates.value).forEach((key) => {
      accordionStates.value[key] = false;
    });
    accordionStates.value[section] = true;
  }
};

// Flag to track if the initial data has been loaded
const initialLoadComplete = ref(false);

// Function to check if form is dirty (has unsaved changes)
const checkIfDirty = () => {
  if (!initialLoadComplete.value) {
    // Don't consider it dirty until initial load is complete
    return false;
  }

  // Compare all fields in detector.value with originalDetector.value
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

// Watch for changes to detector fields and update isDirty flag
watch(
  detector,
  () => {
    isDirty.value = checkIfDirty();
  },
  { deep: true }
);

// Initialize component
onMounted(async () => {
  // Load required data
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
    // For new detector, initialize originalDetector as empty to track changes from initial state
    originalDetector.value = {
      label: '',
      serial: '',
      status: '',
      configuration: null,
      location: null,
      detector_model: null,
      firmware: null,
      notes: null,
      purchase_date: '',
      purchase_cost: null,
      location_updated: null
    };
  }

  // Mark that initial load is complete, so now changes will affect isDirty
  initialLoadComplete.value = true;
  isDirty.value = checkIfDirty(); // Check if form is dirty after initial load
});

// Fetch detector models from the API
const fetchDetectorModels = async () => {
  try {
    const result = await get('/api/inventory/detectormodels/');

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    detectorModels.value = extractList(result.data);
  } catch (error) {
    console.error('Error fetching detector models:', error);
  }
};

// Fetch locations from the API
const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    locations.value = extractList(result.data);
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
};

// Fetch sensor types from the API
const fetchSensorTypes = async () => {
  try {
    const result = await get('/api/inventory/sensortypes/');

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    sensorTypes.value = extractList(result.data);
  } catch (error) {
    console.error('Error fetching sensor types:', error);
  }
};

// Fetch detector model configurations from the API
const fetchDetectorModelConfigurations = async () => {
  try {
    const result = await get('/api/inventory/detectormodelconfigurations/');

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    detectorModelConfigurations.value = extractList(result.data);
  } catch (error) {
    console.error('Error fetching detector model configurations:', error);
  }
};
</script>

<style scoped>
.detector-details-page {
  min-height: 100vh;
}

.page-container {
  width: 100%;
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 2rem;
}

h1 {
  color: #2c3e50;
  margin-bottom: 2rem;
}

.layout-container {
  display: grid;
  grid-template-columns: 0.9fr 1fr;
  gap: 1rem;
}

.fixed-box {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 0;
}

.fixed-box h2 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.left {
  grid-column: 1;
}

.right {
  grid-column: 2;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-container {
  min-width: 0;
}

.accordion {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.accordion-header {
  background-color: #f8f9fa;
  padding: 1rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.accordion-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #2c3e50;
}

.accordion-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.accordion-content {
  padding: 1rem;
  background-color: white;
}

.detector-form {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.form-row {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 100px;
  flex-basis: calc(50% - 2rem);
  padding: 0 0.25rem;
  box-sizing: border-box;
}

.form-group.full-width {
  flex: 1;
  min-width: 100%;
  flex-basis: 100%;
  padding: 0 0.25rem;
  box-sizing: border-box;
}

/* On smaller screens, make form groups full width */
@media (max-width: 768px) {
  .form-group {
    flex-basis: 100%;
  }
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.form-control {
  width: 100%;
  max-width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.table-container {
  flex: 1;
  overflow-y: auto;
}

.summary-table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.summary-table th,
.summary-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
  font-size: 0.9rem;
}

.summary-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  position: sticky;
  top: 0;
}

/* Specific column widths for the sensors table */
.sensors-table th:nth-child(1),
.sensors-table td:nth-child(1) {
  width: 20%;
}

.sensors-table th:nth-child(2),
.sensors-table td:nth-child(2) {
  width: 20%;
}

.sensors-table th:nth-child(3),
.sensors-table td:nth-child(3) {
  width: 20%;
}

.sensors-table th:nth-child(4),
.sensors-table td:nth-child(4) {
  width: 20%;
}

.summary-table tbody tr:hover {
  background-color: #f8f9fa;
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

.btn-primary:hover {
  background-color: #36966d;
}

.btn-primary:disabled {
  background-color: #cccccc;
  color: #666666;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-primary:disabled:hover {
  background-color: #cccccc;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-box {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  text-align: center;
  max-width: 400px;
  width: 90%;
  z-index: 1001;
}

.dialog-box h3 {
  margin-top: 0;
  color: #2c3e50;
}

.dialog-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.sensor-slot-link {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

.sensor-slot-link:hover {
  text-decoration: underline;
}

.fault-report-link {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

.fault-report-link:hover {
  text-decoration: underline;
}

.maintenance-link {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

.maintenance-link:hover {
  text-decoration: underline;
}

.add-fault-button {
  margin-top: 1rem;
  text-align: center;
}

.add-maintenance-button {
  margin-top: 1rem;
  text-align: center;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
}

.pagination-controls .page-info {
  color: #666;
  font-size: 0.9rem;
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

  .page-container {
    padding: 0 1rem;
    margin-top: 1rem;
  }

  .layout-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
    gap: 1rem;
    height: auto;
  }

  .left,
  .right {
    grid-column: 1;
  }

  .form-row {
    flex-direction: column;
  }

  .form-group {
    min-width: 100%;
  }

  .form-actions {
    flex-direction: column;
  }
}

.error-list {
  max-height: 200px;
  overflow-y: auto;
  margin: 1rem 0;
  padding: 0.5rem;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.error-item {
  margin: 0.25rem 0;
  color: #721c24;
  font-weight: 500;
}

.status-open {
  color: red;
  font-weight: bold;
}

.status-resolved {
  color: blue;
  font-weight: bold;
}

.date-upcoming {
  color: orange;
  font-weight: bold;
}

.date-performed {
  color: blue;
  font-weight: bold;
}

.date-overdue {
  color: red;
  font-weight: bold;
}

.date-warning {
  color: orange;
  font-weight: bold;
}

.date-future {
  color: blue;
  font-weight: bold;
}
</style>