export type UserRole = 'user' | 'admin'

export type NotificationSettings = {
  comment_replies: boolean
  comment_admin_actions: boolean
  forum_thread_replies: boolean
  forum_post_replies: boolean
  forum_admin_actions: boolean
}

export type AvatarOption = {
  id: string
  label: string
  image_url?: string | null
}

export type EmailVerificationStatus = {
  email: string
  email_verified: boolean
  email_verification_sent_at?: string | null
  email_verification_expires_at?: string | null
}

export type EmailVerificationSendResponse = {
  message: string
  expires_at?: string | null
}

export type EmailVerificationConfirmResponse = {
  message: string
  email_verified: boolean
}

export type UserPublic = {
  id: string
  username: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export type UserProfile = {
  id: string
  username: string
  email: string
  role: UserRole
  is_active?: boolean
  avatar_id?: string | null
  created_at: string
  notification_settings?: NotificationSettings
  email_verified?: boolean
  username_updated_at?: string | null
  username_can_be_changed_at?: string | null
}

export type TokenResponse = {
  access_token: string
  token_type: string
}

export type RegisterPayload = {
  username: string
  email: string
  password: string
}

export type LoginPayload = {
  username: string
  password: string
}

export type AuthState = {
  token: string | null
  user: UserProfile | null
  isInitialized: boolean
}