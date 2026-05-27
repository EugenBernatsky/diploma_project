<script setup lang="ts">
import type { Category } from '../../types/media'

type CategoryFilterValue = Category | null

defineProps<{
  selectedCategory: CategoryFilterValue
  isLoading?: boolean
}>()

const emit = defineEmits<{
  (event: 'change', value: CategoryFilterValue): void
}>()

const options: Array<{
  label: string
  value: CategoryFilterValue
}> = [
  { label: 'All', value: null },
  { label: 'Movies', value: 'movie' },
  { label: 'Series', value: 'series' },
  { label: 'Books', value: 'book' },
]
</script>

<template>
  <div class="recommendation-category-filter">
    <button
      v-for="option in options"
      :key="option.value ?? 'all'"
      type="button"
      class="recommendation-category-filter__button"
      :class="{
        'recommendation-category-filter__button--active':
          selectedCategory === option.value,
      }"
      :disabled="isLoading"
      @click="emit('change', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<style scoped>
.recommendation-category-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 14px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(9, 14, 25, 0.72);
}

.recommendation-category-filter__button {
  min-height: 44px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: transparent;
  color: #cbd5e1;
  cursor: pointer;
  font-weight: 700;
}

.recommendation-category-filter__button--active {
  border-color: transparent;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
}

.recommendation-category-filter__button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>