<script setup>
import { onMounted } from 'vue'
import { store } from './store'
import { authService } from './services/authService'
import { apiKeyService } from './services/apiKeyService'
import AppHeader from './components/AppHeader.vue'

onMounted(async () => {
  authService.checkHealth()
  if (store.isLoggedIn) {
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
  </div>
</template>
