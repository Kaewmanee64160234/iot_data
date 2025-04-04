import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/sensor',
      name: 'sensor',
  
      component: () => import('../views/SensorView.vue'),
    },
    {
      path: '/sensor-dashboard',
      name: 'sensor-dashboard',
      component: () => import('../views/SensorDashboard.vue'),
    },
    
  ],
})

export default router
