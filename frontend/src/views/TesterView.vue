<script setup>
import { ref, computed } from 'vue'
import { store } from '../store'
import { API_BASE_URL } from '../utils'

const testEndpoint = ref('GET:/api/v1/faces')
const testUserId = ref('')
const testUserName = ref('')
const testFile = ref(null)
const testResponse = ref('')
const isSendingTest = ref(false)

const endpointOptions = [
  { value: 'GET:/api/v1/faces', label: 'GET /api/v1/faces' },
  { value: 'GET:/api/v1/faces/{user_id}', label: 'GET /api/v1/faces/{user_id}' },
  { value: 'POST:/api/v1/faces', label: 'POST /api/v1/faces (Register)' },
  { value: 'POST:/api/v1/faces/no-liveness', label: 'POST /api/v1/faces/no-liveness' },
  { value: 'PUT:/api/v1/faces/{user_id}', label: 'PUT /api/v1/faces/{user_id}' },
  { value: 'DELETE:/api/v1/faces/{user_id}', label: 'DELETE /api/v1/faces/{user_id}' },
  { value: 'POST:/api/v1/faces/compare', label: 'POST /api/v1/faces/compare' },
  { value: 'POST:/api/v1/faces/extract', label: 'POST /api/v1/faces/extract' },
  { value: 'POST:/api/v1/faces/recognize', label: 'POST /api/v1/faces/recognize' },
  { value: 'POST:/api/v1/faces/recognize/multi', label: 'POST /api/v1/faces/recognize/multi' }
]

const currentMethod = computed(() => testEndpoint.value.split(':')[0])
const currentPath = computed(() => testEndpoint.value.split(':')[1])

const needsUserId = computed(() =>
  ['GET:/api/v1/faces/{user_id}', 'POST:/api/v1/faces/compare', 'PUT:/api/v1/faces/{user_id}', 'DELETE:/api/v1/faces/{user_id}'].includes(testEndpoint.value)
)
const isUserIdRequired = computed(() =>
  ['GET:/api/v1/faces/{user_id}', 'PUT:/api/v1/faces/{user_id}', 'DELETE:/api/v1/faces/{user_id}'].includes(testEndpoint.value)
)
const needsUserName = computed(() =>
  ['POST:/api/v1/faces', 'POST:/api/v1/faces/no-liveness'].includes(testEndpoint.value)
)
const needsFile = computed(() =>
  currentMethod.value !== 'GET' && currentMethod.value !== 'DELETE'
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
    let urlPath = currentPath.value

    if (currentMethod.value === 'GET') {
      urlPath = urlPath.replace('{user_id}', testUserId.value.trim())
      options = { method: 'GET', headers: { 'Authorization': `Bearer ${activeKey}` } }
    } else if (currentMethod.value === 'DELETE') {
      urlPath = urlPath.replace('{user_id}', testUserId.value.trim())
      options = { method: 'DELETE', headers: { 'Authorization': `Bearer ${activeKey}` } }
    } else if (currentMethod.value === 'PUT') {
      urlPath = urlPath.replace('{user_id}', testUserId.value.trim())
      const fd = new FormData()
      if (testFile.value) fd.append('file', testFile.value)
      if (needsUserName.value && testUserName.value.trim()) fd.append('user_name', testUserName.value.trim())
      options = { method: 'PUT', body: fd, headers: { 'Authorization': `Bearer ${activeKey}` } }
    } else {
      const fd = new FormData()
      if (testFile.value) fd.append('file', testFile.value)
      if (needsUserId.value && testUserId.value.trim()) fd.append('user_id', testUserId.value.trim())
      if (needsUserName.value && testUserName.value.trim()) fd.append('user_name', testUserName.value.trim())
      options = { method: 'POST', body: fd, headers: { 'Authorization': `Bearer ${activeKey}` } }
    }
    const res = await fetch(`${API_BASE_URL}${urlPath}`, options)
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
