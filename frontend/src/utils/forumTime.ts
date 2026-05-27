const TIMEZONE_SUFFIX_RE = /(Z|[+-]\d{2}:\d{2})$/i

export function parseApiDate(value: string): Date {
  const raw = value?.trim()

  if (!raw) {
    return new Date(Number.NaN)
  }

  const normalized = TIMEZONE_SUFFIX_RE.test(raw) ? raw : `${raw}Z`
  return new Date(normalized)
}

export function formatRelativeTime(value: string): string {
  const target = parseApiDate(value).getTime()

  if (Number.isNaN(target)) {
    return 'Unknown'
  }

  const diffSeconds = Math.max(0, Math.floor((Date.now() - target) / 1000))

  if (diffSeconds < 45) {
    return 'just now'
  }

  const diffMinutes = Math.floor(diffSeconds / 60)
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

  return parseApiDate(value).toLocaleDateString('en-GB')
}