import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

import vue3GoogleLogin from 'vue3-google-login'

const app = createApp(App)

app.use(router)
app.use(vue3GoogleLogin, {
  clientId: '282777297757-tmh830klh32ve5j1lm7h9357m7othvoc.apps.googleusercontent.com'
})

app.mount('#app')
