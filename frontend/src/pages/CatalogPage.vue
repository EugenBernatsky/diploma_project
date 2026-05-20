<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CatalogToolbar from '../components/catalog/CatalogToolbar.vue'
import CatalogFiltersSidebar from '../components/catalog/CatalogFiltersSidebar.vue'
import CatalogPagination from '../components/catalog/CatalogPagination.vue'
import MediaItemCard from '../components/catalog/MediaItemCard.vue'
import { getItems } from '../services/api'
import type { Category, MediaItem } from '../types/media'
import type {
  CatalogCategory,
  CatalogSort,
  DurationBucket,
  YearBucket,
} from '../utils/catalog'
import {
  getItemRating,
  matchesDurationBucket,
  matchesYearBucket,
  sortCatalogItems,
} from '../utils/catalog'

const route = useRoute()
const router = useRouter()

const allItems = ref<MediaItem[]>([])
const isLoading = ref(true)
const errorText = ref('')

const currentCategory = ref<CatalogCategory>('all')
const searchQuery = ref('')
const sortBy = ref<CatalogSort>('popular')

const selectedGenres = ref<string[]>([])
const selectedYearBucket = ref<YearBucket>('any')
const minRating = ref(0)
const selectedDurationBucket = ref<DurationBucket>('any')

const currentPage = ref(1)
const itemsPerPage = 12

const applyingRouteState = ref(false)
const pendingGenresFromRoute = ref<string[] | null>(null)

function uniqueById(items: MediaItem[]) {
  const seen = new Set<string>()
  const result: MediaItem[] = []

  for (const item of items) {
    const key = String(item.id)
    if (seen.has(key)) continue
    seen.add(key)
    result.push(item)
  }

  return result
}

function parseCategoryQuery(value: unknown): CatalogCategory {
  if (value === 'movie' || value === 'series' || value === 'book' || value === 'all') {
    return value
  }

  return 'all'
}

function parseGenresQuery(value: unknown): string[] {
  if (typeof value !== 'string' || !value.trim()) {
    return []
  }

  return value
    .split(',')
    .map((genre) => genre.trim())
    .filter(Boolean)
}

function applyRouteFilters() {
  applyingRouteState.value = true

  currentCategory.value = parseCategoryQuery(route.query.category)
  pendingGenresFromRoute.value = parseGenresQuery(route.query.genres)

  applyingRouteState.value = false
}

function syncRouteFilters() {
  const nextQuery = { ...route.query }

  if (currentCategory.value !== 'all') {
    nextQuery.category = currentCategory.value
  } else {
    delete nextQuery.category
  }

  if (selectedGenres.value.length) {
    nextQuery.genres = selectedGenres.value.join(',')
  } else {
    delete nextQuery.genres
  }

  router.replace({ query: nextQuery })
}

async function loadCatalog() {
  isLoading.value = true
  errorText.value = ''

  try {
    const categories: Category[] = ['movie', 'series', 'book']

    const results = await Promise.allSettled(
      categories.map((category) => getItems(category)),
    )

    const successfulItems = results
      .filter(
        (result): result is PromiseFulfilledResult<MediaItem[]> =>
          result.status === 'fulfilled',
      )
      .flatMap((result) => result.value)

    if (successfulItems.length === 0) {
      throw new Error('Catalog data was not loaded from the API.')
    }

    allItems.value = uniqueById(successfulItems)
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Unknown catalog error'
    allItems.value = []
  } finally {
    isLoading.value = false
  }
}

const categoryItems = computed(() => {
  if (currentCategory.value === 'all') {
    return allItems.value
  }

  return allItems.value.filter((item) => item.category === currentCategory.value)
})

const availableGenres = computed(() => {
  const set = new Set<string>()

  for (const item of categoryItems.value) {
    for (const genre of item.genres || []) {
      if (genre?.trim()) {
        set.add(genre.trim())
      }
    }
  }

  return Array.from(set).sort((a, b) => a.localeCompare(b))
})

const filteredItems = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  return categoryItems.value.filter((item) => {
    const matchesSearch =
      !query ||
      item.title.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query) ||
      item.genres.some((genre) => genre.toLowerCase().includes(query))

    const matchesGenres =
      selectedGenres.value.length === 0 ||
      selectedGenres.value.every((genre) => item.genres.includes(genre))

    const rating = getItemRating(item)
    const matchesRating = rating === null || rating >= minRating.value
    const matchesYear = matchesYearBucket(item, selectedYearBucket.value)
    const matchesDuration = matchesDurationBucket(item, selectedDurationBucket.value)

    return (
      matchesSearch &&
      matchesGenres &&
      matchesRating &&
      matchesYear &&
      matchesDuration
    )
  })
})

const sortedItems = computed(() => {
  return sortCatalogItems(filteredItems.value, sortBy.value)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(sortedItems.value.length / itemsPerPage))
})

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return sortedItems.value.slice(start, start + itemsPerPage)
})

function toggleGenre(genre: string) {
  if (selectedGenres.value.includes(genre)) {
    selectedGenres.value = selectedGenres.value.filter((item) => item !== genre)
    return
  }

  selectedGenres.value = [...selectedGenres.value, genre]
}

function resetSidebarFilters() {
  selectedGenres.value = []
  selectedYearBucket.value = 'any'
  minRating.value = 0
  selectedDurationBucket.value = 'any'
}

function handleCategoryChange(value: CatalogCategory) {
  currentCategory.value = value
  selectedGenres.value = []
}

watch(
  () => route.query,
  () => {
    applyRouteFilters()
  },
  { deep: true },
)

watch(availableGenres, (genres) => {
  if (pendingGenresFromRoute.value) {
    selectedGenres.value = pendingGenresFromRoute.value.filter((genre) =>
      genres.includes(genre),
    )
    pendingGenresFromRoute.value = null
    return
  }

  selectedGenres.value = selectedGenres.value.filter((genre) => genres.includes(genre))
})

watch(
  [currentCategory, selectedGenres],
  () => {
    if (applyingRouteState.value || pendingGenresFromRoute.value) {
      return
    }

    syncRouteFilters()
  },
  { deep: true },
)

watch(
  [
    currentCategory,
    searchQuery,
    sortBy,
    selectedGenres,
    selectedYearBucket,
    minRating,
    selectedDurationBucket,
  ],
  () => {
    currentPage.value = 1
  },
  { deep: true },
)

watch(totalPages, (pages) => {
  if (currentPage.value > pages) {
    currentPage.value = pages
  }
})

onMounted(async () => {
  applyRouteFilters()
  await loadCatalog()
})
</script>

<template>
  <section class="catalog-page">
    <div class="catalog-page__inner">
      <header class="catalog-page__hero">
        <h1 class="catalog-page__title">Explore Catalog</h1>
        <p class="catalog-page__text">
          Discover thousands of stories across our vast library of cinema, literature,
          and television series.
        </p>
      </header>

      <div class="catalog-page__content">
        <div class="catalog-page__main">
          <CatalogToolbar
            :category="currentCategory"
            :search-query="searchQuery"
            :sort-by="sortBy"
            @update:category="handleCategoryChange"
            @update:searchQuery="searchQuery = $event"
            @update:sortBy="sortBy = $event"
          />

          <div class="catalog-page__summary">
            <p class="catalog-page__summary-text">
              <span>{{ sortedItems.length }}</span> items found
            </p>

            <button type="button" class="catalog-page__refresh" @click="loadCatalog">
              Refresh
            </button>
          </div>

          <p v-if="errorText" class="catalog-page__error">
            {{ errorText }}
          </p>

          <div v-if="isLoading" class="catalog-grid">
            <div v-for="index in 12" :key="index" class="catalog-skeleton"></div>
          </div>

          <div v-else-if="paginatedItems.length > 0" class="catalog-grid">
            <MediaItemCard
              v-for="item in paginatedItems"
              :key="item.id"
              :item="item"
            />
          </div>

          <div v-else class="catalog-page__empty">
            No items match the current filters.
          </div>

          <CatalogPagination
            :current-page="currentPage"
            :total-pages="totalPages"
            @update:page="currentPage = $event"
          />
        </div>

        <CatalogFiltersSidebar
          :genres="availableGenres"
          :selected-genres="selectedGenres"
          :selected-year-bucket="selectedYearBucket"
          :min-rating="minRating"
          :selected-duration-bucket="selectedDurationBucket"
          @toggleGenre="toggleGenre"
          @update:yearBucket="selectedYearBucket = $event"
          @update:minRating="minRating = $event"
          @update:durationBucket="selectedDurationBucket = $event"
          @reset="resetSidebarFilters"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.catalog-page {
  width: 100%;
  padding: 30px 0 56px;
}

.catalog-page__inner {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding: 30px 0 0;
}

.catalog-page__hero {
  padding: 34px 28px 30px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  border-radius: 0 0 24px 24px;
  background:
    radial-gradient(circle at left top, rgba(37, 99, 235, 0.16), transparent 36%),
    rgba(7, 14, 24, 0.9);
  margin-bottom: 26px;
}

.catalog-page__title {
  margin: 0 0 12px;
  color: #f8fafc;
  font-size: clamp(42px, 5vw, 64px);
  line-height: 1;
  letter-spacing: -0.04em;
}

.catalog-page__text {
  max-width: 720px;
  margin: 0;
  color: #94a3b8;
  font-size: 18px;
  line-height: 1.7;
}

.catalog-page__content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 24px;
  align-items: start;
}

.catalog-page__main {
  min-width: 0;
}

.catalog-page__summary {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin: 18px 0 20px;
}

.catalog-page__summary-text {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

.catalog-page__summary-text span {
  color: #f8fafc;
  font-weight: 800;
}

.catalog-page__refresh {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
  color: #e2e8f0;
  border: 1px solid rgba(148, 163, 184, 0.1);
  cursor: pointer;
  font-weight: 600;
}

.catalog-page__error {
  margin: 0 0 16px;
  color: #fca5a5;
}

.catalog-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.catalog-skeleton {
  aspect-ratio: 0.76 / 1.28;
  border-radius: 18px;
  background: linear-gradient(
    90deg,
    rgba(15, 23, 42, 0.9) 0%,
    rgba(30, 41, 59, 0.95) 50%,
    rgba(15, 23, 42, 0.9) 100%
  );
  background-size: 220% 100%;
  animation: shimmer 1.4s linear infinite;
}

.catalog-page__empty {
  padding: 32px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(9, 14, 25, 0.7);
  color: #94a3b8;
  text-align: center;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }

  100% {
    background-position: -20% 0;
  }
}

@media (max-width: 1200px) {
  .catalog-page__content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1080px) {
  .catalog-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .catalog-page__inner {
    width: min(100%, calc(100% - 32px));
  }

  .catalog-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .catalog-page__hero {
    padding: 28px 20px 24px;
  }

  .catalog-page__summary {
    flex-direction: column;
    align-items: flex-start;
  }

  .catalog-grid {
    grid-template-columns: 1fr;
  }
}
</style>