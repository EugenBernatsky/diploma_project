<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CatalogToolbar from '../components/catalog/CatalogToolbar.vue'
import type { CatalogViewMode } from '../components/catalog/CatalogToolbar.vue'
import CatalogFiltersSidebar from '../components/catalog/CatalogFiltersSidebar.vue'
import CatalogPagination from '../components/catalog/CatalogPagination.vue'
import MediaItemCard from '../components/catalog/MediaItemCard.vue'
import { getItems } from '../services/api'
import type { Category, GetItemsParams, MediaItem } from '../types/media'
import type {
  CatalogCategory,
  CatalogSort,
  DurationBucket,
  YearBucket,
} from '../utils/catalog'
import {
  getDurationBucketRange,
  getYearBucketRange,
  mapCatalogSortToItemSort,
} from '../utils/catalog'

const route = useRoute()
const router = useRouter()

const pageItems = ref<MediaItem[]>([])
const totalItemsCount = ref(0)
const isLoading = ref(true)
const errorText = ref('')

const currentCategory = ref<CatalogCategory>('all')
const searchQuery = ref('')
const sortBy = ref<CatalogSort>('popular')
const viewMode = ref<CatalogViewMode>('grid')

const selectedGenres = ref<string[]>([])
const selectedYearBucket = ref<YearBucket>('any')
const minRating = ref(0)
const selectedDurationBucket = ref<DurationBucket>('any')

const currentPage = ref(1)
const itemsPerPage = 12

const applyingRouteState = ref(false)

function parseCategoryQuery(value: unknown): CatalogCategory {
  if (value === 'movie' || value === 'series' || value === 'book' || value === 'all') {
    return value
  }

  return 'all'
}

function parseGenresQuery(value: unknown): string[] {
  const rawValue = Array.isArray(value)
    ? value.filter((item): item is string => typeof item === 'string').join(',')
    : value

  if (typeof rawValue !== 'string' || !rawValue.trim()) {
    return []
  }

  return rawValue
    .split(',')
    .map((genre) => genre.trim())
    .filter(Boolean)
}

function parseStringQuery(value: unknown): string {
  if (typeof value === 'string') {
    return value.trim()
  }

  if (Array.isArray(value) && typeof value[0] === 'string') {
    return value[0].trim()
  }

  return ''
}

function getApiCategory(): Category | undefined {
  if (currentCategory.value === 'all') {
    return undefined
  }

  return currentCategory.value
}

function getCatalogRequestParams(): GetItemsParams {
  const category = getApiCategory()
  const skip = (currentPage.value - 1) * itemsPerPage
  const query = searchQuery.value.trim()
  const yearRange = getYearBucketRange(selectedYearBucket.value)
  const params: GetItemsParams = {
    category,
    limit: itemsPerPage,
    skip,
    sort: mapCatalogSortToItemSort(sortBy.value, query),
    ...yearRange,
  }

  if (query) {
    params.search = query
  }

  if (selectedGenres.value.length > 0) {
    params.genres = selectedGenres.value
  }

  if (minRating.value > 0) {
    params.min_rating = minRating.value
  }

  if (category === 'movie' || category === 'series') {
    Object.assign(params, getDurationBucketRange(selectedDurationBucket.value))
  }

  return params
}

function applyRouteFilters() {
  applyingRouteState.value = true

  currentCategory.value = parseCategoryQuery(route.query.category)
  selectedGenres.value = parseGenresQuery(route.query.genres)
  searchQuery.value = parseStringQuery(route.query.search)

  nextTick(() => {
    applyingRouteState.value = false
  })
}

function getRouteQueryValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value
      .filter((item): item is string => typeof item === 'string')
      .join(',')
  }

  if (typeof value === 'string') {
    return value
  }

  return ''
}

function syncRouteFilters(): boolean {
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

  const normalizedSearch = searchQuery.value.trim()

  if (normalizedSearch) {
    nextQuery.search = normalizedSearch
  } else {
    delete nextQuery.search
  }

  const changed =
    getRouteQueryValue(route.query.category) !== getRouteQueryValue(nextQuery.category) ||
    getRouteQueryValue(route.query.genres) !== getRouteQueryValue(nextQuery.genres) ||
    getRouteQueryValue(route.query.search) !== getRouteQueryValue(nextQuery.search)

  if (changed) {
    router.replace({ query: nextQuery })
  }

  return changed
}

async function loadCatalog() {
  isLoading.value = true
  errorText.value = ''

  try {
    const response = await getItems(getCatalogRequestParams())

    pageItems.value = response.results
    totalItemsCount.value = response.total
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Unknown catalog error'
    pageItems.value = []
    totalItemsCount.value = 0
  } finally {
    isLoading.value = false
  }
}

const availableGenres = computed(() => {
  const set = new Set<string>()

  for (const genre of selectedGenres.value) {
    if (genre.trim()) {
      set.add(genre.trim())
    }
  }

  for (const item of pageItems.value) {
    for (const genre of item.genres || []) {
      if (genre?.trim()) {
        set.add(genre.trim())
      }
    }
  }

  return Array.from(set).sort((a, b) => a.localeCompare(b))
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(totalItemsCount.value / itemsPerPage))
})

const shownItemsCount = computed(() => pageItems.value.length)

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
  currentPage.value = 1
}

watch(
  () => route.query,
  () => {
    applyRouteFilters()
    currentPage.value = 1
    loadCatalog()
  },
  { deep: true },
)

watch(
  [
    searchQuery,
    currentCategory,
    sortBy,
    selectedGenres,
    selectedYearBucket,
    minRating,
    selectedDurationBucket,
  ],
  () => {
    if (applyingRouteState.value) {
      return
    }

    currentPage.value = 1

    if (!syncRouteFilters()) {
      loadCatalog()
    }
  },
  { deep: true },
)

watch(totalPages, (pages) => {
  if (currentPage.value > pages) {
    currentPage.value = pages
    loadCatalog()
  }
})

function handlePageChange(page: number) {
  if (page === currentPage.value) {
    return
  }

  currentPage.value = page
  loadCatalog()
}

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
            :view-mode="viewMode"
            @update:category="handleCategoryChange"
            @update:searchQuery="searchQuery = $event"
            @update:sortBy="sortBy = $event"
            @update:viewMode="viewMode = $event"
          />

          <div class="catalog-page__summary">
            <p class="catalog-page__summary-text">
              <span>{{ shownItemsCount }}</span> shown from
              <span>{{ totalItemsCount }}</span> items
            </p>

            <button type="button" class="catalog-page__refresh" @click="loadCatalog">
              Refresh
            </button>
          </div>

          <p v-if="errorText" class="catalog-page__error">
            {{ errorText }}
          </p>

          <div
            v-if="isLoading"
            class="catalog-grid"
            :class="{ 'catalog-grid--list': viewMode === 'list' }"
            >
            <div v-for="index in 12" :key="index" class="catalog-skeleton"></div>
          </div>

          <div
            v-else-if="pageItems.length > 0"
            class="catalog-grid"
            :class="{ 'catalog-grid--list': viewMode === 'list' }"
            >
            <MediaItemCard
              v-for="item in pageItems"
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
            @update:page="handlePageChange"
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

.catalog-grid--list {
  grid-template-columns: 1fr;
}

.catalog-grid--list :deep(.catalog-card) {
  display: grid;
  grid-template-columns: 132px minmax(0, 1fr);
  align-items: stretch;
}

.catalog-grid--list :deep(.catalog-card__poster) {
  aspect-ratio: auto;
  min-height: 178px;
  height: 100%;
}

.catalog-grid--list :deep(.catalog-card__body) {
  display: grid;
  align-content: center;
  padding: 20px 22px;
}

.catalog-grid--list :deep(.catalog-card__title) {
  font-size: 24px;
}

.catalog-grid--list :deep(.catalog-card__meta) {
  font-size: 15px;
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

  .catalog-grid--list :deep(.catalog-card) {
  grid-template-columns: 1fr;
  }

  .catalog-grid--list :deep(.catalog-card__poster) {
    aspect-ratio: 0.76 / 1;
    min-height: auto;
  }
}
</style>
