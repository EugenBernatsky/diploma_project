import type { Category, MediaItem } from '../types/media'

export type CatalogCategory = 'all' | Category
export type CatalogSort = 'popular' | 'newest' | 'oldest' | 'title'
export type YearBucket =
  | 'any'
  | '2024'
  | '2023'
  | '2022'
  | '2021'
  | '2020'
  | '2010s'
  | 'classic'

export type DurationBucket =
  | 'any'
  | '10'
  | '20'
  | '30'
  | '50'
  | '80'
  | '120'
  | '180'
  | '240'
  | '400'

const fallbackImages: Record<Category, string> = {
  movie:
    'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=900&q=80',
  series:
    'https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=900&q=80',
  book:
    'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80',
}

const IMAGE_BASE_URL = (import.meta.env.VITE_IMAGE_BASE_URL || '').replace(/\/+$/, '')

export const yearFilterOptions: Array<{ label: string; value: YearBucket }> = [
  { label: 'Any', value: 'any' },
  { label: '2024', value: '2024' },
  { label: '2023', value: '2023' },
  { label: '2022', value: '2022' },
  { label: '2021', value: '2021' },
  { label: '2020', value: '2020' },
  { label: '2010s', value: '2010s' },
  { label: 'Classic', value: 'classic' },
]

export const durationFilterOptions: Array<{ label: string; value: DurationBucket }> = [
  { label: 'Any', value: 'any' },
  { label: '10+ min', value: '10' },
  { label: '20+ min', value: '20' },
  { label: '30+ min', value: '30' },
  { label: '50+ min', value: '50' },
  { label: '80+ min', value: '80' },
  { label: '120+ min', value: '120' },
  { label: '180+ min', value: '180' },
  { label: '240+ min', value: '240' },
  { label: '400+ min', value: '400' },
]

export function getCategoryLabel(category: Category): string {
  if (category === 'movie') return 'Movie'
  if (category === 'series') return 'TV Series'
  return 'Book'
}

export function normalizeImageUrl(url: string | null | undefined): string | null {
  if (!url) return null

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }

  if (url.startsWith('/') && IMAGE_BASE_URL) {
    return `${IMAGE_BASE_URL}${url}`
  }

  return url
}

export function getItemImage(item: MediaItem): string {
  return (
    normalizeImageUrl(item.poster_url) ||
    normalizeImageUrl(item.backdrop_url) ||
    fallbackImages[item.category]
  )
}

export function getItemRating(item: MediaItem): number | null {
  const rating =
    item.category === 'book' ? item.book_rating_average : item.tmdb_vote_average

  if (typeof rating === 'number' && Number.isFinite(rating)) {
    return Number(rating.toFixed(1))
  }

  return null
}

export function getItemSecondaryMeta(item: MediaItem): string {
  const primaryGenre = item.genres?.[0] || ''

  if (item.category === 'book') {
    const author = item.authors?.[0] || ''
    if (author && primaryGenre) return `${author} • ${primaryGenre}`
    return author || primaryGenre || 'Media item'
  }

  if (item.year && primaryGenre) return `${item.year} • ${primaryGenre}`
  return String(item.year || primaryGenre || 'Media item')
}

export function sortCatalogItems(items: MediaItem[], sortBy: CatalogSort): MediaItem[] {
  const cloned = [...items]

  if (sortBy === 'title') {
    return cloned.sort((a, b) => a.title.localeCompare(b.title))
  }

  if (sortBy === 'newest') {
    return cloned.sort((a, b) => (b.year ?? 0) - (a.year ?? 0))
  }

  if (sortBy === 'oldest') {
    return cloned.sort((a, b) => (a.year ?? 0) - (b.year ?? 0))
  }

  return cloned.sort((a, b) => {
    const ratingA = getItemRating(a) ?? 0
    const ratingB = getItemRating(b) ?? 0

    if (ratingB !== ratingA) {
      return ratingB - ratingA
    }

    return (b.year ?? 0) - (a.year ?? 0)
  })
}

export function matchesYearBucket(item: MediaItem, yearBucket: YearBucket): boolean {
  if (yearBucket === 'any') return true

  const year = item.year ?? 0

  if (yearBucket === 'classic') return year < 2010
  if (yearBucket === '2010s') return year >= 2010 && year <= 2019

  return String(year) === yearBucket
}

function getScreenDuration(item: MediaItem): number | null {
  if (item.category === 'book') {
    return null
  }

  if (item.category === 'series') {
    const episodeRuntime = item.episode_run_time?.[0]
    if (typeof episodeRuntime === 'number') {
      return episodeRuntime
    }
  }

  if (typeof item.runtime === 'number') {
    return item.runtime
  }

  return null
}

export function matchesDurationBucket(
  item: MediaItem,
  durationBucket: DurationBucket,
): boolean {
  if (durationBucket === 'any') return true

  if (item.category === 'book') return true

  const duration = getScreenDuration(item)
  if (duration === null) return true

  const minDuration = Number(durationBucket)
  return duration >= minDuration
}