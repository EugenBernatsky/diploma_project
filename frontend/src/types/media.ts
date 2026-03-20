export type Category = 'movie' | 'series' | 'book'

export type MediaItem = {
  id: number
  title: string
  category: Category
  year: number
  genres: string[]
  description: string
}