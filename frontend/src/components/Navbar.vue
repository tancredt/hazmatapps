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
      <!-- Detectors Dropdown -->
      <div class="dropdown" :class="{ 'is-active': activeDropdown === 'detectors' }">
        <button class="dropdown-button nav-link" @click.stop="toggleDropdown('detectors')">
          Detectors
          <svg class="caret" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="dropdown-content">
          <router-link to="/detectors" class="dropdown-item" @click="closeDropdown">List</router-link>
          <router-link to="/faults" class="dropdown-item" @click="closeDropdown">Faults</router-link>
        </div>
      </div>

      <!-- Cylinders Dropdown -->
      <div class="dropdown" :class="{ 'is-active': activeDropdown === 'cylinders' }">
        <button class="dropdown-button nav-link" @click.stop="toggleDropdown('cylinders')">
          Cylinders
          <svg class="caret" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="dropdown-content">
          <router-link to="/cylinders" class="dropdown-item" @click="closeDropdown">List</router-link>
          <router-link to="/cylinderfaults" class="dropdown-item" @click="closeDropdown">Faults</router-link>
        </div>
      </div>

      <router-link to="/sensors" class="nav-link">Sensors</router-link>
      <router-link to="/maintenances" class="nav-link">Maintenance</router-link>

      <!-- Locations Dropdown -->
      <div class="dropdown" :class="{ 'is-active': activeDropdown === 'locations' }">
        <button class="dropdown-button nav-link" @click.stop="toggleDropdown('locations')">
          Locations
          <svg class="caret" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="dropdown-content">
          <router-link to="/location-slots" class="dropdown-item" @click="closeDropdown">Location Detector Slots</router-link>
          <router-link to="/location-cylinder-slots" class="dropdown-item" @click="closeDropdown">Location Cylinder Slots</router-link>
        </div>
      </div>

      <button @click="handleLogout" class="nav-link logout-button">Logout</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// State to track which dropdown is currently open
const activeDropdown = ref(null);

const toggleDropdown = (name) => {
  activeDropdown.value = activeDropdown.value === name ? null : name;
};

const closeDropdown = () => {
  activeDropdown.value = null;
};

// Close dropdown when clicking anywhere outside of it
const handleClickOutside = (event) => {
  if (!event.target.closest('.dropdown')) {
    activeDropdown.value = null;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

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
  gap: 1.5rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  transition: background-color 0.3s;
  font-size: 0.95rem;
}

.nav-link:hover, .nav-link.router-link-active {
  background-color: #34495e;
}

.logout-button {
  background-color: #e74c3c;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
  margin-left: 0.5rem;
}

.logout-button:hover {
  background-color: #c0392b;
}

/* --- Dropdown Styles --- */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-button {
  background-color: transparent;
  color: white;
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.95rem;
  transition: background-color 0.3s;
}

.dropdown-button:hover, .dropdown.is-active .dropdown-button {
  background-color: #34495e;
}

.caret {
  width: 12px;
  height: 12px;
  transition: transform 0.2s ease;
}

.dropdown.is-active .caret {
  transform: rotate(180deg);
}

.dropdown-content {
  position: absolute;
  top: calc(100% + 8px); /* Adds a nice little gap between button and menu */
  left: 0;
  min-width: 180px;
  background-color: #ffffff;
  border-radius: 6px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 0.5rem 0;
  
  /* Animation properties */
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.2s ease-in-out;
  z-index: 1000;
  border: 1px solid #e9ecef;
}

.dropdown.is-active .dropdown-content {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: block;
  padding: 0.6rem 1.2rem;
  color: #333;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
  color: #42b883;
  border-left-color: #42b883;
}

/* Highlights the current active page in the dropdown */
.dropdown-item.router-link-active {
  background-color: #e8f8f2;
  color: #42b883;
  font-weight: 600;
  border-left-color: #42b883;
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    height: auto;
  }

  .nav-links {
    order: 3;
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>