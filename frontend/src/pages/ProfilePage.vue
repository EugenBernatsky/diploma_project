<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '../services/auth'
import {
  confirmEmailVerificationCode,
  getAvatarOptions,
  getEmailVerificationStatus,
  getNotificationSettings,
  sendEmailVerificationCode,
  updateMyAvatar,
  updateMyUsername,
  updateNotificationSettings,
} from '../services/profile'
import type {
  AvatarOption,
  EmailVerificationStatus,
  NotificationSettings,
  UserProfile,
} from '../types/auth'
import { getAvatarImageUrl } from '../utils/avatars'
import ProfileLibrarySection from '../components/profile/ProfileLibrarySection.vue'
import AdminPanelModal from '../components/admin/AdminPanelModal.vue'


const router = useRouter()
const { authState, fetchCurrentUser, logoutUser } = useAuth()

const profile = computed(() => authState.user)

const avatarOptions = ref<AvatarOption[]>([])
const notificationSettings = ref<NotificationSettings | null>(null)
const emailStatus = ref<EmailVerificationStatus | null>(null)

const usernameDraft = ref('')
const verificationCode = ref('')

const isLoading = ref(true)
const isAvatarBusy = ref(false)
const isUsernameBusy = ref(false)
const isSettingsBusy = ref(false)
const isSendingCode = ref(false)
const isConfirmingCode = ref(false)

const errorText = ref('')
const successText = ref('')

const isAdminPanelOpen = ref(false)

const notificationOptions: Array<{
  key: keyof NotificationSettings
  title: string
  description: string
}> = [
  {
    key: 'comment_replies',
    title: 'Comment replies',
    description: 'Notify me when someone replies to my item comments.',
  },
  {
    key: 'comment_admin_actions',
    title: 'Comment moderation',
    description: 'Notify me when an admin moderates my comments.',
  },
  {
    key: 'forum_thread_replies',
    title: 'Forum thread replies',
    description: 'Notify me when someone replies to my forum thread.',
  },
  {
    key: 'forum_post_replies',
    title: 'Forum post replies',
    description: 'Notify me when someone replies to my forum post.',
  },
  {
    key: 'forum_admin_actions',
    title: 'Forum moderation',
    description: 'Notify me when an admin moderates my forum content.',
  },
]

const currentAvatarOption = computed(() => {
  if (!profile.value?.avatar_id) {
    return null
  }

  return avatarOptions.value.find((avatar) => avatar.id === profile.value?.avatar_id) ?? null
})

const currentAvatarImageUrl = computed(() => {
  const localAvatarUrl = getAvatarImageUrl(profile.value?.avatar_id)

  if (localAvatarUrl) {
    return localAvatarUrl
  }

  return currentAvatarOption.value?.image_url ?? null
})

const userInitial = computed(() => {
  return profile.value?.username?.trim()?.charAt(0)?.toUpperCase() || 'U'
})

const isEmailVerified = computed(() => {
  return Boolean(emailStatus.value?.email_verified || profile.value?.email_verified)
})

const isAdmin = computed(() => {
  return profile.value?.role === 'admin'
})

const usernameCanBeChangedAt = computed(() => {
  const value = profile.value?.username_can_be_changed_at

  if (!value) {
    return null
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return null
  }

  return date
})

const canChangeUsername = computed(() => {
  if (!usernameCanBeChangedAt.value) {
    return true
  }

  return usernameCanBeChangedAt.value.getTime() <= Date.now()
})

const usernameCooldownText = computed(() => {
  if (!usernameCanBeChangedAt.value || canChangeUsername.value) {
    return ''
  }

  return `Username can be changed after ${formatDateTime(usernameCanBeChangedAt.value.toISOString())}.`
})

function setUserProfile(nextProfile: UserProfile) {
  authState.user = nextProfile
  usernameDraft.value = nextProfile.username
}

function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback
}

function getAuthorInitial(value: string | undefined): string {
  return value?.trim()?.charAt(0)?.toUpperCase() || 'U'
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return '—'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '—'
  }

  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function clearMessages() {
  errorText.value = ''
  successText.value = ''
}

async function loadProfilePage() {
  isLoading.value = true
  clearMessages()

  try {
    const [nextProfile, avatars, settings, verification] = await Promise.all([
      fetchCurrentUser(),
      getAvatarOptions(),
      getNotificationSettings(),
      getEmailVerificationStatus(),
    ])

    setUserProfile(nextProfile)
    avatarOptions.value = avatars
    notificationSettings.value = settings
    emailStatus.value = verification
  } catch (error) {
    errorText.value = getErrorMessage(error, 'Failed to load profile.')
  } finally {
    isLoading.value = false
  }
}

async function handleAvatarSelect(avatarId: string) {
  if (isAvatarBusy.value || profile.value?.avatar_id === avatarId) {
    return
  }

  clearMessages()
  isAvatarBusy.value = true

  try {
    const updatedProfile = await updateMyAvatar(avatarId)
    setUserProfile(updatedProfile)
    successText.value = 'Avatar updated.'
  } catch (error) {
    errorText.value = getErrorMessage(error, 'Failed to update avatar.')
  } finally {
    isAvatarBusy.value = false
  }
}

async function handleUsernameUpdate() {
  const nextUsername = usernameDraft.value.trim()

  if (!profile.value || isUsernameBusy.value) {
    return
  }

  if (!nextUsername) {
    errorText.value = 'Username cannot be empty.'
    return
  }

  if (nextUsername === profile.value.username) {
    successText.value = 'Username is already up to date.'
    return
  }

  if (!canChangeUsername.value) {
    errorText.value = usernameCooldownText.value || 'Username cannot be changed yet.'
    return
  }

  clearMessages()
  isUsernameBusy.value = true

  try {
    const updatedProfile = await updateMyUsername(nextUsername)
    setUserProfile(updatedProfile)
    successText.value = 'Username updated.'
  } catch (error) {
    errorText.value = getErrorMessage(error, 'Failed to update username.')
  } finally {
    isUsernameBusy.value = false
  }
}

async function handleToggleNotification(key: keyof NotificationSettings) {
  if (!notificationSettings.value || isSettingsBusy.value) {
    return
  }

  clearMessages()
  isSettingsBusy.value = true

  const nextValue = !notificationSettings.value[key]

  try {
    const updatedSettings = await updateNotificationSettings({
      [key]: nextValue,
    } as Partial<NotificationSettings>)

    notificationSettings.value = updatedSettings

    if (authState.user) {
      authState.user = {
        ...authState.user,
        notification_settings: updatedSettings,
      }
    }

    successText.value = 'Notification settings updated.'
  } catch (error) {
    errorText.value = getErrorMessage(error, 'Failed to update notification settings.')
  } finally {
    isSettingsBusy.value = false
  }
}

async function handleSendVerificationCode() {
  clearMessages()
  isSendingCode.value = true

  try {
    const response = await sendEmailVerificationCode()

    emailStatus.value = {
      email: emailStatus.value?.email ?? profile.value?.email ?? '',
      email_verified: false,
      email_verification_sent_at: new Date().toISOString(),
      email_verification_expires_at: response.expires_at ?? null,
    }

    successText.value = response.message || 'Verification code sent.'
  } catch (error) {
    errorText.value = getErrorMessage(error, 'Failed to send verification code.')
  } finally {
    isSendingCode.value = false
  }
}

async function handleConfirmVerificationCode() {
  const code = verificationCode.value.trim()

  if (!code) {
    errorText.value = 'Enter verification code.'
    return
  }

  clearMessages()
  isConfirmingCode.value = true

  try {
    const response = await confirmEmailVerificationCode(code)

    emailStatus.value = {
      email: emailStatus.value?.email ?? profile.value?.email ?? '',
      email_verified: response.email_verified,
      email_verification_sent_at: emailStatus.value?.email_verification_sent_at ?? null,
      email_verification_expires_at: emailStatus.value?.email_verification_expires_at ?? null,
    }

    if (authState.user) {
      authState.user = {
        ...authState.user,
        email_verified: response.email_verified,
      }
    }

    verificationCode.value = ''
    successText.value = response.message || 'Email verified.'
  } catch (error) {
    errorText.value = getErrorMessage(error, 'Failed to confirm verification code.')
  } finally {
    isConfirmingCode.value = false
  }
}

function handleLogout() {
  logoutUser()
  router.push('/')
}

onMounted(() => {
  loadProfilePage()
})
</script>

<template>
  <section class="profile-page">
    <div class="profile-page__inner">
      <aside class="profile-sidebar">
        <RouterLink to="/profile" class="profile-sidebar__link profile-sidebar__link--active">
          My Profile
        </RouterLink>

        <a href="#library" class="profile-sidebar__link">My Library</a>
        <a href="#email" class="profile-sidebar__link">Email Verification</a>
        <a href="#avatar" class="profile-sidebar__link">Avatar</a>
        <a href="#notifications" class="profile-sidebar__link">Notifications</a>

        <button
          v-if="isAdmin"
          type="button"
          class="profile-sidebar__admin"
          @click="isAdminPanelOpen = true"
        >
          Admin Panel
        </button>

        <button type="button" class="profile-sidebar__logout" @click="handleLogout">
          Logout
        </button>
      </aside>

      <main class="profile-main">
        <div v-if="isLoading" class="profile-state">
          Loading profile...
        </div>

        <div v-else-if="!profile" class="profile-state profile-state--error">
          Profile is not available.
        </div>

        <template v-else>
          <section class="profile-hero">
            <div class="profile-hero__avatar">
              <img
                v-if="currentAvatarImageUrl"
                :src="currentAvatarImageUrl"
                :alt="currentAvatarOption?.label || profile.username"
              />

              <span v-else>{{ userInitial }}</span>

              <span
                class="profile-hero__status"
                :class="{ 'profile-hero__status--verified': isEmailVerified }"
              ></span>
            </div>

            <div class="profile-hero__content">
              <div class="profile-hero__top">
                <div>
                  <h1 class="profile-hero__title">{{ profile.username }}</h1>
                  <p class="profile-hero__meta">
                    {{ profile.email }}
                    <span>•</span>
                    <span>{{ profile.role }}</span>
                    <span>•</span>
                    <span>Joined {{ formatDateTime(profile.created_at) }}</span>
                  </p>
                </div>

                <span
                  class="profile-hero__badge"
                  :class="{ 'profile-hero__badge--warning': !isEmailVerified }"
                >
                  {{ isEmailVerified ? 'Email verified' : 'Email not verified' }}
                </span>
              </div>

              <div class="profile-hero__actions">
                <a href="#username" class="profile-hero__button profile-hero__button--primary">
                  Edit Profile
                </a>

                <button
                  type="button"
                  class="profile-hero__button profile-hero__button--ghost"
                  @click="loadProfilePage"
                >
                  Refresh
                </button>

                <button
                  v-if="isAdmin"
                  type="button"
                  class="profile-hero__button profile-hero__button--admin"
                  @click="isAdminPanelOpen = true"
                >
                  Admin Panel
                </button>
              </div>
            </div>
          </section>

          <div v-if="errorText || successText" class="profile-messages">
            <p v-if="errorText" class="profile-message profile-message--error">
              {{ errorText }}
            </p>

            <p v-if="successText" class="profile-message profile-message--success">
              {{ successText }}
            </p>
          </div>

          <section class="profile-stats-grid">
            <article class="profile-stat-card">
              <span class="profile-stat-card__icon">#</span>
              <div>
                <p class="profile-stat-card__label">User ID</p>
                <strong>{{ profile.id.slice(0, 8) }}</strong>
              </div>
            </article>

            <article class="profile-stat-card">
              <span class="profile-stat-card__icon">★</span>
              <div>
                <p class="profile-stat-card__label">Role</p>
                <strong>{{ profile.role }}</strong>
              </div>
            </article>

            <article class="profile-stat-card">
              <span class="profile-stat-card__icon">@</span>
              <div>
                <p class="profile-stat-card__label">Username cooldown</p>
                <strong>{{ canChangeUsername ? 'Available' : 'Locked' }}</strong>
              </div>
            </article>

            <article class="profile-stat-card">
              <span class="profile-stat-card__icon">✓</span>
              <div>
                <p class="profile-stat-card__label">Email status</p>
                <strong>{{ isEmailVerified ? 'Verified' : 'Not verified' }}</strong>
              </div>
            </article>
          </section>

          <ProfileLibrarySection />

          <section id="username" class="profile-panel">
            <div class="profile-panel__head">
              <div>
                <h2>Username</h2>
                <p>You can change username only once every 7 days.</p>
              </div>
            </div>

            <div class="profile-form-row">
              <label class="profile-field">
                <span>Username</span>
                <input
                  v-model="usernameDraft"
                  type="text"
                  placeholder="new_username"
                  autocomplete="username"
                />
              </label>

              <button
                type="button"
                class="profile-primary-btn"
                :disabled="isUsernameBusy || !canChangeUsername"
                @click="handleUsernameUpdate"
              >
                {{ isUsernameBusy ? 'Saving...' : 'Save Username' }}
              </button>
            </div>

            <p v-if="usernameCooldownText" class="profile-hint profile-hint--warning">
              {{ usernameCooldownText }}
            </p>
          </section>

          <section id="email" class="profile-panel">
            <div class="profile-panel__head">
              <div>
                <h2>Email Verification</h2>
                <p>Verify your email to make your account more complete.</p>
              </div>

              <span
                class="profile-pill"
                :class="{ 'profile-pill--success': isEmailVerified }"
              >
                {{ isEmailVerified ? 'Verified' : 'Not verified' }}
              </span>
            </div>

            <div class="profile-email-box">
              <p>
                <strong>Email:</strong>
                {{ emailStatus?.email || profile.email }}
              </p>

              <p v-if="emailStatus?.email_verification_expires_at">
                <strong>Code expires:</strong>
                {{ formatDateTime(emailStatus.email_verification_expires_at) }}
              </p>
            </div>

            <div v-if="!isEmailVerified" class="profile-form-row">
              <button
                type="button"
                class="profile-secondary-btn"
                :disabled="isSendingCode"
                @click="handleSendVerificationCode"
              >
                {{ isSendingCode ? 'Sending...' : 'Send Code' }}
              </button>

              <label class="profile-field profile-field--code">
                <span>Verification code</span>
                <input
                  v-model="verificationCode"
                  type="text"
                  placeholder="123456"
                  inputmode="numeric"
                />
              </label>

              <button
                type="button"
                class="profile-primary-btn"
                :disabled="isConfirmingCode"
                @click="handleConfirmVerificationCode"
              >
                {{ isConfirmingCode ? 'Confirming...' : 'Confirm Email' }}
              </button>
            </div>
          </section>

          <section id="avatar" class="profile-panel">
            <div class="profile-panel__head">
              <div>
                <h2>Avatar</h2>
                <p>Select one of predefined avatars.</p>
              </div>
            </div>

            <div v-if="avatarOptions.length" class="profile-avatar-grid">
              <button
                v-for="avatar in avatarOptions"
                :key="avatar.id"
                type="button"
                class="profile-avatar-option"
                :class="{
                  'profile-avatar-option--active': profile.avatar_id === avatar.id,
                }"
                :disabled="isAvatarBusy"
                @click="handleAvatarSelect(avatar.id)"
              >
                <img
                  v-if="getAvatarImageUrl(avatar.id) || avatar.image_url"
                  :src="getAvatarImageUrl(avatar.id) || avatar.image_url || undefined"
                  :alt="avatar.label"
                />

                <span v-else>{{ getAuthorInitial(avatar.label) }}</span>

                <small>{{ avatar.label }}</small>
              </button>
            </div>

            <p v-else class="profile-hint">
              No avatar options available.
            </p>
          </section>

          <section id="notifications" class="profile-panel">
            <div class="profile-panel__head">
              <div>
                <h2>Notification Settings</h2>
                <p>Choose which account events should create notifications.</p>
              </div>
            </div>

            <div v-if="notificationSettings" class="profile-settings-list">
              <label
                v-for="option in notificationOptions"
                :key="option.key"
                class="profile-setting"
              >
                <div>
                  <strong>{{ option.title }}</strong>
                  <span>{{ option.description }}</span>
                </div>

                <input
                  type="checkbox"
                  :checked="notificationSettings[option.key]"
                  :disabled="isSettingsBusy"
                  @change="handleToggleNotification(option.key)"
                />
              </label>
            </div>

            <p v-else class="profile-hint">
              Notification settings are not available.
            </p>
          </section>
        </template>
      </main>
    </div>

    <AdminPanelModal
      :open="isAdminPanelOpen"
      @close="isAdminPanelOpen = false"
    />
  </section>
</template>

<style scoped>
.profile-page {
  min-height: calc(100vh - 160px);
  padding: 34px 0 64px;
}

.profile-page__inner {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 32px;
  align-items: start;
}

.profile-sidebar {
  position: sticky;
  top: 98px;
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.92);
}

.profile-sidebar__link,
.profile-sidebar__logout,
.profile-sidebar__admin {
  min-height: 42px;
  padding: 0 14px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  border: none;
  background: transparent;
  color: #94a3b8;
  font-weight: 700;
  cursor: pointer;
}

.profile-sidebar__link--active {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
}

.profile-sidebar__admin {
  background: rgba(37, 99, 235, 0.14);
  color: #bfdbfe;
}

.profile-sidebar__link:hover,
.profile-sidebar__logout:hover,
.profile-sidebar__admin:hover {
  color: #ffffff;
  background: rgba(15, 23, 42, 0.72);
}

.profile-main {
  display: grid;
  gap: 22px;
}

.profile-state,
.profile-panel,
.profile-hero,
.profile-stat-card {
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
}

.profile-state {
  padding: 28px;
  border-radius: 22px;
  color: #94a3b8;
}

.profile-state--error {
  color: #fca5a5;
}

.profile-hero {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr);
  gap: 24px;
  align-items: center;
  padding: 28px;
  border-radius: 24px;
}

.profile-hero__avatar {
  position: relative;
  width: 96px;
  height: 96px;
  border-radius: 28px;
  overflow: hidden;
  background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
  color: #0f172a;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 34px;
  font-weight: 900;
}

.profile-hero__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-hero__status {
  position: absolute;
  right: 8px;
  bottom: 8px;
  width: 18px;
  height: 18px;
  border-radius: 999px;
  border: 3px solid #0f172a;
  background: #f97316;
}

.profile-hero__status--verified {
  background: #22c55e;
}

.profile-hero__content {
  min-width: 0;
  display: grid;
  gap: 18px;
}

.profile-hero__top {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: start;
}

.profile-hero__title {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: clamp(34px, 4vw, 48px);
  line-height: 1;
  letter-spacing: -0.04em;
}

.profile-hero__meta {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: #94a3b8;
  font-size: 14px;
}

.profile-hero__badge,
.profile-pill {
  flex: 0 0 auto;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.14);
  color: #86efac;
  font-size: 12px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.profile-hero__badge--warning,
.profile-pill {
  background: rgba(249, 115, 22, 0.14);
  color: #fdba74;
}

.profile-pill--success {
  background: rgba(34, 197, 94, 0.14);
  color: #86efac;
}

.profile-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.profile-hero__button,
.profile-primary-btn,
.profile-secondary-btn {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  border: none;
  text-decoration: none;
  color: #ffffff;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.profile-hero__button--primary,
.profile-primary-btn {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
}

.profile-hero__button--ghost,
.profile-secondary-btn {
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
}

.profile-hero__button--admin {
  background: linear-gradient(135deg, #7c3aed 0%, #60a5fa 100%);
}

.profile-primary-btn:disabled,
.profile-secondary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.profile-messages {
  display: grid;
  gap: 10px;
}

.profile-message {
  margin: 0;
  padding: 14px 16px;
  border-radius: 14px;
  font-weight: 700;
}

.profile-message--error {
  background: rgba(239, 68, 68, 0.12);
  color: #fca5a5;
}

.profile-message--success {
  background: rgba(34, 197, 94, 0.12);
  color: #86efac;
}

.profile-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.profile-stat-card {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 18px;
  border-radius: 18px;
}

.profile-stat-card__icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: rgba(37, 99, 235, 0.14);
  color: #60a5fa;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
}

.profile-stat-card__label {
  margin: 0 0 4px;
  color: #64748b;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 800;
}

.profile-stat-card strong {
  color: #f8fafc;
  font-size: 18px;
  text-transform: capitalize;
}

.profile-panel {
  display: grid;
  gap: 18px;
  padding: 24px;
  border-radius: 24px;
}

.profile-panel__head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: start;
}

.profile-panel__head h2 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 30px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.profile-panel__head p,
.profile-hint {
  margin: 0;
  color: #94a3b8;
  line-height: 1.7;
}

.profile-hint--warning {
  color: #fdba74;
}

.profile-form-row {
  display: flex;
  gap: 14px;
  align-items: end;
  flex-wrap: wrap;
}

.profile-field {
  flex: 1 1 260px;
  display: grid;
  gap: 8px;
}

.profile-field--code {
  max-width: 220px;
}

.profile-field span {
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 800;
}

.profile-field input {
  width: 100%;
  min-height: 44px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  outline: none;
}

.profile-email-box {
  display: grid;
  gap: 8px;
  padding: 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.55);
}

.profile-email-box p {
  margin: 0;
  color: #cbd5e1;
}

.profile-avatar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(118px, 1fr));
  gap: 14px;
}

.profile-avatar-option {
  display: grid;
  justify-items: center;
  gap: 10px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.72);
  color: #e2e8f0;
  cursor: pointer;
}

.profile-avatar-option img,
.profile-avatar-option > span {
  width: 64px;
  height: 64px;
  border-radius: 18px;
}

.profile-avatar-option img {
  object-fit: cover;
}

.profile-avatar-option > span {
  background: linear-gradient(135deg, #f8fafc 0%, #dbeafe 100%);
  color: #0f172a;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
}

.profile-avatar-option small {
  color: #94a3b8;
  font-weight: 700;
}

.profile-avatar-option--active {
  border-color: rgba(96, 165, 250, 0.45);
  background: rgba(37, 99, 235, 0.14);
}

.profile-avatar-option:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.profile-settings-list {
  display: grid;
  gap: 12px;
}

.profile-setting {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  padding: 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.55);
}

.profile-setting strong {
  display: block;
  margin-bottom: 4px;
  color: #f8fafc;
}

.profile-setting span {
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.6;
}

.profile-setting input {
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
}

@media (max-width: 1080px) {
  .profile-page__inner {
    grid-template-columns: 1fr;
  }

  .profile-sidebar {
    position: static;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .profile-stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .profile-page__inner {
    width: min(100%, calc(100% - 32px));
  }

  .profile-hero {
    grid-template-columns: 1fr;
  }

  .profile-hero__top,
  .profile-panel__head,
  .profile-setting {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-sidebar,
  .profile-stats-grid {
    grid-template-columns: 1fr;
  }

  .profile-form-row {
    align-items: stretch;
  }

  .profile-primary-btn,
  .profile-secondary-btn {
    width: 100%;
  }
}
</style>