<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { get, post, put } from '@/utils/api';

const router = useRouter();
const route = useRoute();

// State for related data
const locations = ref([]);
const detectorFaultTypes = ref([]);

// State variables
const detectorId = ref(route.params.detectorId);
const detectorLabel = ref('');
const faultReport = ref({
  report_dt: new Date().toISOString().split('T')[0],
  fault_type: '',
  reported_by: '',
  report_location: '',
  status: 'OP', // Default to Open
  submit_notes: '',
  resolve_dt: '',
  resolved_by: '',
  resolve_notes: ''
});

// State for status change dialog
const showStatusChangeDialog = ref(false);
const faultTypeChoices = ref([]);
const showSuccessDialog = ref(false);
const showMissingResolveDateWarning = ref(false);

// Track the initial status when the form loads
const initialStatus = ref('');

// Check if we're creating a new fault report or editing an existing one
const isNewFault = computed(() => !route.params.faultId || route.params.faultId === 'new');

// Determine where to return to based on the referrer
const returnTo = computed(() => {
  if (route.query.from === 'faults') {
    return '/faults';
  } else {
    return `/detectors/${detectorId.value}`;
  }
});

// Check if fault report status is Closed ('CL') and form was loaded with Closed status
const isClosed = computed(() => {
  return initialStatus.value === 'CL' && faultReport.value.status === 'CL';
});

// Get location label
const getLocationLabel = (locationId) => {
  if (!locationId) return 'N/A';
  const location = locations.value.find(loc => loc.id === locationId);
  return location ? location.label : 'Unknown Location';
};

// Fetch choice options from the API
const fetchChoices = async () => {
  try {
    const result = await get('/api/inventory/detector-fault-types/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    detectorFaultTypes.value = result.data;
    faultTypeChoices.value = detectorFaultTypes.value;
  } catch (error) {
    console.error('Error fetching choice options:', error);
  }
};
 
// Fetch fault report details if editing existing
const fetchFaultReport = async () => {
  if (route.params.faultId && route.params.faultId !== 'new') {
    try {
      const result = await get(`/api/inventory/detectorfaults/${route.params.faultId}/`);
      if (!result.ok) {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
      const data = result.data;
      faultReport.value = {
        ...data,
        report_dt: data.report_dt ? new Date(data.report_dt).toISOString().split('T')[0] : '',
        resolve_dt: data.resolve_dt ? new Date(data.resolve_dt).toISOString().split('T')[0] : '',
        status: data.status || 'OP'
      };
    } catch (error) {
      console.error('Error fetching fault report:', error);
    }
  }
};

// Fetch detector details
const fetchDetectorDetails = async () => {
  try {
    const result = await get(`/api/inventory/detectors/${detectorId.value}/`);
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    detectorLabel.value = result.data.label;
  } catch (error) {
    console.error('Error fetching detector details:', error);
  }
};

// Save fault report function
const saveFaultReport = async () => {
  try {
    if (!faultReport.value.report_dt) {
      alert('Report Date is required.');
      return;
    }

    if (faultReport.value.status === 'CL' && !faultReport.value.resolve_dt) {
      showMissingResolveDateWarning.value = true;
      return;
    }

    if (faultReport.value.resolve_dt && faultReport.value.report_dt) {
      const resolveDate = new Date(faultReport.value.resolve_dt);
      const reportDate = new Date(faultReport.value.report_dt);

      if (resolveDate < reportDate) {
        alert('Resolve Date must be greater than or equal to Report Date.');
        return;
      }
    }

    const preparePayload = (obj) => {
      const payload = { ...obj };
      if (payload.resolve_dt === '') {
        payload.resolve_dt = null;
      }
      return payload;
    };

    const payload = preparePayload(faultReport.value);
    let result;

    if (isNewFault.value) {
      result = await post('/api/inventory/detectorfaults/', {
        ...payload,
        detector: parseInt(detectorId.value)
      });
    } else {
      result = await put(`/api/inventory/detectorfaults/${route.params.faultId}/`, payload);
    }

    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }

    showSuccessDialog.value = true;
  } catch (error) {
    console.error('Error saving fault report:', error);
    alert('Error saving fault report: ' + error.message);
  }
};

const closeDialogAndReturn = () => {
  showSuccessDialog.value = false;
  router.push(returnTo.value);
};

const closeDialog = () => {
  showSuccessDialog.value = false;
};

const closeMissingResolveDateWarning = () => {
  showMissingResolveDateWarning.value = false;
};

watch(() => faultReport.value.resolve_dt, (newVal, oldVal) => {
  if (newVal && faultReport.value.status === 'OP') {
    if (faultReport.value.report_dt) {
      const resolveDate = new Date(newVal);
      const reportDate = new Date(faultReport.value.report_dt);

      if (resolveDate >= reportDate) {
        showStatusChangeDialog.value = true;
      } else {
        alert('Resolve Date must be greater than or equal to Report Date.');
        faultReport.value.resolve_dt = '';
      }
    }
  }
});

const handleStatusChangeDialog = (shouldChange) => {
  if (shouldChange) {
    faultReport.value.status = 'CL';
  }
  showStatusChangeDialog.value = false;
};

const fetchLocations = async () => {
  try {
    const result = await get('/api/inventory/locations/');
    if (!result.ok) {
      throw new Error(`HTTP error! status: ${result.status}`);
    }
    locations.value = result.data;
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
};

onMounted(async () => {
  await Promise.all([
    fetchLocations(),
    fetchChoices()
  ]);

  await fetchDetectorDetails();

  if (!isNewFault.value) {
    await fetchFaultReport();
  }

  initialStatus.value = faultReport.value.status;
});
</script>