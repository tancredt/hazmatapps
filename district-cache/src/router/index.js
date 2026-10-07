import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Menu Components
import MainMenu from '../components/MainMenu.vue'
import CylindersMenu from '../components/CylindersMenu.vue'
import DetectorsMenu from '../components/DetectorsMenu.vue'
import DistrictMainMenu from '../components/DistrictMainMenu.vue' // <-- NEW
import DistrictOperationsMenu from '../components/DistrictOperationsMenu.vue' // <-- NEW

// Action Components
import LocationChanger from '../components/LocationChanger.vue'
import ReturnScreen from '../components/ReturnScreen.vue'
import RestockScreen from '../components/RestockScreen.vue'
import DistrictStatus from '../components/DistrictStatus.vue'
import LoginScreen from '../components/LoginScreen.vue'
import ReportCylinderEmpty from '../components/ReportCylinderEmpty.vue'
import ReportDetectorFault from '../components/ReportDetectorFault.vue'
import CylinderSwapScreen from '../components/CylinderSwapScreen.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: LoginScreen, meta: { requiresAuth: false } },
  
  // --- NEW DISTRICT ROUTES ---
  {
    path: '/district-menu',
    name: 'DistrictMainMenu',
    component: DistrictMainMenu,
    meta: { requiresAuth: true }
  },
  {
    path: '/:district/district-operations',
    name: 'DistrictOperationsMenu',
    component: DistrictOperationsMenu,
    props: true,
    meta: { requiresAuth: true }
  },

  // --- STATION MENUS ---
  { path: '/:district/:location_label/mainmenu', name: 'MainMenu', component: MainMenu, props: true, meta: { requiresAuth: true } },
  { path: '/:district/:location_label/cylindermenu', name: 'CylindersMenu', component: CylindersMenu, props: true, meta: { requiresAuth: true } },
  { path: '/:district/:location_label/cylinder/swap', name: 'CylinderSwap', component: CylinderSwapScreen, props: true, meta: { requiresAuth: true } },
  { path: '/:district/:location_label/detectorsmenu', name: 'DetectorsMenu', component: DetectorsMenu, props: true, meta: { requiresAuth: true } },

  // --- STATION ACTIONS ---
  { path: '/:district/:location_label/cylinder/report', name: 'CylinderEmpty', component: ReportCylinderEmpty, props: true, meta: { requiresAuth: true } },
  { path: '/:district/:location_label/detector/report', name: 'DetectorFault', component: ReportDetectorFault, props: true, meta: { requiresAuth: true } },
  { path: '/:district/:location_label/detector/swap', name: 'LocationChanger', component: LocationChanger, props: true, meta: { requiresAuth: true } },

  // --- DISTRICT ACTIONS (Updated to remove location_label) ---
  { path: '/:district/detector/return', name: 'Return', component: ReturnScreen, props: true, meta: { requiresAuth: true } },
  { path: '/:district/detector/restock', name: 'Restock', component: RestockScreen, props: true, meta: { requiresAuth: true } },
  { path: '/:district/detector/status', name: 'DistrictStatus', component: DistrictStatus, props: true, meta: { requiresAuth: true } },

  { path: '/:pathMatch(.*)*', name: 'NotFound', component: { template: `<div style="padding: 2rem; text-align: center; color: red;"><h1>404 - Route Not Found</h1></div>` } }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) await authStore.checkAuth()
    if (!authStore.isAuthenticated) next({ name: 'Login', query: { redirect: to.fullPath } })
    else next()
  } else {
    next()
  }
})

export default router
