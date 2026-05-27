import type {
  InteractionActionResponse,
  InteractionCreatePayload,
  InteractionResponse,
  InteractionType,
} from '../types/interaction'
import { apiRequest } from './http'

export async function createInteraction(
  payload: InteractionCreatePayload,
): Promise<InteractionActionResponse> {
  return apiRequest<InteractionActionResponse>('/interactions', {
    method: 'POST',
    body: JSON.stringify({
      item_id: payload.item_id,
      interaction_type: payload.interaction_type,
      source: payload.source ?? 'other',
    }),
  })
}

export async function getMyInteractions(params?: {
  interaction_type?: InteractionType
  item_id?: string
  limit?: number
}): Promise<InteractionResponse[]> {
  const search = new URLSearchParams()

  if (params?.interaction_type) {
    search.set('interaction_type', params.interaction_type)
  }

  if (params?.item_id) {
    search.set('item_id', params.item_id)
  }

  if (typeof params?.limit === 'number') {
    search.set('limit', String(params.limit))
  }

  const suffix = search.toString() ? `?${search.toString()}` : ''

  return apiRequest<InteractionResponse[]>(`/interactions/me${suffix}`)
}