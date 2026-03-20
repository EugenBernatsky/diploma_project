<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import MediaItemCard from '../components/catalog/MediaItemCard.vue'
import { checkHealth, getItems } from '../services/api'
import type { Category, MediaItem } from '../types/media'

const apiStatus = ref('loading')
const apiMessage = ref('Перевіряємо з’єднання з backend...')
const errorText = ref('')
const items = ref<MediaItem[]>([])
const searchQuery = ref('')
const selectedGenre = ref('all')
const currentCategory = ref<Category>('movie')

const categoryLabels: Record<Category, string> = {
  movie: 'Фільми',
  series: 'Серіали',
  book: 'Книги',
}

const availableGenres = computed(() => {
  const genres = new Set<string>()

  for (const item of items.value) {
    for (const genre of item.genres) {
      genres.add(genre)
    }
  }

  return Array.from(genres).sort((a, b) => a.localeCompare(b))
})

const filteredItems = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  return items.value.filter((item) => {
    const matchesSearch =
      !query ||
      item.title.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query) ||
      item.genres.some((genre) => genre.toLowerCase().includes(query))

    const matchesGenre =
      selectedGenre.value === 'all' ||
      item.genres.includes(selectedGenre.value)

    return matchesSearch && matchesGenre
  })
})

async function loadPageData() {
  try {
    const health = await checkHealth()
    const data = await getItems(currentCategory.value)

    apiStatus.value = health.status
    apiMessage.value = `Показуємо каталог: ${categoryLabels[currentCategory.value]}`
    items.value = data
    errorText.value = ''
  } catch (error) {
    apiStatus.value = 'error'
    apiMessage.value = 'Не вдалося підключитися до backend.'
    errorText.value =
      error instanceof Error ? error.message : 'Невідома помилка'
  }
}

function resetFilters() {
  searchQuery.value = ''
  selectedGenre.value = 'all'
}

watch(currentCategory, () => {
  resetFilters()
  loadPageData()
})

onMounted(() => {
  loadPageData()
})
</script>

<template>
  <section class="catalog-page">
    <div class="catalog-page__inner">
      <div class="catalog-page__hero">
        <p class="catalog-page__tag">MediaCompass</p>
        <h2 class="catalog-page__title">Веб-портал для підбору медіа-контенту</h2>
        <p class="catalog-page__text">
          {{ apiMessage }}
        </p>
      </div>

      <div class="status-box">
        <span class="status-box__label">Статус API:</span>
        <span
          class="status-box__value"
          :class="{
            ok: apiStatus === 'ok',
            loading: apiStatus === 'loading',
            error: apiStatus === 'error'
          }"
        >
          {{ apiStatus }}
        </span>
      </div>

      <button class="action-button" @click="loadPageData">
        Оновити дані
      </button>

      <p v-if="errorText" class="error-text">
        Деталі: {{ errorText }}
      </p>

      <div class="category-switcher">
        <button
          class="category-button"
          :class="{ active: currentCategory === 'movie' }"
          @click="currentCategory = 'movie'"
        >
          Фільми
        </button>

        <button
          class="category-button"
          :class="{ active: currentCategory === 'series' }"
          @click="currentCategory = 'series'"
        >
          Серіали
        </button>

        <button
          class="category-button"
          :class="{ active: currentCategory === 'book' }"
          @click="currentCategory = 'book'"
        >
          Книги
        </button>
      </div>

      <section class="items-section">
        <div class="items-header">
          <h3 class="items-title">{{ categoryLabels[currentCategory] }}</h3>

          <div class="filters">
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Пошук за назвою, описом або жанром..."
            />

            <select v-model="selectedGenre" class="genre-select">
              <option value="all">Усі жанри</option>
              <option
                v-for="genre in availableGenres"
                :key="genre"
                :value="genre"
              >
                {{ genre }}
              </option>
            </select>

            <button class="secondary-button" @click="resetFilters">
              Скинути фільтри
            </button>
          </div>
        </div>

        <p class="results-info">
          Знайдено: {{ filteredItems.length }}
        </p>

        <ul v-if="filteredItems.length > 0" class="items-list">
          <MediaItemCard
            v-for="item in filteredItems"
            :key="item.id"
            :item="item"
          />
        </ul>

        <p v-else class="empty-state">
          У цій категорії нічого не знайдено.
        </p>
      </section>
    </div>
  </section>
</template>

<style scoped>
.catalog-page {
  width: 100%;
  padding: 40px 16px 56px;
}

.catalog-page__inner {
  width: min(920px, 100%);
  margin: 0 auto;
  padding: 32px;
  border-radius: 24px;
  background: #071533;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
}

.catalog-page__hero {
  margin-bottom: 24px;
}

.catalog-page__tag {
  margin: 0 0 12px;
  color: #60a5fa;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 14px;
}

.catalog-page__title {
  margin: 0 0 16px;
  font-size: 48px;
  line-height: 1.1;
  color: #f8fafc;
}

.catalog-page__text {
  margin: 0;
  color: #cbd5e1;
  font-size: 20px;
}

.status-box {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px 18px;
  border-radius: 14px;
  background: #1f2937;
}

.status-box__label {
  color: #cbd5e1;
  font-weight: 600;
}

.status-box__value {
  font-weight: 700;
  text-transform: uppercase;
}

.status-box__value.ok {
  color: #4ade80;
}

.status-box__value.loading {
  color: #facc15;
}

.status-box__value.error {
  color: #f87171;
}

.error-text {
  margin: 0 0 20px;
  color: #fca5a5;
}

.category-switcher {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin: 20px 0;
}

.category-button {
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 10px 16px;
  background: #111827;
  color: #e5e7eb;
  cursor: pointer;
  font-weight: 600;
}

.category-button:hover {
  border-color: #60a5fa;
}

.category-button.active {
  background: #2563eb;
  border-color: #2563eb;
  color: white;
}

.action-button {
  border: none;
  border-radius: 12px;
  padding: 12px 18px;
  background: #2563eb;
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.action-button:hover {
  background: #1d4ed8;
}

.items-section {
  margin-top: 32px;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.items-title {
  margin: 0;
  font-size: 28px;
  color: #f8fafc;
}

.filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  width: 100%;
}

.search-input {
  width: 100%;
  max-width: 320px;
  padding: 12px 14px;
  border: 1px solid #374151;
  border-radius: 12px;
  background: #0f172a;
  color: #e5e7eb;
  outline: none;
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-input:focus {
  border-color: #60a5fa;
}

.genre-select {
  min-width: 180px;
  padding: 12px 14px;
  border: 1px solid #374151;
  border-radius: 12px;
  background: #0f172a;
  color: #e5e7eb;
  outline: none;
}

.genre-select:focus {
  border-color: #60a5fa;
}

.secondary-button {
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 12px 18px;
  background: transparent;
  color: #e5e7eb;
  cursor: pointer;
  font-weight: 600;
}

.secondary-button:hover {
  border-color: #60a5fa;
}

.results-info {
  margin: 0 0 16px;
  color: #cbd5e1;
}

.items-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 16px;
}

.empty-state {
  margin: 0;
  padding: 18px;
  border-radius: 14px;
  background: #1f2937;
  color: #cbd5e1;
}

@media (max-width: 768px) {
  .catalog-page__inner {
    padding: 24px;
  }

  .catalog-page__title {
    font-size: 36px;
  }

  .catalog-page__text {
    font-size: 18px;
  }

  .search-input {
    max-width: 100%;
  }
}
</style>