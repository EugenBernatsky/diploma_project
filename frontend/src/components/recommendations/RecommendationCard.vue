<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { MediaItem } from '../../types/media'
import { getItemImage, getItemSecondaryMeta, getItemRating } from '../../utils/catalog'

const props = defineProps<{
  item: MediaItem
  badge?: string
}>()

const image = getItemImage(props.item)
const meta = getItemSecondaryMeta(props.item)
const rating = getItemRating(props.item)
</script>

<template>
  <RouterLink :to="`/items/${item.id}`" class="recommendation-card">
    <div class="recommendation-card__poster">
      <img :src="image" :alt="item.title" />

      <span v-if="badge" class="recommendation-card__badge">
        {{ badge }}
      </span>

      <span v-if="rating !== null" class="recommendation-card__rating">
        ★ {{ rating.toFixed(1) }}
      </span>
    </div>

    <div class="recommendation-card__body">
      <h3 class="recommendation-card__title">{{ item.title }}</h3>
      <p class="recommendation-card__meta">{{ meta }}</p>
    </div>
  </RouterLink>
</template>

<style scoped>
.recommendation-card {
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

.recommendation-card:hover {
  transform: translateY(-4px);
  border-color: rgba(96, 165, 250, 0.22);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
}

.recommendation-card__poster {
  position: relative;
  aspect-ratio: 0.75 / 1;
  overflow: hidden;
  background: #111827;
}

.recommendation-card__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.recommendation-card__poster::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 45%, rgba(2, 6, 23, 0.22) 100%);
}

.recommendation-card__badge,
.recommendation-card__rating {
  position: absolute;
  z-index: 1;
  top: 10px;
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(2, 6, 23, 0.82);
  color: #dbeafe;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.recommendation-card__badge {
  left: 10px;
}

.recommendation-card__rating {
  right: 10px;
}

.recommendation-card__body {
  padding: 14px 14px 16px;
}

.recommendation-card__title {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 18px;
  line-height: 1.35;
}

.recommendation-card__meta {
  margin: 0;
  color: #94a3b8;
  font-size: 13px;
  line-height: 1.5;
}
</style>