import type {
  FavoriteActionResponse,
  InteractionActionResponse,
  InteractionCreatePayload,
  ItemStatus,
  RatingActionResponse,
  StatusActionResponse,
  UserItemStatusResponse,
  UserRatingResponse,
} from '../types/userItemActions'
import { apiRequest } from './http'
import type { MediaItem } from '../types/media'

type StatusListResponseItem =
  | MediaItem
  | {
      item?: MediaItem | null
      media_item?: MediaItem | null
      status?: ItemStatus
      item_id?: string
    }

function unwrapStatusMediaItem(entry: StatusListResponseItem): MediaItem {
  if ('item' in entry && entry.item) {
    return entry.item
  }

  if ('media_item' in entry && entry.media_item) {
    return entry.media_item
  }

  return entry as MediaItem
}

export async function getMyRating(itemId: string): Promise<number | null> {
  const data = await apiRequest<UserRatingResponse | null>(
    `/ratings/${encodeURIComponent(itemId)}/me`,
    {
      notFoundAsNull: true,
    },
  )

  return data?.score ?? null
}

export async function createRating(
  itemId: string,
  score: number,
): Promise<RatingActionResponse> {
  return apiRequest<RatingActionResponse>(
    `/ratings/${encodeURIComponent(itemId)}`,
    {
      method: 'POST',
      body: JSON.stringify({ score }),
    },
  )
}

export async function updateRating(
  itemId: string,
  score: number,
): Promise<RatingActionResponse> {
  return apiRequest<RatingActionResponse>(
    `/ratings/${encodeURIComponent(itemId)}`,
    {
      method: 'PUT',
      body: JSON.stringify({ score }),
    },
  )
}

export async function deleteRating(
  itemId: string,
): Promise<RatingActionResponse> {
  return apiRequest<RatingActionResponse>(
    `/ratings/${encodeURIComponent(itemId)}`,
    {
      method: 'DELETE',
    },
  )
}

export async function getMyStatus(itemId: string): Promise<ItemStatus | null> {
  const data = await apiRequest<UserItemStatusResponse | null>(
    `/statuses/${encodeURIComponent(itemId)}/me`,
    {
      notFoundAsNull: true,
    },
  )

  return data?.status ?? null
}

export async function setMyStatus(
  itemId: string,
  status: ItemStatus,
): Promise<StatusActionResponse> {
  return apiRequest<StatusActionResponse>(
    `/statuses/${encodeURIComponent(itemId)}`,
    {
      method: 'PUT',
      body: JSON.stringify({ status }),
    },
  )
}

export async function deleteMyStatus(
  itemId: string,
): Promise<StatusActionResponse> {
  return apiRequest<StatusActionResponse>(
    `/statuses/${encodeURIComponent(itemId)}`,
    {
      method: 'DELETE',
    },
  )
}

export async function getFavorites(): Promise<MediaItem[]> {
  return apiRequest<MediaItem[]>('/favorites')
}

export async function getStatusItems(status?: ItemStatus): Promise<MediaItem[]> {
  const search = new URLSearchParams()

  if (status) {
    search.set('status', status)
  }

  const suffix = search.toString() ? `?${search.toString()}` : ''

  const data = await apiRequest<StatusListResponseItem[]>(`/statuses${suffix}`)

  return data.map(unwrapStatusMediaItem)
}

export async function addToFavorites(
  itemId: string,
): Promise<FavoriteActionResponse> {
  return apiRequest<FavoriteActionResponse>(
    `/favorites/${encodeURIComponent(itemId)}`,
    {
      method: 'POST',
    },
  )
}

export async function removeFromFavorites(
  itemId: string,
): Promise<FavoriteActionResponse> {
  return apiRequest<FavoriteActionResponse>(
    `/favorites/${encodeURIComponent(itemId)}`,
    {
      method: 'DELETE',
    },
  )
}

export async function createInteraction(
  payload: InteractionCreatePayload,
): Promise<InteractionActionResponse> {
  return apiRequest<InteractionActionResponse>('/interactions', {
    method: 'POST',
    body: JSON.stringify({
      item_id: payload.item_id,
      interaction_type: payload.interaction_type,
      source: payload.source ?? null,
      value: payload.value ?? 1,
    }),
  })
}