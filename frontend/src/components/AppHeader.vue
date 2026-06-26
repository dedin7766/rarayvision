<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { store } from '../store'
import { authService } from '../services/authService'
import { API_BASE_URL } from '../utils'
import logoImage from '../assets/logo.png'

const router = useRouter()
const showHeaderMenu = ref(false)
const showProfileDropdown = ref(false)
const showDocsDropdown = ref(false)
const showLogoutModal = ref(false)

const toggleHeaderMenu = () => { showHeaderMenu.value = !showHeaderMenu.value }
const closeHeaderMenu = () => { showHeaderMenu.value = false }
const toggleProfileDropdown = () => { showProfileDropdown.value = !showProfileDropdown.value }
const closeProfileDropdown = () => { showProfileDropdown.value = false }
const toggleDocsDropdown = () => { showDocsDropdown.value = !showDocsDropdown.value }
const closeDocsDropdown = () => { showDocsDropdown.value = false }

const isLoggingOut = ref(false)

const confirmLogout = () => {
  isLoggingOut.value = true
  setTimeout(() => {
    authService.logout()
    showLogoutModal.value = false
    isLoggingOut.value = false
    router.push('/')
    closeHeaderMenu()
  }, 600)
}

const goTo = (path) => {
  router.push(path)
  closeHeaderMenu()
}
</script>

<template>
  <header class="top-nav">
    <div class="header-brand">
      <img :src="logoImage" alt="Raray Vision logo" class="brand-logo" />
      <div>
        <p class="eyebrow">Raray Vision</p>
        <h1>Face Recognition API Console</h1>
      </div>
    </div>
    <div class="nav-actions">
      <div class="desktop-menu">
        <a v-if="!store.isLoggedIn" href="#" :class="{ active: $route.path === '/' }" @click.prevent="goTo('/')">Home</a>
        <a v-if="store.isLoggedIn" href="#" :class="{ active: $route.path === '/dashboard' }" @click.prevent="goTo('/dashboard')">Dashboard</a>
        <a v-if="store.isLoggedIn" href="#" :class="{ active: $route.path === '/tester' }" @click.prevent="goTo('/tester')">Tester</a>
        <a v-if="store.isLoggedIn" href="#" :class="{ active: $route.path === '/live' }" @click.prevent="goTo('/live')">Live</a>
        <a href="#" :class="{ active: $route.path === '/about' }" @click.prevent="goTo('/about')">About</a>
        <a href="#" :class="{ active: $route.path === '/installation' }" @click.prevent="goTo('/installation')">Installation</a>
        <!-- Docs dropdown -->
        <div class="docs-menu-wrap" style="position: relative; display: inline-flex;">
          <button type="button" class="docs-btn" @click.stop="toggleDocsDropdown">
            Docs
            <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" style="margin-left:4px;"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div v-if="showDocsDropdown" class="profile-dropdown-overlay" @click="closeDocsDropdown" style="position:fixed; inset:0; z-index:40;"></div>
          <div v-if="showDocsDropdown" class="profile-dropdown docs-dropdown" style="z-index:50; left:0; right:auto;">

            <a :href="`${API_BASE_URL}/redoc`" target="_blank" rel="noopener" @click="closeDocsDropdown" style="display:flex; align-items:center; gap:8px;">
              <svg viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
              API Docs
            </a>
            <a :href="`${API_BASE_URL}/docs`" target="_blank" rel="noopener" @click="closeDocsDropdown" style="display:flex; align-items:center; gap:8px;">
              <svg viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
              Swagger UI
            </a>
          </div>
        </div>
        <a v-if="!store.isLoggedIn" href="#" :class="{ active: $route.path === '/login' }" @click.prevent="goTo('/login')" style="display: inline-flex; align-items: center; gap: 4px;">
          <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>
          Login
        </a>
        <div v-else class="profile-menu-wrap" style="position: relative;">
          <button type="button" class="profile-btn" @click.stop="toggleProfileDropdown" style="padding: 0; width: 36px; height: 36px; overflow: hidden; display: flex; align-items: center; justify-content: center;">
            <img v-if="store.user?.avatar_url" :src="store.user.avatar_url" alt="User Avatar" style="width: 100%; height: 100%; object-fit: cover;" />
            <svg v-else viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          </button>
          <div v-if="showProfileDropdown" class="profile-dropdown-overlay" @click="closeProfileDropdown" style="position:fixed; inset:0; z-index:40;"></div>
          <div v-if="showProfileDropdown" class="profile-dropdown" style="z-index:50;">
            <a href="#" @click.prevent="goTo('/settings'); closeProfileDropdown()" style="display:flex; align-items:center; gap:8px;">
              <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
              Settings
            </a>
            <a href="#" @click.prevent="showLogoutModal = true; closeProfileDropdown()" style="display:flex; align-items:center; gap:8px; color: #ef4444;">
              <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
              Logout
            </a>
          </div>
        </div>
      </div>
      <button type="button" class="menu-toggle" :class="{ active: showHeaderMenu }" @click="toggleHeaderMenu" aria-label="Open menu">
        <span></span><span></span><span></span>
      </button>
      <div v-if="showHeaderMenu" class="header-menu">
        <a v-if="!store.isLoggedIn" href="#" @click.prevent="goTo('/')">Home</a>
        <a v-if="store.isLoggedIn" href="#" @click.prevent="goTo('/dashboard')">Dashboard</a>
        <a v-if="store.isLoggedIn" href="#" @click.prevent="goTo('/tester')">Tester</a>
        <a v-if="store.isLoggedIn" href="#" @click.prevent="goTo('/live')">Live</a>
        <a href="#" @click.prevent="goTo('/about')">About</a>
        <a href="#" @click.prevent="goTo('/installation')">Installation</a>
        <!-- Docs links in mobile menu -->

        <a :href="`${API_BASE_URL}/redoc`" target="_blank" rel="noopener" @click="closeHeaderMenu" style="display:flex; align-items:center; gap:8px;">
          <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          API Docs
        </a>
        <a :href="`${API_BASE_URL}/docs`" target="_blank" rel="noopener" @click="closeHeaderMenu" style="display:flex; align-items:center; gap:8px;">
          <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
          Swagger UI
        </a>
        <a v-if="!store.isLoggedIn" href="#" @click.prevent="goTo('/login')" style="display: inline-flex; align-items: center; gap: 4px;">
          <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>
          Login
        </a>
        <a v-else href="#" @click.prevent="showLogoutModal = true" style="display: inline-flex; align-items: center; gap: 4px;">
          <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
          Logout
        </a>
      </div>
    </div>

    <!-- Logout Modal -->
    <div v-if="showLogoutModal" class="modal-overlay" @click.self="showLogoutModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>Logout Confirmation</h3>
        </div>
        <div class="modal-body">
          <p style="margin: 0; color: #334155;">Are you sure you want to log out of your session?</p>
        </div>
        <div class="modal-footer" style="margin-top: 1rem;">
          <button class="cancel-btn" @click="showLogoutModal = false">Cancel</button>
          <button class="generate-btn danger" style="background: #dc2626; color: white; display:flex; align-items:center; gap:8px;" :disabled="isLoggingOut" @click="confirmLogout">
            <svg v-if="isLoggingOut" class="spinner-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
            {{ isLoggingOut ? 'Logging out...' : 'Log Out' }}
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.profile-btn {
  background: none;
  border: 2px solid #cbd5e1;
  cursor: pointer;
  color: #64748b;
  padding: 6px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.profile-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
  border-color: #94a3b8;
}
.profile-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  min-width: 160px;
  display: flex;
  flex-direction: column;
  padding: 4px;
  z-index: 50;
  animation: dropdownFade 0.15s ease-out;
}
.profile-dropdown a {
  padding: 8px 12px;
  color: #334155 !important;
  text-decoration: none !important;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.15s;
  border: none !important;
  border-bottom: none !important;
  border-radius: 6px !important;
}
.profile-dropdown a:hover {
  background: #f1f5f9;
  border: none !important;
  border-bottom: none !important;
}
@keyframes dropdownFade {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Docs dropdown button — same look as nav links */
.docs-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: inherit;
  font-weight: 500;
  color: #475569;
  padding: 0;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  transition: color 0.2s;
  font-family: inherit;
}
.docs-btn:hover { color: #0f172a; }
.docs-dropdown { min-width: 170px; }
</style>
