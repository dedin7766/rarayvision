<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  window.scrollTo(0, 0)
})
</script>

<template>
  <div class="about-page" style="padding: 4rem 1.5rem; max-width: 900px; margin: 0 auto; color: #0f172a;">
    <div style="text-align: center; margin-bottom: 4rem;">
      <p style="text-transform: uppercase; letter-spacing: 2px; color: #6366f1; font-weight: 700; margin-bottom: 0.5rem; font-size: 0.9rem;">About The Tech</p>
      <h1 style="font-size: 3.5rem; font-weight: 800; line-height: 1.1; margin-bottom: 1.5rem; letter-spacing: -0.02em;">Raray Vision API</h1>
      <p style="font-size: 1.25rem; color: #475569; max-width: 600px; margin: 0 auto; line-height: 1.6;">
        Raray Vision takes its name from the Sundanese word <strong>Raray</strong>, meaning face. The project is dedicated to advancing face recognition technology through open, scalable, and intelligent computer vision.
      </p>
    </div>

    <!-- Features Grid -->
    <div style="display: grid; gap: 2rem; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); margin-bottom: 4rem;">
      <!-- Card 1 -->
      <div style="background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9; transition: transform 0.3s; cursor: default;" onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="background: #0f172a; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem; color: white;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        </div>
        <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 0.75rem 0;">FastAPI Backend</h3>
        <p style="color: #64748b; margin: 0; line-height: 1.6;">Powered by Python's FastAPI, delivering asynchronous, ultra-fast HTTP request handling and automatic Swagger UI generation.</p>
      </div>

      <!-- Card 2 -->
      <div style="background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9; transition: transform 0.3s; cursor: default;" onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="background: #0f172a; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem; color: white;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
        </div>
        <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 0.75rem 0;">YuNet & OpenCV</h3>
        <p style="color: #64748b; margin: 0; line-height: 1.6;">Utilizes OpenCV and the highly efficient YuNet model to detect faces and facial landmarks in milliseconds with pinpoint accuracy.</p>
      </div>

      <!-- Card 3 -->
      <div style="background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9; transition: transform 0.3s; cursor: default;" onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="background: #0f172a; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem; color: white;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
        </div>
        <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 0.75rem 0;">InsightFace</h3>
        <p style="color: #64748b; margin: 0; line-height: 1.6;">Powered by the incredibly sophisticated <strong>insightface</strong> library and state-of-the-art embedding extraction algorithms, converting facial features into vectors for unmatched matching precision.</p>
      </div>

      <!-- Card 4 -->
      <div style="background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9; transition: transform 0.3s; cursor: default;" onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="background: #0f172a; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem; color: white;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        </div>
        <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0 0 0.75rem 0;">Liveness</h3>
        <p style="color: #64748b; margin: 0; line-height: 1.6;">Integrated Anti-Spoofing checks using ONNX Runtime to distinguish real human faces from printed photos or screens in real-time.</p>
      </div>
    </div>

    <!-- Core Tech Stack -->
    <div style="margin-bottom: 4rem;">
      <div style="text-align: center; margin-bottom: 3rem;">
        <h2 style="font-size: 2.5rem; font-weight: 800; letter-spacing: -0.02em;">Core Technology Stack</h2>
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
            Computer Vision & AI
          </h3>
          <ul style="list-style: none; padding: 0; margin: 0; color: #475569; display: flex; flex-direction: column; gap: 0.75rem;">
            <li><strong style="color: #0f172a;">InsightFace</strong> — State-of-the-art face analysis framework.</li>
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
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> CPU & NVIDIA CUDA Acceleration</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Edge Deployment Ready</li>
            <li style="display: flex; align-items: center; gap: 0.5rem;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Horizontal Scalability</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Footer Banner -->
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius: 24px; padding: 4rem 2rem; text-align: center; color: white;">
      <h2 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;">Open by Design, Built for Innovation</h2>
      <p style="font-size: 1.15rem; color: #cbd5e1; max-width: 650px; margin: 0 auto 2rem auto; line-height: 1.6;">
        Designed to accelerate AI development, Raray Vision brings enterprise-grade facial recognition to the community. Build, scale, and integrate advanced computer vision into your applications without commercial barriers or restrictive limits.
      </p>
      <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
        <a href="https://apirv.dfs.co.id/docs" target="_blank" style="display: inline-flex; align-items: center; background: #6366f1; color: white; padding: 1rem 2rem; border-radius: 99px; font-weight: 700; text-decoration: none; transition: background 0.2s;" onmouseover="this.style.background='#4f46e5'" onmouseout="this.style.background='#6366f1'">
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
/* No extra styles needed, using inline css for isolated rapid styling */
</style>