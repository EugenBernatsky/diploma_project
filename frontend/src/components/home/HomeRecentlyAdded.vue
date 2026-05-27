<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import type { RecentlyAddedItem } from '../../types/home'
import { buildItemRoute } from '../../utils/itemRoutes'

const props = defineProps<{
  items: RecentlyAddedItem[]
  isLoading?: boolean
  note?: string
}>()

const AUTOPLAY_DELAY_MS = 4500

const activeIndex = ref(0)
let autoplayId: number | undefined

const hasItems = computed(() => props.items.length > 0)

const activeItem = computed(() => {
  return props.items[activeIndex.value] ?? null
})

const sideItems = computed(() => {
  if (props.items.length <= 1) {
    return []
  }

  return props.items.filter((_, index) => index !== activeIndex.value).slice(0, 4)
})

function normalizeIndex(index: number): number {
  if (!props.items.length) {
    return 0
  }

  return (index + props.items.length) % props.items.length
}

function goToPrevious() {
  activeIndex.value = normalizeIndex(activeIndex.value - 1)
  restartAutoplay()
}

function goToNext() {
  activeIndex.value = normalizeIndex(activeIndex.value + 1)
  restartAutoplay()
}

function goToIndex(index: number) {
  activeIndex.value = normalizeIndex(index)
  restartAutoplay()
}

function stopAutoplay() {
  if (autoplayId) {
    window.clearInterval(autoplayId)
    autoplayId = undefined
  }
}

function startAutoplay() {
  stopAutoplay()

  if (props.items.length <= 1 || props.isLoading) {
    return
  }

  autoplayId = window.setInterval(() => {
    activeIndex.value = normalizeIndex(activeIndex.value + 1)
  }, AUTOPLAY_DELAY_MS)
}

function restartAutoplay() {
  startAutoplay()
}

watch(
  () => props.items,
  () => {
    activeIndex.value = 0
    startAutoplay()
  },
  {
    deep: true,
  },
)

watch(
  () => props.isLoading,
  () => {
    startAutoplay()
  },
)

onMounted(() => {
  startAutoplay()
})

onUnmounted(() => {
  stopAutoplay()
})
</script>

<template>
  <section class="recent-section">
    <div class="recent-section__header">
      <div>
        <h2 class="recent-section__title">Recently Added</h2>
        <p class="recent-section__subtitle">Fresh arrivals in the library this week.</p>
      </div>

      <div class="recent-section__controls">
        <button
          type="button"
          class="recent-section__arrow"
          aria-label="Previous items"
          :disabled="isLoading || items.length <= 1"
          @click="goToPrevious"
        >
          ‹
        </button>

        <button
          type="button"
          class="recent-section__arrow"
          aria-label="Next items"
          :disabled="isLoading || items.length <= 1"
          @click="goToNext"
        >
          ›
        </button>
      </div>
    </div>

    <p v-if="note" class="recent-section__note">
      {{ note }}
    </p>

    <div v-if="isLoading" class="recent-carousel recent-carousel--loading">
      <div class="recent-feature-card recent-feature-card--skeleton">
        <div class="recent-feature-card__image recent-feature-card__image--skeleton"></div>
        <div class="recent-feature-card__content">
          <div class="recent-card__line recent-card__line--title"></div>
          <div class="recent-card__line recent-card__line--meta"></div>
        </div>
      </div>

      <div class="recent-side-grid">
        <div
          v-for="index in 4"
          :key="index"
          class="recent-card recent-card--skeleton"
        >
          <div class="recent-card__poster recent-card__poster--skeleton"></div>
        </div>
      </div>
    </div>

    <div v-else-if="hasItems && activeItem" class="recent-carousel">
      <RouterLink
        :to="buildItemRoute(activeItem.id, 'home')"
        class="recent-feature-card"
      >
        <div class="recent-feature-card__image">
          <img :src="activeItem.image" :alt="activeItem.title" />

          <span v-if="activeItem.rating !== null" class="recent-card__rating">
            ★ {{ activeItem.rating.toFixed(1) }}
          </span>
        </div>

        <div class="recent-feature-card__content">
          <p class="recent-feature-card__eyebrow">{{ activeItem.category }}</p>
          <h3 class="recent-feature-card__title">{{ activeItem.title }}</h3>
          <p class="recent-feature-card__text">
            Recently added to the MediaCompass library. Open the page to view details,
            ratings, availability and similar items.
          </p>
        </div>
      </RouterLink>

      <div class="recent-side-grid">
        <button
          v-for="item in sideItems"
          :key="item.id"
          type="button"
          class="recent-card recent-card--button"
          @click="goToIndex(items.findIndex((candidate) => candidate.id === item.id))"
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
        </button>
      </div>
    </div>

    <div v-else class="recent-section__empty">
      No recent items available yet.
    </div>

    <div
      v-if="!isLoading && items.length > 1"
      class="recent-section__dots"
      aria-label="Recently added carousel pagination"
    >
      <button
        v-for="(_, index) in items"
        :key="index"
        type="button"
        class="recent-section__dot"
        :class="{ 'recent-section__dot--active': activeIndex === index }"
        :aria-label="`Show item ${index + 1}`"
        @click="goToIndex(index)"
      ></button>
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

.recent-section__arrow:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.recent-carousel {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.9fr);
  gap: 18px;
  align-items: stretch;
}

.recent-feature-card {
  min-height: 390px;
  overflow: hidden;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background:
    radial-gradient(circle at right top, rgba(37, 99, 235, 0.16), transparent 34%),
    rgba(8, 14, 24, 0.92);
  display: grid;
  grid-template-columns: minmax(220px, 0.72fr) minmax(0, 1fr);
  text-decoration: none;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease;
}

.recent-feature-card:hover {
  transform: translateY(-3px);
  border-color: rgba(96, 165, 250, 0.22);
}

.recent-feature-card__image {
  position: relative;
  min-height: 390px;
  background: #111827;
  overflow: hidden;
}

.recent-feature-card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}


.recent-feature-card__content {
  padding: 28px;
  display: grid;
  align-content: center;
  gap: 12px;
}

.recent-feature-card__eyebrow {
  margin: 0;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.recent-feature-card__title {
  margin: 0;
  color: #f8fafc;
  font-size: clamp(30px, 3.4vw, 48px);
  line-height: 1.05;
  letter-spacing: -0.04em;
}

.recent-feature-card__text {
  margin: 0;
  color: #94a3b8;
  line-height: 1.8;
}

.recent-side-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.recent-card {
  overflow: hidden;
}

.recent-card--button {
  padding: 0;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.recent-card--button:hover .recent-card__poster {
  border-color: rgba(96, 165, 250, 0.25);
  transform: translateY(-3px);
}

.recent-card__poster {
  position: relative;
  height: 210px;
  border-radius: 18px;
  overflow: hidden;
  background: #111827;
  border: 1px solid rgba(148, 163, 184, 0.08);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.24);
  transition:
    transform 0.2s ease,
    border-color 0.2s ease;
}

.recent-card__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  filter: saturate(1.04);
}

.recent-card__poster::after,
.recent-feature-card__image::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 35%, rgba(2, 6, 23, 0.18) 100%);
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
  padding: 12px 4px 0;
}

.recent-card__title {
  margin: 0 0 4px;
  color: #f8fafc;
  font-size: 16px;
  line-height: 1.3;
}

.recent-card__category {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  letter-spacing: 0.12em;
}

.recent-section__dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 18px;
}

.recent-section__dot {
  width: 8px;
  height: 8px;
  padding: 0;
  border: none;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.28);
  cursor: pointer;
}

.recent-section__dot--active {
  width: 24px;
  background: #60a5fa;
}

.recent-section__empty {
  padding: 24px;
  border-radius: 18px;
  border: 1px dashed rgba(148, 163, 184, 0.18);
  background: rgba(15, 23, 42, 0.48);
  color: #94a3b8;
}

.recent-card__poster--skeleton,
.recent-feature-card__image--skeleton,
.recent-card__line,
.recent-feature-card--skeleton {
  background: linear-gradient(
    90deg,
    rgba(15, 23, 42, 0.9) 0%,
    rgba(30, 41, 59, 0.95) 50%,
    rgba(15, 23, 42, 0.9) 100%
  );
  background-size: 220% 100%;
  animation: shimmer 1.4s linear infinite;
}

.recent-card__line {
  height: 12px;
}

.recent-card__line--title {
  width: 70%;
  margin-bottom: 10px;
}

.recent-card__line--meta {
  width: 45%;
}

@keyframes shimmer {
  0% {
    background-position: 220% 0;
  }

  100% {
    background-position: -220% 0;
  }
}

@media (max-width: 1080px) {
  .recent-carousel,
  .recent-feature-card {
    grid-template-columns: 1fr;
  }

  .recent-feature-card__image {
    min-height: 340px;
  }
}

@media (max-width: 760px) {
  .recent-section {
    width: min(100%, calc(100% - 32px));
  }

  .recent-section__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .recent-side-grid {
    grid-template-columns: 1fr;
  }
}
</style>