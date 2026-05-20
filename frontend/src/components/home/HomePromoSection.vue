<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { PromoTile } from '../../types/home'

defineProps<{
  tiles: PromoTile[]
}>()
</script>

<template>
  <section class="promo-section">
    <div class="promo-section__content">
      <div class="promo-section__copy">
        <h2 class="promo-section__title">
          <span>Lost in a sea of content?</span>
          <span class="promo-section__title-accent">Let us be your guide.</span>
        </h2>

        <p class="promo-section__text">
          Our algorithm analyzes your unique tastes across mediums to provide truly
          personalized discovery. No more endless scrolling.
        </p>

        <RouterLink to="/register" class="promo-section__button">
          Get Started for Free
        </RouterLink>
      </div>

      <div class="promo-section__gallery">
        <div
          v-for="tile in tiles"
          :key="tile.id"
          class="promo-section__tile"
        >
          <img :src="tile.image" :alt="tile.alt" />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.promo-section {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding: 40px 0 72px;
}

.promo-section__content {
  display: grid;
  grid-template-columns: 1fr 1.05fr;
  gap: 36px;
  align-items: center;
  padding: 54px;
  border: 1px solid rgba(96, 165, 250, 0.1);
  border-radius: 28px;
  background:
    radial-gradient(circle at left center, rgba(37, 99, 235, 0.18), transparent 35%),
    linear-gradient(180deg, rgba(9, 14, 25, 0.98), rgba(3, 8, 18, 0.98));
}

.promo-section__title {
  margin: 0 0 18px;
  display: flex;
  flex-direction: column;
  font-size: clamp(34px, 4vw, 56px);
  line-height: 1.02;
  letter-spacing: -0.04em;
  color: #f8fafc;
}

.promo-section__title-accent {
  color: #3b82f6;
}

.promo-section__text {
  max-width: 520px;
  margin: 0 0 28px;
  color: #94a3b8;
  font-size: 18px;
  line-height: 1.7;
}

.promo-section__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 52px;
  padding: 0 22px;
  border-radius: 999px;
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  color: #ffffff;
  text-decoration: none;
  font-weight: 700;
  box-shadow: 0 12px 30px rgba(37, 99, 235, 0.25);
}

.promo-section__gallery {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.promo-section__tile {
  aspect-ratio: 1 / 1.14;
  overflow: hidden;
  border-radius: 12px;
  background: #111827;
}

.promo-section__tile img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  opacity: 0.9;
}

@media (max-width: 900px) {
  .promo-section {
    width: min(100%, calc(100% - 32px));
  }

  .promo-section__content {
    grid-template-columns: 1fr;
    padding: 28px;
  }
}

@media (max-width: 560px) {
  .promo-section__gallery {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>