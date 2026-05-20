<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { MediaItem } from '../../types/media'
import {
  getCategoryLabel,
  getItemImage,
  getItemRating,
  getItemSecondaryMeta,
} from '../../utils/catalog'

const props = defineProps<{
  item: MediaItem
}>()

const image = getItemImage(props.item)
const rating = getItemRating(props.item)
const categoryLabel = getCategoryLabel(props.item.category)
const secondaryMeta = getItemSecondaryMeta(props.item)
</script>

<template>
  <RouterLink :to="`/items/${item.id}`" class="catalog-card">
    <div class="catalog-card__poster">
      <img :src="image" :alt="item.title" />

      <span class="catalog-card__category">
        {{ categoryLabel }}
      </span>

      <span v-if="rating !== null" class="catalog-card__rating">
        ★ {{ rating.toFixed(1) }}
      </span>
    </div>

    <div class="catalog-card__body">
      <h3 class="catalog-card__title">{{ item.title }}</h3>
      <p class="catalog-card__meta">{{ secondaryMeta }}</p>
    </div>
  </RouterLink>
</template>

<style scoped>
.catalog-card {
  display: block;
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.66);
  text-decoration: none;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.catalog-card:hover {
  transform: translateY(-4px);
  border-color: rgba(96, 165, 250, 0.22);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
}

.catalog-card__poster {
  position: relative;
  aspect-ratio: 0.76 / 1;
  overflow: hidden;
  background: #111827;
}

.catalog-card__poster::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(2, 6, 23, 0.18) 100%);
}

.catalog-card__poster img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.catalog-card__category,
.catalog-card__rating {
  position: absolute;
  z-index: 1;
  top: 10px;
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(2, 6, 23, 0.8);
  color: #dbeafe;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.catalog-card__category {
  left: 10px;
}

.catalog-card__rating {
  right: 10px;
}

.catalog-card__body {
  padding: 14px 14px 16px;
}

.catalog-card__title {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 18px;
  line-height: 1.35;
}

.catalog-card__meta {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.5;
}
</style>