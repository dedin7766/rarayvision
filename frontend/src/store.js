import { reactive } from 'vue'

const initialToken = localStorage.getItem('rarayvision-token')

export const store = reactive({
 isLoggedIn: !!initialToken,
 apiKeys: [],
 loginError: '',
 apiStatus: 'Checking...',
 apiStatusDetail: '',
 isChecking: true,

 logout() {
 localStorage.removeItem('rarayvision-token')
 this.isLoggedIn = false
 this.apiKeys = []
 }
})
