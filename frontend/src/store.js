import { reactive } from 'vue'

const initialToken = localStorage.getItem('rarayvision-token')

export const store = reactive({
 isLoggedIn: !!initialToken,
 user: null,
 apiKeys: [],
 loginError: '',
 apiStatus: 'Checking...',
 apiStatusDetail: '',
 isChecking: true,

 logout() {
 localStorage.removeItem('rarayvision-token')
 this.isLoggedIn = false
 this.user = null
 this.apiKeys = []
 }
})
