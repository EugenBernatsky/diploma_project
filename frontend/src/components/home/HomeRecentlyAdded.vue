<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { RecentlyAddedItem } from '../../types/home'

defineProps<{
  items: RecentlyAddedItem[]
  isLoading?: boolean
  note?: string
}>()
</script>

<template>
  <section class="recent-section">
    <div class="recent-section__header">
      <div>
        <h2 class="recent-section__title">Recently Added</h2>
        <p class="recent-section__subtitle">Fresh arrivals in the library this week.</p>
      </div>

      <div class="recent-section__controls">
        <button type="button" class="recent-section__arrow" aria-label="Previous items">‹</button>
        <button type="button" class="recent-section__arrow" aria-label="Next items">›</button>
      </div>
    </div>

    <p v-if="note" class="recent-section__note">
      {{ note }}
    </p>

    <div v-if="isLoading" class="recent-grid">
      <div v-for="index in 5" :key="index" class="recent-card recent-card--skeleton">
        <div class="recent-card__poster recent-card__poster--skeleton"></div>
        <div class="recent-card__body">
          <div class="recent-card__line recent-card__line--title"></div>
          <div class="recent-card__line recent-card__line--meta"></div>
        </div>
      </div>
    </div>

    <div v-else class="recent-grid">
      <RouterLink
        v-for="item in items"
        :key="item.id"
        :to="`/items/${item.id}`"
        class="recent-card recent-card--link"
      >
        <div class="recent-card__poster">
          <img :src="item.image" :alt="item.title" />
          <span v-if="item.rating !== null" class="recent-card__rating">
            ★ {{ item.rating.toFixed(1) }}
          </span>
        </div>

        <div class="recent-card__body">
          <h3 class="recent-card__title">{{ item.title }}</h3>
          <p class="recent-card__category">{{ item.category }}</p>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.recent-section {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding: 42px 0 56px;
}

.recent-section__header {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 24px;
  margin-bottom: 24px;
}

.recent-section__title {
  margin: 0 0 6px;
  font-size: clamp(28px, 3vw, 42px);
  color: #f8fafc;
  letter-spacing: -0.03em;
}

.recent-section__subtitle {
  margin: 0;
  color: #94a3b8;
  font-size: 15px;
}

.recent-section__note {
  margin: 0 0 20px;
  color: #60a5fa;
  font-size: 14px;
}

.recent-section__controls {
  display: flex;
  gap: 10px;
}

.recent-section__arrow {
  width: 42px;
  height: 42px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 999px;
  background: #0b1220;
  color: #e2e8f0;
  font-size: 22px;
  cursor: pointer;
}

.recent-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 18px;
}

.recent-card {
  overflow: hidden;
}

.recent-card--link {
  text-decoration: none;
  transition:
    transform 0.2s ease,
    opacity 0.2s ease;
}

.recent-card--link:hover {
  transform: translateY(-4px);
}

.recent-card__poster {
  position: relative;
  height: 260px;
  border-radius: 18px;
  overflow: hidden;
  background: #111827;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.24);
}

.recent-card__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  filter: saturate(1.04);
}

.recent-card__poster::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 35%, rgba(2, 6, 23, 0.18) 100%);
}

.recent-card__poster--skeleton {
  background: linear-gradient(
    90deg,
    rgba(15, 23, 42, 0.9) 0%,
    rgba(30, 41, 59, 0.95) 50%,
    rgba(15, 23, 42, 0.9) 100%
  );
  background-size: 220% 100%;
  animation: shimmer 1.4s linear infinite;
}

.recent-card__rating {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1;
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(2, 6, 23, 0.78);
  color: #bfdbfe;
  font-size: 12px;
  font-weight: 700;
}

.recent-card__body {
  padding: 14px 4px 0;
}

.recent-card__title {
  margin: 0 0 4px;
  color: #f8fafc;
  font-size: 18px;
  line-height: 1.3;
}

.recent-card__category {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  letter-spacing: 0.12em;
}

.recent-card__line {
  border-radius: 999px;
  background: linear-gradient(
    90deg,
    rgba(15, 23, 42, 0.9) 0%,
    rgba(30, 41, 59, 0.95) 50%,
    rgba(15, 23, 42, 0.9) 100%
  );
  background-size: 220% 100%;
  animation: shimmer 1.4s linear infinite;
}

.recent-card__line--title {
  width: 80%;
  height: 18px;
  margin-bottom: 10px;
}

.recent-card__line--meta {
  width: 38%;
  height: 12px;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }

  100% {
    background-position: -20% 0;
  }
}

@media (max-width: 1200px) {
  .recent-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .recent-section {
    width: min(100%, calc(100% - 32px));
  }
}

@media (max-width: 700px) {
  .recent-section__header {
    align-items: start;
    flex-direction: column;
  }

  .recent-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .recent-grid {
    grid-template-columns: 1fr;
  }

  .recent-card__poster {
    height: 320px;
  }
}
</style>