<script setup lang="ts">
import { ref } from 'vue'
import RecommendationShelf from './RecommendationShelf.vue'
import type { RecommendationGroup as RecommendationGroupType } from '../../utils/recommendations'

defineProps<{
  group: RecommendationGroupType
}>()

const isOpen = ref(true)
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
            <h2 class="recommendations-group__title">{{ group.title }}</h2>
            <span class="recommendations-group__badge">{{ group.badge }}</span>
          </div>

          <p class="recommendations-group__subtitle">
            {{ group.subtitle }}
          </p>
        </div>
      </div>
    </button>

    <div v-if="isOpen" class="recommendations-group__content">
      <RecommendationShelf
        v-for="shelf in group.shelves"
        :key="shelf.id"
        :shelf="shelf"
      />
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

.recommendations-group__badge {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.08);
  color: #94a3b8;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.recommendations-group__subtitle {
  max-width: 900px;
  margin: 0;
  color: #94a3b8;
  font-size: 15px;
  line-height: 1.7;
}

.recommendations-group__content {
  display: grid;
  gap: 26px;
}
</style>