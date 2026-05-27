<script setup lang="ts">
import type { ForumCategoryType, ForumThreadSort } from '../../types/forum'

type ForumCategoryFilter = 'all' | ForumCategoryType

defineProps<{
  category: ForumCategoryFilter
  searchQuery: string
  sortBy: ForumThreadSort
}>()

const emit = defineEmits<{
  (e: 'update:category', value: ForumCategoryFilter): void
  (e: 'update:searchQuery', value: string): void
  (e: 'update:sortBy', value: ForumThreadSort): void
}>()

const tabs: Array<{ label: string; value: ForumCategoryFilter }> = [
  { label: 'All Topics', value: 'all' },
  { label: 'Movies', value: 'movie' },
  { label: 'Books', value: 'book' },
  { label: 'TV Series', value: 'series' },
  { label: 'Custom', value: 'custom' },
]

const sortOptions: Array<{ label: string; value: ForumThreadSort }> = [
  { label: 'Last Active', value: 'activity' },
  { label: 'Newest', value: 'newest' },
  { label: 'Top Score', value: 'score' },
]
</script>

<template>
  <div class="forum-toolbar">
    <div class="forum-toolbar__tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        type="button"
        class="forum-toolbar__tab"
        :class="{ 'forum-toolbar__tab--active': category === tab.value }"
        @click="emit('update:category', tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <label class="forum-toolbar__search">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M10.5 18a7.5 7.5 0 1 1 5.303-2.197L21 21"
          fill="none"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.8"
        />
      </svg>

      <input
        :value="searchQuery"
        type="text"
        placeholder="Search discussions..."
        @input="emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
      />
    </label>

    <div class="forum-toolbar__sort">
      <select
        :value="sortBy"
        @change="emit('update:sortBy', ($event.target as HTMLSelectElement).value as ForumThreadSort)"
      >
        <option v-for="option in sortOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
    </div>
  </div>
</template>

<style scoped>
.forum-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(240px, 1fr) 170px;
  gap: 14px;
  align-items: center;
  padding: 14px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  border-radius: 22px;
  background: rgba(9, 14, 25, 0.7);
}

.forum-toolbar__tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.forum-toolbar__tab {
  min-height: 42px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: transparent;
  color: #cbd5e1;
  cursor: pointer;
  font-weight: 600;
}

.forum-toolbar__tab--active {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  border-color: transparent;
}

.forum-toolbar__search {
  position: relative;
  display: flex;
  align-items: center;
  height: 46px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.72);
}

.forum-toolbar__search svg {
  position: absolute;
  left: 14px;
  width: 18px;
  height: 18px;
  color: #64748b;
}

.forum-toolbar__search input {
  width: 100%;
  height: 100%;
  padding: 0 14px 0 42px;
  border: none;
  outline: none;
  border-radius: inherit;
  background: transparent;
  color: #f8fafc;
}

.forum-toolbar__search input::placeholder {
  color: #64748b;
}

.forum-toolbar__sort select {
  width: 100%;
  height: 46px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  padding: 0 14px;
  outline: none;
}

@media (max-width: 1100px) {
  .forum-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>