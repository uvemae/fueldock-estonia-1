<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-section">
        <img src="/pic/FuelDock-1_no_bg_s.png" alt="FuelDock" class="logo" />
        <h1>FuelDock Estonia</h1>
        <p class="tagline">Marina Fuel Station Locator</p>
      </div>

      <!-- Toggle between Login/Signup -->
      <div class="mode-tabs">
        <button
          :class="{ active: mode === 'login' }"
          @click="mode = 'login'"
        >
          Login
        </button>
        <button
          :class="{ active: mode === 'signup' }"
          @click="mode = 'signup'"
        >
          Sign Up
        </button>
      </div>

      <!-- Login Form -->
      <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label>Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="your@email.com"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            required
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

        <button type="button" @click="mode = 'forgot'" class="link-btn">
          Forgot password?
        </button>
      </form>

      <!-- Signup Form -->
      <form v-if="mode === 'signup'" @submit.prevent="handleSignup" class="auth-form">
        <div class="form-group">
          <label>Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="your@email.com"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            required
            autocomplete="new-password"
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label>Confirm Password</label>
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="••••••••"
            required
            autocomplete="new-password"
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? 'Creating account...' : 'Create Account' }}
        </button>

        <p class="info-text">
          You'll receive a confirmation email to activate your account.
        </p>
      </form>

      <!-- Forgot Password Form -->
      <form v-if="mode === 'forgot'" @submit.prevent="handleResetPassword" class="auth-form">
        <div class="form-group">
          <label>Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="your@email.com"
            required
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? 'Sending...' : 'Send Reset Link' }}
        </button>

        <button type="button" @click="mode = 'login'" class="link-btn">
          Back to Login
        </button>
      </form>

      <!-- Error/Success Messages -->
      <div v-if="error" class="message error-message">
        {{ error }}
      </div>

      <div v-if="success" class="message success-message">
        {{ success }}
      </div>

      <!-- Continue as Guest -->
      <div class="guest-section">
        <button @click="continueAsGuest" class="guest-btn">
          Continue as Guest
        </button>
        <p class="guest-info">
          Limited view: See marina locations only
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth'

const emit = defineEmits(['guest-mode'])

const { signIn, signUp, resetPassword } = useAuth()

const mode = ref('login') // 'login', 'signup', 'forgot'
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

async function handleLogin() {
  error.value = ''
  success.value = ''

  if (!email.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }

  loading.value = true

  try {
    await signIn(email.value, password.value)
    // App.vue will handle redirect via auth state change
  } catch (err) {
    error.value = err.message || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}

async function handleSignup() {
  error.value = ''
  success.value = ''

  if (!email.value || !password.value || !confirmPassword.value) {
    error.value = 'Please fill in all fields'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  loading.value = true

  try {
    await signUp(email.value, password.value)
    success.value = 'Account created! Please check your email to confirm your account.'
    email.value = ''
    password.value = ''
    confirmPassword.value = ''

    // Switch to login mode after 3 seconds
    setTimeout(() => {
      mode.value = 'login'
      success.value = ''
    }, 3000)
  } catch (err) {
    error.value = err.message || 'Signup failed. Please try again.'
  } finally {
    loading.value = false
  }
}

async function handleResetPassword() {
  error.value = ''
  success.value = ''

  if (!email.value) {
    error.value = 'Please enter your email address'
    return
  }

  loading.value = true

  try {
    await resetPassword(email.value)
    success.value = 'Password reset link sent! Check your email.'
    setTimeout(() => {
      mode.value = 'login'
      success.value = ''
    }, 3000)
  } catch (err) {
    error.value = err.message || 'Failed to send reset link.'
  } finally {
    loading.value = false
  }
}

function continueAsGuest() {
  emit('guest-mode')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  padding: 2rem;
}

.login-card {
  background: white;
  border-radius: 24px;
  padding: 3rem;
  max-width: 450px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.logo-section {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  width: 120px;
  height: auto;
  margin-bottom: 1rem;
}

.logo-section h1 {
  margin: 0 0 0.5rem 0;
  color: #1e40af;
  font-size: 1.75rem;
}

.tagline {
  color: #6b7280;
  margin: 0;
  font-size: 0.95rem;
}

.mode-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  background: #f3f4f6;
  padding: 0.25rem;
  border-radius: 12px;
}

.mode-tabs button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: transparent;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  color: #6b7280;
}

.mode-tabs button.active {
  background: white;
  color: #1e40af;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.875rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
}

.submit-btn {
  padding: 1rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(16, 185, 129, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.link-btn {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0.5rem;
  text-decoration: underline;
}

.link-btn:hover {
  color: #2563eb;
}

.info-text {
  font-size: 0.85rem;
  color: #6b7280;
  text-align: center;
  margin: 0;
}

.message {
  padding: 1rem;
  border-radius: 10px;
  font-size: 0.9rem;
  text-align: center;
  margin-top: 1rem;
  animation: slideIn 0.3s ease;
}

.error-message {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.success-message {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.guest-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e5e7eb;
  text-align: center;
}

.guest-btn {
  padding: 0.875rem 2rem;
  background: white;
  color: #6b7280;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.guest-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #f0f9ff;
}

.guest-info {
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: #9ca3af;
}
</style>
