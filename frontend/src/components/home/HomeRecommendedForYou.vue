<script setup lang="ts">
import { RouterLink } from 'vue-router'
import RecommendationCard from '../recommendations/RecommendationCard.vue'
import RecommendationStatusHint from '../recommendations/RecommendationStatusHint.vue'
import type { RecommendationItem } from '../../types/recommendations'

defineProps<{
  items: RecommendationItem[]
  status: string
  isLoading?: boolean
  note?: string
}>()
</script>

<template>
  <section class="home-recommended">
    <div class="home-recommended__header">
      <div>
        <p class="home-recommended__eyebrow">PERSONALIZED</p>
        <h2 class="home-recommended__title">Recommended for You</h2>
        <p class="home-recommended__subtitle">
          A compact preview from your personal recommendation feed.
        </p>
      </div>

      <RouterLink to="/recommendations" class="home-recommended__link">
        Open all recommendations
      </RouterLink>
    </div>

    <div v-if="isLoading" class="home-recommended__grid">
      <div
        v-for="index in 4"
        :key="index"
        class="home-recommended__skeleton"
      ></div>
    </div>

    <template v-else>
      <RecommendationStatusHint :status="status" />

      <p v-if="note" class="home-recommended__note">
        {{ note }}
      </p>

      <div v-if="items.length" class="home-recommended__grid">
        <RecommendationCard
          v-for="recommendation in items"
          :key="recommendation.item.id"
          :recommendation="recommendation"
          source="home"
          :show-reason="false"
        />
      </div>

      <div v-else class="home-recommended__empty">
        No personal recommendations yet. Rate, save or open more media items to improve this block.
      </div>
    </template>
  </section>
</template>

<style scoped>
.home-recommended {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding: 10px 0 34px;
  display: grid;
  gap: 18px;
}

.home-recommended__header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: end;
}

.home-recommended__eyebrow {
  margin: 0 0 8px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.12em;
}

.home-recommended__title {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: clamp(28px, 3vw, 42px);
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.home-recommended__subtitle {
  margin: 0;
  color: #94a3b8;
  line-height: 1.6;
}

.home-recommended__link {
  flex: 0 0 auto;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  text-decoration: none;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.home-recommended__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.home-recommended__skeleton {
  min-height: 330px;
  border-radius: 18px;
  background: linear-gradient(
    90deg,
    rgba(15, 23, 42, 0.9) 0%,
    rgba(30, 41, 59, 0.95) 50%,
    rgba(15, 23, 42, 0.9) 100%
  );
  background-size: 220% 100%;
  animation: shimmer 1.4s linear infinite;
}

.home-recommended__note,
.home-recommended__empty {
  margin: 0;
  color: #94a3b8;
  line-height: 1.7;
}

.home-recommended__empty {
  padding: 24px;
  border-radius: 18px;
  border: 1px dashed rgba(148, 163, 184, 0.18);
  background: rgba(15, 23, 42, 0.48);
}

@keyframes shimmer {
  0% {
    background-position: 220% 0;
  }

  100% {
    background-position: -220% 0;
  }
}

@media (max-width: 1100px) {
  .home-recommended__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .home-recommended {
    width: min(100%, calc(100% - 32px));
  }

  .home-recommended__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .home-recommended__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .home-recommended__grid {
    grid-template-columns: 1fr;
  }
}
</style>