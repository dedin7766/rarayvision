<script setup>
import { ref, computed } from 'vue'
import { store } from '../store'
import { API_BASE_URL } from '../utils'

const testEndpoint = ref('/api/v1/check-liveness')
const testUserId = ref('')
const testUserName = ref('')
const testFile = ref(null)
const testResponse = ref('')
const isSendingTest = ref(false)

const endpointOptions = [
  { value: '/api/v1/list-faces', label: 'GET /api/v1/list-faces' },
  { value: '/api/v1/check-liveness', label: 'POST /api/v1/check-liveness' },
  { value: '/api/v1/compare-face', label: 'POST /api/v1/compare-face' },
  { value: '/api/v1/extract-face', label: 'POST /api/v1/extract-face' },
  { value: '/api/v1/register-face', label: 'POST /api/v1/register-face (Liveness)' },
  { value: '/api/v1/register-face-noliveness', label: 'POST /api/v1/register-face (No Liveness)' },
  { value: '/api/v1/update-face', label: 'PUT /api/v1/update-face' },
  { value: '/api/v1/delete-face', label: 'DELETE /api/v1/delete-face' },
  { value: '/api/v1/recognize', label: 'POST /api/v1/recognize' }
]

const needsUserId = computed(() =>
  ['/api/v1/compare-face','/api/v1/update-face','/api/v1/delete-face'].includes(testEndpoint.value)
)
const isUserIdRequired = computed(() =>
  ['/api/v1/update-face','/api/v1/delete-face'].includes(testEndpoint.value)
)
const needsUserName = computed(() =>
  ['/api/v1/register-face','/api/v1/register-face-noliveness'].includes(testEndpoint.value)
)
const needsFile = computed(() =>
  testEndpoint.value !== '/api/v1/delete-face' && testEndpoint.value !== '/api/v1/list-faces'
)

const testSelectedLabel = computed(() =>
  endpointOptions.find(i => i.value === testEndpoint.value)?.label || testEndpoint.value
)

const runApiTest = async () => {
  const activeKey = localStorage.getItem('rarayvision-token')
  if (!activeKey) {
    testResponse.value = '❌ Error: Missing API Key or session token.'
    return
  }
  isSendingTest.value = true
  testResponse.value = 'Sending request...'
  try {
    let options = {}
    if (testEndpoint.value === '/api/v1/list-faces') {
      options = { method: 'GET', headers: { 'Authorization': `Bearer ${activeKey}` } }
    } else {
      const fd = new FormData()
      if (testFile.value) fd.append('file', testFile.value)
      if (needsUserId.value && testUserId.value.trim()) fd.append('user_id', testUserId.value.trim())
      if (needsUserName.value && testUserName.value.trim()) fd.append('user_name', testUserName.value.trim())
      const method = testEndpoint.value === '/api/v1/delete-face' ? 'DELETE' : testEndpoint.value === '/api/v1/update-face' ? 'PUT' : 'POST'
      options = { method, body: fd, headers: { 'Authorization': `Bearer ${activeKey}` } }
    }
    const res = await fetch(`${API_BASE_URL}${testEndpoint.value}`, options)
    testResponse.value = JSON.stringify(await res.json(), null, 2)
  } catch (error) {
    testResponse.value = JSON.stringify({ error: error.message }, null, 2)
  } finally {
    isSendingTest.value = false
  }
}
</script>

<template>
  <section class="tester-page">
    <div class="tester-page-header">
      <div>
        <p class="eyebrow">Tools</p>
        <h2>API Tester</h2>
      </div>
    </div>
    <section class="tester-panel tester-panel-full">
      <div class="tester-header">
        <div>
          <p class="eyebrow">Testing</p>
          <h3>Request Builder</h3>
        </div>
        <select v-model="testEndpoint">
          <option v-for="item in endpointOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
        </select>
      </div>
      <div class="tester-controls">
        <label v-if="needsUserId">
          <span>User ID {{ isUserIdRequired ? '(Required)' : '(Optional)' }}</span>
          <input v-model="testUserId" placeholder="Enter user id" />
        </label>
        <label v-if="needsUserName">
          <span>User Name (Optional)</span>
          <input v-model="testUserName" placeholder="Enter name" />
        </label>
        <label v-if="needsFile">
          File Upload
          <input type="file" @change="e => testFile = e.target.files?.[0] || null" />
        </label>
        <button class="send-btn" @click="runApiTest" :disabled="isSendingTest">
          {{ isSendingTest ? 'Running...' : 'Run Request' }}
        </button>
      </div>
      <div class="tester-response">
        <p class="response-label">{{ testSelectedLabel }}</p>
        <pre>{{ testResponse || 'No response yet.' }}</pre>
      </div>
    </section>
  </section>
</template>
