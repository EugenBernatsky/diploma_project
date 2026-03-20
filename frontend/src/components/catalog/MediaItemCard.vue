<script setup lang="ts">
import type { MediaItem } from '../../types/media'
import { RouterLink } from 'vue-router'

defineProps<{
  item: MediaItem
}>()
</script>

<template>
  <li class="item-card">
    <h3 class="item-card__title">{{ item.title }}</h3>

    <p class="item-card__meta">
      <span>Категорія: {{ item.category }}</span>
      <span>Рік: {{ item.year }}</span>
    </p>

    <div class="item-card__genres">
      <span
        v-for="genre in item.genres"
        :key="genre"
        class="item-card__genre-badge"
      >
        {{ genre }}
      </span>
    </div>

    <p class="item-card__description">
      {{ item.description }}
    </p>

    <div class="item-card__actions">
      <RouterLink
        :to="`/items/${item.id}`"
        class="item-card__button"
      >
        Детальніше
      </RouterLink>
    </div>
  </li>
</template>

<style scoped>
.item-card {
  padding: 20px;
  border-radius: 16px;
  background: #1f2937;
  border: 1px solid #253043;
}

.item-card__title {
  margin: 0 0 10px;
  font-size: 28px;
  color: #f8fafc;
}

.item-card__meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin: 0 0 12px;
  color: #cbd5e1;
}

.item-card__genres {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.item-card__genre-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: #0f172a;
  border: 1px solid #374151;
  color: #93c5fd;
  font-size: 14px;
}

.item-card__description {
  margin: 0 0 16px;
  color: #cbd5e1;
  line-height: 1.6;
}

.item-card__actions {
  display: flex;
  gap: 10px;
}

.item-card__button {
  display: inline-block;
  border: none;
  border-radius: 12px;
  padding: 10px 14px;
  background: #2563eb;
  color: white;
  text-decoration: none;
  font-weight: 600;
}

.item-card__button:hover {
  background: #1d4ed8;
}
</style>