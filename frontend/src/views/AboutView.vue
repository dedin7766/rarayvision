<script setup>
import { ref, onMounted } from 'vue'
import { API_BASE_URL } from '../utils'

const name = ref('')
const email = ref('')
const message = ref('')
const status = ref('')
const loading = ref(false)

onMounted(() => {
  window.scrollTo(0, 0)
})

const submitFeedback = async () => {
  if (!name.value || !email.value || !message.value) {
    status.value = 'Please fill out all fields.'
    return
  }
  loading.value = true
  status.value = 'Sending...'
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name.value,
        email: email.value,
        message: message.value
      })
    })
    const data = await res.json()
    if (data.status === 'success') {
      status.value = 'Thank you! Your feedback has been sent successfully.'
      name.value = ''
      email.value = ''
      message.value = ''
    } else {
      status.value = `Error: ${data.message || 'Failed to send feedback'}`
    }
  } catch (err) {
    status.value = `Error: ${err.message}`
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="about-page">
    <div style="text-align: center; margin-bottom: 4rem;">
      <p style="text-transform: uppercase; letter-spacing: 2px; color: #6366f1; font-weight: 700; margin-bottom: 0.5rem; font-size: 0.9rem;">Introduce</p>
      <h1 class="hero-title">Raray Vision API</h1>
      <p class="hero-desc">
        Raray Vision takes its name from the Sundanese word <strong>Raray</strong>, meaning face. The project is dedicated to advancing face recognition technology through open, scalable, and intelligent computer vision.
      </p>
    </div>

    <!-- Features Grid -->
    <div style="display: grid; gap: 2rem; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); margin-bottom: 4rem;">
      <!-- Card 1 -->
      <div style="background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9; transition: transform 0.3s; cursor: default;" onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">

        <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 0.75rem 0;">FastAPI Backend</h3>
        <p style="color: #64748b; margin: 0; line-height: 1.6;">Powered by Python's FastAPI, delivering asynchronous, ultra-fast HTTP request handling and automatic Swagger UI generation.</p>
      </div>

      <!-- Card 2 -->
      <div style="background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9; transition: transform 0.3s; cursor: default;" onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">

        <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 0.75rem 0;">YuNet & OpenCV</h3>
        <p style="color: #64748b; margin: 0; line-height: 1.6;">Utilizes OpenCV and the highly efficient YuNet model to detect faces and facial landmarks in milliseconds with pinpoint accuracy.</p>
      </div>

      <!-- Card 3 -->
      <div style="background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9; transition: transform 0.3s; cursor: default;" onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">

        <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 0.75rem 0;">InsightFace</h3>
        <p style="color: #64748b; margin: 0; line-height: 1.6;">Powered by the incredibly sophisticated <strong>insightface</strong> library and state-of-the-art embedding extraction algorithms, converting facial features into vectors for unmatched matching precision.</p>
      </div>

      <!-- Card 4 -->
      <div style="background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9; transition: transform 0.3s; cursor: default;" onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">

        <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 0.75rem 0;">Liveness</h3>
        <p style="color: #64748b; margin: 0; line-height: 1.6;">Integrated Anti-Spoofing checks using ONNX Runtime to distinguish real human faces from printed photos or screens in real-time.</p>
      </div>
    </div>

    <!-- Core Tech Stack -->
    <div style="margin-bottom: 4rem;">
      <div style="text-align: center; margin-bottom: 3rem;">
        <h2 class="section-title">Core Technology Stack</h2>
        <p style="font-size: 1.1rem; color: #475569; max-width: 700px; margin: 1rem auto 0; line-height: 1.6;">
          Raray Vision is built on a modern, high-performance technology stack optimized for real-time face recognition, scalable API services, and production deployment.
        </p>
      </div>

      <div style="display: grid; gap: 2rem; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));">
        
        <!-- Backend Framework -->
        <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #f1f5f9;">
          <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 0.5rem;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
            Backend Framework
          </h3>
          <ul style="list-style: none; padding: 0; margin: 0; color: #475569; display: flex; flex-direction: column; gap: 0.75rem;">
            <li><strong style="color: #0f172a;">FastAPI</strong> — High-performance asynchronous API framework.</li>
            <li><strong style="color: #0f172a;">Uvicorn</strong> — ASGI server for lightweight deployments.</li>
            <li><strong style="color: #0f172a;">Gunicorn</strong> — Production-grade process manager.</li>
            <li><strong style="color: #0f172a;">Python Socket.IO</strong> — Real-time event streaming.</li>
          </ul>
        </div>

        <!-- Computer Vision & AI -->
        <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #f1f5f9;">
          <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 0.5rem;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg>
            Computer Vision &amp; AI
          </h3>
          <ul style="list-style: none; padding: 0; margin: 0; color: #475569; display: flex; flex-direction: column; gap: 0.75rem;">
            <li><strong style="color: #0f172a;">InsightFace (buffalo_l)</strong> — State-of-the-art face analysis framework providing detection, alignment, and embedding in a single pipeline.</li>
            <li><strong style="color: #0f172a;">ArcFace (ResNet50)</strong> — 512-dimensional facial embeddings for high-accuracy 1:1 and 1:N face recognition.</li>
            <li><strong style="color: #0f172a;">ONNX Runtime</strong> — High-performance inference engine.</li>
            <li><strong style="color: #0f172a;">OpenCV</strong> — Computer vision operations.</li>
            <li><strong style="color: #0f172a;">NumPy</strong> — Numerical computing.</li>
          </ul>
        </div>

        <!-- Data & Storage -->
        <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #f1f5f9;">
          <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 0.5rem;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
            Data & Storage
          </h3>
          <ul style="list-style: none; padding: 0; margin: 0; color: #475569; display: flex; flex-direction: column; gap: 0.75rem;">
            <li><strong style="color: #0f172a;">SQLAlchemy</strong> — ORM and database abstraction layer.</li>
            <li><strong style="color: #0f172a;">MySQL / MariaDB</strong> — Relational database backend.</li>
            <li><strong style="color: #0f172a;">PyMySQL</strong> — MySQL database driver.</li>
          </ul>
        </div>

        <!-- Face Recognition Pipeline -->
        <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #f1f5f9;">
          <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 0.5rem;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            Face Recognition Pipeline
          </h3>
          <ul style="list-style: none; padding: 0; margin: 0; color: #475569; display: flex; flex-direction: column; gap: 0.5rem;">
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Face Detection</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Face Landmark Extraction</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Face Alignment</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Face Embedding Generation</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Face Matching & Identification</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Face Anti-Spoofing (Liveness)</li>
          </ul>
        </div>

        <!-- Authentication & Security -->
        <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #f1f5f9;">
          <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 0.5rem;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            Authentication & Security
          </h3>
          <ul style="list-style: none; padding: 0; margin: 0; color: #475569; display: flex; flex-direction: column; gap: 0.75rem;">
            <li><strong style="color: #0f172a;">AES-256 Encryption</strong> — Face embeddings are strictly secured in the database using industry-standard cryptography.</li>
            <li><strong style="color: #0f172a;">In-Memory Processing</strong> — Original images are processed in-memory and immediately discarded unless explicitly enabled, supporting UU PDP and GDPR compliance.</li>
            <li><strong style="color: #0f172a;">Passlib (bcrypt)</strong> — Password hashing and credential protection.</li>
            <li><strong style="color: #0f172a;">PyJWT</strong> — JWT-based authentication and authorization.</li>
            <li><strong style="color: #0f172a;">python-multipart</strong> — Multipart form and file processing.</li>
          </ul>
        </div>

        <!-- Deployment & Hardware -->
        <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #f1f5f9;">
          <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 0.5rem;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
            Deployment & Hardware
          </h3>
          <ul style="list-style: none; padding: 0; margin: 0; color: #475569; display: flex; flex-direction: column; gap: 0.5rem;">
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Linux Server / Docker Ready</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Nginx Reverse Proxy & HTTPS</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Lightweight CPU Inference (Optional NVIDIA CUDA)</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Edge Deployment Ready</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Horizontal Scalability</li>
          </ul>
        </div>
      </div>

      <!-- How Face Embedding Works -->
      <div style="margin-top: 2rem; background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #f1f5f9;">
        <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 0.5rem;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
          How Face Embedding Works
        </h3>
        <p style="color: #475569; margin: 0 0 0.75rem 0; line-height: 1.6; font-size: 0.95rem;">
          Raray Vision uses the <strong style="color: #0f172a;">ArcFace</strong> algorithm with a <strong style="color: #0f172a;">ResNet50</strong> backbone. ArcFace applies an <em>Additive Angular Margin Loss</em> during training, which forces the model to learn highly discriminative features by maximizing the angular distance between different identities in the embedding space.
        </p>
        <p style="color: #475569; margin: 0 0 0.75rem 0; line-height: 1.6; font-size: 0.95rem;">
          Each detected face is aligned using 5-point facial landmarks, then passed through the ResNet50 network to produce a compact <strong style="color: #0f172a;">512-dimensional float32 vector</strong> (embedding). This vector is a unique numerical "fingerprint" of the face.
        </p>
        <p style="color: #475569; margin: 0; line-height: 1.6; font-size: 0.95rem;">
          Matching is performed using <strong style="color: #0f172a;">Cosine Similarity</strong> — measuring the angle between two embedding vectors. A similarity score above <strong style="color: #0f172a;">0.45</strong> (1:1 verification) or <strong style="color: #0f172a;">0.50</strong> (1:N identification) indicates a positive match.
        </p>
      </div>
    </div>

    <!-- Feedback Section -->
    <div style="margin-bottom: 4rem;">
      <div style="text-align: center; margin-bottom: 3rem;">
        <p style="text-transform: uppercase; letter-spacing: 2px; color: #6366f1; font-weight: 700; margin-bottom: 0.5rem; font-size: 0.9rem;">We Value Your Input</p>
        <h2 class="section-title">Send Feedback</h2>
        <p style="font-size: 1.1rem; color: #475569; max-width: 600px; margin: 1rem auto 0; line-height: 1.6;">
          Have a suggestion, found a bug, or want to request a feature? Let us know below!
        </p>
      </div>
      <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9;">
        <form @submit.prevent="submitFeedback" style="display: flex; flex-direction: column; gap: 1.5rem;">
          <div>
            <label style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: #334155;">Your Name</label>
            <input type="text" v-model="name" placeholder="John Doe" required style="width: 100%; padding: 0.75rem 1rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; outline: none; transition: border-color 0.2s; box-sizing: border-box;" onfocus="this.style.borderColor='#000'" onblur="this.style.borderColor='#cbd5e1'" />
          </div>
          <div>
            <label style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: #334155;">Email Address</label>
            <input type="email" v-model="email" placeholder="john@example.com" required style="width: 100%; padding: 0.75rem 1rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; outline: none; transition: border-color 0.2s; box-sizing: border-box;" onfocus="this.style.borderColor='#000'" onblur="this.style.borderColor='#cbd5e1'" />
          </div>
          <div>
            <label style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: #334155;">Message</label>
            <textarea v-model="message" rows="5" placeholder="Write your suggestions, bugs, or questions here..." required style="width: 100%; padding: 0.75rem 1rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; outline: none; resize: vertical; transition: border-color 0.2s; box-sizing: border-box;" onfocus="this.style.borderColor='#000'" onblur="this.style.borderColor='#cbd5e1'"></textarea>
          </div>
          <button type="submit" :disabled="loading" style="background: #000; color: white; padding: 1rem; border-radius: 8px; font-weight: 700; font-size: 1rem; border: none; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#333'" onmouseout="this.style.background='#000'">
            {{ loading ? 'Sending...' : 'Send Feedback' }}
          </button>
        </form>
        <div v-if="status" style="margin-top: 1.5rem; padding: 1rem; border-radius: 8px; font-weight: 600; text-align: center;" :style="status.includes('Error') ? 'background:#fef2f2;color:#ef4444;' : 'background:#f0fdf4;color:#16a34a;'">
          {{ status }}
        </div>
      </div>
    </div>

    <!-- Creator Quote Section -->
    <div style="max-width: 800px; margin: 0 auto 4rem auto; background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9; display: flex; flex-wrap: wrap; align-items: flex-start; gap: 2rem; justify-content: center;">
      <img src="/creator.jpg" alt="Creator of Raray Vision" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; box-shadow: 0 4px 10px rgba(0,0,0,0.1);" />
      <div style="flex: 1; min-width: 250px;">
        <p style="font-size: 1.15rem; color: #334155; font-style: italic; line-height: 1.6; margin: 0 0 1rem 0; position: relative;">
          "For me, engineering is more than writing code—it's about creating technology that people can trust, maintain, and truly own. Every project I build is driven by simplicity, reliability, and a commitment to open innovation."
        </p>
        <p style="font-size: 1rem; font-weight: 700; color: #0f172a; margin: 0;">— Dedin, Founder & Lead Engineer Raray Vision</p>
        <div style="margin-top: 1.5rem;">
          <a href="https://wa.me/6282299331066?text=Hi%20Dedin%2C%20I'm%20interested%20in%20a%20business%20collaboration%20regarding%20Raray%20Vision." target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; background: #25D366; color: white; padding: 0.75rem 1.5rem; border-radius: 99px; font-weight: 700; text-decoration: none; font-size: 0.95rem; transition: background 0.2s;" onmouseover="this.style.background='#128C7E'" onmouseout="this.style.background='#25D366'">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12.002 0h-.005A11.97 11.97 0 0 0 0 11.983c0 2.128.558 4.21 1.616 6.046L.347 24l6.113-1.603a11.97 11.97 0 0 0 5.541 1.344h.005A11.968 11.968 0 0 0 24 11.983 11.968 11.968 0 0 0 12.002 0zm0 21.684a9.92 9.92 0 0 1-5.065-1.39l-.363-.215-3.76 1.013.986-3.665-.236-.375A9.928 9.928 0 0 1 2.039 11.983a9.92 9.92 0 0 1 9.963-9.94h.004a9.922 9.922 0 0 1 9.96 9.94 9.922 9.922 0 0 1-9.964 9.94zm5.452-7.447c-.299-.15-1.77-.874-2.044-.975-.274-.1-.473-.15-.672.15s-.77 1.036-.944 1.25c-.175.214-.35.24-.65.09-1.637-.81-2.92-1.922-3.83-3.486-.176-.3-.021-.465.127-.614.135-.136.3-.35.45-.526.15-.175.2-.3.3-.5.1-.2.05-.375-.025-.525-.075-.15-.672-1.62-.921-2.215-.24-.58-.485-.502-.672-.511-.174-.01-.373-.01-.572-.01-.2 0-.522.075-.796.375-.274.3-1.046 1.025-1.046 2.5 0 1.475 1.07 2.9 1.22 3.1.15.2 2.116 3.23 5.122 4.526 2.05 1 2.5.825 3.025.775.525-.05 1.77-.725 2.02-1.425.25-.7.25-1.3.175-1.425-.075-.125-.274-.2-.573-.35z"/></svg>
            Business & Collaboration
          </a>
        </div>
      </div>
    </div>

    <!-- Footer Banner -->
    <div class="footer-banner" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius: 24px; text-align: center; color: white;">
      <h2 class="banner-title">Open by Design, Built for Innovation</h2>
      <p style="font-size: 1.15rem; color: #cbd5e1; max-width: 650px; margin: 0 auto 2rem auto; line-height: 1.6;">
        Designed to accelerate AI development, Raray Vision brings enterprise-grade facial recognition to the community. Build, scale, and integrate advanced computer vision into your applications without commercial barriers or restrictive limits.
      </p>
      <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
        <a href="https://apirv.dfs.co.id/redoc" target="_blank" style="display: inline-flex; align-items: center; background: #6366f1; color: white; padding: 1rem 2rem; border-radius: 99px; font-weight: 700; text-decoration: none; transition: background 0.2s;" onmouseover="this.style.background='#4f46e5'" onmouseout="this.style.background='#6366f1'">
          Explore API Documentation
        </a>
        <a href="https://github.com" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; background: #ffffff; color: #0f172a; padding: 1rem 2rem; border-radius: 99px; font-weight: 700; text-decoration: none; transition: background 0.2s;" onmouseover="this.style.background='#f1f5f9'" onmouseout="this.style.background='#ffffff'">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
          View on GitHub
        </a>
      </div>
    </div>
  </div>
</template>


<style scoped>
.about-page {
  padding: 4rem 1.5rem;
  max-width: 900px;
  margin: 0 auto;
  color: #0f172a;
}
.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  letter-spacing: -0.02em;
}
.hero-desc {
  font-size: 1.25rem;
  color: #475569;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}
.section-title {
  font-size: 2.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.banner-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 1rem;
}
.footer-banner {
  padding: 4rem 2rem;
}

@media (max-width: 768px) {
  .about-page {
    padding: 2rem 1rem;
  }
  .hero-title {
    font-size: 2.2rem;
  }
  .hero-desc {
    font-size: 1rem;
  }
  .section-title {
    font-size: 1.8rem;
  }
  .banner-title {
    font-size: 1.8rem;
  }
  .footer-banner {
    padding: 2.5rem 1.5rem;
  }
}
</style>
