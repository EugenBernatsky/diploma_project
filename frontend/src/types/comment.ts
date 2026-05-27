export type CommentBase = {
  id: string
  item_id: string
  user_id: string
  author_username: string
  author_avatar_id: string
  text: string
  parent_comment_id: string | null
  reply_to_comment_id: string | null
  reply_to_user_id: string | null
  reply_to_username: string | null
  created_at: string
  updated_at: string
  edited: boolean
}

export type CommentReply = CommentBase

export type Comment = CommentBase & {
  replies: CommentReply[]
}

export type CommentCreatePayload = {
  text: string
  reply_to_comment_id?: string
}

export type CommentUpdatePayload = {
  text: string
}

export type CommentActionResponse = {
  message: string
}