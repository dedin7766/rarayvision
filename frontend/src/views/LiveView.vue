<script setup>
import { ref, nextTick, watch, onUnmounted } from 'vue'
import { store } from '../store'
import { API_BASE_URL, emotionEmoji } from '../utils'

const liveVideoEl = ref(null)
const liveCanvasEl = ref(null)
const liveStream = ref(null)
const liveActive = ref(false)
const liveLoading = ref(false)
const liveError = ref('')
const liveResult = ref(null)
const liveInterval = ref(null)
const liveFps = ref(0)
const liveFrameCount = ref(0)
const liveFpsTimer = ref(null)
const liveProcessing = ref(false)
const liveRafId = ref(null)
const targetFaceData = ref(null)
const currentFaceData = ref(null)
const liveMode = ref('identify')

const kycStages = ['smile', 'blink', 'turn_left', 'turn_right']
const kycCurrentStageIndex = ref(0)
const kycCurrentStage = ref('smile')
const kycCompleted = ref(false)
const kycMessage = ref('Silakan tersenyum / Please smile')

watch(liveMode, (newMode) => {
  if (newMode === 'kyc') {
    kycCurrentStageIndex.value = 0
    kycCurrentStage.value = kycStages[0]
    kycCompleted.value = false
    kycMessage.value = 'Silakan tersenyum / Please smile'
    liveResult.value = null
  }
})

const showRegisterModal = ref(false)
const registerUserId = ref('')
const registerUserName = ref('')
const registerLoading = ref(false)
const registerResult = ref(null)
const registerError = ref('')

let mediaPipeFaceMesh = null
const mediaPipeLoading = ref(false)

const ensureMediaPipe = async () => {
  if (mediaPipeFaceMesh) return
  mediaPipeLoading.value = true
  if (!window.FaceMesh) {
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
  }
  mediaPipeFaceMesh = new window.FaceMesh({locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
  }});
  mediaPipeFaceMesh.setOptions({
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
  });
  mediaPipeFaceMesh.onResults((results) => {
    if (liveMode.value !== 'landmark' && liveMode.value !== 'emotion' && liveMode.value !== 'identify' && liveMode.value !== 'kyc' && liveMode.value !== 'liveness_landmark' && liveMode.value !== 'liveness_identify') return
    const canvas = liveCanvasEl.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
      ctx.save()
      ctx.translate(canvas.width, 0)
      ctx.scale(-1, 1)
      let meshColor = '#06b6d4'
      let eyeColor = '#22d3ee'
      
      if ((liveMode.value === 'liveness_landmark' || liveMode.value === 'liveness_identify') && liveResult.value && liveResult.value.data && liveResult.value.data.is_real !== undefined) {
         if (liveResult.value.data.is_real) {
             meshColor = '#06b6d4'
             eyeColor = '#22d3ee'
         } else {
             meshColor = '#ef4444'
             eyeColor = '#f87171'
         }
      }

      for (const landmarks of results.multiFaceLandmarks) {
        window.drawConnectors(ctx, landmarks, window.FACEMESH_TESSELATION, {color: meshColor, lineWidth: 1});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_RIGHT_EYE, {color: eyeColor, lineWidth: 2});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_RIGHT_EYEBROW, {color: eyeColor, lineWidth: 2});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_LEFT_EYE, {color: eyeColor, lineWidth: 2});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_LEFT_EYEBROW, {color: eyeColor, lineWidth: 2});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_FACE_OVAL, {color: eyeColor, lineWidth: 2});
        window.drawConnectors(ctx, landmarks, window.FACEMESH_LIPS, {color: eyeColor, lineWidth: 2});
      }
      ctx.restore()
      ctx.font = 'bold 16px Inter, sans-serif'
      let badgeText = 'Google MediaPipe 468-Mesh'
      let bgColor = 'rgba(6,182,212,0.85)'
      if (liveMode.value === 'liveness_landmark' || liveMode.value === 'liveness_identify') {
        if (liveResult.value && liveResult.value.data && liveResult.value.data.liveness_score !== undefined) {
           if (liveResult.value.data.is_real) {
               if (liveMode.value === 'liveness_identify') {
                   if (liveResult.value.match) {
                       bgColor = 'rgba(22,163,74,0.85)'
                       badgeText = `Real | ${liveResult.value.data.name || liveResult.value.data.id} ${(liveResult.value.data.similarity * 100).toFixed(1)}%`
                   } else {
                       bgColor = 'rgba(217,119,6,0.85)'
                       badgeText = `Real | Unknown Face`
                   }
               } else {
                   bgColor = 'rgba(6,182,212,0.85)'
                   badgeText = `Real ${(liveResult.value.data.liveness_score * 100).toFixed(1)}%`
               }
           } else {
               bgColor = 'rgba(239,68,68,0.85)'
               badgeText = `Spoof! ${(liveResult.value.data.liveness_score * 100).toFixed(1)}%`
           }
        } else {
           bgColor = 'rgba(100,116,139,0.85)'
           badgeText = 'Analyzing...'
        }
      } else if (liveMode.value === 'emotion') {
        const emoStr = (liveResult.value && liveResult.value.data && liveResult.value.data.emotion) ? liveResult.value.data.emotion : 'Unknown'
        const emoEmoji = emoStr === 'Happy' ? '😊' : emoStr === 'Sad' ? '😢' : emoStr === 'Angry' ? '😠' : emoStr === 'Surprise' ? '😲' : emoStr === 'Fear' ? '😨' : emoStr === 'Disgust' ? '🤢' : '😐'
        bgColor = 'rgba(168,85,247,0.85)'
        badgeText = `${emoEmoji} ${emoStr}`
        if (liveResult.value && liveResult.value.data) {
           if (liveResult.value.data.mask) badgeText += ' 😷 Mask'
           if (liveResult.value.data.glasses) badgeText += ' 👓 Glasses'
        }
      } else if (liveMode.value === 'kyc') {
        bgColor = kycCompleted.value ? 'rgba(22,163,74,0.85)' : 'rgba(217,119,6,0.85)'
        badgeText = kycMessage.value
        
        if (!kycCompleted.value && results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
          const landmarks = results.multiFaceLandmarks[0]
          const dist = (p1, p2) => Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2))
          const stage = kycCurrentStage.value
          let passed = false
          
          if (stage === 'smile') {
            const mouthWidth = dist(landmarks[61], landmarks[291])
            const mouthHeight = dist(landmarks[13], landmarks[14])
            if (mouthWidth > 0.08 && mouthHeight > 0.015) passed = true
          } else if (stage === 'blink') {
            const leftEyeH = dist(landmarks[159], landmarks[145])
            const rightEyeH = dist(landmarks[386], landmarks[374])
            if (leftEyeH < 0.01 && rightEyeH < 0.01) passed = true
          } else if (stage === 'turn_left') {
            const leftDist = dist(landmarks[1], landmarks[234])
            const rightDist = dist(landmarks[1], landmarks[454])
            if (rightDist < leftDist * 0.5) passed = true
          } else if (stage === 'turn_right') {
            const leftDist = dist(landmarks[1], landmarks[234])
            const rightDist = dist(landmarks[1], landmarks[454])
            if (leftDist < rightDist * 0.5) passed = true
          }

          if (passed) {
            kycCurrentStageIndex.value++
            if (kycCurrentStageIndex.value >= kycStages.length) {
              kycCompleted.value = true
              kycMessage.value = 'KYC Lulus! Memverifikasi...'
            } else {
              kycCurrentStage.value = kycStages[kycCurrentStageIndex.value]
              if (kycCurrentStage.value === 'blink') kycMessage.value = 'Silakan berkedip / Please blink'
              else if (kycCurrentStage.value === 'turn_left') kycMessage.value = 'Tengok ke kiri / Turn left'
              else if (kycCurrentStage.value === 'turn_right') kycMessage.value = 'Tengok ke kanan / Turn right'
            }
          }
        }
      } else if (liveResult.value && liveResult.value.status === 'success') {
        if (liveResult.value.match) {
          bgColor = 'rgba(22,163,74,0.85)'
          badgeText = `✓ ${liveResult.value.data.name || liveResult.value.data.id} ${(liveResult.value.data.similarity * 100).toFixed(1)}%`
        } else {
          bgColor = 'rgba(217,119,6,0.85)'
          badgeText = '? Unknown Face'
        }
      }
      const textW = ctx.measureText(badgeText).width
      const badgeW = textW + 24
      const badgeH = 32
      const badgeX = (canvas.width / 2) - (badgeW / 2)
      const badgeY = 16
      ctx.fillStyle = bgColor
      ctx.beginPath()
      ctx.roundRect(badgeX, badgeY, badgeW, badgeH, 6)
      ctx.fill()
      ctx.fillStyle = '#fff'
      ctx.textAlign = 'center'
      ctx.fillText(badgeText, canvas.width / 2, badgeY + 22)
      ctx.textAlign = 'left'
    } else {
      ctx.fillStyle = 'rgba(239,68,68,0.75)'
      ctx.fillRect(8, 8, canvas.width - 16, 36)
      ctx.fillStyle = '#fff'
      ctx.font = 'bold 16px Inter, sans-serif'
      ctx.fillText('No face detected', 18, 31)
    }
  });
  mediaPipeLoading.value = false
}

const startCamera = async () => {
  liveError.value = ''
  liveLoading.value = true
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
      audio: false
    })
    liveStream.value = stream
    await nextTick()
    liveVideoEl.value.srcObject = stream
    await liveVideoEl.value.play()
    liveActive.value = true
    targetFaceData.value = null
    currentFaceData.value = null
    startRenderLoop()
    startApiLoop()
    startFpsCounter()
  } catch (e) {
    liveError.value = `Camera error: ${e.message}`
  } finally {
    liveLoading.value = false
  }
}

const stopCamera = () => {
  if (liveStream.value) {
    liveStream.value.getTracks().forEach(t => t.stop())
    liveStream.value = null
  }
  cancelAnimationFrame(liveRafId.value)
  clearInterval(liveInterval.value)
  clearInterval(liveFpsTimer.value)
  liveActive.value = false
  liveResult.value = null
  liveFrameCount.value = 0
  liveFps.value = 0
  liveProcessing.value = false
  targetFaceData.value = null
  currentFaceData.value = null
  const canvas = liveCanvasEl.value
  if (canvas) {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
  }
}

const startApiLoop = () => {
  liveInterval.value = setInterval(captureAndRecognize, 150)
}

const captureAndRecognize = async () => {
  const video = liveVideoEl.value
  const canvas = liveCanvasEl.value
  if (!video || !canvas || video.readyState < 2 || liveProcessing.value) return
  if (liveMode.value === 'kyc' && !kycCompleted.value) return
  
  liveProcessing.value = true
  const offscreen = document.createElement('canvas')
  offscreen.width = video.videoWidth
  offscreen.height = video.videoHeight
  offscreen.getContext('2d').drawImage(video, 0, 0)
  offscreen.toBlob(async (blob) => {
    if (!blob) { liveProcessing.value = false; return }
    try {
      const fd = new FormData()
      fd.append('file', blob, 'frame.jpg')
      const reqMode = (liveMode.value === 'kyc') ? 'identify' : (liveMode.value === 'liveness_landmark' ? 'liveness' : liveMode.value)
      fd.append('mode', reqMode)
      const token = localStorage.getItem('rarayvision-token')
      const headers = {}
      if (token) headers['Authorization'] = `Bearer ${token}`
      const endpoint = liveMode.value === 'identify_multi' ? '/api/v1/faces/recognize/live-multi' : '/api/v1/faces/recognize/live'
      const res = await fetch(`${API_BASE_URL}${endpoint}`, { method: 'POST', body: fd, headers })
      const data = await res.json()
      liveResult.value = data
      liveFrameCount.value++
      if (data.status === 'success') {
        if (liveMode.value === 'identify_multi') {
          targetFaceData.value = data.faces
        } else if (data.data && data.data.bbox) {
          targetFaceData.value = data.data
        } else {
          targetFaceData.value = null
          currentFaceData.value = null
        }
      } else {
        targetFaceData.value = null
        currentFaceData.value = null
      }
    } catch { /* silent */ } finally {
      liveProcessing.value = false
    }
  }, 'image/jpeg', 0.92)
}

const startRenderLoop = () => {
  let isSending = false
  const loop = async () => {
    liveRafId.value = requestAnimationFrame(loop)
    if (liveMode.value === 'landmark' || liveMode.value === 'emotion' || liveMode.value === 'identify' || liveMode.value === 'kyc' || liveMode.value === 'liveness_landmark' || liveMode.value === 'liveness_identify') {
      if (!window.FaceMesh && !mediaPipeLoading.value) {
        ensureMediaPipe()
      } else if (mediaPipeFaceMesh && !mediaPipeLoading.value && !isSending) {
        const video = liveVideoEl.value
        if (video && video.readyState >= 2) {
          if (liveCanvasEl.value && liveCanvasEl.value.width !== video.videoWidth) {
            liveCanvasEl.value.width = video.videoWidth
            liveCanvasEl.value.height = video.videoHeight
          }
          isSending = true
          await mediaPipeFaceMesh.send({image: video}).catch(e => console.error(e))
          isSending = false
        }
      }
    } else {
      updateAndDraw()
    }
  }
  loop()
}

const updateAndDraw = () => {
  const canvas = liveCanvasEl.value
  const video = liveVideoEl.value
  if (!canvas || !video) return
  const ctx = canvas.getContext('2d')
  if (canvas.width !== video.videoWidth) {
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
  }
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  if (!targetFaceData.value) {
    if (liveResult.value && liveResult.value.status !== 'success') {
      ctx.fillStyle = 'rgba(239,68,68,0.75)'
      ctx.fillRect(8, 8, canvas.width - 16, 36)
      ctx.fillStyle = '#fff'
      ctx.font = 'bold 16px Inter, sans-serif'
      ctx.fillText(liveResult.value.message || 'No face detected', 18, 31)
    }
    return
  }
  if (liveMode.value === 'identify_multi') {
    currentFaceData.value = targetFaceData.value
    if (Array.isArray(currentFaceData.value)) {
      for (const face of currentFaceData.value) {
        drawOverlay(ctx, canvas, { ...liveResult.value, mode: 'identify', data: face.data, match: face.match })
      }
    }
    return
  }
  if (!currentFaceData.value) {
    currentFaceData.value = JSON.parse(JSON.stringify(targetFaceData.value))
  } else {
    for (let i = 0; i < 4; i++) {
      currentFaceData.value.bbox[i] += (targetFaceData.value.bbox[i] - currentFaceData.value.bbox[i]) * 0.35
    }
    if (targetFaceData.value.landmarks && currentFaceData.value.landmarks) {
      for (let i = 0; i < targetFaceData.value.landmarks.length; i++) {
        currentFaceData.value.landmarks[i][0] += (targetFaceData.value.landmarks[i][0] - currentFaceData.value.landmarks[i][0]) * 0.35
        currentFaceData.value.landmarks[i][1] += (targetFaceData.value.landmarks[i][1] - currentFaceData.value.landmarks[i][1]) * 0.35
      }
    }
    currentFaceData.value.liveness_score = targetFaceData.value.liveness_score
    currentFaceData.value.is_real = targetFaceData.value.is_real
    currentFaceData.value.similarity = targetFaceData.value.similarity
    currentFaceData.value.id = targetFaceData.value.id
    currentFaceData.value.name = targetFaceData.value.name
    currentFaceData.value.age = targetFaceData.value.age
    currentFaceData.value.gender = targetFaceData.value.gender
    currentFaceData.value.emotion = targetFaceData.value.emotion
    currentFaceData.value.mask = targetFaceData.value.mask
    currentFaceData.value.glasses = targetFaceData.value.glasses
  }
  drawOverlay(ctx, canvas, { ...liveResult.value, data: currentFaceData.value })
}

const drawOverlay = (ctx, canvas, data) => {
  const faceData = data.data
  if (!faceData || !faceData.bbox) return
  const bbox = faceData.bbox
  const landmarks = faceData.landmarks
  const w = bbox[2] - bbox[0]
  const h = bbox[3] - bbox[1]
  const x1 = canvas.width - bbox[2]
  const y1 = bbox[1]
  let color = '#22c55e'
  let bgColor = 'rgba(22,163,74,0.85)'
  let badgeText = ''
  if (data.mode === 'analyze') {
    color = '#3b82f6'; bgColor = 'rgba(59,130,246,0.85)'
    badgeText = `${faceData.gender}, ${faceData.age} yo`
  } else if (data.mode === 'liveness') {
    if (faceData.is_real) {
      color = '#22c55e'; bgColor = 'rgba(22,163,74,0.85)'
      badgeText = `Real ${(faceData.liveness_score * 100).toFixed(1)}%`
    } else {
      color = '#ef4444'; bgColor = 'rgba(239,68,68,0.85)'
      badgeText = `Spoof! ${(faceData.liveness_score * 100).toFixed(1)}%`
    }
  } else if (data.mode === 'emotion') {
    color = '#a855f7'; bgColor = 'rgba(168,85,247,0.85)'
    const emoStr = faceData.emotion || 'Unknown'
    badgeText = `${emotionEmoji(emoStr)} ${emoStr}`
  } else if (data.mode === 'attributes') {
    color = '#ec4899'; bgColor = 'rgba(236,72,153,0.85)'
    const maskStr = faceData.mask ? 'Mask' : 'No Mask'
    const glassStr = faceData.glasses ? 'Glasses' : 'No Glasses'
    badgeText = `${maskStr}, ${glassStr}`
  } else if (data.mode === 'landmark') {
    color = '#06b6d4'; bgColor = 'rgba(6,182,212,0.85)'
    badgeText = 'Sci-Fi Topology'
  } else {
    if (data.match) {
      color = '#22c55e'; bgColor = 'rgba(22,163,74,0.85)'
      badgeText = `✓ ${faceData.name || faceData.id} ${(faceData.similarity * 100).toFixed(1)}%`
    } else {
      color = '#f59e0b'; bgColor = 'rgba(217,119,6,0.85)'
      badgeText = '? Unknown Face'
    }
  }
  ctx.lineWidth = 3
  ctx.strokeStyle = color
  ctx.shadowColor = color
  ctx.shadowBlur = 10
  const cl = 20
  ctx.beginPath()
  ctx.moveTo(x1, y1 + cl); ctx.lineTo(x1, y1); ctx.lineTo(x1 + cl, y1)
  ctx.moveTo(x1 + w - cl, y1); ctx.lineTo(x1 + w, y1); ctx.lineTo(x1 + w, y1 + cl)
  ctx.moveTo(x1 + w, y1 + h - cl); ctx.lineTo(x1 + w, y1 + h); ctx.lineTo(x1 + w - cl, y1 + h)
  ctx.moveTo(x1 + cl, y1 + h); ctx.lineTo(x1, y1 + h); ctx.lineTo(x1, y1 + h - cl)
  ctx.stroke()
  ctx.shadowBlur = 0
  if (landmarks) {
    ctx.fillStyle = color
    landmarks.forEach(point => {
      const px = canvas.width - point[0]
      const py = point[1]
      ctx.beginPath()
      ctx.arc(px, py, 3, 0, 2 * Math.PI)
      ctx.fill()
    })
  }
  ctx.font = 'bold 16px Inter, sans-serif'
  const textW = ctx.measureText(badgeText).width
  const badgeW = textW + 24
  const badgeH = 32
  const badgeX = x1 + (w / 2) - (badgeW / 2)
  const badgeY = Math.max(8, y1 - badgeH - 10)
  ctx.fillStyle = bgColor
  ctx.beginPath()
  ctx.roundRect(badgeX, badgeY, badgeW, badgeH, 6)
  ctx.fill()
  ctx.fillStyle = '#fff'
  ctx.textAlign = 'center'
  ctx.fillText(badgeText, x1 + (w / 2), badgeY + 22)
  ctx.textAlign = 'left'
}

const startFpsCounter = () => {
  liveFpsTimer.value = setInterval(() => {
    liveFps.value = liveFrameCount.value
    liveFrameCount.value = 0
  }, 1000)
}

const openRegisterModal = () => {
  registerUserId.value = ''
  registerUserName.value = ''
  registerResult.value = null
  registerError.value = ''
  showRegisterModal.value = true
}

const closeRegisterModal = () => { showRegisterModal.value = false }

const registerFromCamera = async () => {
  const video = liveVideoEl.value
  if (!video || video.readyState < 2) { registerError.value = 'Kamera belum siap.'; return }
  registerLoading.value = true
  registerError.value = ''
  registerResult.value = null
  const offscreen = document.createElement('canvas')
  offscreen.width = video.videoWidth
  offscreen.height = video.videoHeight
  offscreen.getContext('2d').drawImage(video, 0, 0)
  offscreen.toBlob(async (blob) => {
    try {
      const fd = new FormData()
      fd.append('file', blob, 'register.jpg')
      if (registerUserName.value.trim()) fd.append('user_name', registerUserName.value.trim())
      const res = await fetch(`${API_BASE_URL}/api/v1/faces/live`, { 
        method: 'POST', 
        headers: { 'Authorization': `Bearer ${localStorage.getItem('rarayvision-token')}` },
        body: fd 
      })
      const data = await res.json()
      registerResult.value = data
      if (data.status === 'success') { registerError.value = '' }
      else { registerError.value = data.message || 'Gagal register.' }
    } catch (e) {
      registerError.value = `Error: ${e.message}`
    } finally {
      registerLoading.value = false
    }
  }, 'image/jpeg', 0.9)
}

onUnmounted(() => stopCamera())
</script>

<template>
  <section class="live-page">
    <div class="live-header">
      <div>
        <p class="eyebrow">Real-time</p>
        <h2>Live Face Recognition</h2>
      </div>
      <div class="live-controls">
        <select v-model="liveMode" class="mode-select">
          <option value="identify">Identification (Single Face)</option>
          <option value="identify_multi">Multi-Face Identification</option>
          <option value="analyze">Demographics</option>
          <option value="liveness">Passive Liveness (Anti-Spoofing)</option>
          <option value="liveness_landmark">Passive Liveness (with Landmark)</option>
          <option value="liveness_identify">Passive Liveness + Recognition</option>
          <option value="emotion">Emotion Analysis</option>
          <option value="attributes">Face Attributes</option>
          <option value="kyc">Active Liveness</option>
        </select>
        <button v-if="liveActive" class="register-live-btn" @click="openRegisterModal">+ Register Face</button>
        <button v-if="!liveActive" class="start-btn" @click="startCamera" :disabled="liveLoading">
          {{ liveLoading ? 'Starting...' : 'Start Camera' }}
        </button>
        <button v-else class="stop-btn" @click="stopCamera">Stop</button>
      </div>
    </div>

    <p v-if="liveError" class="error-text">{{ liveError }}</p>

    <div class="live-layout">
      <div class="live-feed-wrap">
        <div class="live-feed" :class="{ active: liveActive }">
          <video ref="liveVideoEl" class="live-video" autoplay playsinline muted></video>
          <canvas ref="liveCanvasEl" class="live-canvas"></canvas>
          <div v-if="mediaPipeLoading" style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.5); color: white; font-size: 14px; z-index: 10; border-radius: 12px;">
            <div class="live-spinner" style="margin-right: 10px;"></div>
            Loading MediaPipe...
          </div>
          <div v-if="!liveActive && !liveLoading" class="live-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9A2.25 2.25 0 0013.5 5.25h-9A2.25 2.25 0 002.25 9v9A2.25 2.25 0 004.5 18.75z"/>
            </svg>
            <p>Click <strong>Start Camera</strong> to begin</p>
          </div>
          <div v-if="liveLoading" class="live-placeholder">
            <div class="live-spinner"></div>
            <p>Requesting camera access...</p>
          </div>
        </div>
      </div>

      <div class="live-sidebar">
        <div class="live-result-card" v-if="liveResult">
          <p class="eyebrow">Last Result</p>
          <div class="result-body">
            <div class="result-row">
              <span class="result-label">Status</span>
              <span class="result-value" :class="liveResult.status === 'success' ? 'text-green' : 'text-red'">
                {{ liveResult.status }}
              </span>
            </div>
            <div class="result-row" v-if="liveResult.message">
              <span class="result-label">Message</span>
              <span class="result-value">{{ liveResult.message }}</span>
            </div>
            
            <div class="result-divider" v-if="(liveResult.data || liveResult.faces) && liveResult.status === 'success'"></div>
            
            <template v-if="liveMode === 'identify_multi' && liveResult.faces">
                <div v-for="(face, idx) in liveResult.faces" :key="idx" style="margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #e2e8f0;">
                   <div class="result-row">
                     <span class="result-label">Face #{{ idx + 1 }}</span>
                     <span class="result-value" :class="face.match ? 'text-green' : 'text-red'">{{ face.match ? 'Matched' : 'Unknown' }}</span>
                   </div>
                   <div class="result-row" v-if="face.match">
                     <span class="result-label">Name</span>
                     <span class="result-value">{{ face.data.name }} ({{ (face.data.similarity * 100).toFixed(1) }}%)</span>
                   </div>
                </div>
            </template>
            <template v-else-if="liveResult.data && liveResult.status === 'success'">
              <div class="result-row" v-if="liveResult.mode === 'identify'">
                <span class="result-label">Match</span>
                <span class="result-value" style="display: flex; align-items: center; justify-content: flex-end; gap: 4px;">
                  <template v-if="liveResult.match">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    Yes
                  </template>
                  <template v-else>No</template>
                </span>
              </div>
              <div class="result-row" v-if="liveResult.data.id">
                <span class="result-label">User ID</span>
                <span class="result-value">{{ liveResult.data.id }}</span>
              </div>
              <div class="result-row" v-if="liveResult.data.name">
                <span class="result-label">Name</span>
                <span class="result-value">{{ liveResult.data.name }}</span>
              </div>
              <div class="result-row" v-if="liveResult.data.similarity !== undefined">
                <span class="result-label">Confidence</span>
                <span class="result-value">{{ (liveResult.data.similarity * 100).toFixed(1) }}%</span>
              </div>
              
              <div class="result-row" v-if="liveResult.data.emotion">
                <span class="result-label">Emotion</span>
                <span class="result-value">
                  {{ emotionEmoji(liveResult.data.emotion) }} {{ liveResult.data.emotion }}
                  <small>({{ (liveResult.data.emotion_score * 100).toFixed(1) }}%)</small>
                </span>
              </div>
              
              <div class="result-row" v-if="liveResult.data.age">
                <span class="result-label">Demographics</span>
                <span class="result-value">
                  {{ liveResult.data.gender }}, {{ liveResult.data.age }} yo
                </span>
              </div>
              
              <div class="result-row" v-if="liveResult.data.glasses !== undefined">
                <span class="result-label">Glasses</span>
                <span class="result-value">
                  {{ liveResult.data.glasses ? 'Yes' : 'No' }}
                </span>
              </div>

              <div class="result-row" v-if="liveResult.data.mask !== undefined">
                <span class="result-label">Mask</span>
                <span class="result-value">
                  {{ liveResult.data.mask ? 'Yes' : 'No' }}
                </span>
              </div>
              
              <div class="result-row" v-if="liveResult.data.liveness_score !== undefined">
                <span class="result-label">Liveness</span>
                <span class="result-value">
                  {{ liveResult.data.is_real ? 'Real' : 'Spoof' }}
                  <small>({{ (liveResult.data.liveness_score * 100).toFixed(1) }}%)</small>
                </span>
              </div>
            </template>
          </div>
        </div>

        <div class="live-result-card" v-if="liveMode === 'kyc'" style="margin-top: 16px; background: #f0fdfa; border-color: #5eead4;">
          <p class="eyebrow" style="color: #0d9488;">Info: Active KYC Architecture</p>
          <div class="result-body" style="background: transparent; border: none; padding: 0; margin-top: 8px; color: #0f766e; line-height: 1.5;">
            The motion detection instructions (Smile, Blink, Turn Head) run entirely in <strong>Real-time on the Client side (Browser)</strong> using Google MediaPipe. This prevents <em>lag</em> and saves server load.<br><br>
            After all challenges are completed, <strong>1 best photo frame is sent to the Backend</strong> for the final face recognition process.
          </div>
        </div>

        <div class="live-result-card" v-if="liveMode === 'liveness'" style="margin-top: 16px; background: #eff6ff; border-color: #93c5fd;">
          <p class="eyebrow" style="color: #1d4ed8;">Info: Anti-Spoofing API</p>
          <div class="result-body" style="background: transparent; border: none; padding: 0; margin-top: 8px; color: #1e40af; line-height: 1.5;">
            The Liveness API endpoint is strictly designed to capture and process live streaming data directly from the camera in real-time. It does <strong>not</strong> support POST requests containing raw uploaded image files.
          </div>
        </div>
      </div>
    </div>

    <!-- Register Modal -->
    <div v-if="showRegisterModal" class="modal-overlay" @click.self="closeRegisterModal">
      <div class="modal-panel">
        <div class="modal-header">
          <h3>Register Face from Camera</h3>
          <button class="modal-close" @click="closeRegisterModal">✕</button>
        </div>
        <div class="modal-body">
          <label>
            User Name (Optional)
            <input v-model="registerUserName" placeholder="e.g. John Doe" />
          </label>
          <p v-if="registerError" class="error-text">{{ registerError }}</p>
 <div v-if="registerResult && registerResult.status === 'success'" class="register-success">
 <div class="register-success-icon">✓</div>
 <div>
 <strong>Wajah berhasil didaftarkan!</strong>
 <p v-if="registerResult.user_name">Name: {{ registerResult.user_name }}</p>
 <p v-if="registerResult.user_id">ID: {{ registerResult.user_id }}</p>
 <p v-if="registerResult.total">Total wajah: {{ registerResult.total }}</p>
 </div>
 </div>
        </div>
        <div class="modal-footer">
          <button class="generate-btn" @click="registerFromCamera" :disabled="registerLoading">
            {{ registerLoading ? 'Registering...' : 'Capture & Register' }}
          </button>
          <button @click="closeRegisterModal">Cancel</button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.result-body {
  margin-top: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
}
.result-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.result-row:last-child {
  margin-bottom: 0;
}
.result-label {
  color: #64748b;
}
.result-value {
  font-weight: 500;
  color: #1e293b;
  text-align: right;
}
.result-value small {
  color: #94a3b8;
  font-size: 12px;
  margin-left: 4px;
}
.result-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 10px 0;
}
.text-green {
  color: #22c55e;
}
.text-red {
  color: #ef4444;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.modal-panel {
  background: #ffffff;
  border-radius: 12px;
  width: 90%;
  max-width: 420px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1e293b;
}
.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #64748b;
  padding: 4px;
}
.modal-close:hover {
  color: #ef4444;
}
.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.modal-body label {
  display: flex;
  flex-direction: column;
  font-size: 14px;
  color: #475569;
  font-weight: 500;
}
.modal-body input {
  margin-top: 8px;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 14px;
}
.modal-body input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
}
.modal-footer {
  padding: 16px 20px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.modal-footer button {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  font-size: 14px;
}
.modal-footer button:not(.generate-btn) {
  background: white;
  border: 1px solid #cbd5e1;
  color: #334155;
}
.modal-footer button:not(.generate-btn):hover {
  background: #f1f5f9;
}
.register-success {
 display: flex;
 align-items: center;
 gap: 12px;
 background: #f0fdf4;
 border: 1px solid #bbf7d0;
 border-radius: 8px;
 padding: 12px 14px;
 color: #15803d;
 font-size: 13px;
}
.register-success strong {
 display: block;
 font-size: 14px;
 margin-bottom: 2px;
}
.register-success p {
 margin: 2px 0 0;
 color: #166534;
}
.register-success-icon {
 font-size: 22px;
 font-weight: 700;
 color: #22c55e;
 line-height: 1;
}
</style>
