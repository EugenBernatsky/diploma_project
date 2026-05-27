<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { MediaItem } from '../../types/media'
import type { RecommendationItem } from '../../types/recommendations'
import {
  getItemImage,
  getItemRating,
  getItemSecondaryMeta,
} from '../../utils/catalog'

const props = defineProps<{
  currentItem: MediaItem
  recommendations: RecommendationItem[]
}>()


const catalogLink = computed(() => {
  const query: Record<string, string> = {
    category: props.currentItem.category,
  }

  if (props.currentItem.genres.length) {
    query.genres = props.currentItem.genres.join(',')
  }

  return {
    path: '/catalog',
    query,
  }
})

function getScoreLabel(score: number): string {
  if (!Number.isFinite(score)) {
    return ''
  }

  if (score >= 0 && score <= 1) {
    return `${Math.round(score * 100)}% similar`
  }

  return `Score ${score.toFixed(2)}`
}


</script>

<template>
  <section v-if="recommendations.length" class="item-similar">
    <div class="item-similar__header">
      <div>
        <h2 class="item-similar__title">Similar Items</h2>
        <p class="item-similar__subtitle">
          Content-based recommendations from the backend similarity model.
        </p>
      </div>

      <RouterLink :to="catalogLink" class="item-similar__link">
        View Entire Catalog
      </RouterLink>
    </div>

    <div class="item-similar__grid">
      <RouterLink
        v-for="recommendation in recommendations"
        :key="recommendation.item.id"
        :to="{
          path: `/items/${recommendation.item.id}`,
          query: {
            source: 'similar_items',
          },
        }"
        class="item-similar__card"
      >
        <div class="item-similar__poster">
          <img
            :src="getItemImage(recommendation.item)"
            :alt="recommendation.item.title"
          />

          <span
            v-if="getItemRating(recommendation.item) !== null"
            class="item-similar__rating"
          >
            ★ {{ getItemRating(recommendation.item)?.toFixed(1) }}
          </span>

          <span
            v-if="getScoreLabel(recommendation.score)"
            class="item-similar__score"
          >
            {{ getScoreLabel(recommendation.score) }}
          </span>
        </div>

        <div class="item-similar__body">
          <h3 class="item-similar__card-title">
            {{ recommendation.item.title }}
          </h3>

          <p class="item-similar__meta">
            {{ getItemSecondaryMeta(recommendation.item) }}
          </p>

          <p v-if="recommendation.reason" class="item-similar__reason">
            {{ recommendation.reason }}
          </p>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.item-similar {
  padding: 8px 0 0;
}

.item-similar__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 20px;
}

.item-similar__title {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 36px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.item-similar__subtitle {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.6;
}

.item-similar__link {
  color: #60a5fa;
  text-decoration: none;
  font-weight: 700;
  flex: 0 0 auto;
}

.item-similar__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.item-similar__card {
  display: block;
  text-decoration: none;
  border-radius: 18px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(148, 163, 184, 0.08);
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.item-similar__card:hover {
  transform: translateY(-4px);
  border-color: rgba(96, 165, 250, 0.22);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
}

.item-similar__poster {
  position: relative;
  aspect-ratio: 0.72 / 1;
  overflow: hidden;
  background: #111827;
}

.item-similar__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.item-similar__rating,
.item-similar__score {
  position: absolute;
  z-index: 1;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(2, 6, 23, 0.82);
  color: #dbeafe;
  font-size: 11px;
  font-weight: 700;
}

.item-similar__rating {
  top: 10px;
  right: 10px;
}

.item-similar__score {
  left: 10px;
  bottom: 10px;
}

.item-similar__body {
  padding: 12px 12px 14px;
}

.item-similar__card-title {
  margin: 0 0 6px;
  color: #f8fafc;
  font-size: 17px;
  line-height: 1.35;
}

.item-similar__meta {
  margin: 0;
  color: #94a3b8;
  font-size: 13px;
  line-height: 1.5;
}

.item-similar__reason {
  margin: 10px 0 0;
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.6;
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

@media (max-width: 1200px) {
  .item-similar__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .item-similar__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .item-similar__header {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 520px) {
  .item-similar__grid {
    grid-template-columns: 1fr;
  }
}
</style>