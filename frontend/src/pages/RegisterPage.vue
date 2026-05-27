<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { registerUser } from '../services/auth'

const router = useRouter()
const route = useRoute()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)
const errorText = ref('')

const redirectTarget = computed(() => {
  const redirect = route.query.redirect
  return typeof redirect === 'string' && redirect.trim() ? redirect : '/'
})

async function handleSubmit() {
  errorText.value = ''

  if (!username.value.trim() || !email.value.trim() || !password.value.trim()) {
    errorText.value = 'Please fill in all required fields.'
    return
  }

  if (username.value.trim().length < 3) {
    errorText.value = 'Username must be at least 3 characters long.'
    return
  }

  if (password.value.length < 6) {
    errorText.value = 'Password must be at least 6 characters long.'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorText.value = 'Passwords do not match.'
    return
  }

  isSubmitting.value = true

  try {
    await registerUser({
      username: username.value.trim(),
      email: email.value.trim(),
      password: password.value,
    })

    await router.push(redirectTarget.value)
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Registration failed.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="auth-page__card">
      <div class="auth-page__copy">
        <p class="auth-page__eyebrow">CREATE ACCOUNT</p>
        <h1 class="auth-page__title">Sign up for MediaCompass</h1>
        <p class="auth-page__text">
          Create your account to unlock recommendations, forum access, and your
          personal media profile.
        </p>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <label class="auth-form__field">
          <span>Username</span>
          <input
            v-model="username"
            type="text"
            placeholder="Choose a username"
            autocomplete="username"
          />
        </label>

        <label class="auth-form__field">
          <span>Email</span>
          <input
            v-model="email"
            type="email"
            placeholder="you@example.com"
            autocomplete="email"
          />
        </label>

        <label class="auth-form__field">
          <span>Password</span>
          <input
            v-model="password"
            type="password"
            placeholder="At least 6 characters"
            autocomplete="new-password"
          />
        </label>

        <label class="auth-form__field">
          <span>Confirm Password</span>
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="Repeat your password"
            autocomplete="new-password"
          />
        </label>

        <p v-if="errorText" class="auth-form__error">
          {{ errorText }}
        </p>

        <button
          type="submit"
          class="auth-form__submit"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? 'Creating account...' : 'Sign Up' }}
        </button>
      </form>

      <p class="auth-page__switch">
        Already have an account?
        <RouterLink to="/login">Log in</RouterLink>
      </p>
    </div>
  </section>
</template>

<style scoped>
.auth-page {
  width: 100%;
  min-height: calc(100vh - 180px);
  padding: 40px 16px 56px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-page__card {
  width: min(560px, 100%);
  padding: 32px;
  border-radius: 28px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.16), transparent 32%),
    rgba(8, 14, 24, 0.92);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.24);
}

.auth-page__copy {
  margin-bottom: 24px;
}

.auth-page__eyebrow {
  margin: 0 0 10px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.auth-page__title {
  margin: 0 0 12px;
  color: #f8fafc;
  font-size: clamp(34px, 4vw, 46px);
  line-height: 1.02;
  letter-spacing: -0.04em;
}

.auth-page__text {
  margin: 0;
  color: #94a3b8;
  line-height: 1.75;
  font-size: 16px;
}

.auth-form {
  display: grid;
  gap: 16px;
}

.auth-form__field {
  display: grid;
  gap: 8px;
}

.auth-form__field span {
  color: #cbd5e1;
  font-size: 14px;
  font-weight: 600;
}

.auth-form__field input {
  width: 100%;
  height: 50px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  padding: 0 14px;
  outline: none;
}

.auth-form__field input::placeholder {
  color: #64748b;
}

.auth-form__error {
  margin: 0;
  color: #fca5a5;
  font-size: 14px;
}

.auth-form__submit {
  min-height: 52px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
}

.auth-form__submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.auth-page__switch {
  margin: 18px 0 0;
  color: #94a3b8;
  font-size: 14px;
}

.auth-page__switch a {
  color: #60a5fa;
  text-decoration: none;
  font-weight: 700;
}
</style>