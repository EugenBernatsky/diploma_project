<script setup lang="ts">
import { ref } from 'vue'
import type { DurationBucket, YearBucket } from '../../utils/catalog'
import { durationFilterOptions, yearFilterOptions } from '../../utils/catalog'

const props = defineProps<{
  genres: string[]
  selectedGenres: string[]
  selectedYearBucket: YearBucket
  minRating: number
  selectedDurationBucket: DurationBucket
}>()

const emit = defineEmits<{
  (e: 'toggleGenre', value: string): void
  (e: 'update:yearBucket', value: YearBucket): void
  (e: 'update:minRating', value: number): void
  (e: 'update:durationBucket', value: DurationBucket): void
  (e: 'reset'): void
}>()

const genresOpen = ref(true)
const yearOpen = ref(true)
const ratingOpen = ref(true)
const durationOpen = ref(true)

function isGenreSelected(genre: string) {
  return props.selectedGenres.includes(genre)
}
</script>

<template>
  <aside class="catalog-filters">
    <div class="catalog-filters__top">
      <div class="catalog-filters__title-wrap">
        <span class="catalog-filters__icon">☷</span>
        <h2 class="catalog-filters__title">Filters</h2>
      </div>

      <button type="button" class="catalog-filters__reset" @click="emit('reset')">
        Reset
      </button>
    </div>

    <section class="catalog-filters__section">
      <button
        type="button"
        class="catalog-filters__section-head"
        @click="genresOpen = !genresOpen"
      >
        <h3>Genres</h3>
        <span>{{ genresOpen ? '−' : '+' }}</span>
      </button>

      <div v-if="genresOpen" class="catalog-filters__checkbox-list">
        <label
          v-for="genre in genres"
          :key="genre"
          class="catalog-filters__checkbox"
        >
          <input
            type="checkbox"
            :checked="isGenreSelected(genre)"
            @change="emit('toggleGenre', genre)"
          />
          <span>{{ genre }}</span>
        </label>

        <p v-if="genres.length === 0" class="catalog-filters__empty">
          No genres for current selection.
        </p>
      </div>
    </section>

    <section class="catalog-filters__section">
      <button
        type="button"
        class="catalog-filters__section-head"
        @click="yearOpen = !yearOpen"
      >
        <h3>Release Year</h3>
        <span>{{ yearOpen ? '−' : '+' }}</span>
      </button>

      <div v-if="yearOpen" class="catalog-filters__select-wrap">
        <select
          class="catalog-filters__select"
          :value="props.selectedYearBucket"
          @change="emit('update:yearBucket', ($event.target as HTMLSelectElement).value as YearBucket)"
        >
          <option
            v-for="option in yearFilterOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
    </section>

    <section class="catalog-filters__section">
      <button
        type="button"
        class="catalog-filters__section-head"
        @click="ratingOpen = !ratingOpen"
      >
        <h3>Minimum Rating</h3>
        <span>{{ ratingOpen ? '−' : '+' }}</span>
      </button>

      <div v-if="ratingOpen" class="catalog-filters__range-wrap">
        <input
          class="catalog-filters__range"
          type="range"
          min="0"
          max="10"
          step="0.1"
          :value="props.minRating"
          @input="emit('update:minRating', Number(($event.target as HTMLInputElement).value))"
        />

        <div class="catalog-filters__range-labels">
          <span>Any</span>
          <span>{{ props.minRating.toFixed(1) }}</span>
          <span>10.0</span>
        </div>
      </div>
    </section>

    <section class="catalog-filters__section">
      <button
        type="button"
        class="catalog-filters__section-head"
        @click="durationOpen = !durationOpen"
      >
        <h3>Screen Duration</h3>
        <span>{{ durationOpen ? '−' : '+' }}</span>
      </button>

      <div v-if="durationOpen" class="catalog-filters__select-wrap">
        <select
          class="catalog-filters__select"
          :value="props.selectedDurationBucket"
          @change="emit('update:durationBucket', ($event.target as HTMLSelectElement).value as DurationBucket)"
        >
          <option
            v-for="option in durationFilterOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>

        <p class="catalog-filters__hint">
          Works for movies and TV series. Books are ignored by this filter.
        </p>
      </div>
    </section>
  </aside>
</template>

<style scoped>
.catalog-filters {
  position: sticky;
  top: 96px;
  align-self: start;
  padding: 24px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.92);
}

.catalog-filters__top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.catalog-filters__title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.catalog-filters__icon {
  color: #60a5fa;
}

.catalog-filters__title {
  margin: 0;
  color: #f8fafc;
  font-size: 30px;
  letter-spacing: -0.03em;
}

.catalog-filters__reset {
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  font-weight: 600;
}

.catalog-filters__section {
  padding-top: 20px;
  margin-top: 20px;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
}

.catalog-filters__section:first-of-type {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

.catalog-filters__section-head {
  width: 100%;
  padding: 0;
  margin: 0 0 16px;
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #f8fafc;
  cursor: pointer;
}

.catalog-filters__section-head h3 {
  margin: 0;
  font-size: 16px;
}

.catalog-filters__checkbox-list {
  display: grid;
  gap: 12px;
}

.catalog-filters__checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #cbd5e1;
  font-size: 14px;
}

.catalog-filters__checkbox input {
  width: 16px;
  height: 16px;
}

.catalog-filters__empty {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.catalog-filters__select-wrap {
  display: grid;
  gap: 12px;
}

.catalog-filters__select {
  width: 100%;
  height: 46px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.75);
  color: #f8fafc;
  padding: 0 14px;
  outline: none;
}

.catalog-filters__range-wrap {
  display: grid;
  gap: 14px;
}

.catalog-filters__range {
  width: 100%;
}

.catalog-filters__range-labels {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #94a3b8;
  font-size: 13px;
}

.catalog-filters__hint {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}

@media (max-width: 1200px) {
  .catalog-filters {
    position: static;
  }
}
</style>