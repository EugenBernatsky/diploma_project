import { computed, reactive } from 'vue'
import type {
  AuthState,
  LoginPayload,
  RegisterPayload,
  TokenResponse,
  UserProfile,
  UserPublic,
} from '../types/auth'
import {
  apiRequest,
  getAccessToken,
  removeAccessToken,
  saveAccessToken,
  setUnauthorizedHandler,
} from './http'

const authState = reactive<AuthState>({
  token: null,
  user: null,
  isInitialized: false,
})

const isLoggedIn = computed(() => Boolean(authState.token && authState.user))
const isAdmin = computed(() => authState.user?.role === 'admin')

function saveToken(token: string) {
  authState.token = token
  saveAccessToken(token)
}

function clearAuth() {
  authState.token = null
  authState.user = null
  removeAccessToken()
}

setUnauthorizedHandler(() => {
  clearAuth()
  authState.isInitialized = true
})

async function fetchCurrentUserRequest(): Promise<UserProfile> {
  return apiRequest<UserProfile>('/profile/me')
}

export async function initializeAuth(): Promise<void> {
  if (authState.isInitialized) {
    return
  }

  const storedToken = getAccessToken()

  if (!storedToken) {
    authState.isInitialized = true
    return
  }

  authState.token = storedToken

  try {
    authState.user = await fetchCurrentUserRequest()
  } catch {
    clearAuth()
  } finally {
    authState.isInitialized = true
  }
}

export async function fetchCurrentUser(): Promise<UserProfile> {
  if (!authState.token) {
    throw new Error('No auth token found')
  }

  const user = await fetchCurrentUserRequest()
  authState.user = user
  return user
}

export async function registerUser(payload: RegisterPayload): Promise<UserPublic> {
  const createdUser = await apiRequest<UserPublic>('/auth/register', {
    method: 'POST',
    auth: false,
    body: JSON.stringify(payload),
  })

  await loginUser({
    username: payload.username,
    password: payload.password,
  })

  return createdUser
}

export async function loginUser(payload: LoginPayload): Promise<UserProfile> {
  const formData = new URLSearchParams()
  formData.set('username', payload.username)
  formData.set('password', payload.password)

  const tokenData = await apiRequest<TokenResponse>('/auth/login', {
    method: 'POST',
    auth: false,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  })

  saveToken(tokenData.access_token)

  const user = await fetchCurrentUser()
  authState.isInitialized = true

  return user
}

export function logoutUser() {
  clearAuth()
  authState.isInitialized = true
}

export function useAuth() {
  return {
    authState,
    isLoggedIn,
    isAdmin,
    initializeAuth,
    fetchCurrentUser,
    registerUser,
    loginUser,
    logoutUser,
  }
}