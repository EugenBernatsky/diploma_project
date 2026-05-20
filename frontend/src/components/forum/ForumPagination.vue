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
  <div v-if="props.totalPages > 1" class="forum-pagination">
    <button
      type="button"
      class="forum-pagination__arrow"
      :disabled="props.currentPage === 1"
      @click="goToPage(props.currentPage - 1)"
    >
      Previous
    </button>

    <template v-for="token in pageTokens" :key="String(token)">
      <span
        v-if="token === 'ellipsis-left' || token === 'ellipsis-right'"
        class="forum-pagination__ellipsis"
      >
        ...
      </span>

      <button
        v-else
        type="button"
        class="forum-pagination__page"
        :class="{ 'forum-pagination__page--active': token === props.currentPage }"
        @click="goToPage(token)"
      >
        {{ token }}
      </button>
    </template>

    <button
      type="button"
      class="forum-pagination__arrow"
      :disabled="props.currentPage === props.totalPages"
      @click="goToPage(props.currentPage + 1)"
    >
      Next
    </button>
  </div>
</template>

<style scoped>
.forum-pagination {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.forum-pagination__arrow,
.forum-pagination__page {
  min-width: 42px;
  height: 42px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.72);
  color: #cbd5e1;
  cursor: pointer;
  font-weight: 700;
}

.forum-pagination__page--active {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  border-color: transparent;
}

.forum-pagination__ellipsis {
  min-width: 26px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-weight: 700;
}

.forum-pagination__arrow:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>