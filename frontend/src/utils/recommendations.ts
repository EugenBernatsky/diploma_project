import type { Category, MediaItem } from '../types/media'
import { getItemRating } from './catalog'

export type RecommendationShelf = {
  id: string
  title: string
  subtitle: string
  category: Category
  badge: string
  items: MediaItem[]
}

export type RecommendationGroup = {
  id: string
  title: string
  subtitle: string
  badge: string
  shelves: RecommendationShelf[]
}

type CatalogBuckets = {
  movie: MediaItem[]
  series: MediaItem[]
  book: MediaItem[]
}

function sortByRatingThenYear(items: MediaItem[]): MediaItem[] {
  return [...items].sort((a, b) => {
    const ratingA = getItemRating(a) ?? 0
    const ratingB = getItemRating(b) ?? 0

    if (ratingB !== ratingA) {
      return ratingB - ratingA
    }

    return (b.year ?? 0) - (a.year ?? 0)
  })
}

function sortByNewestThenRating(items: MediaItem[]): MediaItem[] {
  return [...items].sort((a, b) => {
    const yearA = a.year ?? 0
    const yearB = b.year ?? 0

    if (yearB !== yearA) {
      return yearB - yearA
    }

    return (getItemRating(b) ?? 0) - (getItemRating(a) ?? 0)
  })
}

function rotateItems(items: MediaItem[], offset: number): MediaItem[] {
  if (!items.length) return []

  const normalizedOffset = ((offset % items.length) + items.length) % items.length
  return [...items.slice(normalizedOffset), ...items.slice(0, normalizedOffset)]
}

function takeWindow(items: MediaItem[], count: number, offset = 0): MediaItem[] {
  if (!items.length) return []

  const rotated = rotateItems(items, offset)
  return rotated.slice(0, Math.min(count, rotated.length))
}

export function buildRecommendationGroups(
  buckets: CatalogBuckets,
  seed: number,
): RecommendationGroup[] {
  const topBooks = sortByRatingThenYear(buckets.book)
  const topMovies = sortByRatingThenYear(buckets.movie)
  const topSeries = sortByRatingThenYear(buckets.series)

  const newestBooks = sortByNewestThenRating(buckets.book)
  const newestMovies = sortByNewestThenRating(buckets.movie)
  const newestSeries = sortByNewestThenRating(buckets.series)

  const groups: RecommendationGroup[] = [
    {
      id: 'preferences',
      title: 'Based on your preferences',
      subtitle:
        'Direct picks built from your current catalog signals. For now this uses real items with lightweight frontend logic until the real recommendation engine is plugged in.',
      badge: 'YOUR PROFILE',
      shelves: [
        {
          id: 'pref-books',
          title: 'Recommended Books',
          subtitle: 'Strong-rated books that fit a thoughtful discovery shelf.',
          category: 'book',
          badge: 'Best Match',
          items: takeWindow(topBooks, 4, seed),
        },
        {
          id: 'pref-movies',
          title: 'Recommended Movies',
          subtitle: 'Top movie picks rotated from the current catalog pool.',
          category: 'movie',
          badge: 'Viewer Match',
          items: takeWindow(topMovies, 4, seed + 1),
        },
        {
          id: 'pref-series',
          title: 'Recommended TV Series',
          subtitle: 'Series with strong ratings and stable long-form appeal.',
          category: 'series',
          badge: 'Most Relevant',
          items: takeWindow(topSeries, 4, seed + 2),
        },
      ],
    },
    {
      id: 'community',
      title: 'Based on users with similar tastes',
      subtitle:
        'A community-style view built from other high-value catalog candidates. Still mock recommendation logic, but fed by real backend items.',
      badge: 'COMMUNITY WISDOM',
      shelves: [
        {
          id: 'community-books',
          title: 'Books Similar Minds Love',
          subtitle: 'Books that surface well when we rotate through high-quality titles.',
          category: 'book',
          badge: 'Readers Pick',
          items: takeWindow(newestBooks, 3, seed + 3),
        },
        {
          id: 'community-movies',
          title: 'Movies Gaining Traction',
          subtitle: 'Movie picks biased toward freshness and stronger ratings.',
          category: 'movie',
          badge: 'Community Pulse',
          items: takeWindow(newestMovies, 3, seed + 4),
        },
        {
          id: 'community-series',
          title: 'TV Series Everyone’s Talking About',
          subtitle: 'Series picks rotated from fresh and high-performing titles.',
          category: 'series',
          badge: 'Trending Now',
          items: takeWindow(newestSeries, 3, seed + 5),
        },
      ],
    },
  ]

  return groups.map((group) => ({
    ...group,
    shelves: group.shelves.filter((shelf) => shelf.items.length > 0),
  }))
}