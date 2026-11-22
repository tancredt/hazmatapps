import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiFetch } from '@/utils/api'

// Menu Components
// import MainMenu from '../components/MainMenu.vue'
// import CylindersMenu from '../components/CylindersMenu.vue'
// import DetectorsMenu from '../components/DetectorsMenu.vue'
// import DistrictMainMenu from '../components/DistrictMainMenu.vue'
// import DistrictOperationsMenu from '../components/DistrictOperationsMenu.vue'
import DetectorTransfer from '../components/DetectorTransfer.vue'
import CylinderTransfer from '../components/CylinderTransfer.vue'

// Action Components
// import LocationChanger from '../components/LocationChanger.vue'
// import ReturnScreen from '../components/ReturnScreen.vue'
// import RestockScreen from '../components/RestockScreen.vue'
// import DistrictStatus from '../components/DistrictStatus.vue'
import LoginScreen from '../components/LoginScreen.vue'
// import ReportCylinderEmpty from '../components/ReportCylinderEmpty.vue'
// import ReportDetectorFault from '../components/ReportDetectorFault.vue'
// import CylinderSwapScreen from '../components/CylinderSwapScreen.vue'

// Home
import HomePage from '../components/HomePage.vue'

// ==========================================
// DATABASE VALIDATION LOGIC
// ==========================================
// Caches to prevent redundant API calls on every route change
const validDistricts = new Set()
const validLocations = new Map()
const validDetectors = new Map()
const validCylinders = new Map()

async function validateRouteParams(to) {
  const { district, location_label, detector_label, cylinder_label } = to.params

  // 1. Validate District
  if (district) {
    if (validDistricts.size === 0) {
      try {
        const res = await apiFetch('/districts/')
        res.forEach(d => validDistricts.add(d.value.toUpperCase()))
      } catch (e) {
        console.error('Failed to fetch districts', e)
        return false
      }
    }
    if (!validDistricts.has(district.toUpperCase())) {
      return false // District not found in DB
    }
  }

  // 2. Validate Location
  if (location_label) {
    const cacheKey = `${district?.toUpperCase() || 'ANY'}:${location_label.toUpperCase()}`
    if (!validLocations.has(cacheKey)) {
      try {
        let url = `/locations/?label=${encodeURIComponent(location_label)}`
        if (district) {
          url += `&district=${encodeURIComponent(district)}`
        }
        const res = await apiFetch(url)
        // The backend uses 'icontains' for label, so we verify exact match on frontend
        const exists = res.some(loc => loc.label.toUpperCase() === location_label.toUpperCase())
        validLocations.set(cacheKey, exists)
      } catch (e) {
        console.error('Failed to fetch location', e)
        return false
      }
    }
    if (!validLocations.get(cacheKey)) {
      return false // Location not found in DB
    }
  }

  // 3. Validate Detector Label
  if (detector_label) {
    const key = detector_label.toUpperCase()
    if (!validDetectors.has(key)) {
      try {
        const res = await apiFetch(`/detector-labels/?label=${encodeURIComponent(detector_label)}`)
        const exists = Array.isArray(res) && res.some(d => String(d.label).toUpperCase() === key)
        validDetectors.set(key, exists)
      } catch (e) {
        console.error('Failed to fetch detector', e)
        return false
      }
    }
    if (!validDetectors.get(key)) {
      return false // Detector not found in DB -> Triggers 404
    }
  }

  // 4. Validate Cylinder Label
  if (cylinder_label) {
    // Normalize to CYL00123 format to match backend response
    const cleaned = String(cylinder_label).trim().toUpperCase().replace(/\s+/g, '')
    const match = cleaned.match(/^CYL0*(\d+)$/) || cleaned.match(/^0*(\d+)$/)
    const canonicalLabel = match ? `CYL${match[1].padStart(5, '0')}` : cleaned
    const key = canonicalLabel

    if (!validCylinders.has(key)) {
      try {
        const res = await apiFetch(`/cylinders/?label=${encodeURIComponent(canonicalLabel)}`)
        const exists = Array.isArray(res) && res.some(c => {
          const cLabel = String(c.label).toUpperCase().replace(/\s+/g, '')
          const cMatch = cLabel.match(/^CYL0*(\d+)$/) || cLabel.match(/^0*(\d+)$/)
          const cCanonical = cMatch ? `CYL${cMatch[1].padStart(5, '0')}` : cLabel
          return cCanonical === key
        })
        validCylinders.set(key, exists)
      } catch (e) {
        console.error('Failed to fetch cylinder', e)
        return false
      }
    }
    if (!validCylinders.get(key)) {
      return false // Cylinder not found in DB -> Triggers 404
    }
  }

  return true
}

// ==========================================
// ROUTES
// ==========================================
const routes = [
  // --- HOME & AUTH ---
  { path: '/', name: 'Home', alias: '/home', component: HomePage, meta: { requiresAuth: true } },
  { path: '/login', name: 'Login', component: LoginScreen, meta: { requiresAuth: false } },

  // --- TRANSFER ROUTES (with optional label params for 404 validation) ---
  {
    path: '/detector-transfer/:detector_label?',
    name: 'DetectorTransfer',
    component: DetectorTransfer,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/cylinder-transfer/:cylinder_label?',
    name: 'CylinderTransfer',
    component: CylinderTransfer,
    props: true,
    meta: { requiresAuth: true }
  },

  // --- COMMENTED OUT ROUTES ---
  // { path: '/district-menu', name: 'DistrictMainMenu', component: DistrictMainMenu, meta: { requiresAuth: true } },
  // { path: '/:district/district-operations', name: 'DistrictOperationsMenu', component: DistrictOperationsMenu, props: true, meta: { requiresAuth: true } },
  // { path: '/:district/:location_label/mainmenu', name: 'MainMenu', component: MainMenu, props: true, meta: { requiresAuth: true } },
  // { path: '/:district/:location_label/cylindermenu', name: 'CylindersMenu', component: CylindersMenu, props: true, meta: { requiresAuth: true } },
  // { path: '/:district/:location_label/cylinder/swap', name: 'CylinderSwap', component: CylinderSwapScreen, props: true, meta: { requiresAuth: true } },
  // { path: '/:district/:location_label/detectorsmenu', name: 'DetectorsMenu', component: DetectorsMenu, props: true, meta: { requiresAuth: true } },
  // { path: '/:district/:location_label/cylinder/report', name: 'CylinderEmpty', component: ReportCylinderEmpty, props: true, meta: { requiresAuth: true } },
  // { path: '/:district/:location_label/detector/report', name: 'DetectorFault', component: ReportDetectorFault, props: true, meta: { requiresAuth: true } },
  // { path: '/:district/:location_label/detector/swap', name: 'LocationChanger', component: LocationChanger, props: true, meta: { requiresAuth: true } },
  // { path: '/:district/detector/return', name: 'Return', component: ReturnScreen, props: true, meta: { requiresAuth: true } },
  // { path: '/:district/detector/restock', name: 'Restock', component: RestockScreen, props: true, meta: { requiresAuth: true } },
  // { path: '/:district/detector/status', name: 'DistrictStatus', component: DistrictStatus, props: true, meta: { requiresAuth: true } },

  // --- 404 CATCH-ALL ---
  {
    // Note: Fixed the catch-all syntax to properly match any unmatched route
    path: '/:pathMatch(.*)*', 
    name: 'NotFound',
    component: {
      template: `<div style="padding: 2rem; text-align: center; color: red;"> <h1>404 - Not Found</h1> <p>The route, district, location, or equipment label you entered does not exist.</p> </div>`
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// ==========================================
// GLOBAL NAVIGATION GUARD
// ==========================================
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 1. Authentication Check
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) await authStore.checkAuth()
    if (!authStore.isAuthenticated) {
      return next({ name: 'Login', query: { redirect: to.fullPath } })
    }
  }

  // 2. Database Validation for Parameters
  if (to.params.district || to.params.location_label || to.params.detector_label || to.params.cylinder_label) {
    const isValid = await validateRouteParams(to)
    if (!isValid) {
      // If the parameter isn't in the database, trigger the 404 page
      return next({ name: 'NotFound' })
    }
  }

  next()
})

export default router
