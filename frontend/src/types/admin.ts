import type { Category, MediaProviderLink, MediaTrailer } from './media'
import type { ForumCategoryType  } from './forum'
export type AdminPurchaseLinkPayload = {
  store_name: string
  url: string
  region?: string | null
  provider_type?: string | null
}

export type PaginatedResponse<T> = {
  results: T[]
  total: number
  limit: number
  skip: number
}

export type AdminDashboardStats = {
  users_count: number
  items_count: number
  comments_count: number
  forum_threads_count: number
  forum_posts_count: number
  unread_notifications_count: number
}

export type AdminItem = {
  id: string
  title: string
  category: Category
  year: number
  genres: string[]
  description: string
  poster_url: string | null
  backdrop_url: string | null
  runtime: number | null
  page_count: number | null
  external_source: string | null
  external_id: string | null
  created_at: string
  updated_at: string | null
}

export type AdminComment = {
  id: string
  item_id: string
  item_title: string | null
  user_id: string
  author_username: string
  author_avatar_id: string | null
  content: string
  parent_comment_id: string | null
  reply_to_comment_id: string | null
  reply_to_username: string | null
  created_at: string
  updated_at: string | null
}

export type AdminForumThread = {
  id: string
  title: string
  content: string
  category: ForumCategoryType 
  custom_category: string | null
  user_id: string
  author_username: string
  author_avatar_id: string | null
  posts_count: number
  votes_count: number
  created_at: string
  updated_at: string | null
}

export type AdminForumPost = {
  id: string
  thread_id: string
  thread_title: string | null
  user_id: string
  author_username: string
  author_avatar_id: string | null
  content: string
  parent_post_id: string | null
  reply_to_post_id: string | null
  reply_to_username: string | null
  votes_count: number
  created_at: string
  updated_at: string | null
}

export type AdminListParams = {
  search?: string
  limit?: number
  skip?: number
}

export type AdminItemsParams = AdminListParams & {
  category?: Category | ''
}

export type AdminCommentsParams = AdminListParams & {
  item_id?: string
  user_id?: string
}

export type AdminForumThreadsParams = AdminListParams & {
  category?: ForumCategoryType  | ''
  user_id?: string
}

export type AdminForumPostsParams = AdminListParams & {
  thread_id?: string
  user_id?: string
}

export type AdminItemUpdatePayload = {
  title?: string
  category?: Category
  year?: number
  genres?: string[]
  description?: string
  poster_url?: string | null
  backdrop_url?: string | null
  runtime?: number | null
  page_count?: number | null
  trailers?: MediaTrailer[]
  watch_links?: MediaProviderLink[]
  purchase_links?: AdminPurchaseLinkPayload[]
}

export type AdminActionResponse = {
  message?: string
}