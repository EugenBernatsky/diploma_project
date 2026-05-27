<script setup lang="ts">
import { computed, ref } from 'vue'
import type { InteractionSource } from '../../types/interaction'
import type { RecommendationSection } from '../../types/recommendations'
import RecommendationCard from './RecommendationCard.vue'
import RecommendationStatusHint from './RecommendationStatusHint.vue'

const props = withDefaults(
  defineProps<{
    section: RecommendationSection
    source?: InteractionSource
  }>(),
  {
    source: 'recommendations',
  },
)

const isOpen = ref(true)

const hasItems = computed(() => props.section.items.length > 0)

const algorithmLabel = computed(() => {
  return props.section.algorithm.replace(/_/g, ' ')
})

const emptyText = computed(() => {
  if (props.section.status === 'waiting_for_more_user_data') {
    return 'This section will appear after more users rate media items.'
  }

  if (props.section.status === 'model_not_trained') {
    return 'Recommendations are temporarily unavailable.'
  }

  if (props.section.status === 'unavailable') {
    return 'No recommendations available right now.'
  }

  return 'No items in this section yet.'
})
</script>

<template>
  <section class="recommendations-group">
    <button
      type="button"
      class="recommendations-group__header"
      @click="isOpen = !isOpen"
    >
      <div class="recommendations-group__left">
        <span class="recommendations-group__marker">
          {{ isOpen ? '−' : '+' }}
        </span>

        <div>
          <div class="recommendations-group__title-row">
            <h2 class="recommendations-group__title">{{ section.title }}</h2>

            <span class="recommendations-group__badge">
              {{ section.status }}
            </span>

            <span class="recommendations-group__algorithm">
              {{ algorithmLabel }}
            </span>
          </div>
        </div>
      </div>
    </button>

    <div v-if="isOpen" class="recommendations-group__content">
      <RecommendationStatusHint :status="section.status" />

      <div v-if="hasItems" class="recommendations-group__grid">
        <RecommendationCard
          v-for="recommendation in section.items"
          :key="recommendation.item.id"
          :recommendation="recommendation"
          :source="source"
        />
      </div>

      <div v-else class="recommendations-group__empty">
        {{ emptyText }}
      </div>
    </div>
  </section>
</template>

<style scoped>
.recommendations-group {
  display: grid;
  gap: 18px;
}

.recommendations-group__header {
  padding: 0;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.recommendations-group__left {
  display: flex;
  gap: 14px;
  align-items: start;
}

.recommendations-group__marker {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.14);
  color: #60a5fa;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  margin-top: 4px;
}

.recommendations-group__title-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-bottom: 6px;
}

.recommendations-group__title {
  margin: 0;
  color: #f8fafc;
  font-size: 34px;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.recommendations-group__badge,
.recommendations-group__algorithm {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.08);
  color: #94a3b8;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.recommendations-group__algorithm {
  color: #bfdbfe;
  background: rgba(37, 99, 235, 0.12);
}

.recommendations-group__content {
  display: grid;
  gap: 16px;
}

.recommendations-group__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.recommendations-group__empty {
  padding: 24px;
  border-radius: 18px;
  border: 1px dashed rgba(148, 163, 184, 0.18);
  background: rgba(15, 23, 42, 0.48);
  color: #94a3b8;
  line-height: 1.7;
}

@media (max-width: 1100px) {
  .recommendations-group__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .recommendations-group__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .recommendations-group__title {
    font-size: 28px;
  }
}

@media (max-width: 520px) {
  .recommendations-group__grid {
    grid-template-columns: 1fr;
  }
}
</style>