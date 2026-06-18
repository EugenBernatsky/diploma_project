import { apiRequest } from './http'
import type {
  Category,
  GetItemsParams,
  ItemsListResponse,
  MediaItem,
  MediaItemId,
  MediaItemStats,
} from '../types/media'

export type HealthResponse = {
  status: string
}

export async function checkHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>('/health', {
    auth: false,
  })
}

export type ItemsCountResponse = {
  count: number
}

function buildItemsQuery(params?: GetItemsParams): string {
  const search = new URLSearchParams()

  if (!params) {
    return ''
  }

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') {
      return
    }

    if (key === 'genres') {
      const genres = Array.isArray(value) ? value : []

      genres.forEach((genre) => {
        const normalized = genre.trim()

        if (normalized) {
          search.append('genres', normalized)
        }
      })

      return
    }

    if (typeof value === 'string') {
      const normalized = value.trim()

      if (normalized) {
        search.set(key, normalized)
      }

      return
    }

    search.set(key, String(value))
  })

  return search.toString()
}

export async function getItems(
  params: GetItemsParams = {},
): Promise<ItemsListResponse> {
  const query = buildItemsQuery(params)
  const suffix = query ? `?${query}` : ''

  return apiRequest<ItemsListResponse>(`/items${suffix}`, {
    auth: false,
  })
}

export async function getItemsCount(
  category?: Category,
): Promise<ItemsCountResponse> {
  const suffix = category ? `?category=${encodeURIComponent(category)}` : ''

  return apiRequest<ItemsCountResponse>(`/items/count${suffix}`, {
    auth: false,
  })
}

export async function getItemById(itemId: MediaItemId): Promise<MediaItem> {
  return apiRequest<MediaItem>(
    `/items/${encodeURIComponent(String(itemId))}`,
    {
      auth: false,
    },
  )
}

export async function getItemStats(
  itemId: MediaItemId,
): Promise<MediaItemStats> {
  return apiRequest<MediaItemStats>(
    `/items/${encodeURIComponent(String(itemId))}/stats`,
    {
      auth: false,
    },
  )
}

function interleaveGroups(groups: MediaItem[][], limit: number): MediaItem[] {
  const result: MediaItem[] = []
  const buckets = groups.map((group) => [...group])

  while (result.length < limit) {
    let addedInRound = false

    for (const bucket of buckets) {
      const item = bucket.shift()

      if (item) {
        result.push(item)
        addedInRound = true
      }

      if (result.length >= limit) {
        break
      }
    }

    if (!addedInRound) {
      break
    }
  }

  return result
}

export async function getHomeShowcaseItems(limit = 5): Promise<MediaItem[]> {
  const categories: Category[] = ['movie', 'series', 'book']

  const results = await Promise.allSettled(
    categories.map((category) =>
      getItems({
        category,
        sort: 'newest',
        limit,
      }),
    ),
  )

  const successfulGroups = results
    .filter(
      (result): result is PromiseFulfilledResult<ItemsListResponse> =>
        result.status === 'fulfilled',
    )
    .map((result) => result.value.results)

  const mixedItems = interleaveGroups(successfulGroups, limit)

  const seenIds = new Set<string>()
  const uniqueItems: MediaItem[] = []

  for (const item of mixedItems) {
    const key = String(item.id)

    if (seenIds.has(key)) {
      continue
    }

    seenIds.add(key)
    uniqueItems.push(item)
  }

  return uniqueItems.slice(0, limit)
}

export async function getPopularMovieItems(limit = 4): Promise<MediaItem[]> {
  const response = await getItems({
    category: 'movie',
    sort: 'rating_desc',
    limit,
  })

  return response.results
}
