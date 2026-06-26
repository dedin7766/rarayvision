<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { API_BASE_URL } from '../utils'

const videoEl = ref(null)
const canvasEl = ref(null)
const stream = ref(null)
const isCameraActive = ref(false)
const isLoading = ref(false)
const registerStatus = ref(null)
const registerError = ref('')
const hasRegisteredFace = ref(false)
const isCheckingStatus = ref(true)

// Profile / Edit Name
const userName = ref('')
const userEmail = ref('')
const isEditingName = ref(false)
const editNameValue = ref('')
const isSavingName = ref(false)
const nameSuccess = ref('')
const nameError = ref('')

// Password
const isEditingPassword = ref(false)
const currentPasswordValue = ref('')
const newPasswordValue = ref('')
const confirmPasswordValue = ref('')
const isSavingPassword = ref(false)
const passwordSuccess = ref('')
const passwordError = ref('')
const hasPassword = ref(true)

let mediaPipeFaceMesh = null
const mediaPipeLoading = ref(false)
const hasMediaPipeFace = ref(false)
const faceRafId = ref(null)

const authHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem('rarayvision-token')}`
})

const fetchProfile = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, { headers: authHeaders() })
    const data = await res.json()
    if (res.ok && data.status === 'success') {
      userName.value = data.user.name || ''
      userEmail.value = data.user.email || ''
      hasPassword.value = data.user.has_password
    }
  } catch (e) {
    console.error('Failed to fetch profile', e)
  }
}

const startEditName = () => {
  editNameValue.value = userName.value
  isEditingName.value = true
  nameSuccess.value = ''
  nameError.value = ''
}

const cancelEditName = () => {
  isEditingName.value = false
  nameError.value = ''
}

const saveName = async () => {
  if (!editNameValue.value.trim()) {
    nameError.value = 'Name cannot be empty.'
    return
  }
  isSavingName.value = true
  nameError.value = ''
  nameSuccess.value = ''
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/update-profile`, {
      method: 'PUT',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: editNameValue.value.trim() })
    })
    const data = await res.json()
    if (res.ok && data.status === 'success') {
      userName.value = data.user.name
      isEditingName.value = false
      nameSuccess.value = 'Name updated successfully!'
      setTimeout(() => { nameSuccess.value = '' }, 3000)
    } else {
      nameError.value = data.detail || 'Failed to update name.'
    }
  } catch (e) {
    nameError.value = `Error: ${e.message}`
  } finally {
    isSavingName.value = false
  }
}

const startEditPassword = () => {
  currentPasswordValue.value = ''
  newPasswordValue.value = ''
  confirmPasswordValue.value = ''
  isEditingPassword.value = true
  passwordSuccess.value = ''
  passwordError.value = ''
}

const cancelEditPassword = () => {
  isEditingPassword.value = false
  passwordError.value = ''
}

const savePassword = async () => {
  if (newPasswordValue.value !== confirmPasswordValue.value) {
    passwordError.value = 'New passwords do not match.'
    return
  }
  if (newPasswordValue.value.length < 6) {
    passwordError.value = 'Password must be at least 6 characters.'
    return
  }
  
  isSavingPassword.value = true
  passwordError.value = ''
  passwordSuccess.value = ''
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/update-password`, {
      method: 'PUT',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        current_password: hasPassword.value ? currentPasswordValue.value : null, 
        new_password: newPasswordValue.value 
      })
    })
    const data = await res.json()
    if (res.ok && data.status === 'success') {
      hasPassword.value = true
      isEditingPassword.value = false
      passwordSuccess.value = 'Password updated successfully!'
      setTimeout(() => { passwordSuccess.value = '' }, 3000)
    } else {
      passwordError.value = data.detail || 'Failed to update password.'
    }
  } catch (e) {
    passwordError.value = `Error: ${e.message}`
  } finally {
    isSavingPassword.value = false
  }
}

const checkRegistrationStatus = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/list-faces`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('rarayvision-token')}` }
    })
    const data = await res.json()
    if (res.ok && data.status === 'success') {
      const faces = data.faces || []
      const loginFace = faces.find(f => f.name === 'Face Login Profile')
      if (loginFace) {
        hasRegisteredFace.value = true
      }
    }
  } catch (e) {
    console.error('Failed to check face status', e)
  } finally {
    isCheckingStatus.value = false
  }
}

onMounted(() => {
  fetchProfile()
  checkRegistrationStatus()
})

const startCamera = async () => {
  registerError.value = ''
  isLoading.value = true
  try {
    const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false })
    stream.value = s
    isCameraActive.value = true
    await nextTick()
    videoEl.value.srcObject = s
    await videoEl.value.play()
    
    startMediaPipeLoop()
  } catch (e) {
    registerError.value = `Camera error: ${e.message}`
  } finally {
    isLoading.value = false
  }
}

const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(t => t.stop())
    stream.value = null
  }
  cancelAnimationFrame(faceRafId.value)
  isCameraActive.value = false
  hasMediaPipeFace.value = false
  const canvas = canvasEl.value
  if (canvas) {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
  }
}

const ensureMediaPipe = async () => {
  if (window.FaceMesh) return
  mediaPipeLoading.value = true
  await new Promise((resolve) => {
    const s1 = document.createElement('script')
    s1.src = 'https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js'
    document.head.appendChild(s1)
    s1.onload = () => {
      const s2 = document.createElement('script')
      s2.src = 'https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/face_mesh.js'
      document.head.appendChild(s2)
      s2.onload = () => {
        const s3 = document.createElement('script')
        s3.src = 'https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js'
        document.head.appendChild(s3)
        s3.onload = resolve
      }
    }
  })
  mediaPipeFaceMesh = new window.FaceMesh({locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
  }});
  mediaPipeFaceMesh.setOptions({ maxNumFaces: 1, refineLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 });
  mediaPipeFaceMesh.onResults((results) => {
    const canvas = canvasEl.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
      hasMediaPipeFace.value = true
      ctx.save()
      ctx.translate(canvas.width, 0)
      ctx.scale(-1, 1)
      for (const landmarks of results.multiFaceLandmarks) {
        window.drawConnectors(ctx, landmarks, window.FACEMESH_TESSELATION, {color: '#06b6d4', lineWidth: 1});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_RIGHT_EYE, {color: '#22d3ee', lineWidth: 2});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_RIGHT_EYEBROW, {color: '#22d3ee', lineWidth: 2});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_LEFT_EYE, {color: '#22d3ee', lineWidth: 2});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_LEFT_EYEBROW, {color: '#22d3ee', lineWidth: 2});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_FACE_OVAL, {color: '#22d3ee', lineWidth: 2});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_LIPS, {color: '#22d3ee', lineWidth: 2});
      }
      ctx.restore()
      ctx.font = 'bold 14px Inter, sans-serif'
      const badgeText = 'Google MediaPipe 468-Mesh'
      const textW = ctx.measureText(badgeText).width
      const badgeW = textW + 20
      const badgeH = 26
      const badgeX = (canvas.width / 2) - (badgeW / 2)
      const badgeY = 10
      ctx.fillStyle = 'rgba(6,182,212,0.85)'
      ctx.beginPath()
      ctx.roundRect(badgeX, badgeY, badgeW, badgeH, 4)
      ctx.fill()
      ctx.fillStyle = '#fff'
      ctx.textAlign = 'center'
      ctx.fillText(badgeText, canvas.width / 2, badgeY + 18)
      ctx.textAlign = 'left'
    } else {
      hasMediaPipeFace.value = false
    }
  });
  mediaPipeLoading.value = false
}

const startMediaPipeLoop = () => {
  let isSending = false
  const loop = async () => {
    faceRafId.value = requestAnimationFrame(loop)
    if (!isCameraActive.value) return
    if (!window.FaceMesh && !mediaPipeLoading.value) {
      ensureMediaPipe()
    } else if (mediaPipeFaceMesh && !mediaPipeLoading.value && !isSending) {
      const video = videoEl.value
      if (video && video.readyState >= 2) {
        if (canvasEl.value && canvasEl.value.width !== video.videoWidth) {
          canvasEl.value.width = video.videoWidth
          canvasEl.value.height = video.videoHeight
        }
        isSending = true
        await mediaPipeFaceMesh.send({image: video}).catch(e => console.error(e))
        isSending = false
      }
    }
  }
  loop()
}

const registerFace = async () => {
  if (!hasMediaPipeFace.value) return
  const video = videoEl.value
  if (!video || video.readyState < 2) return
  isLoading.value = true
  registerError.value = ''
  registerStatus.value = null

  const offscreen = document.createElement('canvas')
  offscreen.width = video.videoWidth
  offscreen.height = video.videoHeight
  offscreen.getContext('2d').drawImage(video, 0, 0)
  
  offscreen.toBlob(async (blob) => {
    try {
      const fd = new FormData()
      fd.append('file', blob, 'login_face.jpg')
      
      const res = await fetch(`${API_BASE_URL}/api/v1/register-login-face`, { 
        method: 'POST', 
        headers: { 'Authorization': `Bearer ${localStorage.getItem('rarayvision-token')}` },
        body: fd 
      })
      const data = await res.json()

      if (res.ok && data.status === 'success') {
          registerStatus.value = hasRegisteredFace.value ? 'Face updated successfully! You can now log in using your new face.' : 'Face registered successfully! You can now log in using your face.'
          hasRegisteredFace.value = true
      } else {
          registerError.value = data.message || 'Failed to process face registration.'
      }
    } catch (e) {
      registerError.value = `Error: ${e.message}`
    } finally {
      isLoading.value = false
      stopCamera()
    }
  }, 'image/jpeg', 0.9)
}

onUnmounted(() => {
  stopCamera()
})
</script>

<template>
  <section class="dashboard-page">
    <div class="dashboard-header">
      <div>
        <p class="eyebrow">Account</p>
        <h2>Settings</h2>
      </div>
    </div>

    <!-- Profile Card -->
    <div class="card" style="margin-top: 24px;">
      <h3 style="margin-bottom: 16px;">Profile</h3>
      
      <div class="profile-field">
        <label class="field-label">Email</label>
        <p class="field-value">{{ userEmail }}</p>
      </div>

      <div class="profile-field">
        <label class="field-label">Name</label>
        <div v-if="!isEditingName" class="field-row">
          <p class="field-value">{{ userName || '—' }}</p>
          <button class="edit-btn" @click="startEditName">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
            Edit
          </button>
        </div>
        <div v-else class="edit-name-form">
          <input
            v-model="editNameValue"
            type="text"
            placeholder="Enter your name"
            class="name-input"
            @keyup.enter="saveName"
          />
          <div class="edit-name-actions">
            <button class="primary-btn save-name-btn" @click="saveName" :disabled="isSavingName">
              {{ isSavingName ? 'Saving...' : 'Save' }}
            </button>
            <button class="cancel-name-btn" @click="cancelEditName">Cancel</button>
          </div>
        </div>
        <p v-if="nameError" class="inline-error">{{ nameError }}</p>
      </div>

      <div v-if="nameSuccess" class="inline-success">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
        {{ nameSuccess }}
      </div>
      
      <div class="profile-field" style="margin-top: 24px;">
        <label class="field-label">Password</label>
        <div v-if="!isEditingPassword" class="field-row">
          <p class="field-value">{{ hasPassword ? '••••••••' : 'No password set (Google Login)' }}</p>
          <button class="edit-btn" @click="startEditPassword">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
            {{ hasPassword ? 'Change' : 'Set Password' }}
          </button>
        </div>
        <div v-else class="edit-name-form">
          <input
            v-if="hasPassword"
            v-model="currentPasswordValue"
            type="password"
            placeholder="Current Password"
            class="name-input"
          />
          <input
            v-model="newPasswordValue"
            type="password"
            placeholder="New Password"
            class="name-input"
          />
          <input
            v-model="confirmPasswordValue"
            type="password"
            placeholder="Confirm New Password"
            class="name-input"
            @keyup.enter="savePassword"
          />
          <div class="edit-name-actions" style="margin-top: 4px;">
            <button class="primary-btn save-name-btn" @click="savePassword" :disabled="isSavingPassword">
              {{ isSavingPassword ? 'Saving...' : 'Save' }}
            </button>
            <button class="cancel-name-btn" @click="cancelEditPassword">Cancel</button>
          </div>
        </div>
        <p v-if="passwordError" class="inline-error">{{ passwordError }}</p>
      </div>

      <div v-if="passwordSuccess" class="inline-success">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
        {{ passwordSuccess }}
      </div>
    </div>
    
    <div class="card" style="margin-top: 16px;">
      <h3 style="margin-bottom: 16px;">Face Login Settings</h3>
      <div v-if="isCheckingStatus" style="color: #64748b; font-size: 14px;">Loading settings...</div>
      <template v-else>
        <div v-if="hasRegisteredFace" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background: #dbeafe; color: #2563eb; display: flex; align-items: center; justify-content: center;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            </div>
            <div>
              <p style="margin: 0; font-weight: 600; color: #0f172a;">Face Login is Active</p>
              <p style="margin: 0; font-size: 13px; color: #64748b;">You can use your face to sign in.</p>
            </div>
          </div>
        </div>
        <p v-else style="color: #64748b; margin-bottom: 24px; font-size: 14px;">Register your face to enable passwordless login into your workspace.</p>
        
        <div v-if="!isCameraActive && !registerStatus" style="display: flex; gap: 16px;">
          <button class="primary-btn" @click="startCamera" :disabled="isLoading">
            {{ isLoading ? 'Starting camera...' : (hasRegisteredFace ? 'Update Face Login' : 'Setup Face Login') }}
          </button>
        </div>

        <div v-if="registerStatus" class="success-banner" style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 16px; border-radius: 8px; color: #166534; margin-bottom: 16px;">
          <div style="font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            Success
          </div>
          {{ registerStatus }}
          <div style="margin-top: 12px;">
              <button class="secondary-btn" @click="registerStatus = null" style="background: white; border: 1px solid #cbd5e1; padding: 6px 12px; border-radius: 6px; cursor: pointer;">Close</button>
          </div>
        </div>

        <div v-if="registerError" class="error-banner" style="color: #dc2626; margin-bottom: 16px;">
          {{ registerError }}
        </div>
        
        <div v-if="isCameraActive" style="width: 100%; max-width: 400px;">
          <div style="position: relative; aspect-ratio: 4/3; background: #0f172a; border-radius: 8px; overflow: hidden; margin-bottom: 16px;">
            <video ref="videoEl" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1);" autoplay playsinline muted></video>
            <canvas ref="canvasEl" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></canvas>
            <div v-if="mediaPipeLoading" style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.5); color: white; font-size: 14px;">Loading MediaPipe...</div>
            <div v-else-if="!hasMediaPipeFace" style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); color: white; font-size: 14px;">
              <svg class="spinner-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
              Detecting Face...
            </div>
          </div>
          <div style="display: flex; gap: 12px;">
            <button class="primary-btn" @click="registerFace" :disabled="isLoading || !hasMediaPipeFace" style="flex: 1;" :style="{ opacity: (!hasMediaPipeFace || isLoading) ? 0.7 : 1 }">
              {{ isLoading ? 'Processing...' : 'Capture & Register' }}
            </button>
            <button class="secondary-btn" @click="stopCamera" style="padding: 8px 16px; border: 1px solid #cbd5e1; background: white; border-radius: 6px; cursor: pointer;">
              Cancel
            </button>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<style scoped>
.dashboard-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}
.dashboard-header h2 {
  font-size: 32px;
  letter-spacing: -0.02em;
  margin: 8px 0;
  color: #0f172a;
}
.eyebrow {
  color: #6366f1; /* Purple like About page */
  font-weight: 600;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}
.card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.primary-btn {
  background: #0f172a; /* Black background */
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.primary-btn:hover {
  background: #1e293b;
}
.primary-btn:disabled {
  cursor: not-allowed;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.spinner-icon {
  animation: spin 1s linear infinite;
}

/* Profile Edit Name */
.profile-field {
  margin-bottom: 16px;
}
.field-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #94a3b8;
  margin-bottom: 4px;
}
.field-value {
  margin: 0;
  font-size: 15px;
  color: #0f172a;
  font-weight: 500;
}
.field-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.edit-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 13px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}
.edit-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}
.edit-name-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 360px;
}
.name-input {
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 14px;
  color: #0f172a;
  background: #fff;
  outline: none;
  transition: border-color 0.15s;
}
.name-input:focus {
  border-color: #94a3b8;
}
.edit-name-actions {
  display: flex;
  gap: 8px;
}
.save-name-btn {
  padding: 6px 16px !important;
  font-size: 13px;
}
.cancel-name-btn {
  background: none;
  border: 1px solid #e2e8f0;
  color: #64748b;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.cancel-name-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}
.inline-error {
  margin: 6px 0 0;
  font-size: 13px;
  color: #dc2626;
}
.inline-success {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #16a34a;
  font-weight: 500;
  margin-top: 4px;
}
</style>
