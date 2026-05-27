import type { Category } from '../types/media'
import type {
  RecommendationsResponse,
  SimilarItemsResponse,
} from '../types/recommendations'
import { apiRequest } from './http'

export type GetRecommendationsParams = {
  limit?: number
  category?: Category | null
}

export type GetSimilarItemsParams = {
  itemId: string
  limit?: number
  category?: Category | null
}

function buildRecommendationsQuery(params: {
  limit?: number
  category?: Category | null
}): string {
  const search = new URLSearchParams()

  if (typeof params.limit === 'number') {
    search.set('limit', String(params.limit))
  }

  if (params.category) {
    search.set('category', params.category)
  }

  return search.toString()
}

export async function getRecommendations(
  params: GetRecommendationsParams = {},
): Promise<RecommendationsResponse> {
  const query = buildRecommendationsQuery(params)
  const suffix = query ? `?${query}` : ''

  return apiRequest<RecommendationsResponse>(`/recommendations${suffix}`)
}

export async function getSimilarItems(
  params: GetSimilarItemsParams,
): Promise<SimilarItemsResponse> {
  const query = buildRecommendationsQuery({
    limit: params.limit,
    category: params.category,
  })

  const suffix = query ? `?${query}` : ''

  return apiRequest<SimilarItemsResponse>(
    `/recommendations/similar/${encodeURIComponent(params.itemId)}${suffix}`,
    {
      auth: false,
    },
  )
}