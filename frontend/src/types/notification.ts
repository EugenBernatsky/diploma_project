export type NotificationType =
  | 'reply_to_comment'
  | 'comment_deleted_by_admin'
  | 'reply_to_forum_thread'
  | 'reply_to_forum_post'
  | 'forum_thread_deleted_by_admin'
  | 'forum_post_deleted_by_admin'

export type UserNotification = {
  id: string
  user_id: string
  type: NotificationType
  title: string
  message: string
  is_read: boolean
  item_id?: string | null
  comment_id?: string | null
  thread_id?: string | null
  post_id?: string | null
  created_at: string
}

export type UnreadCountResponse = {
  count?: number
  unread_count?: number
}

export type NotificationActionResponse = {
  message: string
}