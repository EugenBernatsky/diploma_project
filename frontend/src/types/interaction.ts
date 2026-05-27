export type InteractionType =
  | 'item_view'
  | 'trailer_click'
  | 'external_link_click'

export type InteractionSource =
  | 'catalog'
  | 'search'
  | 'recommendations'
  | 'similar_items'
  | 'favorites'
  | 'statuses'
  | 'home'
  | 'item_page'
  | 'profile'
  | 'forum'
  | 'other'

export type InteractionCreatePayload = {
  item_id: string
  interaction_type: InteractionType
  source?: InteractionSource
}

export type InteractionActionResponse = {
  message: string
}

export type InteractionResponse = {
  id: string
  item_id: string
  interaction_type: InteractionType
  source: InteractionSource
  created_at: string
}