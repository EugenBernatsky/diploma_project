<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getAdminItems } from '../../services/admin'
import type { AdminItem } from '../../types/admin'
import type { Category } from '../../types/media'

const emit = defineEmits<{
  (event: 'close'): void
}>()

const router = useRouter()

const PAGE_SIZE = 20
const SEARCH_DEBOUNCE_MS = 450

const items = ref<AdminItem[]>([])
const searchInput = ref('')
const categoryFilter = ref<Category | ''>('')
const skip = ref(0)
const total = ref(0)

const isLoading = ref(false)
const errorText = ref('')

let searchTimeoutId: number | undefined

const currentPage = computed(() => {
  return Math.floor(skip.value / PAGE_SIZE) + 1
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(total.value / PAGE_SIZE))
})

const searchTerm = computed(() => {
  const value = searchInput.value.trim()

  if (value.length >= 3) {
    return value
  }

  return ''
})

const searchHint = computed(() => {
  const value = searchInput.value.trim()

  if (value.length > 0 && value.length < 3) {
    return 'Enter at least 3 characters to search.'
  }

  return ''
})

function formatDate(value: string | null): string {
  if (!value) {
    return '—'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '—'
  }

  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date)
}

function formatGenres(item: AdminItem): string {
  if (!item.genres.length) {
    return 'No genres'
  }

  return item.genres.slice(0, 3).join(' • ')
}

async function loadItems() {
  isLoading.value = true
  errorText.value = ''

  try {
    const response = await getAdminItems({
      search: searchTerm.value || undefined,
      category: categoryFilter.value || undefined,
      limit: PAGE_SIZE,
      skip: skip.value,
    })

    items.value = response.results
    total.value = response.total
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load admin items.'
    items.value = []
    total.value = 0
  } finally {
    isLoading.value = false
  }
}

function scheduleReload() {
  window.clearTimeout(searchTimeoutId)

  searchTimeoutId = window.setTimeout(() => {
    skip.value = 0
    loadItems()
  }, SEARCH_DEBOUNCE_MS)
}

function goToPage(page: number) {
  const safePage = Math.min(Math.max(page, 1), totalPages.value)
  skip.value = (safePage - 1) * PAGE_SIZE
  loadItems()
}

function openItem(itemId: string) {
  emit('close')
  router.push(`/items/${itemId}`)
}

watch(searchInput, () => {
  scheduleReload()
})

watch(categoryFilter, () => {
  skip.value = 0
  loadItems()
})

onMounted(() => {
  loadItems()
})
</script>

<template>
  <section class="admin-items-tab">
    <header class="admin-items-tab__header">
      <div>
        <p class="admin-items-tab__eyebrow">Items</p>
        <h3>Media Items</h3>
        <span>
          Search media content, filter by category and open item details.
        </span>
      </div>

      <button
        type="button"
        class="admin-items-tab__refresh"
        :disabled="isLoading"
        @click="loadItems"
      >
        {{ isLoading ? 'Loading...' : 'Refresh' }}
      </button>
    </header>

    <div class="admin-items-tab__filters">
      <label class="admin-items-tab__field">
        <span>Search</span>
        <input
          v-model="searchInput"
          type="search"
          placeholder="Search by title, description, external id..."
          autocomplete="off"
        />
      </label>

      <label class="admin-items-tab__field admin-items-tab__field--select">
        <span>Category</span>
        <select v-model="categoryFilter">
          <option value="">All categories</option>
          <option value="movie">Movies</option>
          <option value="series">Series</option>
          <option value="book">Books</option>
        </select>
      </label>
    </div>

    <p v-if="searchHint" class="admin-items-tab__hint">
      {{ searchHint }}
    </p>

    <p v-if="errorText" class="admin-items-tab__error">
      {{ errorText }}
    </p>

    <div class="admin-items-tab__summary">
      <span>
        Page {{ currentPage }} of {{ totalPages }}
      </span>

      <strong>
        {{ total }} total items
      </strong>
    </div>

    <div v-if="isLoading" class="admin-items-tab__state">
      Loading items...
    </div>

    <div v-else-if="items.length === 0" class="admin-items-tab__state">
      No items found.
    </div>

    <div v-else class="admin-items-tab__list">
      <article
        v-for="item in items"
        :key="item.id"
        class="admin-item-card"
      >
        <div class="admin-item-card__poster">
          <img
            v-if="item.poster_url"
            :src="item.poster_url"
            :alt="item.title"
          />

          <span v-else>{{ item.title.charAt(0).toUpperCase() }}</span>
        </div>

        <div class="admin-item-card__body">
          <div class="admin-item-card__top">
            <div>
              <h4>{{ item.title }}</h4>

              <p>
                {{ item.category }}
                <span>•</span>
                {{ item.year || 'Unknown year' }}
                <span>•</span>
                {{ formatGenres(item) }}
              </p>
            </div>

            <span class="admin-item-card__source">
              {{ item.external_source || 'local' }}
            </span>
          </div>

          <p class="admin-item-card__description">
            {{ item.description || 'No description.' }}
          </p>

          <div class="admin-item-card__meta">
            <span>ID: {{ item.id }}</span>
            <span>External: {{ item.external_id || '—' }}</span>
            <span>Updated: {{ formatDate(item.updated_at || item.created_at) }}</span>
          </div>
        </div>

        <div class="admin-item-card__actions">
          <button
            type="button"
            class="admin-item-card__button"
            @click="openItem(item.id)"
          >
            Open
          </button>
        </div>
      </article>
    </div>

    <footer class="admin-items-tab__pagination">
      <button
        type="button"
        :disabled="isLoading || currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        Previous
      </button>

      <span>
        {{ currentPage }} / {{ totalPages }}
      </span>

      <button
        type="button"
        :disabled="isLoading || currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        Next
      </button>
    </footer>
  </section>
</template>

<style scoped>
.admin-items-tab {
  display: grid;
  gap: 18px;
}

.admin-items-tab__header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: start;
}

.admin-items-tab__eyebrow {
  margin: 0 0 8px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.admin-items-tab__header h3 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 30px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.admin-items-tab__header span,
.admin-items-tab__hint,
.admin-items-tab__summary span {
  color: #94a3b8;
  line-height: 1.6;
}

.admin-items-tab__refresh,
.admin-item-card__button,
.admin-items-tab__pagination button {
  min-height: 40px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #ffffff;
  font-weight: 800;
  cursor: pointer;
}

.admin-items-tab__refresh:disabled,
.admin-items-tab__pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.admin-items-tab__filters {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  gap: 14px;
}

.admin-items-tab__field {
  display: grid;
  gap: 8px;
}

.admin-items-tab__field span {
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 800;
}

.admin-items-tab__field input,
.admin-items-tab__field select {
  width: 100%;
  min-height: 44px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  outline: none;
}

.admin-items-tab__field input:focus,
.admin-items-tab__field select:focus {
  border-color: rgba(96, 165, 250, 0.55);
}

.admin-items-tab__error {
  margin: 0;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(239, 68, 68, 0.12);
  color: #fca5a5;
  font-weight: 700;
}

.admin-items-tab__summary {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.48);
}

.admin-items-tab__summary strong {
  color: #f8fafc;
}

.admin-items-tab__state {
  padding: 26px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.48);
  color: #94a3b8;
}

.admin-items-tab__list {
  display: grid;
  gap: 12px;
}

.admin-item-card {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.48);
}

.admin-item-card__poster {
  width: 82px;
  aspect-ratio: 0.72 / 1;
  overflow: hidden;
  border-radius: 14px;
  background: rgba(37, 99, 235, 0.16);
  color: #bfdbfe;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 900;
}

.admin-item-card__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.admin-item-card__body {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.admin-item-card__top {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: start;
}

.admin-item-card h4 {
  margin: 0 0 5px;
  color: #f8fafc;
  font-size: 18px;
}

.admin-item-card p {
  margin: 0;
}

.admin-item-card__top p,
.admin-item-card__description,
.admin-item-card__meta {
  color: #94a3b8;
  line-height: 1.5;
}

.admin-item-card__top p span {
  margin: 0 6px;
  color: #475569;
}

.admin-item-card__description {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.admin-item-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  font-size: 12px;
  color: #64748b;
}

.admin-item-card__source {
  flex: 0 0 auto;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.16);
  color: #93c5fd;
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
}

.admin-item-card__actions {
  display: flex;
  justify-content: flex-end;
}

.admin-item-card__button {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  border: none;
}

.admin-items-tab__pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 14px;
}

.admin-items-tab__pagination span {
  color: #cbd5e1;
  font-weight: 800;
}

@media (max-width: 860px) {
  .admin-items-tab__header,
  .admin-items-tab__summary,
  .admin-item-card__top {
    flex-direction: column;
    align-items: flex-start;
  }

  .admin-items-tab__filters {
    grid-template-columns: 1fr;
  }

  .admin-item-card {
    grid-template-columns: 72px minmax(0, 1fr);
  }

  .admin-item-card__actions {
    grid-column: 1 / -1;
    justify-content: stretch;
  }

  .admin-item-card__button {
    width: 100%;
  }
}

@media (max-width: 560px) {
  .admin-item-card {
    grid-template-columns: 1fr;
  }

  .admin-item-card__poster {
    width: 100%;
    max-height: 240px;
  }

  .admin-items-tab__pagination {
    display: grid;
    grid-template-columns: 1fr;
  }

  .admin-items-tab__pagination button {
    width: 100%;
  }
}
</style>