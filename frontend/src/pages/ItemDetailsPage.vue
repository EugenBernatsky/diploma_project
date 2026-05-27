<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import ItemHeroPanel from '../components/item/ItemHeroPanel.vue'
import ItemDescriptionSection from '../components/item/ItemDescriptionSection.vue'
import ItemTrailersSection from '../components/item/ItemTrailersSection.vue'
import ItemAvailabilitySection from '../components/item/ItemAvailabilitySection.vue'
import ItemSimilarItems from '../components/item/ItemSimilarItems.vue'
import ItemCommunitySection from '../components/item/ItemCommunitySection.vue'
import ItemStatsSection from '../components/item/ItemStatsSection.vue'
import { getItemById, getItemStats } from '../services/api'
import { getSimilarItems } from '../services/recommendations'
import type { MediaItem, MediaItemStats } from '../types/media'
import type { RecommendationItem } from '../types/recommendations'
import { getDescriptionHeading } from '../utils/itemDetails'
import AdminItemEditModal from '../components/admin/AdminItemEditModal.vue'
import { useAuth } from '../services/auth'

const route = useRoute()
const { authState } = useAuth()

const itemActionSource = computed(() => {
  const source = route.query.source

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
})

const item = ref<MediaItem | null>(null)
const itemStats = ref<MediaItemStats | null>(null)
const similarItems = ref<RecommendationItem[]>([])
const similarItemsStatus = ref('')

const isLoading = ref(true)
const errorText = ref('')

const isItemEditOpen = ref(false)

const itemId = computed(() => String(route.params.id ?? ''))

const breadcrumbCategory = computed(() => {
  if (!item.value) return 'Catalog'

  if (item.value.category === 'movie') return 'Movies'
  if (item.value.category === 'series') return 'TV Series'
  return 'Books'
})

const descriptionHeading = computed(() => {
  return item.value ? getDescriptionHeading(item.value) : 'Description'
})

const isAdmin = computed(() => {
  return authState.user?.role === 'admin'
})

async function refreshItemStats() {
  if (!item.value) {
    return
  }

  try {
    itemStats.value = await getItemStats(item.value.id)
  } catch {
    // stats refresh should not break the page
  }
}

async function loadSimilarItems(currentItem: MediaItem) {
  try {
    const response = await getSimilarItems({
      itemId: currentItem.id,
      limit: 8,
    })

    similarItemsStatus.value = response.status

    if (response.status === 'available' && response.items.length > 0) {
      similarItems.value = response.items.filter((recommendation) => {
        return recommendation.item.id !== currentItem.id
      })

      return
    }

    similarItems.value = []
  } catch {
    similarItemsStatus.value = 'unavailable'
    similarItems.value = []
  }
}

async function loadItemPage() {
  isLoading.value = true
  errorText.value = ''

  try {
    if (!itemId.value.trim()) {
      throw new Error('Invalid item id')
    }

        const currentItem = await getItemById(itemId.value)
        item.value = currentItem
        similarItems.value = []
        similarItemsStatus.value = ''

        const [stats] = await Promise.all([
          getItemStats(currentItem.id),
          loadSimilarItems(currentItem),
        ])

        itemStats.value = stats
  } catch (error) {
    item.value = null
    itemStats.value = null
    similarItems.value = []
    similarItemsStatus.value = ''
    errorText.value =
      error instanceof Error ? error.message : 'Unknown item details error'
  } finally {
    isLoading.value = false
  }
}

async function handleItemSaved(updatedItem: MediaItem) {
  item.value = updatedItem
  isItemEditOpen.value = false

  await loadSimilarItems(updatedItem)
}

watch(
  () => route.params.id,
  () => {
    loadItemPage()
  },
)

onMounted(() => {
  loadItemPage()
})
</script>

<template>
  <section class="item-page">
    <div class="item-page__inner">
      <div class="item-page__breadcrumbs">
        <RouterLink to="/">Home</RouterLink>
        <span>›</span>
        <RouterLink to="/catalog">Catalog</RouterLink>
        <span>›</span>
        <span>{{ breadcrumbCategory }}</span>
        <span v-if="item">›</span>
        <span v-if="item">{{ item.title }}</span>
      </div>

      <div v-if="isLoading" class="item-page__state">
        Loading item details...
      </div>

      <div v-else-if="errorText" class="item-page__state item-page__state--error">
        {{ errorText }}
      </div>

      <template v-else-if="item">
        <div v-if="isAdmin && item" class="item-details-page__admin-bar">
          <div>
            <strong>Admin mode</strong>
            <span>You can edit this media item.</span>
          </div>

          <button
            type="button"
            class="item-details-page__admin-button"
            @click="isItemEditOpen = true"
          >
            Edit Item
          </button>
        </div>


        <ItemHeroPanel
          :item="item"
          :source="itemActionSource"
          @stats-changed="refreshItemStats"
        />

        <ItemStatsSection
          v-if="itemStats"
          :stats="itemStats"
        />

        <ItemDescriptionSection
          :title="descriptionHeading"
          :description="item.description"
        />

        <ItemTrailersSection
          :item-id="item.id"
          :trailers="item.trailers ?? []"
        />

        <ItemAvailabilitySection
          :item-id="item.id"
          :watch-links="item.watch_links ?? []"
          :purchase-links="item.purchase_links ?? []"
        />
        
        <ItemSimilarItems
          v-if="similarItemsStatus === 'available' && similarItems.length > 0"
          :current-item="item"
          :recommendations="similarItems"
        />

        <ItemCommunitySection
          :item-id="item.id"
          @changed="refreshItemStats"
        />
      </template>
    </div>

    <AdminItemEditModal
      :open="isItemEditOpen"
      :item="item"
      @close="isItemEditOpen = false"
      @saved="handleItemSaved"
    />
  </section>
</template>

<style scoped>
.item-page {
  width: 100%;
  padding: 26px 0 56px;
}

.item-page__inner {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  display: grid;
  gap: 34px;
}

.item-page__breadcrumbs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  color: #64748b;
  font-size: 13px;
}

.item-page__breadcrumbs a {
  color: #94a3b8;
  text-decoration: none;
}

.item-page__breadcrumbs a:hover {
  color: #dbeafe;
}

.item-page__state {
  padding: 32px;
  border-radius: 22px;
  background: rgba(8, 14, 24, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.08);
  color: #cbd5e1;
}

.item-page__state--error {
  color: #fca5a5;
}

.item-details-page__admin-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid rgba(96, 165, 250, 0.22);
  background: rgba(37, 99, 235, 0.12);
}

.item-details-page__admin-bar div {
  display: grid;
  gap: 4px;
}

.item-details-page__admin-bar strong {
  color: #dbeafe;
  font-size: 15px;
}

.item-details-page__admin-bar span {
  color: #93c5fd;
  font-size: 13px;
}

.item-details-page__admin-button {
  min-height: 42px;
  padding: 0 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #7c3aed 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 900;
  cursor: pointer;
}

@media (max-width: 680px) {
  .item-details-page__admin-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .item-details-page__admin-button {
    width: 100%;
  }
}

@media (max-width: 900px) {
  .item-page__inner {
    width: min(100%, calc(100% - 32px));
  }
}
</style>