<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-grid">
        <div class="footer-col">
          <h3>Raray Vision</h3>
          <p>An open-source, high-performance computer vision API for face recognition, liveness detection, and facial analysis.</p>
          <h3 style="margin-top: 24px;">Support Us</h3>
          <a href="https://trakteer.id/dedin_toyibah" target="_blank" style="display: inline-block; margin-top: 4px; transition: transform 0.2s; height: 40px;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <img src="https://cdn.trakteer.id/images/embed/trbtn-red-1.png" height="40" style="border:0px;height:40px;" alt="Trakteer Saya" />
          </a>
        </div>
        
        <div class="footer-col">
          <h3>Contact</h3>
          <ul>
            <li><a href="mailto:say.hi@dfs.co.id">say.hi@dfs.co.id</a></li>
          </ul>
        </div>
        
        <div class="footer-col">
          <h3>Security & Privacy</h3>
          <ul>
            <li><a href="#" @click.prevent="showPrivacyModal = true">Privacy Policy & Terms</a></li>
            <li><a href="#" @click.prevent="showSecurityModal = true">API Security Guidelines</a></li>
          </ul>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; {{ new Date().getFullYear() }} Raray Vision. All rights reserved.</p>
        <p class="security-note">
          <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          Enterprise-grade security. Images are processed in-memory and never stored without explicit consent.
        </p>
      </div>
    </div>

    <!-- Privacy Modal -->
    <div v-if="showPrivacyModal" class="modal-overlay" @click.self="showPrivacyModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showPrivacyModal = false">&times;</button>
        <div class="modal-header">
          <h2>Privacy Policy & Terms of Service</h2>
          <p>How we handle and protect biometric data</p>
        </div>
        <div class="modal-body">
          <section>
            <h4>Our Stance on Privacy</h4>
            <p><strong>By default, Raray Vision does not store original face images.</strong> Images are processed in memory to generate encrypted face embeddings and are immediately discarded unless explicitly configured otherwise.</p>
            <p>Raray Vision is designed with privacy and security best practices. Organizations remain responsible for complying with applicable regulations such as UU PDP and GDPR.</p>
          </section>

          <section>
            <h4>What Data is Processed?</h4>
            <ul>
              <li><strong>Face Embeddings:</strong> We extract mathematical representations (embeddings) of faces. These are securely encrypted before being stored.</li>
              <li><strong>Original Images:</strong> By default, original images are <em>never</em> stored. They are kept in memory only for the duration of the request and discarded immediately after processing.</li>
              <li><strong>Demographic & Attribute Data:</strong> Estimated attributes (e.g., age, gender, emotion) are returned in the API response but not permanently logged unless configured by the customer.</li>
            </ul>
          </section>
          
          <section>
            <h4>How Data is Protected</h4>
            <p>Face embeddings are encrypted using AES-256 before being stored in the database. All data in transit is secured via HTTPS. Access to the API and Dashboard is strictly controlled via API keys and JWT authentication.</p>
          </section>

          <section>
            <h4>Deployment Options</h4>
            <h5>Self-Hosted</h5>
            <p>When deployed on your own infrastructure, you retain complete ownership of the system. Raray Vision has absolutely no access to customer data, logs, or encryption keys.</p>
            <h5>Cloud API</h5>
            <p>Our managed cloud API strictly adheres to the principle of storing only encrypted embeddings. Original images are not stored by default and can only be optionally stored if the customer explicitly enables it for auditing purposes.</p>
          </section>
        </div>
      </div>
    </div>

    <!-- Security Modal -->
    <div v-if="showSecurityModal" class="modal-overlay" @click.self="showSecurityModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showSecurityModal = false">&times;</button>
        <div class="modal-header">
          <h2>API Security Guidelines</h2>
          <p>Security architecture and data protection in Raray Vision</p>
        </div>
        <div class="modal-body">
          <section>
            <h4>Security by Design</h4>
            <p>Raray Vision prioritizes the security of biometric data. We implement industry-standard encryption and access controls to ensure that face data is protected against unauthorized access.</p>
          </section>

          <section>
            <h4>Core Security Features</h4>
            <ul>
              <li><strong>Data at Rest Encryption:</strong> Face embeddings are encrypted using strong AES-256 encryption before being stored in the database.</li>
              <li><strong>Secrets Management:</strong> Encryption keys are never hardcoded and are strictly managed via environment variables or a secure secrets manager.</li>
              <li><strong>Data in Transit:</strong> HTTPS is strictly enforced in production to protect data against interception.</li>
              <li><strong>Authentication:</strong> API endpoints are secured with API Key authentication. Dashboard and admin panels are protected using secure JWT (JSON Web Tokens).</li>
              <li><strong>Rate Limiting:</strong> Endpoints are protected against abuse and brute-force attacks via rate limiting.</li>
              <li><strong>Audit Logging:</strong> Comprehensive audit logs are maintained for critical actions including user registration, updates, deletions, and logins.</li>
            </ul>
          </section>
          
          <section>
            <h4>Best Practices for Integration</h4>
            <p>When integrating the Raray Vision API into your application, we strongly recommend:</p>
            <ul>
              <li>Never expose your API keys in frontend applications (e.g., mobile apps, web browsers).</li>
              <li>Route all requests through your own backend servers.</li>
              <li>Regularly rotate your API keys via the dashboard.</li>
              <li>Adhere to local regulations regarding user consent before processing biometric data.</li>
            </ul>
          </section>
        </div>
      </div>
    </div>

  </footer>
</template>

<script setup>
import { ref } from 'vue'

const showPrivacyModal = ref(false)
const showSecurityModal = ref(false)
</script>

<style scoped>
.app-footer {
  margin-top: 60px;
  border-top: 1px solid #e2e8f0;
  padding: 40px 0 20px;
  background-color: #f8fafc;
  color: #475569;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 32px;
  margin-bottom: 40px;
}

.footer-col h3 {
  color: #0f172a;
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 16px;
}

.footer-col p {
  line-height: 1.6;
  font-size: 0.95rem;
  margin-bottom: 12px;
}

.footer-col ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-col ul li {
  margin-bottom: 12px;
}

.footer-col a {
  color: #475569;
  text-decoration: none;
  transition: color 0.2s;
  font-size: 0.95rem;
  cursor: pointer;
}

.footer-col a:hover {
  color: #0f172a;
  text-decoration: underline;
}

.website-url a {
  color: #2563eb;
  font-weight: 500;
}

.footer-bottom {
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.footer-bottom p {
  font-size: 0.9rem;
  margin: 0;
}

.security-note {
  display: flex;
  align-items: center;
  color: #ffffff;
  background-color: #059669;
  padding: 6px 12px;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
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
  justify-content: center;
  align-items: center;
  z-index: 10000;
  padding: 24px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #64748b;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-header {
  padding: 32px 32px 0 32px;
  margin-bottom: 24px;
}

.modal-header h2 {
  font-size: 1.5rem;
  color: #0f172a;
  margin: 0 0 8px 0;
}

.modal-header p {
  color: #64748b;
  margin: 0;
  font-size: 1rem;
}

.modal-body {
  padding: 0 32px 32px 32px;
}

.modal-body section {
  margin-bottom: 24px;
}

.modal-body h4 {
  font-size: 1.1rem;
  color: #1e293b;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-body h5 {
  font-size: 1rem;
  color: #334155;
  margin: 16px 0 8px 0;
}

.modal-body p {
  line-height: 1.6;
  color: #475569;
  margin: 0 0 12px 0;
  font-size: 0.95rem;
}

.modal-body ul {
  padding-left: 20px;
  margin: 0 0 12px 0;
}

.modal-body li {
  line-height: 1.6;
  color: #475569;
  margin-bottom: 8px;
  font-size: 0.95rem;
}
</style>
