<template>
  <div class="login-screen">
    <div class="login-box">
      <h2>District Cache Access</h2>
      <p>Enter your 4-digit PIN to continue</p>
      
      <form @submit.prevent="submitPinLogin">
        <div class="pin-inputs">
          <input 
            v-for="(digit, index) in pinDigits" 
            :key="index"
            :ref="el => { if (el) inputs[index] = el }"
            type="text" 
            inputmode="numeric"
            pattern="[0-9]*"
            maxlength="1"
            v-model="pinDigits[index]"
            @input="handleDigitInput(index, $event)"
            @keydown.backspace="handleBackspace(index, $event)"
            class="pin-digit"
            :disabled="isLoading"
            required
          />
        </div>
        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
        <button type="submit" :disabled="isLoading || pin.length !== 4" class="submit-btn">
          {{ isLoading ? 'Checking...' : 'Unlock' }}
        </button>
      </form>
      
      <div v-if="redirectPath" class="redirect-info">
        <small>After login, you'll be redirected to: {{ redirectPath }}</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const pinDigits = ref(['', '', '', ''])
const inputs = ref([])
const isLoading = ref(false)
const errorMsg = ref('')

const pin = computed(() => pinDigits.value.join(''))

// 🎯 Capture the redirect path from the query parameter
const redirectPath = computed(() => {
  const path = route.query.redirect
  console.log('🔑 [LoginScreen] Redirect path from query:', path)
  return path
})

onMounted(() => {
  inputs.value[0]?.focus()
})

const handleDigitInput = (index, event) => {
  const value = event.target.value
  if (value.length === 1 && index < 3) {
    inputs.value[index + 1]?.focus()
  }
}

const handleBackspace = (index, event) => {
  if (event.target.value === '' && index > 0) {
    inputs.value[index - 1]?.focus()
  }
}

const submitPinLogin = async () => {
  if (pin.value.length !== 4) return

  isLoading.value = true
  errorMsg.value = ''

  console.log('🔑 [LoginScreen] Attempting PIN login with:', pin.value)
  console.log('🔑 [LoginScreen] Full route object:', route)
  console.log('🔑 [LoginScreen] Route query:', route.query)
  
  const result = await auth.pinLogin(pin.value)
  console.log('🔑 [LoginScreen] Login result:', result)

  if (result.success) {
    // 🎯 Determine where to redirect
    let destination = redirectPath.value
    
    // If no redirect path or it's just the login page, go to a default location
    if (!destination || destination === '/' || destination === '/apps/cache/') {
      destination = '/W1/FS40' // Default operational route
      console.log('🔑 [LoginScreen] No valid redirect path, using default:', destination)
    } else {
      console.log('🚀 [LoginScreen] Redirecting to saved path:', destination)
    }
    
    // Use replace to prevent user from clicking "back" to login screen
    router.replace(destination)
  } else {
    console.warn('❌ [LoginScreen] Login failed:', result.message)
    errorMsg.value = result.message || 'Invalid PIN. Please try again.'
    pinDigits.value = ['', '', '', '']
    inputs.value[0]?.focus()
  }

  isLoading.value = false
}
</script>

<style scoped>
.login-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}
.login-box {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  text-align: center;
  width: 320px;
}
.pin-inputs {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin: 1.5rem 0;
}
.pin-digit {
  width: 50px;
  height: 60px;
  font-size: 1.5rem;
  text-align: center;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.pin-digit:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}
.submit-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}
.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.error-msg {
  color: #e74c3c;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
.redirect-info {
  margin-top: 1.5rem;
  padding: 0.75rem;
  background-color: #e8f5e9;
  border-radius: 4px;
  color: #2e7d32;
  font-size: 0.85rem;
}
</style>