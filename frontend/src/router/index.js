import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Welcome from '@/components/Welcome.vue'
import Detectors from '@/components/Detectors.vue'
import DetectorDetails from '@/components/DetectorDetails.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Welcome',
      component: Welcome,
      meta: { title: 'Login - FRV Hazmat Equipment Inventory' }
    },
    {
      path: '/detectors',
      name: 'Detectors',
      component: Detectors,
      meta: { requiresAuth: true, title: 'Detectors - FRV Hazmat Equipment Inventory' }
    },
    {
      path: '/detectors/add-multiple',
      name: 'AddMultipleDetectors',
      component: () => import('@/components/AddMultipleDetectors.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/detectors/:id',
      name: 'DetectorDetails',
      component: DetectorDetails,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/sensorslots/:detectorId/:slotId/edit',
      name: 'SensorSlotEdit',
      component: () => import('@/components/SensorSlotEdit.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/detectors/:detectorId/sensorgas/:sensorGas/edit',
      name: 'SensorSlotEditBySensorGas',
      component: () => import('@/components/SensorSlotEdit.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/faultreports/:detectorId/:faultId?',
      name: 'FaultReportDetails',
      component: () => import('@/components/FaultReportDetails.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/cylinderfaultreports/:cylinderId/:faultId?',
      name: 'CylinderFaultReportDetails',
      component: () => import('@/components/CylinderFaultReportDetails.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/maintenances/:detectorId/:maintenanceId?',
      name: 'MaintenanceDetails',
      component: () => import('@/components/MaintenanceDetails.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/cylinders',
      name: 'Cylinders',
      component: () => import('@/components/Cylinders.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/cylinders/:id',
      name: 'CylinderDetails',
      component: () => import('@/components/CylinderDetails.vue'),
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/cylinders/add-multiple',
      name: 'AddMultipleCylinders',
      component: () => import('@/components/AddMultipleCylinders.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/cylinders/update-multiple',
      name: 'UpdateMultipleCylinders',
      component: () => import('@/components/UpdateMultipleCylinders.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/location-cylinder-slots',
      name: 'LocationCylinderSlots',
      component: () => import('@/components/LocationCylinderSlots.vue'),
      meta: { requiresAuth: true, title: 'Location Cylinder Slots - FRV Hazmat Equipment Inventory' }
    },
    {
      path: '/sensors',
      name: 'Sensors',
      component: () => import('@/components/Sensors.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/sensors/:id',
      name: 'SensorDetails',
      component: () => import('@/components/SensorDetails.vue'),
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/sensors/add-multiple',
      name: 'AddMultipleSensors',
      component: () => import('@/components/AddMultipleSensors.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/sensors/update-multiple',
      name: 'UpdateMultipleSensors',
      component: () => import('@/components/UpdateMultipleSensors.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/maintenances',
      name: 'Maintenances',
      component: () => import('@/components/Maintenances.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/faults',
      name: 'Faults',
      component: () => import('@/components/Faults.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/cylinderfaults',
      name: 'CylinderFaults',
      component: () => import('@/components/CylinderFaults.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/location-slots',
      name: 'LocationSlots',
      component: () => import('@/components/LocationSlots.vue'),
      meta: { requiresAuth: true, title: 'Location Slots - FRV Hazmat Equipment Inventory' }
    }
  ],
})

// Global route guard
router.beforeEach(async (to, from, next) => {
  const title = to.meta?.title || 'FRV Hazmat Equipment Inventory';
  document.title = title;

  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()
    await authStore.checkAuth()
    if (authStore.isAuthenticated) {
      next()
    } else {
      next({ name: 'Welcome' })
    }
  } else {
    next()
  }
})

export default router
