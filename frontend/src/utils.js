export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:5000'
    : 'https://apirv.dfs.co.id'
)

export const formatDate = (value) => {
  if (!value) return '-'
  let dateStr = value
  if (!dateStr.endsWith('Z')) dateStr += 'Z'
  const date = new Date(dateStr)
  return date.toLocaleString('id-ID', {
    timeZone: 'Asia/Jakarta',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export const emotionEmoji = (emotion) => {
  const map = {
    'Neutral': '😐',
    'Happy': '😄',
    'Surprise': '😲',
    'Sad': '😢',
    'Angry': '😠',
    'Disgust': '🤢',
    'Fear': '😨',
    'Contempt': '😒'
  }
  return map[emotion] || '🎭'
}

export const maskedKey = (key) => {
  if (!key || key.length <= 16) return key
  return `${key.slice(0, 12)}...${key.slice(-8)}`
}

export const isKeyExpired = (item) => {
  if (!item.expiresAt) return false
  return new Date(item.expiresAt) <= new Date()
}

export const keyExpiryLabel = (item) => {
  if (!item.expiresAt) return 'Never'
  return formatDate(item.expiresAt)
}
