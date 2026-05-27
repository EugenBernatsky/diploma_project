<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useAuth } from '../../services/auth'
import {
  addToFavorites,
  createInteraction,
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
import type { InteractionSource, ItemStatus } from '../../types/userItemActions'

const props = defineProps<{
  itemId: string
  source?: string | null
}>()

const { isLoggedIn } = useAuth()

const isLoading = ref(true)
const errorText = ref('')
const successText = ref('')

const currentRating = ref<number | null>(null)
const selectedRating = ref<number>(0)

const currentStatus = ref<ItemStatus | null>(null)
const isFavorite = ref(false)

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
    source === 'favorites' ||
    source === 'statuses'
  ) {
    return source
  }

  return 'other'
}

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

async function trackOpenDetails() {
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
      interaction_type: 'open_details',
      source: normalizeSource(props.source),
      value: 1,
    })
  } catch {
    // no-op
  }
}

async function handleSaveRating() {
  if (!isLoggedIn.value) {
    errorText.value = 'Log in to rate this item.'
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
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to remove rating.'
  } finally {
    isRatingBusy.value = false
  }
}

async function handleSetStatus(status: ItemStatus) {
  if (!isLoggedIn.value) {
    errorText.value = 'Log in to set a status.'
    return
  }

  errorText.value = ''
  successText.value = ''
  isStatusBusy.value = true

  try {
    await setMyStatus(props.itemId, status)
    currentStatus.value = status
    successText.value = 'Status updated.'
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
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to remove status.'
  } finally {
    isStatusBusy.value = false
  }
}

async function handleToggleFavorite() {
  if (!isLoggedIn.value) {
    errorText.value = 'Log in to manage favorites.'
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
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to update favorites.'
  } finally {
    isFavoriteBusy.value = false
  }
}

watch(
  () => props.itemId,
  async () => {
    await loadUserState()
    await trackOpenDetails()
  },
)

watch(
  () => isLoggedIn.value,
  async () => {
    await loadUserState()
    await trackOpenDetails()
  },
)

onMounted(async () => {
  await loadUserState()
  await trackOpenDetails()
})
</script>

<template>
  <section class="item-user-actions">
    <div class="item-user-actions__head">
      <div>
        <h2 class="item-user-actions__title">Your Actions</h2>
        <p class="item-user-actions__subtitle">
          Save your rating, track progress, and manage favorites.
        </p>
      </div>
    </div>

    <div v-if="!isLoggedIn" class="item-user-actions__state">
      Log in to rate this item, save a status, and add it to favorites.
    </div>

    <div v-else-if="isLoading" class="item-user-actions__state">
      Loading your item actions...
    </div>

    <template v-else>
      <section class="item-user-actions__card">
        <div class="item-user-actions__section-head">
          <h3>Your Rating</h3>
          <span v-if="currentRating !== null" class="item-user-actions__current">
            Current: {{ currentRating }}/10
          </span>
        </div>

        <div class="item-user-actions__rating-grid">
          <button
            v-for="score in 10"
            :key="score"
            type="button"
            class="item-user-actions__rating-chip"
            :class="{
              'item-user-actions__rating-chip--active': selectedRating === score,
            }"
            @click="selectedRating = score"
          >
            {{ score }}
          </button>
        </div>

        <div class="item-user-actions__actions-row">
          <button
            type="button"
            class="item-user-actions__primary-btn"
            :disabled="isRatingBusy"
            @click="handleSaveRating"
          >
            {{ isRatingBusy ? 'Saving...' : ratingButtonLabel }}
          </button>

          <button
            v-if="currentRating !== null"
            type="button"
            class="item-user-actions__secondary-btn"
            :disabled="isRatingBusy"
            @click="handleRemoveRating"
          >
            Remove Rating
          </button>
        </div>
      </section>

      <section class="item-user-actions__card">
        <div class="item-user-actions__section-head">
          <h3>Status</h3>
          <span v-if="currentStatus" class="item-user-actions__current">
            Current: {{ currentStatus }}
          </span>
        </div>

        <div class="item-user-actions__status-grid">
          <button
            v-for="option in statusOptions"
            :key="option.value"
            type="button"
            class="item-user-actions__status-chip"
            :class="{
              'item-user-actions__status-chip--active': currentStatus === option.value,
            }"
            :disabled="isStatusBusy"
            @click="handleSetStatus(option.value)"
          >
            {{ option.label }}
          </button>
        </div>

        <div class="item-user-actions__actions-row">
          <button
            v-if="currentStatus !== null"
            type="button"
            class="item-user-actions__secondary-btn"
            :disabled="isStatusBusy"
            @click="handleClearStatus"
          >
            Remove Status
          </button>
        </div>
      </section>

      <section class="item-user-actions__card">
        <div class="item-user-actions__section-head">
          <h3>Favorites</h3>
        </div>

        <div class="item-user-actions__actions-row">
          <button
            type="button"
            class="item-user-actions__primary-btn"
            :disabled="isFavoriteBusy"
            @click="handleToggleFavorite"
          >
            {{
              isFavoriteBusy
                ? 'Saving...'
                : isFavorite
                  ? 'Remove from Favorites'
                  : 'Add to Favorites'
            }}
          </button>
        </div>
      </section>

      <p v-if="errorText" class="item-user-actions__error">
        {{ errorText }}
      </p>

      <p v-if="successText" class="item-user-actions__success">
        {{ successText }}
      </p>
    </template>
  </section>
</template>

<style scoped>
.item-user-actions {
  display: grid;
  gap: 16px;
}

.item-user-actions__title {
  margin: 0 0 6px;
  color: #f8fafc;
  font-size: 30px;
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.item-user-actions__subtitle {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.7;
}

.item-user-actions__state,
.item-user-actions__card {
  padding: 18px;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
}

.item-user-actions__section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.item-user-actions__section-head h3 {
  margin: 0;
  color: #f8fafc;
  font-size: 20px;
}

.item-user-actions__current {
  color: #60a5fa;
  font-size: 13px;
  font-weight: 700;
}

.item-user-actions__rating-grid,
.item-user-actions__status-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.item-user-actions__rating-chip,
.item-user-actions__status-chip {
  min-height: 40px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #e2e8f0;
  cursor: pointer;
  font-weight: 700;
}

.item-user-actions__rating-chip--active,
.item-user-actions__status-chip--active {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  border-color: transparent;
}

.item-user-actions__actions-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 14px;
}

.item-user-actions__primary-btn,
.item-user-actions__secondary-btn {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
}

.item-user-actions__primary-btn {
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
}

.item-user-actions__secondary-btn {
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #e2e8f0;
}

.item-user-actions__error {
  margin: 0;
  color: #fca5a5;
  font-size: 14px;
}

.item-user-actions__success {
  margin: 0;
  color: #86efac;
  font-size: 14px;
}

@media (max-width: 700px) {
  .item-user-actions__section-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>