<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '../../services/auth'

const router = useRouter()
const { authState, isLoggedIn, logoutUser } = useAuth()

function handleLogout() {
  logoutUser()
  router.push('/')
}
</script>

<template>
  <header class="header">
    <div class="header__inner">
      <div class="header__brand">
        <p class="header__tag">MediaCompass</p>
        <h1 class="header__title">Навігація у цифровому контенті</h1>
      </div>

      <nav class="header__nav">
        <RouterLink to="/" class="header__link" active-class="header__link--active">
          Головна
        </RouterLink>

        <RouterLink
          to="/catalog"
          class="header__link"
          active-class="header__link--active"
        >
          Каталог
        </RouterLink>

        <RouterLink
          to="/recommendations"
          class="header__link"
          active-class="header__link--active"
        >
          Рекомендації
        </RouterLink>

        <RouterLink
          to="/forum"
          class="header__link"
          active-class="header__link--active"
        >
          Форум
        </RouterLink>
      </nav>

      <div class="header__actions">
        <input
          type="text"
          class="header__search"
          placeholder="Глобальний пошук (заглушка)"
        />

        <template v-if="isLoggedIn">
          <span class="header__user">
            {{ authState.user?.name }}
          </span>

          <RouterLink
            to="/profile"
            class="header__button header__button--primary"
          >
            Профіль
          </RouterLink>

          <button class="header__button" type="button" @click="handleLogout">
            Вийти
          </button>
        </template>

        <template v-else>
          <RouterLink to="/login" class="header__button">
            Увійти
          </RouterLink>

          <RouterLink
            to="/register"
            class="header__button header__button--primary"
          >
            Реєстрація
          </RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  width: 100%;
  border-bottom: 1px solid #1f2937;
  background: rgba(2, 6, 23, 0.9);
  backdrop-filter: blur(12px);
}

.header__inner {
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto;
  padding: 18px 0;
  display: grid;
  grid-template-columns: 1.2fr 1fr 1.2fr;
  gap: 20px;
  align-items: center;
}

.header__brand {
  min-width: 0;
}

.header__tag {
  margin: 0 0 6px;
  color: #60a5fa;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
}

.header__title {
  margin: 0;
  font-size: 22px;
  line-height: 1.2;
  color: #f8fafc;
}

.header__nav {
  display: flex;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
}

.header__link {
  color: #cbd5e1;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.header__link:hover {
  color: #60a5fa;
}

.header__link--active {
  color: #60a5fa;
}

.header__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.header__search {
  width: 100%;
  max-width: 240px;
  padding: 10px 12px;
  border: 1px solid #374151;
  border-radius: 12px;
  background: #0f172a;
  color: #e5e7eb;
  outline: none;
}

.header__search::placeholder {
  color: #94a3b8;
}

.header__search:focus {
  border-color: #60a5fa;
}

.header__button {
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 10px 14px;
  background: transparent;
  color: #e5e7eb;
  cursor: pointer;
  font-weight: 600;
  text-decoration: none;
}

.header__button:hover {
  border-color: #60a5fa;
}

.header__button--primary {
  background: #2563eb;
  border-color: #2563eb;
  color: white;
}

.header__button--primary:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

.header__user {
  color: #cbd5e1;
  font-weight: 600;
}

@media (max-width: 1024px) {
  .header__inner {
    grid-template-columns: 1fr;
  }

  .header__nav {
    justify-content: flex-start;
  }

  .header__actions {
    justify-content: flex-start;
  }
}
</style>