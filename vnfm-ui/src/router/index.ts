import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'instances', name: 'Instances', component: () => import('../views/InstanceList.vue') },
      { path: 'packages', name: 'Packages', component: () => import('../views/PackageList.vue') },
      { path: 'topology/:id', name: 'Topology', component: () => import('../views/TopologyView.vue') },
      { path: 'vims', name: 'Vims', component: () => import('../views/VimList.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
