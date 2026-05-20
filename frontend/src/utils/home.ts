import type { RecentlyAddedItem, PopularFilm } from '../types/home'
import type { Category, MediaItem } from '../types/media'

const fallbackImages: Record<Category, string> = {
  movie:
    'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=900&q=80',
  series:
    'https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=900&q=80',
  book:
    'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80',
}

const IMAGE_BASE_URL = (import.meta.env.VITE_IMAGE_BASE_URL || '').replace(/\/+$/, '')

function formatCategoryLabel(category: Category): string {
  if (category === 'movie') return 'MOVIE'
  if (category === 'series') return 'TV SERIES'
  return 'BOOK'
}

function normalizeImageUrl(url: string | null | undefined): string | null {
  if (!url) return null

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }

  if (url.startsWith('/') && IMAGE_BASE_URL) {
    return `${IMAGE_BASE_URL}${url}`
  }

  return url
}

function resolveImage(item: MediaItem): string {
  return (
    normalizeImageUrl(item.poster_url) ||
    normalizeImageUrl(item.backdrop_url) ||
    fallbackImages[item.category]
  )
}

function resolveRating(item: MediaItem, index = 0): number | null {
  let rating: number | null = null

  if (item.category === 'book') {
    rating =
      typeof item.book_rating_average === 'number'
        ? item.book_rating_average
        : null
  } else {
    rating =
      typeof item.tmdb_vote_average === 'number'
        ? item.tmdb_vote_average
        : null
  }

  if (typeof rating === 'number' && Number.isFinite(rating)) {
    return Number(rating.toFixed(1))
  }

  const fallbackRatings = [8.9, 4.5, 9.2, 7.8, 8.4]
  return fallbackRatings[index % fallbackRatings.length] ?? null
}

export function toRecentlyAddedItem(
  item: MediaItem,
  index: number,
): RecentlyAddedItem {
  return {
    id: item.id,
    title: item.title,
    category: formatCategoryLabel(item.category),
    rating: resolveRating(item, index),
    image: resolveImage(item),
  }
}

export function toPopularFilm(item: MediaItem, index: number): PopularFilm {
  return {
    id: item.id,
    title: item.title,
    year: item.year ?? null,
    rating: resolveRating(item, index),
    genres: item.genres?.slice(0, 2) ?? [],
    image: resolveImage(item),
  }
}