import type { RouteLocationRaw } from 'vue-router'
import type { InteractionSource } from '../types/interaction'

export function buildItemRoute(
  itemId: string | number,
  source: InteractionSource,
): RouteLocationRaw {
  return {
    path: `/items/${String(itemId)}`,
    query: { source },
  }
}