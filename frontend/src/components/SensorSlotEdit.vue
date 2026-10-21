<template>
  <div class="sensorslot-edit-page">

    <div class="page-container">
      <h1>Edit Sensor Slot</h1>

      <div class="form-container">
        <form @submit.prevent="saveSensorSlot" class="sensorslot-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="detector">Detector:</label>
              <input type="text" id="detector" :value="detectorLabel" disabled class="form-control readonly">
            </div>

            <div class="form-group">
              <label for="sensorGas">Sensor Gas:</label>
              <input type="text" id="sensorGas" :value="gas1Label" disabled class="form-control readonly">
            </div>

            <div class="form-group">
              <label for="currentSensor">Current Sensor:</label>
              <input type="text" id="currentSensor" :value="currentSensorLabel" disabled class="form-control readonly">
            </div>

            <div class="form-group">
              <label for="newSensor">New Sensor:</label>
              <select id="newSensor" v-model="selectedSensor" class="form-control">
                <option value="">Select a sensor</option>
                <option v-for="sensor in availableSensors" :key="sensor.id" :value="sensor.id">
                  {{ sensor.serial }} ({{ sensor.expiry_date || 'No expiry' }})
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="installDate">Install Date:</label>
              <input type="date" id="installDate" v-model="installDate" class="form-control">
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Update Sensor Slot</button>
            <router-link :to="`/detectors/${detectorId}`" class="btn btn-secondary">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-box" @click.stop>
        <h3>Success!</h3>
        <p>Sensor slot has been updated successfully.</p>
        <div class="dialog-actions">
          <button @click="closeDialogAndReturn" class="btn btn-primary">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { get, patch } from '@/utils/api';

const router = useRouter();
const route = useRoute();

// State variables
const detectorId = ref(route.params.detectorId);
// Check if we have sensorGas (new route format) or slotId (old route format)
const slotId = ref(route.params.sensorGas || route.params.slotId);
const detectorLabel = ref('');
const sensorTypeLabel = ref('');
const gas1Label = ref('');
const currentSensorLabel = ref('');
const selectedSensor = ref('');
const installDate = ref(new Date().toISOString().split('T')[0]);
const availableSensors = ref([]);
const showSuccessDialog = ref(false);
const sensorGasChoices = ref([]);

// Fetch the sensor slot details and related data
const fetchSensorSlotDetails = async () => {
  try {
    // Fetch all current sensor slots for this detector
    const slotsResult = await get(`/api/inventory/sensorslots/?detector=${detectorId.value}&is_current=true`);    
    if (gasResult.ok) {
      sensorGasChoices.value = gasResult.data;
    }

    let slotData;

    // Check if slotId is actually a sensor gas value (new route format)
    // If route has sensorGas, we need to find the slot for this detector and sensor gas
    if (route.params.sensorGas) {
      // Fetch all sensor slots for this detector
      const slotsResult = await get(`/api/inventory/sensorslots/?detector=${detectorId.value}`);
      if (!slotsResult.ok) {
        throw new Error(`HTTP error! status: ${slotsResult.status}`);
      }
      const allSlots = slotsResult.data;

      // Find the slot that matches the sensor gas
      // Prefer slots that don't have a sensor assigned yet, otherwise pick the first one
      const matchingSlots = allSlots.filter(slot => slot.sensorgas == route.params.sensorGas);
      if (matchingSlots.length === 0) {
        throw new Error(`No sensor slot found for detector ${detectorId.value} with sensor gas ${route.params.sensorGas}`);
      }

      // If there are multiple slots with the same sensor gas,
      // prefer the one that doesn't have a sensor assigned yet
      let matchingSlot = matchingSlots.find(slot => !slot.sensor);
      if (!matchingSlot) {
        // If all slots have sensors, just use the first one
        matchingSlot = matchingSlots[0];
      }

      const foundSlotData = matchingSlot;
      // Update the slotId to the actual slot ID
      slotId.value = foundSlotData.id;
      slotData = foundSlotData;
    } else {
      // Fetch the sensor slot details using the slot ID (old route format)
      const slotResult = await get(`/api/inventory/sensorslots/${slotId.value}`);
      if (!slotResult.ok) {
        throw new Error(`HTTP error! status: ${slotResult.status}`);
      }
      slotData = slotResult.data;
    }

    // Fetch detector details
    const detectorResult = await get(`/api/inventory/detectors/${detectorId.value}/`);
    if (detectorResult.ok) {
      detectorLabel.value = detectorResult.data.label;
    }

    // Set gas label from the slot data
    gas1Label.value = getSensorGasLabel(slotData.sensorgas);

    // Set current sensor if exists
    if (slotData.sensor) {
      const sensorResult = await get(`/api/inventory/sensors/${slotData.sensor}/`);
      if (sensorResult.ok) {
        const sensorData = sensorResult.data;
        currentSensorLabel.value = sensorData.serial || 'N/A';
        // Don't pre-select the current sensor since we want the user to select a new one
      }
    } else {
      currentSensorLabel.value = 'None';
    }

    // Fetch available sensors matching the sensor gas that are in stock
    const sensorsResult = await get(`/api/inventory/sensors/?status=IS`);
    if (sensorsResult.ok) {
      const allSensors = sensorsResult.data;
      // Filter sensors by matching sensor gas through sensor_type
      const sensorTypesResult = await get('/api/inventory/sensortypes/');
      if (sensorTypesResult.ok) {
        const sensorTypes = sensorTypesResult.data;
        const matchingSensorTypeIds = sensorTypes
          .filter(st => st.sensorgas === slotData.sensorgas)
          .map(st => st.id);
        availableSensors.value = allSensors.filter(s =>
          s.status === 'IS' && matchingSensorTypeIds.includes(s.sensor_type)
        );
      }
    }
  } catch (error) {
    console.error('Error fetching sensor slot details:', error);
  }
};

// Get sensor status display
const getSensorStatusLabel = (statusValue) => {
  const statusMap = {
    'OP': 'Operational',
    'IS': 'In Stock',
    'OO': 'On Order',
    'DC': 'Decommissioned'
  };
  return statusMap[statusValue] || statusValue;
};

// Get sensor gas label from choices
const getSensorGasLabel = (gasValue) => {
  const choice = sensorGasChoices.value.find(c => c.value === gasValue);
  return choice ? choice.label : gasValue;
};

watch(selectedSensor, () => {
})
// Save sensor slot update
const saveSensorSlot = async () => {
  try {
    // If a new sensor was selected, update the sensor's detector and install date
    if (selectedSensor.value) {

      const sensorPayload = {
        detector: parseInt(detectorId.value),  // Convert string ID to integer
        status: 'OP'  // Set status to Operational
      };

      if (installDate.value) {
        sensorPayload.install_date = installDate.value;
      }

      // Update the sensor's detector and install date
      const result = await patch(`/api/inventory/sensors/${selectedSensor.value}/`, sensorPayload);

      if (!result.ok) {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
    }

    // Show success dialog
    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error updating sensor slot:', error);
    alert('Error updating sensor slot: ' + error.message);
  }
};

// Close dialog and return to detector details
const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push(`/detectors/${detectorId.value}`);
};

// Close dialog
const closeDialog = () => {
  showSuccessDialog.value = false;
};

// Initialize component
onMounted(async () => {
  await fetchSensorSlotDetails();
});
</script>

