<template>
<div class="location-form-page">
<div class="page-container">
   <h1>Add New Location</h1>
   <div class="form-container">
     <form @submit.prevent="saveLocation" class="location-form">
       <div class="form-row">
         <div class="form-group">
           <label for="label">Label *</label>
           <input
             type="text"
             id="label"
             v-model="location.label"
             required
             maxlength="16"
             class="form-control"
             placeholder="Enter location label"
           >
         </div>
         <div class="form-group">
           <label for="address">Address</label>
           <input
             type="text"
             id="address"
             v-model="location.address"
             maxlength="256"
             class="form-control"
             placeholder="Enter location address"
           >
         </div>
       </div>
       <div class="form-row">
         <div class="form-group">
           <label for="location_type">Location Type *</label>
           <select id="location_type" v-model="location.location_type" required class="form-control">
             <option value="">Select Location Type</option>
             <option v-for="choice in locationTypeChoices" :key="choice.value" :value="choice.value">
               {{ choice.label }}
             </option>
           </select>
         </div>
         <div class="form-group">
           <label for="district">District</label>
           <select id="district" v-model="location.district" class="form-control">
  	     <option value="">No District</option>
             <option v-for="district in districts" :key="district.value" :value="district.value">
               {{ district.label }}
             </option>
           </select>
         </div>
       </div>
       <div class="form-row">
         <div class="form-group">
           <label for="priority">Priority</label>
           <input
             type="number"
             id="priority"
             v-model.number="location.priority"
             min="1"
             class="form-control"
             placeholder="Enter priority (higher numbers have higher priority)"
           >
         </div>
         <div class="form-group">
           <!-- Empty space to maintain layout -->
         </div>
       </div>
       <div class="form-actions">
         <button type="submit" class="btn btn-primary">Save Location</button>
         <router-link to="/detectors" class="btn btn-secondary">Cancel</router-link>
       </div>
     </form>
   </div>
 </div>
 <!-- Success Dialog -->
 <div v-if="showSuccessDialog" class="dialog-overlay" @click="closeDialog">
   <div class="dialog-box" @click.stop>
     <h3>Success!</h3>
     <p>Location has been saved successfully.</p>
     <div class="dialog-actions">
       <button @click="closeDialogAndReturn" class="btn btn-primary">OK</button>
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { get, post } from '@/utils/api.js';

const router = useRouter();

// State for the location
const location = ref({
label: '',
address: '',
location_type: 'ST', // Default to Station (matches model default)
district: '',
priority: 1
});

// State for related data
const locationTypeChoices = ref([]);
const districts = ref([]);

// State for success dialog
const showSuccessDialog = ref(false);

// State for error dialog
const showErrorDialog = ref(false);
const errorMessages = ref([]);

// Fetch location type choices from the API
const fetchLocationTypes = async () => {
try {
const result = await get('/api/inventory/location-types/');
if (!result.ok) {
throw new Error(`HTTP error! status: ${result.status}`);
}
locationTypeChoices.value = result.data;
} catch (error) {
console.error('Error fetching location types:', error);
}
};

// Fetch districts from the API
const fetchDistricts = async () => {
try {
const result = await get('/api/inventory/districts/');
if (!result.ok) {
throw new Error(`HTTP error! status: ${result.status}`);
}
districts.value = result.data;
} catch (error) {
console.error('Error fetching districts:', error);
}
};

// Save location function
const saveLocation = async () => {
try {
// Build payload matching LocationSerializer fields
// Build payload matching LocationSerializer fields
// Build payload matching LocationSerializer fields
const payload = {
  label: location.value.label,
  address: location.value.address || '',
  location_type: location.value.location_type,
  district: location.value.district || null, // Pass the string value directly
  priority: location.value.priority || 1
};

const result = await post('/api/inventory/locations/', payload);

if (!result.ok) {
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
return;
}

// Show success dialog
showSuccessDialog.value = true;
} catch (error) {
console.error('Error saving location:', error);
alert('Error saving location: ' + error.message);
}
};

// Close dialog and return to detectors page
const closeDialogAndReturn = () => {
showSuccessDialog.value = false;
router.push('/detectors');
};

// Close dialog functions
const closeDialog = () => {
showSuccessDialog.value = false;
};

const closeErrorDialog = () => {
showErrorDialog.value = false;
errorMessages.value = [];
};

// Initialize component
onMounted(async () => {
await Promise.all([
fetchLocationTypes(),
fetchDistricts()
]);
});
</script>
<style scoped>
.location-form-page {
min-height: 100vh;
display: flex;
flex-direction: column;
}

.page-container {
max-width: 1200px;
margin: 2rem auto;
padding: 0 2rem;
flex: 1;
}

h1 {
color: #2c3e50;
margin-bottom: 2rem;
}

.form-container {
background: white;
border-radius: 8px;
padding: 1.5rem;
box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.location-form {
display: flex;
flex-direction: column;
}

.form-row {
display: flex;
gap: 1.5rem;
margin-bottom: 1.5rem;
flex-wrap: wrap;
}

.form-group {
flex: 1;
min-width: 200px;
flex-basis: calc(50% - 0.75rem); /* Two columns by default */
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
padding: 0.75rem;
border: 1px solid #ddd;
border-radius: 4px;
font-size: 1rem;
}

.form-control:focus {
outline: none;
border-color: #42b883;
box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

.form-actions {
display: flex;
gap: 1rem;
margin-top: 2rem;
padding-top: 1rem;
border-top: 1px solid #eee;
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
</style>