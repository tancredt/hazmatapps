import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LocationChanger from '../components/LocationChanger.vue'
import ReturnScreen from '../components/ReturnScreen.vue'
import RestockScreen from '../components/RestockScreen.vue'
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
    path: 'restock/:district/',
    name: 'Restock',
    component: RestockScreen,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: {
      template: `<div style="padding: 2rem; text-align: center; color: red; font-family: sans-serif;">
        <h1>404 - Route Not Found</h1>
        <p>The URL you entered is invalid.</p>
      </div>`
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 🛡️ Global route guard - saves the intended destination
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // If the route requires authentication
  if (to.meta.requiresAuth) {
    // Check if user is already authenticated
    if (!authStore.isAuthenticated) {
      await authStore.checkAuth()
    }
    
    // If still not authenticated, redirect to login with the intended path
    if (!authStore.isAuthenticated) {
      console.log('🔒 [Router] Not authenticated. Redirecting to login from:', to.fullPath)
      
      // Use fullPath to preserve query params and hash if any
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
