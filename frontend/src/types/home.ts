export type HeroAction = {
  label: string
  to: string
  variant: 'primary' | 'secondary'
}

export type RecentlyAddedItem = {
  id: string | number
  title: string
  category: string
  rating: number | null
  image: string
}

export type PopularFilm = {
  id: string | number
  title: string
  year: number | null
  rating: number | null
  genres: string[]
  image: string
}

export type ForumTopic = {
  id: number
  title: string
  replies: number
  views: number
  timeAgo: string
  author: string
}

export type PromoTile = {
  id: number
  image: string
  alt: string
}

export type HomePageData = {
  hero: {
    badge: string
    title: string
    accentTitle: string
    description: string
    backgroundImage: string
    actions: HeroAction[]
  }
  recentlyAdded: RecentlyAddedItem[]
  popularFilms: PopularFilm[]
  hotTopics: ForumTopic[]
  promoTiles: PromoTile[]
}