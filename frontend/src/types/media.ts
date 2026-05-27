export type Category = 'movie' | 'series' | 'book'
export type MediaItemId = string

export type MediaTrailer = {
  name: string
  site: string
  url: string
  language?: string | null
}

export type MediaProviderLink = {
  provider_name: string
  provider_type: string
  region?: string | null
  url: string
}

export type MediaItemStatusCounts = {
  planned: number
  in_progress: number
  completed: number
  dropped: number
}

export type MediaItemStats = {
  item_id: string
  user_rating_average: number | null
  user_ratings_count: number
  favorites_count: number
  statuses_total_count: number
  status_counts: MediaItemStatusCounts
  comments_count: number
}

export type MediaItem = {
  id: string
  title: string
  category: Category
  year: number
  genres: string[]
  description: string

  poster_url?: string | null
  backdrop_url?: string | null

  external_source?: string | null
  external_id?: string | null

  original_title?: string | null
  original_name?: string | null
  original_language?: string | null

  release_date?: string | null
  first_air_date?: string | null

  tagline?: string | null
  content_status?: string | null
  homepage?: string | null

  production_countries?: string[]

  tmdb_vote_average?: number | null
  tmdb_vote_count?: number | null

  runtime?: number | null
  imdb_id?: string | null

  episode_run_time?: number[]
  number_of_seasons?: number | null
  number_of_episodes?: number | null
  networks?: string[]

  subtitle?: string | null
  authors?: string[]
  publisher?: string | null
  published_date?: string | null
  page_count?: number | null

  book_rating_average?: number | null
  book_ratings_count?: number | null

  preview_link?: string | null
  info_link?: string | null
  canonical_link?: string | null
  web_reader_link?: string | null

  saleability?: string | null
  is_ebook?: boolean | null

  viewability?: string | null
  access_view_status?: string | null
  epub_available?: boolean | null
  pdf_available?: boolean | null

  trailers?: MediaTrailer[]
  watch_links?: MediaProviderLink[]
  purchase_links?: MediaProviderLink[]
}