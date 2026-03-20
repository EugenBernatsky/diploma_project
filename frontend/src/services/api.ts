import type { MediaItem, Category} from '../types/media'

export type HealthResponse = {
  status: string
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return response.json()
}

export async function getItems(category: Category): Promise<MediaItem[]> {
  const response = await fetch(`${API_BASE_URL}/items?category=${category}`)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return response.json()
}

export async function getItemById(itemId: number): Promise<MediaItem> {
  const response = await fetch(`${API_BASE_URL}/items/${itemId}`)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return response.json()
}