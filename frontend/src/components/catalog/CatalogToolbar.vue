<script setup lang="ts">
import type { CatalogCategory, CatalogSort } from '../../utils/catalog'
export type CatalogViewMode = 'grid' | 'list'

const props = defineProps<{
  category: CatalogCategory
  searchQuery: string
  sortBy: CatalogSort
  viewMode: CatalogViewMode
}>()

const emit = defineEmits<{
  (e: 'update:category', value: CatalogCategory): void
  (e: 'update:searchQuery', value: string): void
  (e: 'update:sortBy', value: CatalogSort): void
  (e: 'update:viewMode', value: CatalogViewMode): void
}>()

const tabs: Array<{ label: string; value: CatalogCategory }> = [
  { label: 'All Media', value: 'all' },
  { label: 'Movies', value: 'movie' },
  { label: 'Books', value: 'book' },
  { label: 'TV Series', value: 'series' },
]

const sortOptions: Array<{ label: string; value: CatalogSort }> = [
  { label: 'Popular', value: 'popular' },
  { label: 'Newest', value: 'newest' },
  { label: 'Oldest', value: 'oldest' },
  { label: 'Title A–Z', value: 'title' },
]
</script>

<template>
  <div class="catalog-toolbar">
    <div class="catalog-toolbar__tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        type="button"
        class="catalog-toolbar__tab"
        :class="{ 'catalog-toolbar__tab--active': props.category === tab.value }"
        @click="emit('update:category', tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <label class="catalog-toolbar__search">
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
        :value="props.searchQuery"
        type="text"
        placeholder="Quick search title..."
        @input="emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
      />
    </label>

    <div class="catalog-toolbar__sort">
      <select
        :value="props.sortBy"
        @change="emit('update:sortBy', ($event.target as HTMLSelectElement).value as CatalogSort)"
      >
        <option v-for="option in sortOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
    </div>

    <div class="catalog-toolbar__view-buttons">
      <button
        type="button"
        class="catalog-toolbar__view-btn"
        :class="{ 'catalog-toolbar__view-btn--active': props.viewMode === 'grid' }"
        aria-label="Grid view"
        @click="emit('update:viewMode', 'grid')"
      >
        ⊞
      </button>

      <button
        type="button"
        class="catalog-toolbar__view-btn"
        :class="{ 'catalog-toolbar__view-btn--active': props.viewMode === 'list' }"
        aria-label="List view"
        @click="emit('update:viewMode', 'list')"
      >
        ☰
      </button>
    </div>
  </div>
</template>

<style scoped>
.catalog-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(220px, 1fr) 160px auto;
  gap: 14px;
  align-items: center;
  padding: 14px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  border-radius: 22px;
  background: rgba(9, 14, 25, 0.7);
}

.catalog-toolbar__tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.catalog-toolbar__tab {
  min-height: 48px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: transparent;
  color: #cbd5e1;
  cursor: pointer;
  font-weight: 600;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    border-color 0.2s ease;
}

.catalog-toolbar__tab--active {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  border-color: transparent;
}

.catalog-toolbar__search {
  position: relative;
  display: flex;
  align-items: center;
  height: 48px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.7);
}

.catalog-toolbar__search svg {
  position: absolute;
  left: 14px;
  width: 18px;
  height: 18px;
  color: #64748b;
}

.catalog-toolbar__search input {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: #f8fafc;
  padding: 0 16px 0 42px;
  border-radius: inherit;
}

.catalog-toolbar__search input::placeholder {
  color: #64748b;
}

.catalog-toolbar__sort select {
  width: 100%;
  height: 48px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.7);
  color: #f8fafc;
  padding: 0 14px;
  outline: none;
}

.catalog-toolbar__view-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.catalog-toolbar__view-btn {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.7);
  color: #cbd5e1;
  cursor: pointer;
}

.catalog-toolbar__view-btn--active {
  color: #60a5fa;
  border-color: rgba(96, 165, 250, 0.24);
}

@media (max-width: 1220px) {
  .catalog-toolbar {
    grid-template-columns: 1fr 1fr;
  }

  .catalog-toolbar__view-buttons {
    justify-content: flex-start;
  }
}

@media (max-width: 760px) {
  .catalog-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>