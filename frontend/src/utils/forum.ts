import type {
  ForumCategoryType,
  ForumMockThread,
  ForumSortOption,
} from '../types/forum'

export function getForumCategoryLabel(
  categoryType: ForumCategoryType,
  customCategory: string | null,
): string {
  if (categoryType === 'movie') return 'Movies'
  if (categoryType === 'series') return 'TV Series'
  if (categoryType === 'book') return 'Books'
  return customCategory?.trim() || 'Custom'
}

export function formatForumRelativeTime(value: string): string {
  const now = Date.now()
  const target = new Date(value).getTime()

  if (Number.isNaN(target)) return 'Unknown'

  const diffMs = now - target
  const diffMinutes = Math.max(1, Math.floor(diffMs / (1000 * 60)))

  if (diffMinutes < 60) {
    return `${diffMinutes}m ago`
  }

  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) {
    return `${diffHours}h ago`
  }

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) {
    return `${diffDays}d ago`
  }

  const diffWeeks = Math.floor(diffDays / 7)
  if (diffWeeks < 5) {
    return `${diffWeeks}w ago`
  }

  return new Date(value).toLocaleDateString('en-GB')
}

export function formatCompactNumber(value: number): string {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(value >= 10000 ? 0 : 1)}k`
  }

  return String(value)
}

export function sortForumThreads(
  threads: ForumMockThread[],
  sortBy: ForumSortOption,
): ForumMockThread[] {
  const items = [...threads]

  if (sortBy === 'top') {
    return items.sort((a, b) => b.score - a.score)
  }

  if (sortBy === 'replies') {
    return items.sort((a, b) => b.replies_count - a.replies_count)
  }

  if (sortBy === 'newest') {
    return items.sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    )
  }

  return items.sort(
    (a, b) =>
      new Date(b.last_activity_at).getTime() -
      new Date(a.last_activity_at).getTime(),
  )
}

export function countTodayThreads(threads: ForumMockThread[]): number {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  const date = now.getDate()

  return threads.filter((thread) => {
    const created = new Date(thread.created_at)
    return (
      created.getFullYear() === year &&
      created.getMonth() === month &&
      created.getDate() === date
    )
  }).length
}