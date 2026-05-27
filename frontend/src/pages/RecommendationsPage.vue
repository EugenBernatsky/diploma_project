<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import RecommendationCategoryFilter from '../components/recommendations/RecommendationCategoryFilter.vue'
import RecommendationsGroup from '../components/recommendations/RecommendationsGroup.vue'
import RecommendationsHero from '../components/recommendations/RecommendationsHero.vue'
import { getRecommendations } from '../services/recommendations'
import type { Category } from '../types/media'
import type { RecommendationSection } from '../types/recommendations'

const RECOMMENDATIONS_LIMIT = 12

const isLoading = ref(true)
const errorText = ref('')
const selectedCategory = ref<Category | null>(null)
const sections = ref<RecommendationSection[]>([])
const lastUpdatedAt = ref<Date | null>(null)

const visibleSections = computed(() => {
  return sections.value.filter((section) => {
    if (section.items.length > 0) {
      return true
    }

    return [
      'cold_start_fallback',
      'personalized_fallback',
      'waiting_for_more_user_data',
      'model_not_trained',
    ].includes(section.status)
  })
})

const totalItemsLoaded = computed(() => {
  return sections.value.reduce((total, section) => {
    return total + section.items.length
  }, 0)
})

const lastUpdatedLabel = computed(() => {
  if (!lastUpdatedAt.value) {
    return 'Not refreshed yet'
  }

  return `Updated ${lastUpdatedAt.value.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  })}`
})

async function loadRecommendations() {
  isLoading.value = true
  errorText.value = ''

  try {
    const response = await getRecommendations({
      limit: RECOMMENDATIONS_LIMIT,
      category: selectedCategory.value,
    })

    sections.value = response.sections
    lastUpdatedAt.value = new Date()
  } catch (error) {
    errorText.value =
      error instanceof Error
        ? error.message
        : 'Recommendations are temporarily unavailable.'

    sections.value = []
  } finally {
    isLoading.value = false
  }
}

function handleCategoryChange(category: Category | null) {
  if (selectedCategory.value === category) {
    return
  }

  selectedCategory.value = category
  loadRecommendations()
}

function refreshRecommendations() {
  loadRecommendations()
}

onMounted(() => {
  loadRecommendations()
})
</script>

<template>
  <section class="recommendations-page">
    <div class="recommendations-page__inner">
      <RecommendationsHero
        :total-items="totalItemsLoaded"
        :sections-count="sections.length"
        :last-updated-label="lastUpdatedLabel"
        :is-refreshing="isLoading"
        @refresh="refreshRecommendations"
      />

      <RecommendationCategoryFilter
        :selected-category="selectedCategory"
        :is-loading="isLoading"
        @change="handleCategoryChange"
      />

      <div v-if="isLoading" class="recommendations-page__state">
        Loading recommendations...
      </div>

      <div
        v-else-if="errorText"
        class="recommendations-page__state recommendations-page__state--error"
      >
        {{ errorText }}
      </div>

      <template v-else>
        <div
          v-if="visibleSections.length"
          class="recommendations-page__sections"
        >
          <RecommendationsGroup
            v-for="section in visibleSections"
            :key="section.key"
            :section="section"
            source="recommendations"
          />
        </div>

        <div v-else class="recommendations-page__state">
          No recommendations available right now. Try rating, saving or opening
          more media items.
        </div>

        <section class="recommendations-page__cta">
          <div>
            <h2 class="recommendations-page__cta-title">
              Want better recommendations?
            </h2>

            <p class="recommendations-page__cta-text">
              Rate items, add media to favorites, update your watch/read statuses
              and open items from the catalog. These actions help the backend
              improve your personal recommendation profile.
            </p>
          </div>

          <RouterLink to="/catalog" class="recommendations-page__cta-link">
            Explore Catalog
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

.recommendations-page__sections {
  display: grid;
  gap: 30px;
}

.recommendations-page__state {
  padding: 32px;
  border-radius: 22px;
  background: rgba(8, 14, 24, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.08);
  color: #cbd5e1;
  line-height: 1.7;
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