<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { MediaItem } from '../../types/media'
import { getItemImage, getItemRating, getItemSecondaryMeta } from '../../utils/catalog'

const props = defineProps<{
  currentItem: MediaItem
  items: MediaItem[]
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
</script>

<template>
  <section class="item-similar">
    <div class="item-similar__header">
      <h2 class="item-similar__title">Similar Adventures</h2>

      <RouterLink :to="catalogLink" class="item-similar__link">
        View Entire Catalog
      </RouterLink>
    </div>

    <div class="item-similar__grid">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        :to="`/items/${item.id}`"
        class="item-similar__card"
      >
        <div class="item-similar__poster">
          <img :src="getItemImage(item)" :alt="item.title" />
          <span v-if="getItemRating(item) !== null" class="item-similar__rating">
            ★ {{ getItemRating(item)?.toFixed(1) }}
          </span>
        </div>

        <div class="item-similar__body">
          <h3 class="item-similar__card-title">{{ item.title }}</h3>
          <p class="item-similar__meta">{{ getItemSecondaryMeta(item) }}</p>
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
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.item-similar__title {
  margin: 0;
  color: #f8fafc;
  font-size: 36px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.item-similar__link {
  color: #60a5fa;
  text-decoration: none;
  font-weight: 700;
}

.item-similar__grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 16px;
}

.item-similar__card {
  display: block;
  text-decoration: none;
}

.item-similar__poster {
  position: relative;
  aspect-ratio: 0.72 / 1;
  overflow: hidden;
  border-radius: 18px;
  background: #111827;
}

.item-similar__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.item-similar__rating {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(2, 6, 23, 0.8);
  color: #dbeafe;
  font-size: 11px;
  font-weight: 700;
}

.item-similar__body {
  padding: 12px 2px 0;
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