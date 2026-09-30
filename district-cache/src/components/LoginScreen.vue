<template>
  <div class="login-screen">
    <div class="login-box">
      <h2>District Cache Access</h2>
      <p>Enter your 6-digit PIN to continue</p>
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
            :disabled="isLoading || isLockedOut"
            required
          />
        </div>
        
        <!-- Lockout Message -->
        <div v-if="isLockedOut" class="error-msg lockout-msg">
          ⚠️ {{ errorMsg }}
        </div>
        <!-- Standard Error Message -->
        <div v-else-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

        <button type="submit" :disabled="isLoading || isLockedOut || pin.length !== 6" class="submit-btn">
          {{ isLoading ? 'Checking...' : (isLockedOut ? 'Blocked' : 'Unlock') }}
        </button>
      </form>
      <div v-if="redirectPath && !isLockedOut" class="redirect-info">
        <small>After login, you'll be redirected to: {{ redirectPath }}</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

// Expanded to 6 digits
const pinDigits = ref(['', '', '', '', '', '']) 
const inputs = ref([])
const isLoading = ref(false)
const errorMsg = ref('')

// Lockout State
const isLockedOut = ref(false)
const lockoutTimer = ref(null)
const lockoutSeconds = ref(0)

const pin = computed(() => pinDigits.value.join(''))

const redirectPath = computed(() => route.query.redirect)

onMounted(() => {
  inputs.value[0]?.focus()
})

// Clean up timer if component is destroyed
onUnmounted(() => {
  if (lockoutTimer.value) clearInterval(lockoutTimer.value)
})

const handleDigitInput = (index, event) => {
  const value = event.target.value
  if (value.length === 1 && index < 5) { // Changed from 3 to 5
    inputs.value[index + 1]?.focus()
  }
}

const handleBackspace = (index, event) => {
  if (event.target.value === '' && index > 0) {
    inputs.value[index - 1]?.focus()
  }
}

const startLockoutTimer = () => {
  if (lockoutTimer.value) clearInterval(lockoutTimer.value)
  lockoutTimer.value = setInterval(() => {
    lockoutSeconds.value--
    if (lockoutSeconds.value <= 0) {
      clearInterval(lockoutTimer.value)
      isLockedOut.value = false
      errorMsg.value = ''
      pinDigits.value = ['', '', '', '', '', '']
      inputs.value[0]?.focus()
    } else {
      const mins = Math.floor(lockoutSeconds.value / 60)
      const secs = lockoutSeconds.value % 60
      errorMsg.value = `Login blocked. Try again in ${mins}:${secs.toString().padStart(2, '0')}.`
    }
  }, 1000)
}

const submitPinLogin = async () => {
  if (pin.value.length !== 6) return // Changed from 4 to 6
  if (isLockedOut.value) return

  isLoading.value = true
  errorMsg.value = ''

  const result = await auth.pinLogin(pin.value)

  if (result.success) {
    let destination = redirectPath.value
    if (!destination || destination === '/' || destination === '/apps/cache/') {
      destination = '/W1/FS40' 
    }
    router.replace(destination)
  } else {
    errorMsg.value = result.message || 'Invalid PIN. Please try again.'
    
    // Check if backend triggered the 5-minute lockout (HTTP 429)
    if (result.status === 429 || errorMsg.value.includes('blocked for 5 minutes')) {
      isLockedOut.value = true
      lockoutSeconds.value = 300 // 5 minutes in seconds
      startLockoutTimer()
    } else {
      // Standard failure: clear inputs and refocus
      pinDigits.value = ['', '', '', '', '', '']
      inputs.value[0]?.focus()
    }
  }

  isLoading.value = false
}
</script>

