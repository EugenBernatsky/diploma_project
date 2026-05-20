export type ForumCategoryType = 'movie' | 'series' | 'book' | 'custom'

export type ForumSortOption = 'active' | 'top' | 'newest' | 'replies'

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

export type ForumPostBaseResponse = {
  id: string
  thread_id: string
  user_id: string
  author_username: string
  author_avatar_id: string
  text: string
  score: number
  parent_post_id: string | null
  created_at: string
  updated_at: string
  edited: boolean
}

export type ForumPostReplyResponse = ForumPostBaseResponse

export type ForumPostResponse = ForumPostBaseResponse & {
  replies: ForumPostReplyResponse[]
}

export type ForumMockThread = ForumThreadResponse & {
  views: number
  is_trending?: boolean
}

export type ForumMockData = {
  threads: ForumMockThread[]
  postsByThread: Record<string, ForumPostResponse[]>
}