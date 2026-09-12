import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LocationChanger from '../components/LocationChanger.vue'
import ReturnScreen from '../components/ReturnScreen.vue'
import RestockScreen from '../components/RestockScreen.vue'
import DistrictStatus from '../components/DistrictStatus.vue'
import LoginScreen from '../components/LoginScreen.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginScreen,
    meta: { requiresAuth: false }
  },
  {
    path: '/swap/:district/:location_label',
    name: 'LocationChanger',
    component: LocationChanger,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/return/:district',
    name: 'Return',
    component: ReturnScreen,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/restock/:district/',
    name: 'Restock',
    component: RestockScreen,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/status/:district',
    name: 'DistrictStatus',
    component: DistrictStatus,
    props: true,
    meta: { requiresAuth: true }
  },
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
