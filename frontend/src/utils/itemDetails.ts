import type { MediaItem } from '../types/media'

export type ItemHeroChip = {
  label: string
  value: string
}

export type ItemFact = {
  label: string
  value: string
  href?: string
}

export type ItemAction = {
  label: string
  href: string
  variant: 'primary' | 'secondary'
}

export type ItemQuickFact = {
  label: string
  value: string
}

function formatDate(dateString?: string | null): string | null {
  if (!dateString) return null

  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return dateString

  return date.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function formatCountries(countries?: string[]): string | null {
  if (!countries?.length) return null
  return countries.join(', ')
}

function formatLanguage(value?: string | null): string | null {
  if (!value?.trim()) return null
  const normalized = value.trim()

  if (normalized.length <= 3) {
    return normalized.toUpperCase()
  }

  return normalized
}

function prettifyStatus(value?: string | null): string | null {
  if (!value?.trim()) return null

  return value
    .trim()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatRuntime(item: MediaItem): string | null {
  if (item.category === 'book') {
    if (typeof item.page_count === 'number') {
      return `${item.page_count} pages`
    }
    return null
  }

  if (item.category === 'series') {
    const episodeRuntime = item.episode_run_time?.[0]
    if (typeof episodeRuntime === 'number') {
      return `${episodeRuntime} min / ep`
    }
  }

  if (typeof item.runtime === 'number') {
    return `${item.runtime} min`
  }

  return null
}

function getBookFormats(item: MediaItem): string | null {
  const formats: string[] = []

  if (item.epub_available) formats.push('EPUB')
  if (item.pdf_available) formats.push('PDF')

  if (!formats.length) return null
  return formats.join(' • ')
}

function normalizeTitle(value?: string | null): string {
  return (value || '').trim().toLowerCase()
}

export function getOriginalDisplayTitle(item: MediaItem): string | null {
  const original =
    item.category === 'series'
      ? item.original_name?.trim() || item.original_title?.trim() || null
      : item.original_title?.trim() || item.original_name?.trim() || null

  if (!original) return null

  if (normalizeTitle(original) === normalizeTitle(item.title)) {
    return null
  }

  return original
}

export function getItemDisplayRating(item: MediaItem): string | null {
  if (item.category === 'book') {
    if (typeof item.book_rating_average === 'number') {
      return `${item.book_rating_average.toFixed(1)} / 5.0`
    }
    return null
  }

  if (typeof item.tmdb_vote_average === 'number') {
    return `${item.tmdb_vote_average.toFixed(1)} / 10.0`
  }

  return null
}

export function getItemSubtitle(item: MediaItem): string | null {
  if (item.tagline?.trim()) return item.tagline.trim()
  if (item.subtitle?.trim()) return item.subtitle.trim()

  if (item.category === 'movie') return 'Feature film details and metadata.'
  if (item.category === 'series') return 'Series overview, seasons, and release details.'
  return 'Book overview, publication info, and useful links.'
}

export function getHeroChips(item: MediaItem): ItemHeroChip[] {
  const chips: ItemHeroChip[] = []

  const rating = getItemDisplayRating(item)
  if (rating) {
    chips.push({
      label: item.category === 'book' ? 'Book Rating' : 'TMDb Rating',
      value: rating,
    })
  }

  const runtime = formatRuntime(item)
  if (runtime) {
    chips.push({
      label: item.category === 'book' ? 'Length' : 'Duration',
      value: runtime,
    })
  }

  if (item.category === 'movie' && item.release_date) {
    chips.push({
      label: 'Released',
      value: formatDate(item.release_date) || String(item.year),
    })
  } else if (item.category === 'series' && item.first_air_date) {
    chips.push({
      label: 'First aired',
      value: formatDate(item.first_air_date) || String(item.year),
    })
  } else if (item.category === 'book' && item.published_date) {
    chips.push({
      label: 'Published',
      value: formatDate(item.published_date) || String(item.year),
    })
  } else {
    chips.push({
      label: 'Year',
      value: String(item.year),
    })
  }

  const status = prettifyStatus(item.content_status)
  if (status) {
    chips.push({
      label: 'Status',
      value: status,
    })
  }

  if (item.category === 'series' && typeof item.number_of_seasons === 'number') {
    chips.push({
      label: 'Seasons',
      value: String(item.number_of_seasons),
    })
  }

  if (item.category === 'book' && typeof item.is_ebook === 'boolean') {
    chips.push({
      label: 'E-book',
      value: item.is_ebook ? 'Yes' : 'No',
    })
  }

  return chips
}

export function getHeroFacts(item: MediaItem): ItemFact[] {
  const facts: ItemFact[] = []

  if (item.category === 'movie') {
    if (
      item.original_title?.trim() &&
      normalizeTitle(item.original_title) !== normalizeTitle(item.title)
    ) {
      facts.push({ label: 'Original title', value: item.original_title.trim() })
    }

    if (item.release_date) {
      facts.push({
        label: 'Release date',
        value: formatDate(item.release_date) || item.release_date,
      })
    }

    const status = prettifyStatus(item.content_status)
    if (status) {
      facts.push({ label: 'Status', value: status })
    }

    const language = formatLanguage(item.original_language)
    if (language) {
      facts.push({ label: 'Language', value: language })
    }

    const countries = formatCountries(item.production_countries)
    if (countries) {
      facts.push({ label: 'Countries', value: countries })
    }

    if (typeof item.tmdb_vote_count === 'number') {
      facts.push({
        label: 'Vote count',
        value: item.tmdb_vote_count.toLocaleString(),
      })
    }
  }

  if (item.category === 'series') {
    if (
      item.original_name?.trim() &&
      normalizeTitle(item.original_name) !== normalizeTitle(item.title)
    ) {
      facts.push({ label: 'Original name', value: item.original_name.trim() })
    }

    if (item.first_air_date) {
      facts.push({
        label: 'First air date',
        value: formatDate(item.first_air_date) || item.first_air_date,
      })
    }

    const status = prettifyStatus(item.content_status)
    if (status) {
      facts.push({ label: 'Status', value: status })
    }

    if (typeof item.number_of_seasons === 'number') {
      facts.push({ label: 'Seasons', value: String(item.number_of_seasons) })
    }

    if (typeof item.number_of_episodes === 'number') {
      facts.push({ label: 'Episodes', value: String(item.number_of_episodes) })
    }

    const episodeRuntime = item.episode_run_time?.[0]
    if (typeof episodeRuntime === 'number') {
      facts.push({ label: 'Episode length', value: `${episodeRuntime} min` })
    }

    if (item.networks?.length) {
      facts.push({ label: 'Networks', value: item.networks.join(', ') })
    }

    const language = formatLanguage(item.original_language)
    if (language) {
      facts.push({ label: 'Language', value: language })
    }

    const countries = formatCountries(item.production_countries)
    if (countries) {
      facts.push({ label: 'Countries', value: countries })
    }

    if (typeof item.tmdb_vote_count === 'number') {
      facts.push({
        label: 'Vote count',
        value: item.tmdb_vote_count.toLocaleString(),
      })
    }
  }

  if (item.category === 'book') {
    if (item.subtitle?.trim()) {
      facts.push({ label: 'Subtitle', value: item.subtitle.trim() })
    }

    if (item.authors?.length) {
      facts.push({ label: 'Authors', value: item.authors.join(', ') })
    }

    if (item.publisher?.trim()) {
      facts.push({ label: 'Publisher', value: item.publisher.trim() })
    }

    if (item.published_date) {
      facts.push({
        label: 'Published date',
        value: formatDate(item.published_date) || item.published_date,
      })
    }

    if (typeof item.page_count === 'number') {
      facts.push({ label: 'Pages', value: String(item.page_count) })
    }

    if (typeof item.book_ratings_count === 'number') {
      facts.push({
        label: 'Ratings count',
        value: item.book_ratings_count.toLocaleString(),
      })
    }

    if (typeof item.is_ebook === 'boolean') {
      facts.push({ label: 'E-book', value: item.is_ebook ? 'Yes' : 'No' })
    }

    const formats = getBookFormats(item)
    if (formats) {
      facts.push({ label: 'Formats', value: formats })
    }

    if (item.preview_link?.trim()) {
      facts.push({
        label: 'Preview',
        value: 'Open preview',
        href: item.preview_link.trim(),
      })
    }

    const detailsLink = item.info_link?.trim() || item.canonical_link?.trim()
    if (detailsLink) {
      facts.push({
        label: 'More info',
        value: 'Open details',
        href: detailsLink,
      })
    }
  }

  return facts
}

export function getItemActions(item: MediaItem): ItemAction[] {
  const actions: ItemAction[] = []

  if (item.category === 'book') {
    if (item.preview_link?.trim()) {
      actions.push({
        label: 'Preview Book',
        href: item.preview_link.trim(),
        variant: 'primary',
      })
    }

    const detailsLink = item.info_link?.trim() || item.canonical_link?.trim()
    if (detailsLink) {
      actions.push({
        label: 'More Details',
        href: detailsLink,
        variant: 'secondary',
      })
    }

    return actions.slice(0, 2)
  }

  if (item.homepage?.trim()) {
    actions.push({
      label: 'Open Homepage',
      href: item.homepage.trim(),
      variant: 'primary',
    })
  }

  return actions.slice(0, 2)
}

export function getDescriptionHeading(item: MediaItem): string {
  return item.category === 'book' ? 'Book Description' : 'Plot Description'
}

export function getQuickFacts(item: MediaItem): ItemQuickFact[] {
  const facts: ItemQuickFact[] = []

  if (item.category === 'book') {
    if (typeof item.book_ratings_count === 'number') {
      facts.push({
        label: 'Ratings count',
        value: item.book_ratings_count.toLocaleString(),
      })
    }

    if (typeof item.page_count === 'number') {
      facts.push({
        label: 'Pages',
        value: String(item.page_count),
      })
    }

    const formats = getBookFormats(item)
    if (formats) {
      facts.push({
        label: 'Formats',
        value: formats,
      })
    }

    if (typeof item.is_ebook === 'boolean') {
      facts.push({
        label: 'E-book',
        value: item.is_ebook ? 'Yes' : 'No',
      })
    }
  } else {
    if (typeof item.tmdb_vote_count === 'number') {
      facts.push({
        label: 'Vote count',
        value: item.tmdb_vote_count.toLocaleString(),
      })
    }

    const runtime = formatRuntime(item)
    if (runtime) {
      facts.push({
        label: item.category === 'series' ? 'Episode length' : 'Runtime',
        value: runtime,
      })
    }

    const status = prettifyStatus(item.content_status)
    if (status) {
      facts.push({
        label: 'Status',
        value: status,
      })
    }
  }

  if (item.category === 'series' && typeof item.number_of_episodes === 'number') {
    facts.push({
      label: 'Episodes',
      value: String(item.number_of_episodes),
    })
  }

  const language = formatLanguage(item.original_language)
  if (language) {
    facts.push({
      label: 'Language',
      value: language,
    })
  }

  const countries = formatCountries(item.production_countries)
  if (countries) {
    facts.push({
      label: 'Countries',
      value: countries,
    })
  }

  facts.push({
    label: 'Category',
    value:
      item.category === 'movie'
        ? 'Movie'
        : item.category === 'series'
          ? 'TV Series'
          : 'Book',
  })

  return facts.slice(0, 6)
}

export function buildSimilarItems(current: MediaItem, all: MediaItem[], limit = 6): MediaItem[] {
  const currentGenres = new Set(current.genres)

  return [...all]
    .filter((item) => item.id !== current.id)
    .map((item) => {
      const sharedGenres = item.genres.filter((genre) => currentGenres.has(genre)).length
      const rating =
        item.category === 'book'
          ? item.book_rating_average ?? 0
          : item.tmdb_vote_average ?? 0

      const yearDistance = Math.abs((item.year ?? 0) - (current.year ?? 0))
      const score = sharedGenres * 100 + rating * 10 - yearDistance

      return { item, score }
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((entry) => entry.item)
}