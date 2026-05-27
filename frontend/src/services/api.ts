import { apiRequest } from './http'
import type {
  Category,
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

export type GetItemsParams = {
  category?: Category
  limit?: number
  skip?: number
}

export type ItemsCountResponse = {
  count: number
}

function buildItemsQuery(params?: GetItemsParams): string {
  const search = new URLSearchParams()

  if (params?.category) {
    search.set('category', params.category)
  }

  if (typeof params?.limit === 'number') {
    search.set('limit', String(params.limit))
  }

  if (typeof params?.skip === 'number') {
    search.set('skip', String(params.skip))
  }

  return search.toString()
}

export async function getItems(
  categoryOrParams?: Category | GetItemsParams,
): Promise<MediaItem[]> {
  const params: GetItemsParams =
    typeof categoryOrParams === 'string'
      ? { category: categoryOrParams }
      : categoryOrParams ?? {}

  const query = buildItemsQuery(params)
  const suffix = query ? `?${query}` : ''

  return apiRequest<MediaItem[]>(`/items${suffix}`, {
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

function sortItemsForHome(items: MediaItem[]): MediaItem[] {
  return [...items].sort((a, b) => {
    const yearA = a.year ?? 0
    const yearB = b.year ?? 0
    return yearB - yearA
  })
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
    categories.map((category) => getItems(category)),
  )

  const successfulGroups = results
    .filter(
      (result): result is PromiseFulfilledResult<MediaItem[]> =>
        result.status === 'fulfilled',
    )
    .map((result) => sortItemsForHome(result.value))

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

function sortMoviesForPopularity(items: MediaItem[]): MediaItem[] {
  return [...items].sort((a, b) => {
    const ratingA =
      typeof a.tmdb_vote_average === 'number' ? a.tmdb_vote_average : 0
    const ratingB =
      typeof b.tmdb_vote_average === 'number' ? b.tmdb_vote_average : 0

    if (ratingB !== ratingA) {
      return ratingB - ratingA
    }

    const yearA = a.year ?? 0
    const yearB = b.year ?? 0

    return yearB - yearA
  })
}

export async function getPopularMovieItems(limit = 4): Promise<MediaItem[]> {
  const movies = await getItems('movie')
  return sortMoviesForPopularity(movies).slice(0, limit)
}