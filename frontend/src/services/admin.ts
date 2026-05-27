import type {
  AdminActionResponse,
  AdminComment,
  AdminCommentsParams,
  AdminDashboardStats,
  AdminForumPost,
  AdminForumPostsParams,
  AdminForumThread,
  AdminForumThreadsParams,
  AdminItem,
  AdminItemsParams,
  AdminItemUpdatePayload,
  PaginatedResponse,
} from '../types/admin'
import type { MediaItem } from '../types/media'
import { apiRequest } from './http'

function buildQuery(params?: Record<string, string | number | undefined | null>) {
  const search = new URLSearchParams()

  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') {
      return
    }

    search.set(key, String(value))
  })

  const query = search.toString()

  return query ? `?${query}` : ''
}

export async function getAdminDashboardStats(): Promise<AdminDashboardStats> {
  return apiRequest<AdminDashboardStats>('/admin/dashboard/stats')
}

export async function getAdminItems(
  params?: AdminItemsParams,
): Promise<PaginatedResponse<AdminItem>> {
  const query = buildQuery(params)

  return apiRequest<PaginatedResponse<AdminItem>>(`/admin/items${query}`)
}

export async function getAdminComments(
  params?: AdminCommentsParams,
): Promise<PaginatedResponse<AdminComment>> {
  const query = buildQuery(params)

  return apiRequest<PaginatedResponse<AdminComment>>(`/admin/comments${query}`)
}

export async function getAdminForumThreads(
  params?: AdminForumThreadsParams,
): Promise<PaginatedResponse<AdminForumThread>> {
  const query = buildQuery(params)

  return apiRequest<PaginatedResponse<AdminForumThread>>(
    `/admin/forum/threads${query}`,
  )
}

export async function getAdminForumPosts(
  params?: AdminForumPostsParams,
): Promise<PaginatedResponse<AdminForumPost>> {
  const query = buildQuery(params)

  return apiRequest<PaginatedResponse<AdminForumPost>>(
    `/admin/forum/posts${query}`,
  )
}

export async function updateAdminItem(
  itemId: string,
  payload: AdminItemUpdatePayload,
): Promise<MediaItem> {
  return apiRequest<MediaItem>(`/admin/items/${encodeURIComponent(itemId)}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function deleteAdminItem(
  itemId: string,
): Promise<AdminActionResponse> {
  return apiRequest<AdminActionResponse>(
    `/admin/items/${encodeURIComponent(itemId)}`,
    {
      method: 'DELETE',
    },
  )
}

export async function deleteAdminComment(
  commentId: string,
): Promise<AdminActionResponse> {
  return apiRequest<AdminActionResponse>(
    `/admin/comments/${encodeURIComponent(commentId)}`,
    {
      method: 'DELETE',
    },
  )
}

export async function deleteAdminForumThread(
  threadId: string,
): Promise<AdminActionResponse> {
  return apiRequest<AdminActionResponse>(
    `/admin/forum/threads/${encodeURIComponent(threadId)}`,
    {
      method: 'DELETE',
    },
  )
}

export async function deleteAdminForumPost(
  postId: string,
): Promise<AdminActionResponse> {
  return apiRequest<AdminActionResponse>(
    `/admin/forum/posts/${encodeURIComponent(postId)}`,
    {
      method: 'DELETE',
    },
  )
}