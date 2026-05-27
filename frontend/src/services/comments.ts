import type {
  Comment,
  CommentActionResponse,
  CommentCreatePayload,
  CommentUpdatePayload,
} from '../types/comment'
import { apiRequest } from './http'

export async function getItemComments(
  itemId: string,
  limit = 100,
): Promise<Comment[]> {
  const search = new URLSearchParams()
  search.set('limit', String(limit))

  return apiRequest<Comment[]>(
    `/items/${encodeURIComponent(itemId)}/comments?${search.toString()}`,
    {
      auth: false,
    },
  )
}

export async function createItemComment(
  itemId: string,
  payload: CommentCreatePayload,
): Promise<CommentActionResponse> {
  return apiRequest<CommentActionResponse>(
    `/items/${encodeURIComponent(itemId)}/comments`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  )
}

export async function updateItemComment(
  commentId: string,
  payload: CommentUpdatePayload,
): Promise<CommentActionResponse> {
  return apiRequest<CommentActionResponse>(
    `/comments/${encodeURIComponent(commentId)}`,
    {
      method: 'PUT',
      body: JSON.stringify(payload),
    },
  )
}

export async function deleteItemComment(
  commentId: string,
): Promise<CommentActionResponse> {
  return apiRequest<CommentActionResponse>(
    `/comments/${encodeURIComponent(commentId)}`,
    {
      method: 'DELETE',
    },
  )
}