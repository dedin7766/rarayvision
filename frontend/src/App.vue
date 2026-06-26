<script setup>
import { onMounted } from 'vue'
import { store } from './store'
import { authService } from './services/authService'
import { apiKeyService } from './services/apiKeyService'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'

onMounted(async () => {
  authService.checkHealth()
  if (store.isLoggedIn) {
    await authService.fetchMe()
    await apiKeyService.fetch()
  }
})
</script>

<template>
  <div class="app-shell">
    <AppHeader v-if="$route.path !== '/login'" />
    <main class="content">
      <RouterView />
    </main>
    <AppFooter v-if="['/', '/dashboard'].includes($route.path)" />
    
    <RouterLink 
      v-if="$route.path !== '/login' && $route.path !== '/chat'" 
      to="/chat" 
      class="ai-fab"
      title="Ask AI Assistant"
    >
      <div class="ai-fab-icon">🤖</div>
    </RouterLink>
  </div>
</template>
