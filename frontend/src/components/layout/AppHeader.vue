<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuth } from '../../services/auth'
import { getAvatarImageUrl } from '../../utils/avatars'
import {
  getNotifications,
  getUnreadNotificationsCount,
  markAllNotificationsAsRead,
  markNotificationAsRead,
} from '../../services/notifications'
import type { UserNotification } from '../../types/notification'

const route = useRoute()
const router = useRouter()
const { authState, isLoggedIn, logoutUser } = useAuth()

const userInitial = computed(() => {
  return authState.user?.username?.trim()?.charAt(0)?.toUpperCase() || 'U'
})

const userAvatarUrl = computed(() => {
  return getAvatarImageUrl(authState.user?.avatar_id)
})

const notifications = ref<UserNotification[]>([])
const unreadNotificationsCount = ref(0)
const isNotificationsOpen = ref(false)
const isNotificationsLoading = ref(false)
const notificationsError = ref('')

let notificationsIntervalId: number | undefined

const visibleNotifications = computed(() => {
  return notifications.value.slice(0, 8)
})

function formatNotificationTime(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return ''
  }

  const diffMs = Date.now() - date.getTime()
  const diffMinutes = Math.max(1, Math.floor(diffMs / (1000 * 60)))

  if (diffMinutes < 60) {
    return `${diffMinutes}m ago`
  }

  const diffHours = Math.floor(diffMinutes / 60)

  if (diffHours < 24) {
    return `${diffHours}h ago`
  }

  const diffDays = Math.floor(diffHours / 24)

  if (diffDays < 7) {
    return `${diffDays}d ago`
  }

  return date.toLocaleDateString('en-GB')
}

function getNotificationRoute(notification: UserNotification) {
  const focusToken = String(Date.now())

  if (notification.item_id) {
    const query: Record<string, string> = {
      focus: focusToken,
    }

    if (notification.comment_id) {
      query.commentId = notification.comment_id
    }

    return {
      path: `/items/${notification.item_id}`,
      query,
    }
  }

  if (notification.thread_id) {
    const query: Record<string, string> = {
      focus: focusToken,
    }

    if (notification.post_id) {
      query.postId = notification.post_id
    }

    return {
      path: `/forum/threads/${notification.thread_id}`,
      query,
    }
  }

  return {
    path: '/profile',
  }
}

async function loadNotifications() {
  if (!isLoggedIn.value) {
    notifications.value = []
    unreadNotificationsCount.value = 0
    return
  }

  isNotificationsLoading.value = true
  notificationsError.value = ''

  try {
    const [items, count] = await Promise.all([
      getNotifications(),
      getUnreadNotificationsCount(),
    ])

    notifications.value = items
    unreadNotificationsCount.value = count
  } catch (error) {
    notificationsError.value =
      error instanceof Error ? error.message : 'Failed to load notifications.'
  } finally {
    isNotificationsLoading.value = false
  }
}

async function toggleNotifications() {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }

  isNotificationsOpen.value = !isNotificationsOpen.value

  if (isNotificationsOpen.value) {
    await loadNotifications()
  }
}

async function handleNotificationClick(notification: UserNotification) {
  try {
    if (!notification.is_read) {
      await markNotificationAsRead(notification.id)

      notifications.value = notifications.value.map((item) =>
        item.id === notification.id
          ? {
              ...item,
              is_read: true,
            }
          : item,
      )

      unreadNotificationsCount.value = Math.max(
        0,
        unreadNotificationsCount.value - 1,
      )
    }
  } catch {
    // navigation should still work
  }

  isNotificationsOpen.value = false
  router.push(getNotificationRoute(notification))
}

async function handleMarkAllNotificationsRead() {
  if (!notifications.value.length) {
    return
  }

  try {
    await markAllNotificationsAsRead()

    notifications.value = notifications.value.map((item) => ({
      ...item,
      is_read: true,
    }))

    unreadNotificationsCount.value = 0
  } catch (error) {
    notificationsError.value =
      error instanceof Error ? error.message : 'Failed to mark notifications as read.'
  }
}

function isActive(path: string) {
  return route.path === path
}

function handleLogout() {
  isNotificationsOpen.value = false
  notifications.value = []
  unreadNotificationsCount.value = 0
  logoutUser()
  router.push('/')
}

watch(
  () => isLoggedIn.value,
  (value) => {
    if (value) {
      loadNotifications()
      return
    }

    notifications.value = []
    unreadNotificationsCount.value = 0
    isNotificationsOpen.value = false
  },
)

onMounted(() => {
  if (isLoggedIn.value) {
    loadNotifications()
  }

  notificationsIntervalId = window.setInterval(() => {
    if (isLoggedIn.value) {
      getUnreadNotificationsCount()
        .then((count) => {
          unreadNotificationsCount.value = count
        })
        .catch(() => {
          // ignore polling errors
        })
    }
  }, 45000)
})

onUnmounted(() => {
  if (notificationsIntervalId) {
    window.clearInterval(notificationsIntervalId)
  }
})
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

      <div class="header__notifications">
        <button
          class="header__icon-button"
          type="button"
          aria-label="Notifications"
          @click="toggleNotifications"
        >
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

          <span
            v-if="isLoggedIn && unreadNotificationsCount > 0"
            class="header__notification-badge"
          >
            {{ unreadNotificationsCount > 9 ? '9+' : unreadNotificationsCount }}
          </span>
        </button>

        <div
          v-if="isNotificationsOpen && isLoggedIn"
          class="header__notifications-dropdown"
        >
          <div class="header__notifications-head">
            <div>
              <strong>Notifications</strong>
              <span>{{ unreadNotificationsCount }} unread</span>
            </div>

            <button
              type="button"
              :disabled="unreadNotificationsCount === 0"
              @click="handleMarkAllNotificationsRead"
            >
              Mark all read
            </button>
          </div>

          <div v-if="isNotificationsLoading" class="header__notifications-state">
            Loading notifications...
          </div>

          <div
            v-else-if="notificationsError"
            class="header__notifications-state header__notifications-state--error"
          >
            {{ notificationsError }}
          </div>

          <div
            v-else-if="visibleNotifications.length === 0"
            class="header__notifications-state"
          >
            No notifications yet.
          </div>

          <div v-else class="header__notifications-list">
            <button
              v-for="notification in visibleNotifications"
              :key="notification.id"
              type="button"
              class="header__notification-item"
              :class="{ 'header__notification-item--unread': !notification.is_read }"
              @click="handleNotificationClick(notification)"
            >
              <span class="header__notification-dot"></span>

              <span class="header__notification-content">
                <strong>{{ notification.title }}</strong>
                <span>{{ notification.message }}</span>
                <small>{{ formatNotificationTime(notification.created_at) }}</small>
              </span>
            </button>
          </div>
        </div>
      </div>

        <template v-if="isLoggedIn">
          <RouterLink to="/profile" class="header__avatar" aria-label="Open profile">
            <img
              v-if="userAvatarUrl"
              :src="userAvatarUrl"
              :alt="authState.user?.username || 'User avatar'"
            />

            <span v-else>{{ userInitial }}</span>

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

.header__avatar img {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: inherit;
  object-fit: cover;
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

.header__notifications {
  position: relative;
}

.header__icon-button {
  position: relative;
}

.header__notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: #ef4444;
  color: #ffffff;
  font-size: 10px;
  font-weight: 900;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  border: 2px solid #030812;
}

.header__notifications-dropdown {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  width: min(380px, calc(100vw - 32px));
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(8, 14, 24, 0.98);
  box-shadow: 0 22px 60px rgba(0, 0, 0, 0.36);
  overflow: hidden;
  z-index: 80;
}

.header__notifications-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

.header__notifications-head strong {
  display: block;
  margin-bottom: 3px;
  color: #f8fafc;
  font-size: 15px;
}

.header__notifications-head span {
  color: #94a3b8;
  font-size: 12px;
}

.header__notifications-head button {
  border: none;
  background: transparent;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.header__notifications-head button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.header__notifications-state {
  padding: 18px 16px;
  color: #94a3b8;
  font-size: 14px;
}

.header__notifications-state--error {
  color: #fca5a5;
}

.header__notifications-list {
  max-height: 420px;
  overflow-y: auto;
  display: grid;
}

.header__notification-item {
  width: 100%;
  border: none;
  border-bottom: 1px solid rgba(148, 163, 184, 0.06);
  background: transparent;
  padding: 14px 16px;
  display: grid;
  grid-template-columns: 8px minmax(0, 1fr);
  gap: 12px;
  text-align: left;
  cursor: pointer;
}

.header__notification-item:hover {
  background: rgba(15, 23, 42, 0.8);
}

.header__notification-item--unread {
  background: rgba(37, 99, 235, 0.1);
}

.header__notification-dot {
  width: 8px;
  height: 8px;
  margin-top: 6px;
  border-radius: 999px;
  background: transparent;
}

.header__notification-item--unread .header__notification-dot {
  background: #60a5fa;
}

.header__notification-content {
  min-width: 0;
  display: grid;
  gap: 5px;
}

.header__notification-content strong {
  color: #f8fafc;
  font-size: 13px;
  line-height: 1.35;
}

.header__notification-content span {
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.5;
}

.header__notification-content small {
  color: #64748b;
  font-size: 11px;
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