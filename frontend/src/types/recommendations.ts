import type { Category, MediaItem } from './media'

export type RecommendationCategory = Category

export type RecommendationSectionKey =
  | 'based_on_preferences'
  | 'popular_now'
  | 'similar_users'

export type RecommendationAlgorithm =
  | 'hybrid_content_popularity'
  | 'popularity_fallback'
  | 'popularity_score'
  | 'collaborative_filtering'
  | 'content_based_similarity'

export type RecommendationStatus =
  | 'personalized'
  | 'cold_start_fallback'
  | 'personalized_fallback'
  | 'model_not_trained'
  | 'available'
  | 'unavailable'
  | 'waiting_for_more_user_data'

export type RecommendationItem = {
  item: MediaItem
  score: number
  reason: string
}

export type RecommendationSection = {
  key: RecommendationSectionKey | string
  title: string
  algorithm: RecommendationAlgorithm | string
  status: RecommendationStatus | string
  items: RecommendationItem[]
}

export type RecommendationsResponse = {
  sections: RecommendationSection[]
}

export type SimilarItemsResponse = {
  source_item_id: string
  algorithm: 'content_based_similarity' | string
  status: RecommendationStatus | string
  items: RecommendationItem[]
}