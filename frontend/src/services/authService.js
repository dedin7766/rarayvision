import { API_BASE_URL } from '../utils'
import { store } from '../store'

export const authService = {
  async login(email, password) {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    const data = await res.json()
    if (res.ok && data.token) {
      localStorage.setItem('rarayvision-token', data.token)
      store.isLoggedIn = true
      return { success: true }
    }
    return { success: false, error: data.detail || 'Invalid credentials' }
  },

  async register(email, password, name) {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name })
    })
    const data = await res.json()
    if (res.ok && data.status === 'success') return { success: true }
    return { success: false, error: data.detail || 'Registration failed' }
  },

  async loginWithFace(blob) {
    const formData = new FormData()
    formData.append('file', blob, 'face.jpg')
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/login-face`, {
      method: 'POST',
      body: formData
    })
    const data = await res.json()
    if (res.ok && data.status === 'success') {
      localStorage.setItem('rarayvision-token', data.token)
      store.isLoggedIn = true
      return { success: true }
    }
    return { success: false, error: data.detail || 'Face recognition failed' }
  },

  async googleLogin(credential) {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ credential })
    })
    const data = await res.json()
    if (res.ok && data.token) {
      localStorage.setItem('rarayvision-token', data.token)
      store.isLoggedIn = true
      return { success: true }
    }
    return { success: false, error: data.detail || 'Google login failed' }
  },

  async fetchMe() {
    const token = localStorage.getItem('rarayvision-token')
    if (!token) return { success: false }
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to fetch user')
      const data = await res.json()
      if (data.status === 'success') {
        store.user = data.user
        return { success: true }
      }
    } catch {
      return { success: false }
    }
  },

  async checkHealth() {
    try {
      store.isChecking = true
      const res = await fetch(`${API_BASE_URL}/`)
      if (!res.ok) throw new Error('HTTP ' + res.status)
      store.apiStatus = 'Online'
      store.apiStatusDetail = 'Raray Vision API'
    } catch {
      store.apiStatus = 'Offline'
      store.apiStatusDetail = 'Unable to connect to backend'
    } finally {
      store.isChecking = false
    }
  },

  logout() { store.logout() }
}
