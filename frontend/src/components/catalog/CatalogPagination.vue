<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  currentPage: number
  totalPages: number
}>()

const emit = defineEmits<{
  (e: 'update:page', value: number): void
}>()

type PageToken = number | 'ellipsis-left' | 'ellipsis-right'

const pageTokens = computed<PageToken[]>(() => {
  const total = props.totalPages
  const current = props.currentPage

  if (total <= 7) {
    return Array.from({ length: total }, (_, index) => index + 1)
  }

  const tokens: PageToken[] = [1]

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)

  if (start > 2) {
    tokens.push('ellipsis-left')
  }

  for (let page = start; page <= end; page += 1) {
    tokens.push(page)
  }

  if (end < total - 1) {
    tokens.push('ellipsis-right')
  }

  tokens.push(total)

  return tokens
})

function goToPage(page: number) {
  if (page < 1 || page > props.totalPages || page === props.currentPage) {
    return
  }

  emit('update:page', page)
}
</script>

<template>
  <div v-if="props.totalPages > 1" class="catalog-pagination">
    <button
      type="button"
      class="catalog-pagination__arrow"
      :disabled="props.currentPage === 1"
      @click="goToPage(props.currentPage - 1)"
    >
      ‹
    </button>

    <template v-for="token in pageTokens" :key="String(token)">
      <span
        v-if="token === 'ellipsis-left' || token === 'ellipsis-right'"
        class="catalog-pagination__ellipsis"
      >
        ...
      </span>

      <button
        v-else
        type="button"
        class="catalog-pagination__page"
        :class="{ 'catalog-pagination__page--active': token === props.currentPage }"
        @click="goToPage(token)"
      >
        {{ token }}
      </button>
    </template>

    <button
      type="button"
      class="catalog-pagination__arrow"
      :disabled="props.currentPage === props.totalPages"
      @click="goToPage(props.currentPage + 1)"
    >
      ›
    </button>
  </div>
</template>

<style scoped>
.catalog-pagination {
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 28px;
}

.catalog-pagination__arrow,
.catalog-pagination__page {
  min-width: 42px;
  height: 42px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.72);
  color: #cbd5e1;
  cursor: pointer;
  font-weight: 700;
}

.catalog-pagination__page--active {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  border-color: transparent;
}

.catalog-pagination__ellipsis {
  min-width: 32px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-weight: 700;
}

.catalog-pagination__arrow:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>