export type ItemStatus = 'planned' | 'in_progress' | 'completed' | 'dropped'

export type UserRatingResponse = {
  item_id: string
  score: number
}

export type RatingActionResponse = {
  message: string
}

export type UserItemStatusResponse = {
  item_id: string
  status: ItemStatus
}

export type StatusActionResponse = {
  message: string
}

export type FavoriteActionResponse = {
  message: string
}

export type InteractionType =
  | 'view'
  | 'open_details'
  | 'search_click'
  | 'recommendation_click'

export type InteractionSource =
  | 'catalog'
  | 'search'
  | 'recommendations'
  | 'favorites'
  | 'statuses'
  | 'other'

export type InteractionCreatePayload = {
  item_id: string
  interaction_type: InteractionType
  source?: InteractionSource | null
  value?: number
}

export type InteractionActionResponse = {
  message: string
}