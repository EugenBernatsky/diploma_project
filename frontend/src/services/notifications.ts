import type {
  NotificationActionResponse,
  UnreadCountResponse,
  UserNotification,
} from '../types/notification'
import { apiRequest } from './http'

export async function getNotifications(params?: {
  unreadOnly?: boolean
}): Promise<UserNotification[]> {
  const search = new URLSearchParams()

  if (params?.unreadOnly) {
    search.set('unread_only', 'true')
  }

  const suffix = search.toString() ? `?${search.toString()}` : ''

  return apiRequest<UserNotification[]>(`/notifications${suffix}`)
}

export async function getUnreadNotificationsCount(): Promise<number> {
  const response = await apiRequest<UnreadCountResponse>(
    '/notifications/unread-count',
  )

  return response.count ?? response.unread_count ?? 0
}

export async function markNotificationAsRead(
  notificationId: string,
): Promise<NotificationActionResponse> {
  return apiRequest<NotificationActionResponse>(
    `/notifications/${encodeURIComponent(notificationId)}/read`,
    {
      method: 'PATCH',
    },
  )
}

export async function markAllNotificationsAsRead(): Promise<NotificationActionResponse> {
  return apiRequest<NotificationActionResponse>('/notifications/read-all', {
    method: 'PATCH',
  })
}