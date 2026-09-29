import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// New Menu Imports
import MainMenu from '../components/MainMenu.vue'
import CylindersMenu from '../components/CylindersMenu.vue'
import DetectorsMenu from '../components/DetectorsMenu.vue'

// Existing Imports
import LocationChanger from '../components/LocationChanger.vue'
import ReturnScreen from '../components/ReturnScreen.vue'
import RestockScreen from '../components/RestockScreen.vue'
import DistrictStatus from '../components/DistrictStatus.vue'
import LoginScreen from '../components/LoginScreen.vue'
import ReportCylinderEmpty from '../components/ReportCylinderEmpty.vue'
import ReportDetectorFault from '../components/ReportDetectorFault.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginScreen,
    meta: { requiresAuth: false }
  },
  // ================= MENUS =================
  {
    path: '/cache/:district/:location_label/mainmenu',
    name: 'MainMenu',
    component: MainMenu,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/cache/:district/:location_label/cylindermenu',
    name: 'CylindersMenu',
    component: CylindersMenu,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/cache/:district/:location_label/detectorsmenu',
    name: 'DetectorsMenu',
    component: DetectorsMenu,
    props: true,
    meta: { requiresAuth: true }
  },

  // ================= CYLINDER ACTIONS =================
  {
    path: '/cache/:district/:location_label/cylinder/report',
    name: 'CylinderEmpty',
    component: ReportCylinderEmpty,
    props: true,
    meta: { requiresAuth: true }
  },

  // ================= DETECTOR ACTIONS =================
  {
    path: '/cache/:district/:location_label/detector/report',
    name: 'DetectorFault',
    component: ReportDetectorFault,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/cache/:district/:location_label/detector/swap',
    name: 'LocationChanger',
    component: LocationChanger,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/cache/:district/:location_label/detector/return',
    name: 'Return',
    component: ReturnScreen,
    props: true, // Passes both, but ReturnScreen only declares 'district' so it safely ignores location_label
    meta: { requiresAuth: true }
  },
  {
    path: '/cache/:district/:location_label/detector/restock',
    name: 'Restock',
    component: RestockScreen,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/cache/:district/:location_label/detector/status',
    name: 'DistrictStatus',
    component: DistrictStatus,
    props: true,
    meta: { requiresAuth: true }
  },

  // ================= FALLBACK =================
  {
    path: '/:pathMatch(.*)',
    name: 'NotFound',
    component: {
      template: `<div style="padding: 2rem; text-align: center; color: red; font-family: sans-serif;"><h1>404 - Route Not Found</h1><p>The URL you entered is invalid.</p></div>`
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      await authStore.checkAuth()
    }
    
    if (!authStore.isAuthenticated) {
      console.log('🔒 [Router] Not authenticated. Redirecting to login from:', to.fullPath)
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
