import { computed, reactive } from 'vue'
import type { AuthUser } from '../types/auth'

const AUTH_STORAGE_KEY = 'mediacompass_auth_user'

function readStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(AUTH_STORAGE_KEY)

  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw) as AuthUser
  } catch {
    localStorage.removeItem(AUTH_STORAGE_KEY)
    return null
  }
}

const authState = reactive<{
  user: AuthUser | null
}>({
  user: readStoredUser(),
})

function persistUser(user: AuthUser | null) {
  if (user) {
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user))
  } else {
    localStorage.removeItem(AUTH_STORAGE_KEY)
  }
}

//DEMO USER FOR TEST
export function loginDemoUser() {
  const demoUser: AuthUser = {
    id: 1,
    name: 'Євгеній',
    email: 'demo@mediacompass.local',
  }

  authState.user = demoUser
  persistUser(demoUser)
}

export function logoutUser() {
  authState.user = null
  persistUser(null)
}

export function isAuthenticated(): boolean {
  return authState.user !== null
}

export function useAuth() {
  return {
    authState,
    isLoggedIn: computed(() => authState.user !== null),
    loginDemoUser,
    logoutUser,
  }
}