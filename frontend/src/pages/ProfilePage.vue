<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuth, logoutUser } from '../services/auth'

const router = useRouter()
const { authState } = useAuth()

function handleLogout() {
  logoutUser()
  router.push('/')
}
</script>

<template>
  <section class="profile-page">
    <div class="profile-page__inner">
      <h2 class="profile-page__title">Профіль</h2>

      <div v-if="authState.user" class="profile-card">
        <p><strong>Ім’я:</strong> {{ authState.user.name }}</p>
        <p><strong>Email:</strong> {{ authState.user.email }}</p>

        <button class="profile-page__button" @click="handleLogout">
          Вийти
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.profile-page {
  padding: 40px 16px 56px;
}

.profile-page__inner {
  width: min(920px, 100%);
  margin: 0 auto;
  padding: 32px;
  border-radius: 24px;
  background: #071533;
}

.profile-page__title {
  margin: 0 0 20px;
  color: #f8fafc;
}

.profile-card {
  padding: 24px;
  border-radius: 18px;
  background: #1f2937;
  color: #e5e7eb;
}

.profile-page__button {
  margin-top: 16px;
  border: none;
  border-radius: 12px;
  padding: 12px 18px;
  background: #2563eb;
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.profile-page__button:hover {
  background: #1d4ed8;
}
</style>