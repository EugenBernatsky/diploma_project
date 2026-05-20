<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import ItemHeroPanel from '../components/item/ItemHeroPanel.vue'
import ItemDescriptionSection from '../components/item/ItemDescriptionSection.vue'
import ItemTrailersSection from '../components/item/ItemTrailersSection.vue'
import ItemAvailabilitySection from '../components/item/ItemAvailabilitySection.vue'
import ItemSimilarItems from '../components/item/ItemSimilarItems.vue'
import ItemCommunitySection from '../components/item/ItemCommunitySection.vue'
import { getItemById, getItems } from '../services/api'
import { mockReviews } from '../mocks/itemDetails'
import type { MediaItem } from '../types/media'
import { buildSimilarItems, getDescriptionHeading } from '../utils/itemDetails'

const route = useRoute()

const item = ref<MediaItem | null>(null)
const similarItems = ref<MediaItem[]>([])
const isLoading = ref(true)
const errorText = ref('')

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

async function loadItemPage() {
  isLoading.value = true
  errorText.value = ''

  try {
    if (!itemId.value.trim()) {
      throw new Error('Invalid item id')
    }

    const currentItem = await getItemById(itemId.value)
    item.value = currentItem

    const categoryItems = await getItems(currentItem.category)
    similarItems.value = buildSimilarItems(currentItem, categoryItems, 6)
  } catch (error) {
    item.value = null
    similarItems.value = []
    errorText.value =
      error instanceof Error ? error.message : 'Unknown item details error'
  } finally {
    isLoading.value = false
  }
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
        <ItemHeroPanel :item="item" />

        <ItemDescriptionSection
          :title="descriptionHeading"
          :description="item.description"
        />

        <ItemTrailersSection :trailers="item.trailers ?? []" />

        <ItemAvailabilitySection
          :watch-links="item.watch_links ?? []"
          :purchase-links="item.purchase_links ?? []"
        />

        <ItemSimilarItems
          :current-item="item"
          :items="similarItems"
        />

        <ItemCommunitySection
          :item="item"
          :reviews="mockReviews"
        />
      </template>
    </div>
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

@media (max-width: 900px) {
  .item-page__inner {
    width: min(100%, calc(100% - 32px));
  }
}
</style>