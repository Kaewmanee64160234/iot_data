import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import VisualizedDataView from '@/views/VisualizedDataView.vue'

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
      path: '/visualized',
      name: 'visualized',
      component:VisualizedDataView,
    },
  ],
})

export default router
