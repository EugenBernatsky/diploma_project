<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../../services/auth'
import {
  addToFavorites,
  createRating,
  deleteMyStatus,
  deleteRating,
  getFavorites,
  getMyRating,
  getMyStatus,
  removeFromFavorites,
  setMyStatus,
  updateRating,
} from '../../services/userItemActions'
import { createInteraction } from '../../services/interactions'
import type { InteractionSource } from '../../types/interaction'
import type { ItemStatus } from '../../types/userItemActions'

const props = defineProps<{
  itemId: string
  homepageUrl?: string | null
  source?: string | null
}>()

const emit = defineEmits<{
  (e: 'changed'): void
}>()

const { isLoggedIn } = useAuth()
const route = useRoute()
const router = useRouter()

const isLoading = ref(true)
const errorText = ref('')
const successText = ref('')

const currentRating = ref<number | null>(null)
const selectedRating = ref<number>(0)

const currentStatus = ref<ItemStatus | null>(null)
const isFavorite = ref(false)

const isStatusMenuOpen = ref(false)
const isRatingPanelOpen = ref(false)

const isRatingBusy = ref(false)
const isStatusBusy = ref(false)
const isFavoriteBusy = ref(false)

const lastTrackedKey = ref('')

const statusOptions: Array<{ value: ItemStatus; label: string }> = [
  { value: 'planned', label: 'Planned' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'dropped', label: 'Dropped' },
]

function normalizeSource(source?: string | null): InteractionSource {
  if (
    source === 'catalog' ||
    source === 'search' ||
    source === 'recommendations' ||
    source === 'similar_items' ||
    source === 'favorites' ||
    source === 'statuses' ||
    source === 'home' ||
    source === 'item_page' ||
    source === 'profile' ||
    source === 'forum'
  ) {
    return source
  }

  return 'other'
}

function redirectToLogin() {
  router.push({
    path: '/login',
    query: {
      redirect: route.fullPath,
    },
  })
}

const currentStatusLabel = computed(() => {
  if (!isLoggedIn.value) return 'Log in to Set Status'
  if (currentStatus.value === 'planned') return 'Planned'
  if (currentStatus.value === 'in_progress') return 'In Progress'
  if (currentStatus.value === 'completed') return 'Completed'
  if (currentStatus.value === 'dropped') return 'Dropped'
  return 'Set Status'
})

const favoriteButtonLabel = computed(() => {
  if (!isLoggedIn.value) return 'Log in to Add Favorite'
  return isFavorite.value ? 'Remove from Favorites' : 'Add to Favorites'
})

const ratingButtonLabel = computed(() => {
  return currentRating.value === null ? 'Save Rating' : 'Update Rating'
})

async function loadUserState() {
  errorText.value = ''
  successText.value = ''

  if (!isLoggedIn.value) {
    currentRating.value = null
    selectedRating.value = 0
    currentStatus.value = null
    isFavorite.value = false
    isLoading.value = false
    return
  }

  isLoading.value = true

  try {
    const [rating, status, favorites] = await Promise.all([
      getMyRating(props.itemId),
      getMyStatus(props.itemId),
      getFavorites(),
    ])

    currentRating.value = rating
    selectedRating.value = rating ?? 0
    currentStatus.value = status
    isFavorite.value = favorites.some((item) => item.id === props.itemId)
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load your item actions.'
  } finally {
    isLoading.value = false
  }
}

async function trackItemView() {
  if (!isLoggedIn.value || !props.itemId) {
    return
  }

  const key = `${props.itemId}:${normalizeSource(props.source)}`
  if (lastTrackedKey.value === key) {
    return
  }

  lastTrackedKey.value = key

  try {
    await createInteraction({
      item_id: props.itemId,
      interaction_type: 'item_view',
      source: normalizeSource(props.source),
    })
  } catch {
    // ignore
  }
}

function toggleStatusMenu() {
  if (!isLoggedIn.value) {
    redirectToLogin()
    return
  }

  isStatusMenuOpen.value = !isStatusMenuOpen.value
  if (isStatusMenuOpen.value) {
    isRatingPanelOpen.value = false
  }
}

function toggleRatingPanel() {
  if (!isLoggedIn.value) {
    redirectToLogin()
    return
  }

  isRatingPanelOpen.value = !isRatingPanelOpen.value
  if (isRatingPanelOpen.value) {
    isStatusMenuOpen.value = false
  }
}

async function handleSaveRating() {
  if (!isLoggedIn.value) {
    redirectToLogin()
    return
  }

  if (selectedRating.value < 1 || selectedRating.value > 10) {
    errorText.value = 'Choose a rating from 1 to 10.'
    return
  }

  errorText.value = ''
  successText.value = ''
  isRatingBusy.value = true

  try {
    if (currentRating.value === null) {
      await createRating(props.itemId, selectedRating.value)
      successText.value = 'Rating saved.'
    } else {
      await updateRating(props.itemId, selectedRating.value)
      successText.value = 'Rating updated.'
    }

    currentRating.value = selectedRating.value
    isRatingPanelOpen.value = false
    emit('changed')
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to save rating.'
  } finally {
    isRatingBusy.value = false
  }
}

async function handleRemoveRating() {
  if (!isLoggedIn.value || currentRating.value === null) {
    return
  }

  errorText.value = ''
  successText.value = ''
  isRatingBusy.value = true

  try {
    await deleteRating(props.itemId)
    currentRating.value = null
    selectedRating.value = 0
    successText.value = 'Rating removed.'
    isRatingPanelOpen.value = false
    emit('changed')
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to remove rating.'
  } finally {
    isRatingBusy.value = false
  }
}

async function handleSetStatus(status: ItemStatus) {
  if (!isLoggedIn.value) {
    redirectToLogin()
    return
  }

  errorText.value = ''
  successText.value = ''
  isStatusBusy.value = true

  try {
    await setMyStatus(props.itemId, status)
    currentStatus.value = status
    successText.value = 'Status updated.'
    isStatusMenuOpen.value = false
    emit('changed')
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to update status.'
  } finally {
    isStatusBusy.value = false
  }
}

async function handleClearStatus() {
  if (!isLoggedIn.value || currentStatus.value === null) {
    return
  }

  errorText.value = ''
  successText.value = ''
  isStatusBusy.value = true

  try {
    await deleteMyStatus(props.itemId)
    currentStatus.value = null
    successText.value = 'Status removed.'
    isStatusMenuOpen.value = false
    emit('changed')
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to remove status.'
  } finally {
    isStatusBusy.value = false
  }
}

async function handleToggleFavorite() {
  if (!isLoggedIn.value) {
    redirectToLogin()
    return
  }

  errorText.value = ''
  successText.value = ''
  isFavoriteBusy.value = true

  try {
    if (isFavorite.value) {
      await removeFromFavorites(props.itemId)
      isFavorite.value = false
      successText.value = 'Removed from favorites.'
    } else {
      await addToFavorites(props.itemId)
      isFavorite.value = true
      successText.value = 'Added to favorites.'
    }

    emit('changed')
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to update favorites.'
  } finally {
    isFavoriteBusy.value = false
  }
}

async function handleHomepageClick() {
  if (!props.homepageUrl) {
    return
  }

  if (isLoggedIn.value) {
    try {
      await createInteraction({
        item_id: props.itemId,
        interaction_type: 'external_link_click',
        source: 'item_page',
      })
    } catch {
      // ignore
    }
  }

  window.open(props.homepageUrl, '_blank', 'noopener,noreferrer')
}

watch(
  () => props.itemId,
  async () => {
    await loadUserState()
    await trackItemView()
  },
)

watch(
  () => isLoggedIn.value,
  async () => {
    await loadUserState()
    await trackItemView()
  },
)

onMounted(async () => {
  await loadUserState()
  await trackItemView()
})
</script>

<template>
  <section class="item-quick-actions">
    <div class="item-quick-actions__top-row">
      <div class="item-quick-actions__status-wrap">
        <button
          type="button"
          class="item-quick-actions__status-btn"
          :disabled="isLoading || isStatusBusy"
          @click="toggleStatusMenu"
        >
          <span>{{ currentStatusLabel }}</span>
          <span class="item-quick-actions__caret">▾</span>
        </button>

        <div v-if="isStatusMenuOpen" class="item-quick-actions__menu">
          <button
            v-for="option in statusOptions"
            :key="option.value"
            type="button"
            class="item-quick-actions__menu-item"
            :class="{
              'item-quick-actions__menu-item--active': currentStatus === option.value,
            }"
            @click="handleSetStatus(option.value)"
          >
            {{ option.label }}
          </button>

          <button
            v-if="currentStatus !== null"
            type="button"
            class="item-quick-actions__menu-item item-quick-actions__menu-item--danger"
            @click="handleClearStatus"
          >
            Remove Status
          </button>
        </div>
      </div>

      <div class="item-quick-actions__rating-wrap">
        <button
          type="button"
          class="item-quick-actions__rating-trigger"
          :disabled="isLoading"
          :title="isLoggedIn ? 'Rate this item' : 'Log in to rate this item'"
          @click="toggleRatingPanel"
        >
          ★
        </button>

        <div v-if="isRatingPanelOpen" class="item-quick-actions__rating-panel">
          <div class="item-quick-actions__rating-head">
            <strong>Your Rating</strong>
            <span v-if="currentRating !== null">{{ currentRating }}/10</span>
          </div>

          <div class="item-quick-actions__rating-grid">
            <button
              v-for="score in 10"
              :key="score"
              type="button"
              class="item-quick-actions__rating-chip"
              :class="{
                'item-quick-actions__rating-chip--active': selectedRating === score,
              }"
              @click="selectedRating = score"
            >
              {{ score }}
            </button>
          </div>

          <div class="item-quick-actions__rating-actions">
            <button
              type="button"
              class="item-quick-actions__primary-btn"
              :disabled="isRatingBusy"
              @click="handleSaveRating"
            >
              {{ isRatingBusy ? 'Saving...' : ratingButtonLabel }}
            </button>

            <button
              v-if="currentRating !== null"
              type="button"
              class="item-quick-actions__ghost-btn"
              :disabled="isRatingBusy"
              @click="handleRemoveRating"
            >
              Remove
            </button>
          </div>
        </div>
      </div>
    </div>

    <button
      type="button"
      class="item-quick-actions__favorite-btn"
      :disabled="isLoading || isFavoriteBusy"
      @click="handleToggleFavorite"
    >
      {{
        isFavoriteBusy
          ? 'Saving...'
          : favoriteButtonLabel
      }}
    </button>

    <button
      v-if="homepageUrl"
      type="button"
      class="item-quick-actions__homepage-btn"
      @click="handleHomepageClick"
    >
      Open Homepage
    </button>

    <p v-if="errorText" class="item-quick-actions__error">
      {{ errorText }}
    </p>

    <p v-if="successText" class="item-quick-actions__success">
      {{ successText }}
    </p>
  </section>
</template>

<style scoped>
.item-quick-actions {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

.item-quick-actions__top-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 48px;
  gap: 10px;
  align-items: start;
}

.item-quick-actions__status-wrap,
.item-quick-actions__rating-wrap {
  position: relative;
}

.item-quick-actions__status-btn,
.item-quick-actions__favorite-btn,
.item-quick-actions__homepage-btn {
  width: 100%;
  min-height: 44px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
}

.item-quick-actions__status-btn {
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px;
  cursor: pointer;
}

.item-quick-actions__caret {
  color: #94a3b8;
  font-size: 12px;
}

.item-quick-actions__rating-trigger {
  width: 48px;
  min-height: 44px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #fbbf24;
  font-size: 22px;
  font-weight: 800;
  cursor: pointer;
}

.item-quick-actions__favorite-btn {
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  cursor: pointer;
}

.item-quick-actions__homepage-btn {
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #e2e8f0;
  cursor: pointer;
}

.item-quick-actions__menu,
.item-quick-actions__rating-panel {
  position: absolute;
  z-index: 30;
  top: calc(100% + 8px);
  left: 0;
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(8, 14, 24, 0.98);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
}

.item-quick-actions__menu {
  padding: 8px;
  display: grid;
  gap: 6px;
}

.item-quick-actions__menu-item {
  min-height: 40px;
  border-radius: 10px;
  border: none;
  background: rgba(15, 23, 42, 0.72);
  color: #e2e8f0;
  font-weight: 700;
  cursor: pointer;
}

.item-quick-actions__menu-item--active {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
}

.item-quick-actions__menu-item--danger {
  color: #fca5a5;
}

.item-quick-actions__rating-panel {
  left: auto;
  right: 0;
  width: 280px;
  padding: 12px;
  display: grid;
  gap: 12px;
}

.item-quick-actions__rating-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  color: #f8fafc;
  font-size: 14px;
}

.item-quick-actions__rating-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

.item-quick-actions__rating-chip {
  min-height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #e2e8f0;
  font-weight: 700;
  cursor: pointer;
}

.item-quick-actions__rating-chip--active {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  border-color: transparent;
}

.item-quick-actions__rating-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.item-quick-actions__primary-btn,
.item-quick-actions__ghost-btn {
  min-height: 38px;
  padding: 0 12px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.item-quick-actions__primary-btn {
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
}

.item-quick-actions__ghost-btn {
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #e2e8f0;
}

.item-quick-actions__error {
  margin: 0;
  color: #fca5a5;
  font-size: 13px;
}

.item-quick-actions__success {
  margin: 0;
  color: #86efac;
  font-size: 13px;
}
</style>