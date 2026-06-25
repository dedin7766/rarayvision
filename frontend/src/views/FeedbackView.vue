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
  <div class="feedback-page" style="padding: 4rem 1.5rem; max-width: 600px; margin: 0 auto; color: #0f172a;">
    <div style="text-align: center; margin-bottom: 3rem;">
      <p style="text-transform: uppercase; letter-spacing: 2px; color: #6366f1; font-weight: 700; margin-bottom: 0.5rem; font-size: 0.9rem;">We Value Your Input</p>
      <h1 style="font-size: 3rem; font-weight: 800; line-height: 1.1; margin-bottom: 1rem; letter-spacing: -0.02em;">Send Feedback</h1>
      <p style="font-size: 1.1rem; color: #475569; line-height: 1.6;">
        Have a suggestion, found a bug, or want to request a feature? Let us know below!
      </p>
    </div>

    <div style="background: white; border-radius: 16px; padding: 2.5rem; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); border: 1px solid #f1f5f9;">
      <form @submit.prevent="submitFeedback" style="display: flex; flex-direction: column; gap: 1.5rem;">
        <div>
          <label style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: #334155;">Your Name</label>
          <input type="text" v-model="name" placeholder="John Doe" required style="width: 100%; padding: 0.75rem 1rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; outline: none; transition: border-color 0.2s;" onfocus="this.style.borderColor='#000'" onblur="this.style.borderColor='#cbd5e1'" />
        </div>
        <div>
          <label style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: #334155;">Email Address</label>
          <input type="email" v-model="email" placeholder="john@example.com" required style="width: 100%; padding: 0.75rem 1rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; outline: none; transition: border-color 0.2s;" onfocus="this.style.borderColor='#000'" onblur="this.style.borderColor='#cbd5e1'" />
        </div>
        <div>
          <label style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: #334155;">Message</label>
          <textarea v-model="message" rows="5" placeholder="Write your suggestions, bugs, or questions here..." required style="width: 100%; padding: 0.75rem 1rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; outline: none; resize: vertical; transition: border-color 0.2s;" onfocus="this.style.borderColor='#000'" onblur="this.style.borderColor='#cbd5e1'"></textarea>
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
</template>

<style scoped>
/* Scoped styles */
</style>
