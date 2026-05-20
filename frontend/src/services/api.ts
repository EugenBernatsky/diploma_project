import type { Category, MediaItem, MediaItemId } from '../types/media'

export type HealthResponse = {
  status: string
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')

async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return response.json() as Promise<T>
}

export async function checkHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>('/health')
}

export async function getItems(category: Category): Promise<MediaItem[]> {
  return requestJson<MediaItem[]>(`/items?category=${category}`)
}

export async function getItemById(itemId: MediaItemId): Promise<MediaItem> {
  return requestJson<MediaItem>(`/items/${itemId}`)
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

  const results = await Promise.allSettled(categories.map((category) => getItems(category)))

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