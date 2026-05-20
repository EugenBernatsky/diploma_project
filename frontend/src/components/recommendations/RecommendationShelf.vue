<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import RecommendationCard from './RecommendationCard.vue'
import type { RecommendationShelf as RecommendationShelfType } from '../../utils/recommendations'

const props = defineProps<{
  shelf: RecommendationShelfType
}>()

const isOpen = ref(true)
</script>

<template>
  <section class="recommendation-shelf">
    <div class="recommendation-shelf__header">
      <button
        type="button"
        class="recommendation-shelf__toggle"
        @click="isOpen = !isOpen"
      >
        <span class="recommendation-shelf__toggle-icon">
          {{ isOpen ? '−' : '+' }}
        </span>

        <div class="recommendation-shelf__heading">
          <h3 class="recommendation-shelf__title">{{ shelf.title }}</h3>
          <p class="recommendation-shelf__subtitle">{{ shelf.subtitle }}</p>
        </div>
      </button>

      <RouterLink
        :to="{ path: '/catalog', query: { category: shelf.category } }"
        class="recommendation-shelf__link"
      >
        View All
      </RouterLink>
    </div>

    <div v-if="isOpen" class="recommendation-shelf__grid">
      <RecommendationCard
        v-for="item in shelf.items"
        :key="item.id"
        :item="item"
        :badge="shelf.badge"
      />
    </div>
  </section>
</template>

<style scoped>
.recommendation-shelf {
  display: grid;
  gap: 16px;
}

.recommendation-shelf__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
}

.recommendation-shelf__toggle {
  flex: 1;
  padding: 0;
  border: none;
  background: transparent;
  display: flex;
  gap: 12px;
  align-items: start;
  text-align: left;
  cursor: pointer;
}

.recommendation-shelf__toggle-icon {
  width: 24px;
  height: 24px;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.14);
  color: #60a5fa;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  margin-top: 2px;
}

.recommendation-shelf__heading {
  min-width: 0;
}

.recommendation-shelf__title {
  margin: 0 0 4px;
  color: #f8fafc;
  font-size: 24px;
  line-height: 1.2;
  letter-spacing: -0.03em;
}

.recommendation-shelf__subtitle {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.6;
}

.recommendation-shelf__link {
  flex: 0 0 auto;
  color: #60a5fa;
  text-decoration: none;
  font-weight: 700;
}

.recommendation-shelf__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

@media (max-width: 1100px) {
  .recommendation-shelf__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .recommendation-shelf__header {
    flex-direction: column;
  }

  .recommendation-shelf__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .recommendation-shelf__grid {
    grid-template-columns: 1fr;
  }
}
</style>