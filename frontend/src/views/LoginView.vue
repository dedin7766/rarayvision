<script setup>
import { ref, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { store } from '../store'
import { authService } from '../services/authService'
import { apiKeyService } from '../services/apiKeyService'
import logoImage from '../assets/logo.png'

const router = useRouter()
const isRegistering = ref(false)
const email = ref('')
const name = ref('')
const password = ref('')
const loginError = ref('')
const isLoading = ref(false)

const showFaceLogin = ref(false)
const faceVideoEl = ref(null)
const faceCanvasEl = ref(null)
const faceStream = ref(null)
const faceProcessing = ref(false)
const faceRafId = ref(null)
const faceInterval = ref(null)
const faceError = ref('')

let mediaPipeFaceMesh = null
const mediaPipeLoading = ref(false)
const hasMediaPipeFace = ref(false)

const login = async () => {
  loginError.value = ''
  isLoading.value = true
  try {
    const result = await authService.login(email.value, password.value)
    if (result.success) {
      await apiKeyService.fetch()
      router.push('/dashboard')
    } else {
      loginError.value = result.error
    }
  } catch {
    loginError.value = 'Server connection error'
  } finally {
    isLoading.value = false
  }
}

const register = async () => {
  loginError.value = ''
  isLoading.value = true
  try {
    const result = await authService.register(email.value, password.value, name.value)
    if (result.success) {
      isRegistering.value = false
      loginError.value = 'Registration successful! Please login.'
    } else {
      loginError.value = result.error
    }
  } catch {
    loginError.value = 'Server connection error'
  } finally {
    isLoading.value = false
  }
}

const startFaceLogin = async () => {
  showFaceLogin.value = true
  faceError.value = ''
  isLoading.value = true
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }, audio: false })
    faceStream.value = stream
    await nextTick()
    faceVideoEl.value.srcObject = stream
    await faceVideoEl.value.play()
    
    startMediaPipeLoop()
    faceInterval.value = setInterval(captureAndLoginFace, 1000)
  } catch (e) {
    faceError.value = `Camera error: ${e.message}`
  } finally {
    isLoading.value = false
  }
}

const stopFaceLogin = () => {
  if (faceStream.value) {
    faceStream.value.getTracks().forEach(t => t.stop())
    faceStream.value = null
  }
  cancelAnimationFrame(faceRafId.value)
  clearInterval(faceInterval.value)
  showFaceLogin.value = false
  faceProcessing.value = false
  const canvas = faceCanvasEl.value
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
    const canvas = faceCanvasEl.value
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
    if (!showFaceLogin.value) return
    if (!window.FaceMesh && !mediaPipeLoading.value) {
      ensureMediaPipe()
    } else if (mediaPipeFaceMesh && !mediaPipeLoading.value && !isSending) {
      const video = faceVideoEl.value
      if (video && video.readyState >= 2) {
        if (faceCanvasEl.value && faceCanvasEl.value.width !== video.videoWidth) {
          faceCanvasEl.value.width = video.videoWidth
          faceCanvasEl.value.height = video.videoHeight
        }
        isSending = true
        await mediaPipeFaceMesh.send({image: video}).catch(e => console.error(e))
        isSending = false
      }
    }
  }
  loop()
}

const captureAndLoginFace = async () => {
  if (!hasMediaPipeFace.value) return
  const video = faceVideoEl.value
  if (!video || video.readyState < 2 || faceProcessing.value) return
  faceProcessing.value = true
  const offscreen = document.createElement('canvas')
  offscreen.width = video.videoWidth
  offscreen.height = video.videoHeight
  offscreen.getContext('2d').drawImage(video, 0, 0)
  offscreen.toBlob(async (blob) => {
    if (!blob) { faceProcessing.value = false; return }
    try {
      const result = await authService.loginWithFace(blob)
      if (result.success) {
        stopFaceLogin()
        await apiKeyService.fetch()
        router.push('/dashboard')
      } else {
        faceError.value = result.error
      }
    } catch {
       // Ignore network errors to retry
    } finally {
      faceProcessing.value = false
    }
  }, 'image/jpeg', 0.9)
}

onUnmounted(() => {
  stopFaceLogin()
})

const loginWithGoogle = () => { alert('Google login is not connected yet.') }
</script>

<template>
  <section class="login-layout">
    <div class="login-panel" style="position: relative;">
      <button @click="router.push('/')" style="position: absolute; top: 20px; left: 20px; background: none; border: none; cursor: pointer; color: #64748b; padding: 4px; display: flex; align-items: center; justify-content: center; transition: color 0.2s;" onmouseover="this.style.color='#0f172a'" onmouseout="this.style.color='#64748b'" title="Back to Home">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
      </button>
      <div style="display:flex;flex-direction:column;align-items:center;text-align:center;margin-bottom:20px;">
        <img :src="logoImage" alt="Logo" class="brand-logo" style="margin-bottom:12px;width:48px;height:48px;" />
        <h2>{{ showFaceLogin ? 'Face Login' : (isRegistering ? 'Create your workspace' : 'Sign in to your workspace') }}</h2>
      </div>

      <div v-if="showFaceLogin" style="width: 100%; display: flex; flex-direction: column; align-items: center;">
        <div style="position: relative; width: 100%; max-width: 300px; aspect-ratio: 4/3; background: #0f172a; border-radius: 8px; overflow: hidden; margin-bottom: 16px;">
          <video ref="faceVideoEl" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1);" autoplay playsinline muted></video>
          <canvas ref="faceCanvasEl" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></canvas>
          <div v-if="mediaPipeLoading" style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.5); color: white; font-size: 14px;">Loading MediaPipe...</div>
          <div v-else-if="!hasMediaPipeFace" style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); color: white; font-size: 14px;">
            <svg class="spinner-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
            Detecting Face...
          </div>
        </div>
        <p class="error-text" v-if="faceError" style="margin-bottom: 16px;">{{ faceError }}</p>
        <p style="font-size: 14px; color: #64748b; margin-bottom: 16px; text-align: center;">Position your face in the camera to login automatically...</p>
        <button type="button" class="register-btn" @click="stopFaceLogin" style="width: 100%; margin-top: 8px;">Back to Password Login</button>
      </div>

      <template v-else>
        <form @submit.prevent="isRegistering ? register() : login()">
          <label v-if="isRegistering">
            Full Name
            <input type="text" v-model="name" required placeholder="John Doe" />
          </label>
          <label>
            Email
            <input type="email" v-model="email" required placeholder="admin@rarayvision.com" />
          </label>
          <label>
            Password
            <input type="password" v-model="password" required placeholder="••••••••" />
          </label>
          <p class="error-text" v-if="loginError">{{ loginError }}</p>
          <button type="submit" :disabled="isLoading" style="display: flex; align-items: center; justify-content: center; gap: 8px;">
            <svg v-if="isLoading" class="spinner-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
            {{ isLoading ? 'Processing...' : (isRegistering ? 'Create Account' : 'Sign In') }}
          </button>
        </form>
        <div class="divider" style="margin:20px 0;"><span>or</span></div>
        <div class="social-login">
          <button type="button" class="google-btn" @click="startFaceLogin" style="background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; justify-content: center; gap: 8px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path><circle cx="12" cy="13" r="3"></circle></svg>
            Login with Face
          </button>
          <button type="button" class="google-btn" @click="loginWithGoogle">
            <svg viewBox="0 0 24 24" class="google-icon" style="width:20px;height:20px;margin-right:8px;">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.1c-.22-.66-.35-1.36-.35-2.1s.13-1.44.35-2.1V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.84z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            Login with Google
          </button>
          <button type="button" class="register-btn" @click="isRegistering = !isRegistering">
            {{ isRegistering ? 'Back to Login' : 'Register' }}
          </button>
        </div>
      </template>
    </div>
  </section>
</template>
