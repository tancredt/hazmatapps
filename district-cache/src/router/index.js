import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// ==========================================
// ACTIVE IMPORTS
// ==========================================
import HomePage from '../components/HomePage.vue'
import DetectorTransfer from '../components/DetectorTransfer.vue'
import CylinderTransfer from '../components/CylinderTransfer.vue'
import LoginScreen from '../components/LoginScreen.vue'

// ==========================================
// ROUTES
// ==========================================
// Labels are verified INSIDE the transfer page, not here. A bad label keeps the
// user on /detector-transfer/<label> (or /cylinder-transfer/<label>) and the page
// swaps its form for a 404 panel — no redirect to a separate error route.
const routes = [
  { path: '/', name: 'Home', alias: '/home', component: HomePage, meta: { requiresAuth: true } },
  { path: '/login', name: 'Login', component: LoginScreen, meta: { requiresAuth: false } },

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

  // Genuinely unknown paths fall back to the landing page.
  { path: '/:pathMatch(.*)*', name: 'Unknown', redirect: { name: 'Home' } }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// ==========================================
// GLOBAL NAVIGATION GUARD — auth only
// ==========================================
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) await authStore.checkAuth()
    if (!authStore.isAuthenticated) {
      return next({ name: 'Login', query: { redirect: to.fullPath } })
    }
  }

  next()
})

export default router
