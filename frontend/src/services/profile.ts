import type {
  AvatarOption,
  EmailVerificationConfirmResponse,
  EmailVerificationSendResponse,
  EmailVerificationStatus,
  NotificationSettings,
  UserProfile,
} from '../types/auth'
import { apiRequest } from './http'

export async function getMyProfile(): Promise<UserProfile> {
  return apiRequest<UserProfile>('/profile/me')
}

export async function getAvatarOptions(): Promise<AvatarOption[]> {
  return apiRequest<AvatarOption[]>('/profile/avatar-options')
}

export async function updateMyAvatar(avatarId: string): Promise<UserProfile> {
  return apiRequest<UserProfile>('/profile/me/avatar', {
    method: 'PATCH',
    body: JSON.stringify({
      avatar_id: avatarId,
    }),
  })
}

export async function updateMyUsername(username: string): Promise<UserProfile> {
  return apiRequest<UserProfile>('/profile/me/username', {
    method: 'PATCH',
    body: JSON.stringify({
      username,
    }),
  })
}

export async function getNotificationSettings(): Promise<NotificationSettings> {
  return apiRequest<NotificationSettings>('/profile/me/notification-settings')
}

export async function updateNotificationSettings(
  payload: Partial<NotificationSettings>,
): Promise<NotificationSettings> {
  return apiRequest<NotificationSettings>('/profile/me/notification-settings', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function getEmailVerificationStatus(): Promise<EmailVerificationStatus> {
  return apiRequest<EmailVerificationStatus>(
    '/profile/me/email-verification/status',
  )
}

export async function sendEmailVerificationCode(): Promise<EmailVerificationSendResponse> {
  return apiRequest<EmailVerificationSendResponse>(
    '/profile/me/email-verification/send-code',
    {
      method: 'POST',
    },
  )
}

export async function confirmEmailVerificationCode(
  code: string,
): Promise<EmailVerificationConfirmResponse> {
  return apiRequest<EmailVerificationConfirmResponse>(
    '/profile/me/email-verification/confirm',
    {
      method: 'POST',
      body: JSON.stringify({
        code,
      }),
    },
  )
}