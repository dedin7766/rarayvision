<script setup>
import { computed, onMounted, ref } from 'vue'
import { store } from '../store'
import { apiKeyService } from '../services/apiKeyService'
import { formatDate, maskedKey, isKeyExpired, keyExpiryLabel } from '../utils'

const activeKeys = computed(() =>
  store.apiKeys.filter(k => k.status === 'Active' && !isKeyExpired(k)).length
)

const toastMessage = ref('')
const showToast = (msg) => {
  toastMessage.value = msg
  setTimeout(() => toastMessage.value = '', 3000)
}

const copyKey = (key) => { 
  navigator.clipboard.writeText(key) 
  showToast('API Key copied to clipboard!')
}

const copyUrl = () => {
  navigator.clipboard.writeText('https://yourdomain/api/v1')
  showToast('API Endpoint copied to clipboard!')
}

const showGenerateModal = ref(false)
const showSuccessModal = ref(false)
const showRevokeModal = ref(false)
const keyToRevoke = ref(null)
const newKeyName = ref('New Key')
const newKeyExpiry = ref(null) // null = never
const newlyGeneratedKeyString = ref('')

const handleGenerate = async () => {
  const generated = await apiKeyService.generate(newKeyName.value, newKeyExpiry.value)
  if (generated) {
    newlyGeneratedKeyString.value = generated.key
    showGenerateModal.value = false
    showSuccessModal.value = true
    newKeyName.value = 'New Key'
    newKeyExpiry.value = null
  }
}

const openGenerateModal = () => {
  newKeyName.value = 'New Key'
  newKeyExpiry.value = null
  showGenerateModal.value = true
}

const confirmRevoke = (id) => {
  keyToRevoke.value = id
  showRevokeModal.value = true
}

const handleRevoke = async () => {
  if (keyToRevoke.value) {
    await apiKeyService.revoke(keyToRevoke.value)
    showRevokeModal.value = false
    keyToRevoke.value = null
  }
}

const isSimulatingLoad = ref(true)

onMounted(() => {
  apiKeyService.fetch()
  setTimeout(() => { isSimulatingLoad.value = false }, 800)
})
</script>

<template>
  <section class="dashboard-layout">
    <!-- Shimmer Skeleton -->
    <div v-if="isSimulatingLoad" style="display: flex; flex-direction: column; gap: 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
          <div class="skeleton skeleton-text" style="width: 80px; height: 16px; margin-bottom: 8px;"></div>
          <div class="skeleton skeleton-title" style="width: 200px; height: 36px; margin: 0;"></div>
        </div>
        <div class="skeleton skeleton-text" style="width: 140px; height: 44px; border-radius: 8px; margin: 0;"></div>
      </div>
      <div class="stats-grid">
        <div class="stat-card skeleton" style="height: 120px;"></div>
        <div class="stat-card skeleton" style="height: 120px;"></div>
        <div class="stat-card skeleton" style="height: 120px;"></div>
      </div>
      <div class="keys-panel" style="margin-top: 2rem; padding: 24px;">
        <div class="skeleton skeleton-title" style="width: 150px; height: 28px; margin-bottom: 24px;"></div>
        <div class="skeleton skeleton-row" style="height: 90px; border-radius: 12px;"></div>
        <div class="skeleton skeleton-row" style="height: 90px; border-radius: 12px;"></div>
      </div>
    </div>

    <!-- Actual Content -->
    <div v-else style="display: contents;">
      <div class="dashboard-header">
      <div>
        <p class="eyebrow">Overview</p>
        <h2>Dashboard</h2>
      </div>
      <div style="display: flex; gap: 12px; align-items: center;">
        <button class="generate-btn" @click="openGenerateModal" style="display: inline-flex; align-items: center; gap: 8px;">
          <svg viewBox="0 0 24 24" style="width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round;"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path></svg>
          Generate API Key
        </button>
        <a href="https://trakteer.id/dedin_toyibah" target="_blank" style="display: inline-block; transition: transform 0.2s; height: 40px;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
          <img src="https://cdn.trakteer.id/images/embed/trbtn-red-1.png" height="40" style="border:0px;height:40px;" alt="Trakteer Saya">
        </a>
      </div>
    </div>

    <div class="stats-grid">
      <article class="stat-card">
        <span>API Status</span>
        <strong :class="store.apiStatus.toLowerCase()">{{ store.apiStatus }}</strong>
        <small>{{ store.apiStatusDetail }}</small>
      </article>
      <article class="stat-card">
        <span>Active Keys</span>
        <strong>{{ activeKeys }}</strong>
        <small>Ready for client apps</small>
      </article>
      <article class="stat-card">
        <span>Last Updated</span>
        <strong>{{ store.apiKeys.length ? formatDate(store.apiKeys[0].createdAt) : '-' }}</strong>
        <small>Recent generated key</small>
      </article>
    </div>

    <section class="keys-panel">
      <div class="keys-header">
        <h3>API Keys</h3>
        <span>{{ store.apiKeys.length }} total</span>
      </div>
      <div v-if="store.apiKeys.length" class="keys-list">
        <article v-for="item in store.apiKeys" :key="item.id" class="key-card">
          <div>
            <p class="key-name">{{ item.name }}</p>
            <p class="key-value">{{ item.key }}</p>
            <small>Created {{ formatDate(item.createdAt) }}</small>
            <small v-if="item.expiresAt"> · Expires {{ keyExpiryLabel(item) }}</small>
            <small v-else> · Never expires</small>
            <small v-if="item.usageCount !== undefined"> · Used {{ item.usageCount }} times</small>
            <small v-if="isKeyExpired(item)" class="expired-text"> · Expired</small>
          </div>
          <div class="key-actions">
            <button class="danger" @click="confirmRevoke(item.id)">Revoke</button>
          </div>
        </article>
      </div>
      <p v-else class="empty-state">No API keys yet.</p>
    </section>

    <section class="keys-panel" style="margin-top: 2rem;">
      <div class="keys-header">
        <h3>API Integration</h3>
      </div>
      <div class="webhook-content">
        <p>Use this base URL to integrate our Face Recognition API into your own application.</p>
        <div 
          @click="copyUrl"
          style="background: #f1f5f9; padding: 1rem; border-radius: 8px; margin-top: 1rem; border: 1px solid #e2e8f0; cursor: pointer; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;"
          title="Click to copy API Endpoint"
        >
          <div>
            <p style="margin:0; font-size: 0.85rem; color: #64748b;">Base API Endpoint</p>
            <p style="margin: 0.5rem 0 0 0; font-family: monospace; font-size: 1rem; color: #0f172a; font-weight: 600; word-break: break-all;">https://yourdomain/api/v1</p>
          </div>
          <button style="background: #e2e8f0; border: none; padding: 6px 12px; border-radius: 6px; color: #0f172a; font-size: 0.85rem; font-weight: 600; cursor: pointer;">Copy</button>
        </div>
        <p style="margin-top: 1rem; color: #64748b; font-size: 0.9rem;">
          Send HTTP requests to this domain using the endpoints described in the API Docs. Remember to include your API Key in the Authorization header.
        </p>
      </div>
    </section>
  </div>

    <!-- Modals -->
    <div v-if="showGenerateModal" class="modal-overlay" @click.self="showGenerateModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>Generate New API Key</h3>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>API Key Name</label>
            <input type="text" v-model="newKeyName" placeholder="e.g. Production Key" />
          </div>
          <div class="form-group" style="margin-top: 1rem;">
            <label>Expiration</label>
            <select v-model="newKeyExpiry">
              <option :value="null">Never expire</option>
              <option :value="7">7 Days</option>
              <option :value="30">30 Days</option>
              <option :value="90">90 Days</option>
              <option :value="365">1 Year</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showGenerateModal = false">Cancel</button>
          <button class="generate-btn" @click="handleGenerate">Generate</button>
        </div>
      </div>
    </div>

    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-card">
        <div class="modal-header">
          <h3>API Key Generated</h3>
        </div>
        <div class="modal-body">
          <div style="background: #fffbeb; border: 1px solid #fcd34d; padding: 12px; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: #b45309; font-size: 0.9rem; font-weight: 600;">⚠️ Please copy your API key now. You won't be able to see it again!</p>
          </div>
          <div style="background: #f1f5f9; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; font-family: monospace; font-size: 1.1rem; color: #0f172a; word-break: break-all; margin-bottom: 1rem; text-align: center;">
            {{ newlyGeneratedKeyString }}
          </div>
        </div>
        <div class="modal-footer" style="flex-direction: column; gap: 8px;">
          <button class="generate-btn" style="width: 100%; margin: 0;" @click="copyKey(newlyGeneratedKeyString)">Copy API Key</button>
          <button class="cancel-btn" style="width: 100%;" @click="showSuccessModal = false">I've stored it safely</button>
        </div>
      </div>
    </div>

    <div v-if="showRevokeModal" class="modal-overlay" @click.self="showRevokeModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>Revoke API Key</h3>
        </div>
        <div class="modal-body">
          <p style="margin: 0; color: #334155;">Are you sure you want to revoke this API key? Applications using this key will immediately lose access. This action cannot be undone.</p>
        </div>
        <div class="modal-footer" style="margin-top: 1rem;">
          <button class="cancel-btn" @click="showRevokeModal = false">Cancel</button>
          <button class="generate-btn danger" style="background: #dc2626; color: white;" @click="handleRevoke">Revoke Key</button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="toastMessage" style="position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #10b981; color: white; padding: 12px 24px; border-radius: 8px; font-weight: 600; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); z-index: 1000; display: flex; align-items: center; gap: 8px;">
      <svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;"><polyline points="20 6 9 17 4 12"></polyline></svg>
      {{ toastMessage }}
    </div>
  </section>

  <!-- Generate Key Modal -->
  <div v-if="showGenerateModal" class="modal-overlay" @click.self="showGenerateModal = false">
    <div class="modal-card">
      <div class="modal-header">
        <h3>Generate New API Key</h3>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>API Key Name</label>
          <input type="text" v-model="newKeyName" placeholder="e.g. Production Key" />
        </div>
        <div class="form-group" style="margin-top: 1rem;">
          <label>Expiration</label>
          <select v-model="newKeyExpiry">
            <option :value="null">Never expire</option>
            <option :value="7">7 Days</option>
            <option :value="30">30 Days</option>
            <option :value="90">90 Days</option>
            <option :value="365">1 Year</option>
          </select>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showGenerateModal = false">Cancel</button>
        <button class="generate-btn" @click="handleGenerate">Generate</button>
      </div>
    </div>
  </div>

  <!-- Success Key Modal -->
  <div v-if="showSuccessModal" class="modal-overlay">
    <div class="modal-card">
      <div class="modal-header">
        <h3>API Key Generated</h3>
      </div>
      <div class="modal-body">
        <div style="background: #fffbeb; border: 1px solid #fcd34d; padding: 12px; border-radius: 8px; margin-bottom: 1rem;">
          <p style="margin: 0; color: #b45309; font-size: 0.9rem; font-weight: 600;">⚠️ Please copy your API key now. You won't be able to see it again!</p>
        </div>
        <div style="background: #f1f5f9; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; font-family: monospace; font-size: 1.1rem; color: #0f172a; word-break: break-all; margin-bottom: 1rem; text-align: center;">
          {{ newlyGeneratedKeyString }}
        </div>
      </div>
      <div class="modal-footer" style="flex-direction: column; gap: 8px;">
        <button class="generate-btn" style="width: 100%; margin: 0;" @click="copyKey(newlyGeneratedKeyString)">Copy API Key</button>
        <button class="cancel-btn" style="width: 100%;" @click="showSuccessModal = false">I've stored it safely</button>
      </div>
    </div>
  </div>

  <!-- Revoke Confirm Modal -->
  <div v-if="showRevokeModal" class="modal-overlay" @click.self="showRevokeModal = false">
    <div class="modal-card">
      <div class="modal-header">
        <h3>Revoke API Key</h3>
      </div>
      <div class="modal-body">
        <p style="margin: 0; color: #334155;">Are you sure you want to revoke this API key? Applications using this key will immediately lose access. This action cannot be undone.</p>
      </div>
      <div class="modal-footer" style="margin-top: 1rem;">
        <button class="cancel-btn" @click="showRevokeModal = false">Cancel</button>
        <button class="generate-btn danger" style="background: #dc2626; color: white;" @click="handleRevoke">Revoke Key</button>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div v-if="toastMessage" style="position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #10b981; color: white; padding: 12px 24px; border-radius: 8px; font-weight: 600; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); z-index: 1000; display: flex; align-items: center; gap: 8px;">
    <svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;"><polyline points="20 6 9 17 4 12"></polyline></svg>
    {{ toastMessage }}
  </div>
</template>
