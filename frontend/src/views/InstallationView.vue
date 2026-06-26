<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  window.scrollTo(0, 0)
})

const copyCode = (event) => {
  const btn = event.currentTarget;
  const container = btn.parentElement;
  const preEl = container.querySelector('pre');
  if (preEl) {
    navigator.clipboard.writeText(preEl.innerText).then(() => {
      btn.classList.add('copied');
      const iconSpan = btn.querySelector('.icon');
      if (iconSpan) {
        const originalHTML = iconSpan.innerHTML;
        iconSpan.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#4ade80" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`;
        setTimeout(() => {
          btn.classList.remove('copied');
          iconSpan.innerHTML = originalHTML;
        }, 2000);
      }
    });
  }
}
</script>

<template>
  <div class="install-page">
    <!-- Hero -->
    <div class="install-hero">
      <p class="eyebrow">Self-Hosted</p>
      <h1>Installation Guide</h1>
      <p class="subtitle">
        Deploy <strong>Raray Vision</strong> on your own infrastructure using Docker or bare metal Linux.
        Full control, no vendor lock-in.
      </p>
      <div class="method-pills">
        <a href="#docker" class="pill active">Docker</a>
        <a href="#baremetal" class="pill">Bare Metal</a>
        <a href="#nginx" class="pill">Nginx</a>
        <a href="#auth" class="pill">Authentication</a>
      </div>
    </div>

    <!-- Prerequisites -->
    <div class="section">
      <h2 class="section-title">Prerequisites</h2>
      <div class="prereq-grid">
        <div class="prereq-card">
          <div class="prereq-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
          </div>
          <div>
            <strong>Server</strong>
            <span>Ubuntu 20.04+ / Debian 11+ / any Linux distro</span>
          </div>
        </div>
        <div class="prereq-card">
          <div class="prereq-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          </div>
          <div>
            <strong>Python</strong>
            <span>3.10 or higher</span>
          </div>
        </div>
        <div class="prereq-card">
          <div class="prereq-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
          </div>
          <div>
            <strong>Database</strong>
            <span>MySQL 8+ or MariaDB 10.6+</span>
          </div>
        </div>
        <div class="prereq-card">
          <div class="prereq-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>
          </div>
          <div>
            <strong>Memory</strong>
            <span>Minimum 2 GB RAM (4 GB recommended)</span>
          </div>
        </div>
        <div class="prereq-card">
          <div class="prereq-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
          </div>
          <div>
            <strong>Node.js</strong>
            <span>18+ (for building the frontend)</span>
          </div>
        </div>
        <div class="prereq-card">
          <div class="prereq-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
          </div>
          <div>
            <strong>Internet</strong>
            <span>Required on first boot to download InsightFace models</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Docker Section -->
    <div id="docker" class="section">
      <div class="section-label">Option 1 — Recommended</div>
      <h2 class="section-title">Docker Deployment</h2>
      <p class="section-desc">The fastest way to get Raray Vision running. Docker handles all dependencies automatically.</p>

      <div class="steps">

        <div class="step">
          <div class="step-num">1</div>
          <div class="step-body">
            <h3>Clone the repository</h3>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>git clone https://github.com/dedin7766/rarayvision.git
cd rarayvision</pre>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-num">2</div>
          <div class="step-body">
            <h3>Create the environment file</h3>
            <p>Create a <code>.env</code> file in the project root:</p>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>DATABASE_URL=mysql+pymysql://raray:yourpassword@db:3306/rarayvision
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440</pre>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-num">3</div>
          <div class="step-body">
            <h3>Build and start</h3>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>docker compose up --build -d</pre>
            </div>
            <p style="margin-top: 12px;">This will automatically build the backend, the frontend SPA, and set up MariaDB.</p>
          </div>
        </div>

        <div class="step">
          <div class="step-num">4</div>
          <div class="step-body">
            <h3>Verify the service</h3>
            <p>Access the web interface at <code>http://localhost</code></p>
            <div class="success-note" style="margin-top: 12px;">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              API documentation available at <code>http://localhost/docs</code> and <code>http://localhost/redoc</code>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Bare Metal Section -->
    <div id="baremetal" class="section">
      <div class="section-label">Option 2</div>
      <h2 class="section-title">Bare Metal (Linux)</h2>
      <p class="section-desc">Deploy directly on a Linux server using Python virtual environment and PM2 process manager.</p>

      <div class="steps">

        <div class="step">
          <div class="step-num">1</div>
          <div class="step-body">
            <h3>Clone and enter the project</h3>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>git clone https://github.com/dedin7766/rarayvision.git
cd rarayvision</pre>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-num">2</div>
          <div class="step-body">
            <h3>Install Python dependencies</h3>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt</pre>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-num">3</div>
          <div class="step-body">
            <h3>Set up the database</h3>
            <p>Run these commands in MySQL / MariaDB:</p>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>CREATE DATABASE rarayvision CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'raray'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON rarayvision.* TO 'raray'@'localhost';
FLUSH PRIVILEGES;</pre>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-num">4</div>
          <div class="step-body">
            <h3>Configure environment variables</h3>
            <p>Export these in your shell or add to <code>/etc/environment</code>:</p>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>export DATABASE_URL="mysql+pymysql://raray:yourpassword@localhost:3306/rarayvision"
export SECRET_KEY="your-secret-key-here"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="1440"</pre>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-num">5</div>
          <div class="step-body">
            <h3>Place ONNX model files</h3>
            <p>Copy your model files into <code>backend/models/</code>:</p>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>backend/models/
  best_model_quantized.onnx   # Anti-spoofing model
  emotion-ferplus-8.onnx      # Emotion detection model</pre>
            </div>
            <div class="info-note">InsightFace (buffalo_l) models are downloaded automatically on first run.</div>
          </div>
        </div>

        <div class="step">
          <div class="step-num">6</div>
          <div class="step-body">
            <h3>Start with PM2</h3>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>npm install -g pm2
pm2 start ecosystem.config.js
pm2 save
pm2 startup</pre>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-num">7</div>
          <div class="step-body">
            <h3>Build and serve the frontend</h3>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>cd frontend
npm install
npm run build</pre>
            </div>
            <p style="margin-top: 12px;">The production build is output to <code>frontend/dist/</code>. Point your Nginx root to this directory.</p>
          </div>
        </div>

      </div>
    </div>

    <!-- Nginx Section -->
    <div id="nginx" class="section">
      <h2 class="section-title">Nginx Configuration</h2>
      <p class="section-desc">Configure Nginx as a reverse proxy for both the frontend and backend API.</p>

      <div class="code-block">
        <button class="copy-btn" @click="copyCode($event)" title="Copy code">
          <span class="icon">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
          </span>
        </button>
        <pre>server {
    listen 80;
    server_name yourdomain.com;

    # Frontend (Vue SPA)
    root /path/to/rarayvision/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
        client_max_body_size 20M;
    }

    # Swagger UI and ReDoc
    location ~ ^/(docs|redoc|openapi.json) {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }

    # Socket.IO
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}</pre>
      </div>

      <div class="code-block" style="margin-top: 1.5rem;">
        <button class="copy-btn" @click="copyCode($event)" title="Copy code">
          <span class="icon">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
          </span>
        </button>
        <pre># Enable and reload
ln -s /etc/nginx/sites-available/rarayvision /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Enable HTTPS with Certbot
apt install certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com</pre>
      </div>
    </div>

    <!-- Auth Section -->
    <div id="auth" class="section">
      <h2 class="section-title">API Authentication</h2>
      <p class="section-desc">All face recognition endpoints require a JWT token in the Authorization header.</p>

      <div class="steps">
        <div class="step">
          <div class="step-num">1</div>
          <div class="step-body">
            <h3>Register an account</h3>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>curl -X POST https://yourdomain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"yourpassword","name":"Your Name"}'</pre>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-num">2</div>
          <div class="step-body">
            <h3>Login and get a token</h3>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>curl -X POST https://yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"yourpassword"}'

# Response:
# {"status":"success","token":"eyJ...","user_id":1}</pre>
            </div>
          </div>
        </div>

        <div class="step">
          <div class="step-num">3</div>
          <div class="step-body">
            <h3>Use the token in requests</h3>
            <div class="code-block">
              <button class="copy-btn" @click="copyCode($event)" title="Copy code">
                <span class="icon">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </span>
              </button>
              <pre>curl -X POST https://yourdomain.com/api/v1/recognize \
  -H "Authorization: Bearer eyJ..." \
  -F "file=@photo.jpg"</pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer CTA -->
    <div class="install-footer">
      <h2>Ready to go?</h2>
      <p>Once your server is running, explore the API interactively using the documentation.</p>
      <div class="footer-actions">
        <a :href="`${apiBase}/docs`" target="_blank" class="btn-primary">Swagger UI</a>
        <a :href="`${apiBase}/redoc`" target="_blank" class="btn-secondary">ReDoc</a>
      </div>
    </div>

  </div>
</template>

<script>
import { API_BASE_URL } from '../utils'
export default {
  data() {
    return { apiBase: API_BASE_URL }
  }
}
</script>

<style scoped>
.install-page {
  max-width: 860px;
  margin: 0 auto;
  padding: 3rem 1.5rem 5rem;
  color: #0f172a;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Hero */
.install-hero {
  text-align: center;
  margin-bottom: 4rem;
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #6366f1;
  font-weight: 700;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}
h1 {
  font-size: 3rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 1rem;
}
.subtitle {
  font-size: 1.15rem;
  color: #475569;
  max-width: 600px;
  margin: 0 auto 2rem;
  line-height: 1.65;
}
.method-pills {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.pill {
  background: #f1f5f9;
  color: #475569;
  padding: 6px 16px;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}
.pill:hover, .pill.active {
  background: #0f172a;
  color: #fff;
  border-color: #0f172a;
}

/* Section */
.section {
  margin-bottom: 4rem;
}
.section-label {
  display: block;
  color: #6366f1;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}
.section-title {
  font-size: 1.9rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 0.5rem;
}
.section-desc {
  color: #64748b;
  margin: 0 0 2rem;
  font-size: 1rem;
  line-height: 1.6;
}

/* Prerequisites */
.prereq-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}
.prereq-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
}
.prereq-icon {
  color: #6366f1;
  flex-shrink: 0;
  margin-top: 2px;
}
.prereq-card strong {
  display: block;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 2px;
}
.prereq-card span {
  font-size: 0.85rem;
  color: #64748b;
}

/* Steps */
.steps {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
}
.steps::before {
  content: '';
  position: absolute;
  left: 19px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e2e8f0;
  z-index: 0;
}
.step {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
  padding-bottom: 2rem;
  position: relative;
  z-index: 1;
}
.step-num {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  background: #0f172a;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
}
.step-body {
  flex: 1;
  padding-top: 8px;
}
.step-body h3 {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 0.75rem;
}
.step-body p {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0 0 0.75rem;
  line-height: 1.6;
}

/* Code blocks */
.code-block {
  background: #0f172a;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  overflow-x: auto;
  position: relative;
}
.copy-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.copy-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}
.copy-btn .icon svg {
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.copy-btn.copied .icon svg {
  animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes popIn {
  0% {
    transform: scale(0.5) rotate(-10deg);
    opacity: 0;
  }
  50% {
    transform: scale(1.2) rotate(5deg);
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}
.code-block pre {
  margin: 0;
  color: #e2e8f0;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 0.82rem;
  line-height: 1.7;
  white-space: pre;
}
code {
  background: #f1f5f9;
  color: #6366f1;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85em;
  font-family: monospace;
}

/* Notes */
.success-note {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 0.88rem;
}
.info-note {
  margin-top: 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 0.88rem;
}

/* Footer CTA */
.install-footer {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border-radius: 20px;
  padding: 3.5rem 2rem;
  text-align: center;
  color: #fff;
  margin-top: 2rem;
}
.install-footer h2 {
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 0.75rem;
}
.install-footer p {
  color: #94a3b8;
  margin: 0 0 2rem;
  font-size: 1rem;
}
.footer-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}
.btn-primary {
  background: #6366f1;
  color: #fff;
  padding: 0.8rem 2rem;
  border-radius: 99px;
  font-weight: 700;
  text-decoration: none;
  transition: background 0.2s;
}
.btn-primary:hover { background: #4f46e5; }
.btn-secondary {
  background: #fff;
  color: #0f172a;
  padding: 0.8rem 2rem;
  border-radius: 99px;
  font-weight: 700;
  text-decoration: none;
  transition: background 0.2s;
}
.btn-secondary:hover { background: #f1f5f9; }
</style>
