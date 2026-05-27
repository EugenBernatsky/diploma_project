<script setup lang="ts">
import { computed, onMounted, ref, watch,onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getFavorites, getStatusItems } from '../../services/userItemActions'
import type { MediaItem } from '../../types/media'
import type { ItemStatus } from '../../types/userItemActions'
import {
  getCategoryLabel,
  getItemImage,
  getItemRating,
  getItemSecondaryMeta,
} from '../../utils/catalog'

type LibraryTab = 'favorites' | ItemStatus

const PREVIEW_ITEMS_COUNT = 5
const MODAL_ITEMS_PER_PAGE = 20

const tabs: Array<{
  value: LibraryTab
  label: string
  description: string
}> = [
  {
    value: 'favorites',
    label: 'Favorites',
    description: 'Items you marked as favorite.',
  },
  {
    value: 'planned',
    label: 'Planned',
    description: 'Items you want to watch or read later.',
  },
  {
    value: 'in_progress',
    label: 'In Progress',
    description: 'Items you are currently watching or reading.',
  },
  {
    value: 'completed',
    label: 'Completed',
    description: 'Items you already finished.',
  },
  {
    value: 'dropped',
    label: 'Dropped',
    description: 'Items you decided to stop watching or reading.',
  },
]

const activeTab = ref<LibraryTab>('favorites')
const isLoading = ref(true)
const isRefreshing = ref(false)
const errorText = ref('')
const isModalOpen = ref(false)
const modalSearchQuery = ref('')
const modalCurrentPage = ref(1)

const itemsByTab = ref<Record<LibraryTab, MediaItem[]>>({
  favorites: [],
  planned: [],
  in_progress: [],
  completed: [],
  dropped: [],
})

const loadedTabs = ref<Record<LibraryTab, boolean>>({
  favorites: false,
  planned: false,
  in_progress: false,
  completed: false,
  dropped: false,
})

const activeItems = computed(() => {
  return itemsByTab.value[activeTab.value]
})

const previewItems = computed(() => {
  return activeItems.value.slice(0, PREVIEW_ITEMS_COUNT)
})

const hasMoreThanPreview = computed(() => {
  return activeItems.value.length > PREVIEW_ITEMS_COUNT
})

const filteredModalItems = computed(() => {
  const query = modalSearchQuery.value.trim().toLowerCase()

  if (!query) {
    return activeItems.value
  }

  return activeItems.value.filter((item) => {
    const title = item.title.toLowerCase()
    const genres = item.genres?.join(' ').toLowerCase() ?? ''
    const year = item.year ? String(item.year) : ''
    const category = item.category.toLowerCase()

    return (
      title.includes(query) ||
      genres.includes(query) ||
      year.includes(query) ||
      category.includes(query)
    )
  })
})

const totalModalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredModalItems.value.length / MODAL_ITEMS_PER_PAGE))
})

const paginatedModalItems = computed(() => {
  const start = (modalCurrentPage.value - 1) * MODAL_ITEMS_PER_PAGE
  const end = start + MODAL_ITEMS_PER_PAGE

  return filteredModalItems.value.slice(start, end)
})

const hasModalPagination = computed(() => {
  return totalModalPages.value > 1
})

const activeTabInfo = computed(() => {
  return tabs.find((tab) => tab.value === activeTab.value) ?? tabs[0]
})

const totalItemsCount = computed(() => {
  return Object.values(itemsByTab.value).reduce((sum, items) => sum + items.length, 0)
})

function getTabCount(tab: LibraryTab): number | null {
  if (!loadedTabs.value[tab]) {
    return null
  }

  return itemsByTab.value[tab].length
}

function getTabCountLabel(tab: LibraryTab): string {
  const count = getTabCount(tab)

  if (count === null) {
    return '...'
  }

  return String(count)
}

function formatRating(item: MediaItem): string | null {
  const rating = getItemRating(item)

  if (rating === null) {
    return null
  }

  return rating.toFixed(1)
}

function getItemGenres(item: MediaItem): string {
  if (!item.genres?.length) {
    return 'No genres'
  }

  return item.genres.slice(0, 3).join(' • ')
}

async function fetchTabItems(tab: LibraryTab): Promise<MediaItem[]> {
  if (tab === 'favorites') {
    return getFavorites()
  }

  return getStatusItems(tab)
}

async function loadAllTabs() {
  errorText.value = ''

  try {
    const results = await Promise.all([
      fetchTabItems('favorites'),
      fetchTabItems('planned'),
      fetchTabItems('in_progress'),
      fetchTabItems('completed'),
      fetchTabItems('dropped'),
    ])

    itemsByTab.value = {
      favorites: results[0],
      planned: results[1],
      in_progress: results[2],
      completed: results[3],
      dropped: results[4],
    }

    loadedTabs.value = {
      favorites: true,
      planned: true,
      in_progress: true,
      completed: true,
      dropped: true,
    }
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load your library.'
  }
}

async function loadInitialLibrary() {
  isLoading.value = true
  await loadAllTabs()
  isLoading.value = false
}

async function handleRefresh() {
  isRefreshing.value = true
  await loadAllTabs()
  isRefreshing.value = false
}

function resetModalState() {
  modalSearchQuery.value = ''
  modalCurrentPage.value = 1
}

function selectTab(tab: LibraryTab) {
  activeTab.value = tab
  resetModalState()
}

function openModal() {
  modalCurrentPage.value = 1
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
  resetModalState()
}

function goToModalPage(page: number) {
  modalCurrentPage.value = Math.min(Math.max(page, 1), totalModalPages.value)
}

function handleModalKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && isModalOpen.value) {
    closeModal()
  }
}

watch(isModalOpen, (value) => {
  document.body.style.overflow = value ? 'hidden' : ''
})

watch(modalSearchQuery, () => {
  modalCurrentPage.value = 1
})

watch(totalModalPages, (pages) => {
  if (modalCurrentPage.value > pages) {
    modalCurrentPage.value = pages
  }
})

onMounted(() => {
  loadInitialLibrary()
  window.addEventListener('keydown', handleModalKeydown)
})

onUnmounted(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', handleModalKeydown)
})
</script>

<template>
  <section id="library" class="profile-library">
    <div class="profile-library__head">
      <div>
        <p class="profile-library__eyebrow">My Library</p>
        <h2>Favorites & Status Lists</h2>
        <span>
          Your saved media content from ratings, favorites and status actions.
        </span>
      </div>

      <button
        type="button"
        class="profile-library__refresh"
        :disabled="isLoading || isRefreshing"
        @click="handleRefresh"
      >
        {{ isRefreshing ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <div class="profile-library__tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        type="button"
        class="profile-library__tab"
        :class="{ 'profile-library__tab--active': activeTab === tab.value }"
        @click="selectTab(tab.value)"
      >
        <span>{{ tab.label }}</span>
        <strong>{{ getTabCountLabel(tab.value) }}</strong>
      </button>
    </div>

    <div class="profile-library__summary">
      <div>
        <strong>{{ activeTabInfo.label }}</strong>
        <span>{{ activeTabInfo.description }}</span>
      </div>

      <div class="profile-library__summary-actions">
        <p>
          {{ activeItems.length }} items in this list
        </p>

        <button
          v-if="activeItems.length > 0"
          type="button"
          class="profile-library__see-all"
          @click="openModal"
        >
          See all
        </button>
      </div>
    </div>

    <p v-if="errorText" class="profile-library__error">
      {{ errorText }}
    </p>

    <div v-if="isLoading" class="profile-library__state">
      Loading your library...
    </div>

    <div v-else-if="activeItems.length === 0" class="profile-library__empty">
      <strong>No items here yet.</strong>
      <span>
        Open item details and add something to this list.
      </span>

      <RouterLink to="/catalog">
        Browse Catalog
      </RouterLink>
    </div>

    <div v-else class="profile-library__grid">
      <RouterLink
        v-for="item in previewItems"
        :key="item.id"
        :to="`/items/${item.id}`"
        class="profile-library-card"
      >
        <div class="profile-library-card__poster">
          <img :src="getItemImage(item)" :alt="item.title" />

          <span
            v-if="formatRating(item)"
            class="profile-library-card__rating"
          >
            ★ {{ formatRating(item) }}
          </span>
        </div>

        <div class="profile-library-card__body">
          <span class="profile-library-card__category">
            {{ getCategoryLabel(item.category) }}
          </span>

          <h3>{{ item.title }}</h3>

          <p class="profile-library-card__meta">
            {{ getItemSecondaryMeta(item) }}
          </p>

          <p class="profile-library-card__genres">
            {{ getItemGenres(item) }}
          </p>
        </div>
      </RouterLink>
    </div>

    <div
      v-if="hasMoreThanPreview"
      class="profile-library__footer"
    >
      <span>
        Showing {{ previewItems.length }} of {{ activeItems.length }} items
      </span>

      <button
        type="button"
        class="profile-library__see-all profile-library__see-all--footer"
        @click="openModal"
      >
        See all
      </button>
    </div>

    <p v-if="totalItemsCount === 0 && !isLoading" class="profile-library__hint">
      Your library is still empty. Add ratings, statuses or favorites from item details pages.
    </p>

    <div
      v-if="isModalOpen"
      class="profile-library-modal"
      @click.self="closeModal"
    >
    <div class="profile-library-modal__dialog">
        <div class="profile-library-modal__head">
            <div>
                <p class="profile-library__eyebrow">My Library</p>
                <h3>{{ activeTabInfo.label }}</h3>
                <span>
                {{ filteredModalItems.length }} of {{ activeItems.length }} items
                </span>
            </div>

                <button
                    type="button"
                    class="profile-library-modal__close"
                    aria-label="Close library modal"
                    @click="closeModal"
                >
                    ✕
                </button>
        </div>

        <div class="profile-library-modal__tools">
            <label class="profile-library-modal__search">
                <span>Search in this list</span>

                <input
                v-model="modalSearchQuery"
                type="search"
                placeholder="Search by title, genre, year..."
                autocomplete="off"
                />
            </label>
        </div>

        <div v-if="activeItems.length === 0" class="profile-library__empty">
            <strong>No items here yet.</strong>
            <span>
                Open item details and add something to this list.
            </span>
        </div>

        <div v-else-if="filteredModalItems.length === 0" class="profile-library__empty">
            <strong>No matches found.</strong>
            <span>
                Try another title, genre, year or category.
            </span>
        </div>

        <div v-else class="profile-library-modal__content">
          <div class="profile-library-modal__grid">
            <RouterLink
              v-for="item in paginatedModalItems"
              :key="item.id"
              :to="`/items/${item.id}`"
              class="profile-library-card"
              @click="closeModal"
            >
              <div class="profile-library-card__poster">
                <img :src="getItemImage(item)" :alt="item.title" />

                <span
                  v-if="formatRating(item)"
                  class="profile-library-card__rating"
                >
                  ★ {{ formatRating(item) }}
                </span>
              </div>

              <div class="profile-library-card__body">
                <span class="profile-library-card__category">
                  {{ getCategoryLabel(item.category) }}
                </span>

                <h3>{{ item.title }}</h3>

                <p class="profile-library-card__meta">
                  {{ getItemSecondaryMeta(item) }}
                </p>

                <p class="profile-library-card__genres">
                  {{ getItemGenres(item) }}
                </p>
              </div>
            </RouterLink>
          </div>
        </div>
        <div
            v-if="hasModalPagination"
            class="profile-library-modal__pagination"
        >
            <button
                type="button"
                :disabled="modalCurrentPage === 1"
                @click="goToModalPage(modalCurrentPage - 1)"
            >
                Previous
            </button>

            <span>
                Page {{ modalCurrentPage }} of {{ totalModalPages }}
            </span>

            <button
                type="button"
                :disabled="modalCurrentPage === totalModalPages"
                @click="goToModalPage(modalCurrentPage + 1)"
            >
                Next
            </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.profile-library {
  display: grid;
  gap: 18px;
  padding: 24px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
}

.profile-library__head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: start;
}

.profile-library__eyebrow {
  margin: 0 0 8px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.profile-library__head h2 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 30px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.profile-library__head span {
  color: #94a3b8;
  line-height: 1.7;
}

.profile-library__refresh {
  min-height: 42px;
  padding: 0 16px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
  color: #ffffff;
  font-weight: 800;
  cursor: pointer;
}

.profile-library__refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.profile-library__tabs {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}

.profile-library__tab {
  min-height: 62px;
  padding: 12px;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.55);
  color: #94a3b8;
  cursor: pointer;
  display: grid;
  gap: 6px;
  text-align: left;
}

.profile-library__tab span {
  font-size: 13px;
  font-weight: 800;
}

.profile-library__tab strong {
  color: #f8fafc;
  font-size: 22px;
  line-height: 1;
  min-height: 24px;
}

.profile-library__tab--active {
  border-color: rgba(96, 165, 250, 0.42);
  background: rgba(37, 99, 235, 0.16);
  color: #bfdbfe;
}

.profile-library__summary {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  padding: 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.55);
}

.profile-library__summary strong {
  display: block;
  margin-bottom: 4px;
  color: #f8fafc;
}

.profile-library__summary span,
.profile-library__summary p,
.profile-library__hint {
  margin: 0;
  color: #94a3b8;
  line-height: 1.6;
}

.profile-library__summary-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-library__see-all {
  min-height: 38px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(96, 165, 250, 0.3);
  background: rgba(37, 99, 235, 0.14);
  color: #dbeafe;
  font-weight: 800;
  cursor: pointer;
}

.profile-library__see-all--footer {
  min-height: 36px;
}

.profile-library__error {
  margin: 0;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(239, 68, 68, 0.12);
  color: #fca5a5;
  font-weight: 700;
}

.profile-library__state,
.profile-library__empty {
  padding: 24px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.55);
  color: #94a3b8;
}

.profile-library__empty {
  display: grid;
  gap: 10px;
  justify-items: start;
}

.profile-library__empty strong {
  color: #f8fafc;
  font-size: 18px;
}

.profile-library__empty a {
  min-height: 40px;
  padding: 0 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  text-decoration: none;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
}

.profile-library__grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.profile-library__footer {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  padding-top: 4px;
  color: #94a3b8;
}

.profile-library-card {
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.58);
  color: inherit;
  text-decoration: none;
  transition:
    transform 0.18s ease,
    border-color 0.18s ease;
}

.profile-library-card:hover {
  transform: translateY(-2px);
  border-color: rgba(96, 165, 250, 0.35);
}

.profile-library-card__poster {
  position: relative;
  aspect-ratio: 0.72 / 1;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.9);
}

.profile-library-card__poster img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.profile-library-card__rating {
  position: absolute;
  right: 10px;
  top: 10px;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(2, 6, 23, 0.82);
  color: #facc15;
  font-size: 12px;
  font-weight: 900;
}

.profile-library-card__body {
  display: grid;
  gap: 8px;
  padding: 14px;
}

.profile-library-card__category {
  width: fit-content;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.16);
  color: #93c5fd;
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.profile-library-card h3 {
  margin: 0;
  color: #f8fafc;
  font-size: 16px;
  line-height: 1.25;
}

.profile-library-card__meta,
.profile-library-card__genres {
  margin: 0;
  color: #94a3b8;
  font-size: 13px;
  line-height: 1.45;
}

.profile-library-card__genres {
  color: #64748b;
}

.profile-library-modal {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(2, 6, 23, 0.78);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.profile-library-modal__dialog {
  width: min(1320px, 100%);
  max-height: 88vh;
  overflow: hidden;
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr) auto;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(8, 14, 24, 0.98);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.42);
}

.profile-library-modal__tools {
  padding: 16px 24px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

.profile-library-modal__search {
  display: grid;
  gap: 8px;
}

.profile-library-modal__search span {
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 800;
}

.profile-library-modal__search input {
  width: 100%;
  min-height: 46px;
  padding: 0 14px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  outline: none;
}

.profile-library-modal__search input::placeholder {
  color: #64748b;
}

.profile-library-modal__search input:focus {
  border-color: rgba(96, 165, 250, 0.55);
}

.profile-library-modal__head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: start;
  padding: 22px 24px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

.profile-library-modal__head h3 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 30px;
  line-height: 1;
}

.profile-library-modal__head span {
  color: #94a3b8;
}

.profile-library-modal__close {
  width: 42px;
  height: 42px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
  color: #ffffff;
  font-size: 18px;
  cursor: pointer;
  flex: 0 0 auto;
}

.profile-library-modal__content {
  overflow-y: auto;
  padding: 24px;
}

.profile-library-modal__grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.profile-library-modal__pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 14px;
  padding: 16px 24px;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
}

.profile-library-modal__pagination span {
  color: #cbd5e1;
  font-weight: 800;
}

.profile-library-modal__pagination button {
  min-height: 38px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #ffffff;
  font-weight: 800;
  cursor: pointer;
}

.profile-library-modal__pagination button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

@media (max-width: 1180px) {
  .profile-library__grid,
  .profile-library-modal__grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .profile-library__tabs {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .profile-library__head,
  .profile-library__summary,
  .profile-library__footer,
  .profile-library-modal__head {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-library__tabs {
    grid-template-columns: 1fr;
  }

  .profile-library__grid,
  .profile-library-modal__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .profile-library__refresh,
  .profile-library__see-all {
    width: 100%;
  }

  .profile-library__summary-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .profile-library-modal {
    padding: 12px;
  }

  .profile-library-modal__dialog {
    max-height: 92vh;
  }

  .profile-library-modal__content {
    padding: 16px;
  }

  .profile-library-modal__tools,
    .profile-library-modal__pagination {
    padding: 14px 16px;
    }

    .profile-library-modal__pagination {
    flex-direction: column;
    align-items: stretch;
    }

    .profile-library-modal__pagination button {
    width: 100%;
    }
}
</style>