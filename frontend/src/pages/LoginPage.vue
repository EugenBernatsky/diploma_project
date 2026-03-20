<script setup lang="ts">
import { useRouter } from 'vue-router'
import { loginDemoUser } from '../services/auth'

const router = useRouter()

function handleDemoLogin() {
  loginDemoUser()
  router.push('/profile')
}
</script>

<template>
  <section class="auth-page">
    <div class="auth-page__inner">
      <h2 class="auth-page__title">Вхід</h2>
      <p class="auth-page__text">
        Поки що це demo-авторизація без бекенду.
      </p>

      <button class="auth-page__button" @click="handleDemoLogin">
        Увійти як demo-користувач
      </button>
    </div>
  </section>
</template>

<style scoped>
.auth-page {
  padding: 40px 16px 56px;
}

.auth-page__inner {
  width: min(720px, 100%);
  margin: 0 auto;
  padding: 32px;
  border-radius: 24px;
  background: #071533;
}

.auth-page__title {
  margin: 0 0 12px;
  color: #f8fafc;
}

.auth-page__text {
  margin: 0 0 20px;
  color: #cbd5e1;
}

.auth-page__button {
  border: none;
  border-radius: 12px;
  padding: 12px 18px;
  background: #2563eb;
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.auth-page__button:hover {
  background: #1d4ed8;
}
</style>