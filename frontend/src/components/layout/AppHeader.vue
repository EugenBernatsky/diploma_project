<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuth } from '../../services/auth'

const route = useRoute()
const router = useRouter()
const { authState, isLoggedIn, logoutUser } = useAuth()

const userInitial = computed(() => {
  return authState.user?.name?.trim()?.charAt(0)?.toUpperCase() || 'U'
})

function isActive(path: string) {
  return route.path === path
}

function handleLogout() {
  logoutUser()
  router.push('/')
}
</script>

<template>
  <header class="header">
    <div class="header__inner">
      <RouterLink to="/" class="header__brand">
        <div class="header__logo-mark">
          <span class="header__logo-dot"></span>
        </div>
        <span class="header__brand-text">MediaCompass</span>
      </RouterLink>

      <nav class="header__nav">
        <RouterLink
          to="/"
          class="header__nav-link"
          :class="{ 'header__nav-link--active': isActive('/') }"
        >
          Home
        </RouterLink>

        <RouterLink
          to="/catalog"
          class="header__nav-link"
          :class="{ 'header__nav-link--active': isActive('/catalog') }"
        >
          Catalog
        </RouterLink>

        <RouterLink
          to="/recommendations"
          class="header__nav-link"
          :class="{ 'header__nav-link--active': isActive('/recommendations') }"
        >
          Recommendations
        </RouterLink>

        <RouterLink
          to="/forum"
          class="header__nav-link"
          :class="{ 'header__nav-link--active': isActive('/forum') }"
        >
          Forum
        </RouterLink>
      </nav>

      <div class="header__actions">
        <label class="header__search">
          <svg class="header__search-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M10.5 18a7.5 7.5 0 1 1 5.303-2.197L21 21"
              fill="none"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.8"
            />
          </svg>

          <input type="text" placeholder="Search title, author..." />
        </label>

        <button class="header__icon-button" type="button" aria-label="Notifications">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M15 17H5.5a1 1 0 0 1-.8-1.6L6 13.5V10a6 6 0 1 1 12 0v3.5l1.3 1.9a1 1 0 0 1-.8 1.6H18"
              fill="none"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.8"
            />
            <path
              d="M10 19a2 2 0 0 0 4 0"
              fill="none"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.8"
            />
          </svg>
        </button>

        <template v-if="isLoggedIn">
          <RouterLink to="/profile" class="header__avatar" aria-label="Open profile">
            <span>{{ userInitial }}</span>
            <span class="header__avatar-status"></span>
          </RouterLink>

          <button type="button" class="header__logout" @click="handleLogout">
            Log out
          </button>
        </template>

        <template v-else>
          <RouterLink to="/login" class="header__auth-link">
            Log in
          </RouterLink>

          <RouterLink to="/register" class="header__auth-link header__auth-link--primary">
            Sign up
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
  z-index: 50;
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(3, 8, 18, 0.85);
  backdrop-filter: blur(14px);
}

.header__inner {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  min-height: 74px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 28px;
  align-items: center;
}

.header__brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  color: #ffffff;
  text-decoration: none;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.header__logo-mark {
  position: relative;
  width: 32px;
  height: 32px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 9px;
  background: linear-gradient(180deg, #ffffff, #dbeafe);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.header__logo-mark::before {
  content: '';
  width: 14px;
  height: 14px;
  border: 2px solid #0f172a;
  border-radius: 999px;
}

.header__logo-dot {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: #0f172a;
}

.header__brand-text {
  font-size: 24px;
}

.header__nav {
  display: flex;
  justify-content: center;
  gap: 22px;
  flex-wrap: wrap;
}

.header__nav-link {
  position: relative;
  color: #cbd5e1;
  text-decoration: none;
  font-weight: 600;
  padding: 4px 0;
}

.header__nav-link:hover,
.header__nav-link--active {
  color: #60a5fa;
}

.header__nav-link--active::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -14px;
  height: 2px;
  border-radius: 999px;
  background: #3b82f6;
}

.header__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

.header__search {
  position: relative;
  display: flex;
  align-items: center;
  width: 300px;
  height: 44px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.8);
}

.header__search input {
  width: 100%;
  height: 100%;
  padding: 0 16px 0 42px;
  border: none;
  outline: none;
  border-radius: inherit;
  background: transparent;
  color: #e2e8f0;
}

.header__search input::placeholder {
  color: #64748b;
}

.header__search-icon {
  position: absolute;
  left: 14px;
  width: 18px;
  height: 18px;
  color: #64748b;
}

.header__icon-button {
  width: 42px;
  height: 42px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.8);
  color: #e2e8f0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.header__icon-button svg {
  width: 18px;
  height: 18px;
}

.header__avatar {
  position: relative;
  width: 42px;
  height: 42px;
  border-radius: 999px;
  background: linear-gradient(135deg, #f8fafc 0%, #dbeafe 100%);
  color: #0f172a;
  font-weight: 800;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.header__avatar-status {
  position: absolute;
  right: 1px;
  bottom: 1px;
  width: 10px;
  height: 10px;
  border: 2px solid #020617;
  border-radius: 999px;
  background: #22c55e;
}

.header__logout,
.header__auth-link {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(15, 23, 42, 0.8);
  color: #e2e8f0;
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.header__auth-link--primary {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  border-color: transparent;
  color: #ffffff;
}

@media (max-width: 1180px) {
  .header__inner {
    grid-template-columns: 1fr;
    padding: 16px 0;
  }

  .header__nav {
    justify-content: flex-start;
  }

  .header__actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}

@media (max-width: 900px) {
  .header__inner {
    width: min(100%, calc(100% - 32px));
  }

  .header__search {
    width: 100%;
    max-width: 360px;
  }
}

@media (max-width: 640px) {
  .header__brand-text {
    font-size: 20px;
  }

  .header__nav {
    gap: 14px;
  }

  .header__actions {
    gap: 10px;
  }
}
</style>