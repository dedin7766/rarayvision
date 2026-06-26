import { createRouter, createWebHistory } from 'vue-router'
import { store } from './store'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import TesterView from './views/TesterView.vue'
import LiveView from './views/LiveView.vue'
import AboutView from './views/AboutView.vue'
import InstallationView from './views/InstallationView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/about', component: AboutView },
  { path: '/feedback', redirect: '/about' },
  { path: '/installation', component: InstallationView },
  {
    path: '/dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/tester',
    component: TesterView,
    meta: { requiresAuth: true }
  },
  {
    path: '/live',
    component: LiveView,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    component: () => import('./views/SettingsView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  if (to.meta.requiresAuth && !store.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
