<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import faceImage from '../assets/face.png'
import faceVideo from '../assets/face.mp4'
import showcaseImage from '../assets/img2.jpeg'

const router = useRouter()
const isHoveringFace = ref(false)
const heroVideo = ref(null)
const isSimulatingLoad = ref(true)

setTimeout(() => { isSimulatingLoad.value = false }, 800)

watch(isHoveringFace, (val) => {
  if (!heroVideo.value) return
  if (val) { heroVideo.value.currentTime = 0; heroVideo.value.play() }
  else { heroVideo.value.pause() }
})

const capabilities = [
  {
    title: 'Identification',
    desc: 'Recognize and verify individual identities from facial features with high-accuracy embedding matching.',
    icon: 'identification'
  },
  {
    title: 'Demographics',
    desc: 'Estimate age, gender, and ethnicity attributes from detected faces in real-time.',
    icon: 'demographics'
  },
  {
    title: 'Anti-Spoofing',
    desc: 'Detect presentation attacks including printed photos, screen replays, and 3D masks.',
    icon: 'antispoofing'
  },
  {
    title: 'Emotion Analysis',
    desc: 'Classify facial expressions into emotions like happy, sad, angry, surprised, and more.',
    icon: 'emotion'
  },
  {
    title: 'Face Attributes',
    desc: 'Extract detailed attributes such as glasses, facial hair, head pose, and eye status.',
    icon: 'attributes'
  },
  {
    title: 'Face Landmark',
    desc: 'Detect precise facial landmark points for alignment, tracking, and geometric analysis.',
    icon: 'landmark'
  }
]
</script>

<template>
  <section class="landing-page">
    <div v-if="isSimulatingLoad" class="hero-card" style="padding: 4rem 2rem;">
      <div class="hero-layout" style="display: flex; gap: 4rem;">
        <div class="hero-content" style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
          <div class="skeleton skeleton-title" style="width: 80%; height: 60px; margin-bottom: 24px;"></div>
          <div class="skeleton skeleton-text" style="width: 100%; height: 24px;"></div>
          <div class="skeleton skeleton-text" style="width: 90%; height: 24px; margin-bottom: 32px;"></div>
          <div style="display: flex; gap: 16px;">
            <div class="skeleton" style="width: 140px; height: 50px; border-radius: 8px;"></div>
            <div class="skeleton" style="width: 140px; height: 50px; border-radius: 8px;"></div>
          </div>
        </div>
        <div class="skeleton" style="width: 400px; height: 400px; border-radius: 24px;"></div>
      </div>
    </div>

    <div v-else class="hero-card">
      <div class="hero-layout">
        <div class="hero-content">
          <h2>Own your biometric infrastructure.</h2>
          <p>High-performance face recognition and computer vision API for face recognition, liveness detection, face verification, and facial analysis.</p>
          <div class="hero-actions">
            <button type="button" class="primary-cta" @click="router.push('/login')">Get API Key</button>
            <a class="secondary-cta" href="https://github.com/dedin7766/rarayvision" target="_blank">
              <svg viewBox="0 0 24 24" aria-hidden="true" style="width:20px;height:20px;margin-right:8px;fill:currentColor;">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              GitHub
            </a>
          </div>
        </div>
        <div class="hero-image" @mouseenter="isHoveringFace = true" @mouseleave="isHoveringFace = false">
          <img :src="faceImage" alt="Face recognition illustration" :class="{ 'fade-out': isHoveringFace }" />
          <video ref="heroVideo" :src="faceVideo" loop muted playsinline :class="{ 'fade-in': isHoveringFace }" />
        </div>
      </div>
    </div>

    <div v-if="isSimulatingLoad" class="feature-grid">
      <article class="feature-card skeleton" style="height: 160px;"></article>
      <article class="feature-card skeleton" style="height: 160px;"></article>
      <article class="feature-card skeleton" style="height: 160px;"></article>
      <article class="feature-card skeleton" style="height: 160px;"></article>
    </div>

    <div v-else class="feature-grid">
      <article class="feature-card">
        <h3>Face Recognition</h3>
        <p>Detect, align, extract embeddings, and recognize faces through simple REST endpoints.</p>
      </article>
      <article class="feature-card">
        <h3>Liveness Verification</h3>
        <p>Verify real face presence to reduce spoofing risk in web and mobile flows.</p>
      </article>
      <article class="feature-card">
        <h3>Face Comparison</h3>
        <p>Compare uploaded face images against enrolled identities with FastAPI-powered APIs.</p>
      </article>
      <article class="feature-card">
        <h3>Developer Friendly</h3>
        <p>OpenAPI documentation, API key management, and CPU-friendly inference support.</p>
      </article>
    </div>

    <div class="pipeline-card">
      <div><h3>Image to identity in one API workflow</h3></div>
      <div class="pipeline-steps">
        <span>Face Detection</span>
        <span>Face Alignment</span>
        <span>Embedding</span>
        <span>Similarity Search</span>
        <span>Recognition Result</span>
      </div>
    </div>

    <!-- Capabilities Showcase Section -->
    <div class="capabilities-section">
      <div class="capabilities-header">
        <span class="cap-badge">Capabilities</span>
        <h2>Advanced Face Analysis</h2>
        <p>Comprehensive AI modules for complete facial intelligence.</p>
      </div>

      <div class="showcase-wrapper">
        <div class="showcase-image-card">
          <img :src="showcaseImage" alt="Live Face Recognition Demo" />
        </div>
      </div>

      <div class="cap-grid">
        <article v-for="cap in capabilities" :key="cap.title" class="cap-card">
          <div class="cap-icon-wrap">
            <!-- Identification -->
            <svg v-if="cap.icon === 'identification'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            <!-- Demographics -->
            <svg v-if="cap.icon === 'demographics'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            <!-- Anti-Spoofing -->
            <svg v-if="cap.icon === 'antispoofing'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>
            <!-- Emotion -->
            <svg v-if="cap.icon === 'emotion'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>
            <!-- Face Attributes -->
            <svg v-if="cap.icon === 'attributes'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
            <!-- Face Landmark -->
            <svg v-if="cap.icon === 'landmark'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="12" r="3"/></svg>
          </div>
          <h3>{{ cap.title }}</h3>
          <p>{{ cap.desc }}</p>
          <div class="cap-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
