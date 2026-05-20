<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import RecommendationsHero from '../components/recommendations/RecommendationsHero.vue'
import RecommendationsGroup from '../components/recommendations/RecommendationsGroup.vue'
import { getItems } from '../services/api'
import type { MediaItem } from '../types/media'
import { buildRecommendationGroups } from '../utils/recommendations'

const isLoading = ref(true)
const errorText = ref('')
const refreshSeed = ref(0)
const lastUpdatedAt = ref<Date | null>(null)

const catalogBuckets = ref<{
  movie: MediaItem[]
  series: MediaItem[]
  book: MediaItem[]
}>({
  movie: [],
  series: [],
  book: [],
})

async function loadRecommendationSources() {
  isLoading.value = true
  errorText.value = ''

  try {
    const [movies, series, books] = await Promise.all([
      getItems('movie'),
      getItems('series'),
      getItems('book'),
    ])

    catalogBuckets.value = {
      movie: movies,
      series,
      book: books,
    }

    lastUpdatedAt.value = new Date()
  } catch (error) {
    errorText.value =
      error instanceof Error
        ? error.message
        : 'Failed to load recommendation sources.'
  } finally {
    isLoading.value = false
  }
}

const recommendationGroups = computed(() => {
  return buildRecommendationGroups(catalogBuckets.value, refreshSeed.value).filter(
    (group) => group.shelves.length > 0,
  )
})

const totalItemsLoaded = computed(() => {
  return (
    catalogBuckets.value.movie.length +
    catalogBuckets.value.series.length +
    catalogBuckets.value.book.length
  )
})

const lastUpdatedLabel = computed(() => {
  if (!lastUpdatedAt.value) return 'Not refreshed yet'

  return `Updated ${lastUpdatedAt.value.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  })}`
})

function refreshRecommendations() {
  refreshSeed.value += 1
  lastUpdatedAt.value = new Date()
}

onMounted(() => {
  loadRecommendationSources()
})
</script>

<template>
  <section class="recommendations-page">
    <div class="recommendations-page__inner">
      <RecommendationsHero
        :total-items="totalItemsLoaded"
        :last-updated-label="lastUpdatedLabel"
        @refresh="refreshRecommendations"
      />

      <div v-if="isLoading" class="recommendations-page__state">
        Loading recommendation shelves...
      </div>

      <div
        v-else-if="errorText"
        class="recommendations-page__state recommendations-page__state--error"
      >
        {{ errorText }}
      </div>

      <template v-else>
        <RecommendationsGroup
          v-for="group in recommendationGroups"
          :key="group.id"
          :group="group"
        />

        <section class="recommendations-page__cta">
          <div>
            <h2 class="recommendations-page__cta-title">
              Not finding what you’re looking for?
            </h2>
            <p class="recommendations-page__cta-text">
              Explore the full catalog or jump into the forum and compare notes with
              other users while the real recommendation engine is still being wired in.
            </p>
          </div>

          <RouterLink to="/forum" class="recommendations-page__cta-link">
            Visit Community Forum
          </RouterLink>
        </section>
      </template>
    </div>
  </section>
</template>

<style scoped>
.recommendations-page {
  width: 100%;
  padding: 30px 0 56px;
}

.recommendations-page__inner {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  display: grid;
  gap: 30px;
}

.recommendations-page__state {
  padding: 32px;
  border-radius: 22px;
  background: rgba(8, 14, 24, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.08);
  color: #cbd5e1;
}

.recommendations-page__state--error {
  color: #fca5a5;
}

.recommendations-page__cta {
  padding: 24px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
}

.recommendations-page__cta-title {
  margin: 0 0 10px;
  color: #f8fafc;
  font-size: 28px;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.recommendations-page__cta-text {
  max-width: 760px;
  margin: 0;
  color: #94a3b8;
  line-height: 1.8;
}

.recommendations-page__cta-link {
  flex: 0 0 auto;
  min-height: 46px;
  padding: 0 18px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  text-decoration: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 900px) {
  .recommendations-page__inner {
    width: min(100%, calc(100% - 32px));
  }

  .recommendations-page__cta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>