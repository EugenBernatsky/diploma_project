export type ForumCategoryType = 'movie' | 'series' | 'book' | 'custom'
export type ForumThreadSort = 'activity' | 'newest' | 'score'

export type ForumThreadResponse = {
  id: string
  user_id: string
  author_username: string
  author_avatar_id: string
  title: string
  text: string
  category_type: ForumCategoryType
  custom_category: string | null
  score: number
  replies_count: number
  created_at: string
  updated_at: string
  last_activity_at: string
  edited: boolean
}

export type ForumThreadCreatePayload = {
  title: string
  text: string
  category_type: ForumCategoryType
  custom_category: string | null
}

export type ForumPostBaseResponse = {
  id: string
  thread_id: string
  user_id: string
  author_username: string
  author_avatar_id: string
  text: string
  score: number
  parent_post_id: string | null
  reply_to_post_id: string | null
  reply_to_user_id: string | null
  reply_to_username: string | null
  created_at: string
  updated_at: string
  edited: boolean
}

export type ForumPostReplyResponse = ForumPostBaseResponse

export type ForumPostResponse = ForumPostBaseResponse & {
  replies: ForumPostReplyResponse[]
}

export type ForumPostCreatePayload = {
  text: string
  reply_to_post_id?: string
}

export type ForumVotePayload = {
  value: 1 | -1
}

export type ForumVoteResponse = {
  target_type: 'thread' | 'post'
  target_id: string
  current_vote: 1 | -1 | null
  score: number
  message: string
}

export type ForumMyVoteResponse = {
  target_type: 'thread' | 'post'
  target_id: string
  current_vote: 1 | -1 | null
}