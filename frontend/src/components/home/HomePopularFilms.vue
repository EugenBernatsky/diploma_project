<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { PopularFilm } from '../../types/home'

defineProps<{
  films: PopularFilm[]
  isLoading?: boolean
  note?: string
}>()
</script>

<template>
  <section class="films-panel">
    <div class="films-panel__header">
      <div class="films-panel__title-wrap">
        <span class="films-panel__icon">▣</span>
        <h2 class="films-panel__title">Popular Films</h2>
      </div>

      <RouterLink to="/catalog" class="films-panel__link">See all</RouterLink>
    </div>

    <p v-if="note" class="films-panel__note">
      {{ note }}
    </p>

    <div v-if="isLoading" class="films-grid">
      <div v-for="index in 4" :key="index" class="film-card film-card--skeleton">
        <div class="film-card__poster film-card__poster--skeleton"></div>
        <div class="film-card__body">
          <div class="film-card__line film-card__line--title"></div>
          <div class="film-card__line film-card__line--meta"></div>
          <div class="film-card__line film-card__line--meta-short"></div>
        </div>
      </div>
    </div>

    <div v-else class="films-grid">
      <RouterLink
        v-for="film in films"
        :key="film.id"
        :to="`/items/${film.id}`"
        class="film-card"
      >
        <div class="film-card__poster">
          <img :src="film.image" :alt="film.title" />
        </div>

        <div class="film-card__body">
          <div class="film-card__top">
            <h3 class="film-card__title">{{ film.title }}</h3>
            <span v-if="film.rating !== null" class="film-card__rating">
              {{ film.rating.toFixed(1) }}
            </span>
          </div>

        <p class="film-card__meta">
            <template v-if="film.year">{{ film.year }}</template>
            <template v-if="film.year && film.genres.length"> • </template>
            <template v-if="film.genres.length">{{ film.genres.join(' • ') }}</template>
        </p>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.films-panel {
  padding: 30px;
  border: 1px solid rgba(96, 165, 250, 0.1);
  border-radius: 24px;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 32%),
    rgba(5, 11, 23, 0.9);
}

.films-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.films-panel__title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.films-panel__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.14);
  color: #60a5fa;
  font-size: 15px;
}

.films-panel__title {
  margin: 0;
  color: #f8fafc;
  font-size: 30px;
  letter-spacing: -0.03em;
}

.films-panel__link {
  color: #60a5fa;
  text-decoration: none;
  font-weight: 600;
}

.films-panel__note {
  margin: 0 0 20px;
  color: #60a5fa;
  font-size: 14px;
}

.films-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.film-card {
  display: flex;
  gap: 14px;
  padding: 14px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.72);
  text-decoration: none;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease;
}

.film-card:hover {
  transform: translateY(-3px);
  border-color: rgba(96, 165, 250, 0.3);
}

.film-card__poster {
  flex: 0 0 76px;
  height: 104px;
  overflow: hidden;
  border-radius: 12px;
  background: #1e293b;
}

.film-card__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.film-card__body {
  min-width: 0;
  flex: 1;
}

.film-card__top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: start;
  margin-bottom: 8px;
}

.film-card__title {
  margin: 0;
  color: #ffffff;
  font-size: 17px;
  line-height: 1.35;
}

.film-card__rating {
  flex: 0 0 auto;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.16);
  color: #93c5fd;
  font-size: 12px;
  font-weight: 700;
}

.film-card__meta {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.6;
}

.film-card__poster--skeleton,
.film-card__line {
  background: linear-gradient(
    90deg,
    rgba(15, 23, 42, 0.9) 0%,
    rgba(30, 41, 59, 0.95) 50%,
    rgba(15, 23, 42, 0.9) 100%
  );
  background-size: 220% 100%;
  animation: shimmer 1.4s linear infinite;
}

.film-card__line {
  border-radius: 999px;
}

.film-card__line--title {
  width: 82%;
  height: 18px;
  margin-bottom: 12px;
}

.film-card__line--meta {
  width: 62%;
  height: 12px;
  margin-bottom: 8px;
}

.film-card__line--meta-short {
  width: 40%;
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

@media (max-width: 700px) {
  .films-panel {
    padding: 22px;
  }

  .films-grid {
    grid-template-columns: 1fr;
  }
}
</style>