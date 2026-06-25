import { API_BASE_URL } from '../utils'
import { store } from '../store'

export const apiKeyService = {
  async fetch() {
    const token = localStorage.getItem('rarayvision-token')
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/keys`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await res.json()
      if (res.ok && data.status === 'success') {
        store.apiKeys = data.keys
      } else {
        store.logout()
      }
    } catch (err) { console.error(err) }
  },

  async generate(name = "New Key", expiresInDays = null) {
    const token = localStorage.getItem('rarayvision-token')
    if (!token) return
    try {
      const payload = { name }
      if (expiresInDays !== null) {
        payload.expires_in_days = expiresInDays
      }
      
      const res = await fetch(`${API_BASE_URL}/api/v1/keys`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (res.ok && data.status === 'success') {
        const fullKey = data.key.key
        // push a masked version to store to keep it safe
        const masked = { ...data.key, key: fullKey.substring(0,8) + '...' + fullKey.slice(-6) }
        store.apiKeys.unshift(masked)
        return data.key
      }
    } catch (e) { console.error(e) }
    return null
  },

  async revoke(id) {
    const token = localStorage.getItem('rarayvision-token')
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/keys/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) store.apiKeys = store.apiKeys.filter(k => k.id !== id)
    } catch (e) { console.error(e) }
  }
}
