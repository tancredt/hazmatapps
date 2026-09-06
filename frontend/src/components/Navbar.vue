<template>
  <div class="navbar">
    <div class="nav-left">
      <router-link to="/" class="nav-brand">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon">
          <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
          <path d="M2 17l10 5 10-5"></path>
          <path d="M2 12l10 5 10-5"></path>
        </svg>
        <span>Hazmat Equipment Inventory</span>
      </router-link>
    </div>

    <div class="nav-links">
      <router-link to="/detectors" class="nav-link">Detectors</router-link>
      <router-link to="/cylinders" class="nav-link">Cylinders</router-link>
      <router-link to="/sensors" class="nav-link">Sensors</router-link>
      <router-link to="/maintenances" class="nav-link">Maintenance</router-link>
      <router-link to="/faults" class="nav-link">Faults</router-link>
      
      <!-- Locations Dropdown -->
      <div class="dropdown">
        <button class="dropdown-button nav-link">Locations</button>
        <div class="dropdown-content">
          <router-link to="/location-slots" class="dropdown-item">Location Slots</router-link>
        </div>
      </div>
      
      <!-- Dropdown menu for "Other Stuff" -->
      <div class="dropdown">
        <button class="dropdown-button nav-link">Other Stuff</button>
        <div class="dropdown-content">
          <router-link to="/detectormodels/new" class="dropdown-item">Add New Model</router-link>
          <router-link to="/locations/new" class="dropdown-item">Add New Location</router-link>
          <router-link to="/detectormodelconfigurations/new" class="dropdown-item">Add New Configuration</router-link>
          <router-link to="/cylindertypes/new" class="dropdown-item">Add New Cylinder Type</router-link>
          <router-link to="/sensortypes/new" class="dropdown-item">Add New Sensor Type</router-link>
        </div>
      </div>
      
      <button @click="handleLogout" class="nav-link logout-button">Logout</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const handleLogout = async () => {
  await authStore.logout();
  router.push('/');
};
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 2rem;
  background-color: #2c3e50;
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 1000;
  height: 50px;
  box-sizing: border-box;
}

.nav-left {
  display: flex;
  align-items: center;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  text-decoration: none;
  font-weight: bold;
  font-size: 1.2rem;
}

.nav-icon {
  width: 24px;
  height: 24px;
}

.nav-links {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover, .nav-link.router-link-active {
  background-color: #34495e;
}

.logout-button {
  background-color: #e74c3c;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.logout-button:hover {
  background-color: #c0392b;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-button {
  background-color: #2c3e50;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  text-align: center;
  font-size: 1rem;
}

.dropdown-button:hover {
  background-color: #34495e;
}

.dropdown-content {
  display: none;
  position: absolute;
  background-color: #f9f9f9;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
  z-index: 1;
  border-radius: 4px;
  top: 100%;
  left: 0;
}

.dropdown-content a {
  color: black;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
}

.dropdown-content a:hover {
  background-color: #f1f1f1;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown:hover .dropdown-button {
  background-color: #34495e;
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .nav-links {
    order: 3;
    width: 100%;
    justify-content: center;
  }
}
</style>