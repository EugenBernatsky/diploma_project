import type {
  ForumCategoryType,
  ForumMyVoteResponse,
  ForumPostCreatePayload,
  ForumPostResponse,
  ForumThreadCreatePayload,
  ForumThreadResponse,
  ForumThreadSort,
  ForumVotePayload,
  ForumVoteResponse,
} from '../types/forum'
import { apiRequest } from './http'

type ActionResponse = {
  message: string
}

export async function getForumThreads(params?: {
  limit?: number
  sort?: ForumThreadSort
  category_type?: ForumCategoryType
  custom_category?: string
}): Promise<ForumThreadResponse[]> {
  const search = new URLSearchParams()

  if (params?.limit) {
    search.set('limit', String(params.limit))
  }

  if (params?.sort) {
    search.set('sort', params.sort)
  }

  if (params?.category_type) {
    search.set('category_type', params.category_type)
  }

  if (params?.custom_category?.trim()) {
    search.set('custom_category', params.custom_category.trim())
  }

  const suffix = search.toString() ? `?${search.toString()}` : ''

  return apiRequest<ForumThreadResponse[]>(`/forum/threads${suffix}`, {
    auth: false,
  })
}

export async function getForumThread(
  threadId: string,
): Promise<ForumThreadResponse> {
  return apiRequest<ForumThreadResponse>(
    `/forum/threads/${encodeURIComponent(threadId)}`,
    {
      auth: false,
    },
  )
}

export async function createForumThread(
  payload: ForumThreadCreatePayload,
): Promise<ForumThreadResponse> {
  return apiRequest<ForumThreadResponse>('/forum/threads', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateForumThread(
  threadId: string,
  payload: ForumThreadCreatePayload,
): Promise<ForumThreadResponse> {
  return apiRequest<ForumThreadResponse>(
    `/forum/threads/${encodeURIComponent(threadId)}`,
    {
      method: 'PUT',
      body: JSON.stringify(payload),
    },
  )
}

export async function deleteForumThread(
  threadId: string,
): Promise<ActionResponse> {
  return apiRequest<ActionResponse>(
    `/forum/threads/${encodeURIComponent(threadId)}`,
    {
      method: 'DELETE',
    },
  )
}

export async function voteForumThread(
  threadId: string,
  payload: ForumVotePayload,
): Promise<ForumVoteResponse> {
  return apiRequest<ForumVoteResponse>(
    `/forum/threads/${encodeURIComponent(threadId)}/vote`,
    {
      method: 'PUT',
      body: JSON.stringify(payload),
    },
  )
}

export async function getMyThreadVote(
  threadId: string,
): Promise<ForumMyVoteResponse> {
  return apiRequest<ForumMyVoteResponse>(
    `/forum/threads/${encodeURIComponent(threadId)}/my-vote`,
  )
}

export async function getForumPosts(
  threadId: string,
  limit = 200,
): Promise<ForumPostResponse[]> {
  const search = new URLSearchParams()
  search.set('limit', String(limit))

  return apiRequest<ForumPostResponse[]>(
    `/forum/threads/${encodeURIComponent(threadId)}/posts?${search.toString()}`,
    {
      auth: false,
    },
  )
}

export async function createForumPost(
  threadId: string,
  payload: ForumPostCreatePayload,
): Promise<ForumPostResponse | ForumPostResponse['replies'][number]> {
  return apiRequest<ForumPostResponse | ForumPostResponse['replies'][number]>(
    `/forum/threads/${encodeURIComponent(threadId)}/posts`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  )
}

export async function updateForumPost(
  postId: string,
  payload: { text: string },
): Promise<ActionResponse> {
  return apiRequest<ActionResponse>(
    `/forum/posts/${encodeURIComponent(postId)}`,
    {
      method: 'PUT',
      body: JSON.stringify(payload),
    },
  )
}

export async function deleteForumPost(postId: string): Promise<ActionResponse> {
  return apiRequest<ActionResponse>(
    `/forum/posts/${encodeURIComponent(postId)}`,
    {
      method: 'DELETE',
    },
  )
}

export async function voteForumPost(
  postId: string,
  payload: ForumVotePayload,
): Promise<ForumVoteResponse> {
  return apiRequest<ForumVoteResponse>(
    `/forum/posts/${encodeURIComponent(postId)}/vote`,
    {
      method: 'PUT',
      body: JSON.stringify(payload),
    },
  )
}

export async function getMyPostVote(
  postId: string,
): Promise<ForumMyVoteResponse> {
  return apiRequest<ForumMyVoteResponse>(
    `/forum/posts/${encodeURIComponent(postId)}/my-vote`,
  )
}