<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="home-promo-cta">
    <div class="home-promo-cta__content">
      <p class="home-promo-cta__eyebrow">DISCOVERY</p>
      <h2 class="home-promo-cta__title">
        Stop scrolling. Start discovering.
      </h2>
      <p class="home-promo-cta__text">
        Use MediaCompass to find movies, series, and books that actually match your interests.
      </p>
    </div>

    <RouterLink to="/catalog" class="home-promo-cta__button">
      Open Catalog
    </RouterLink>
  </section>
</template>

<style scoped>
.home-promo-cta {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
  padding: 28px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background:
    radial-gradient(circle at right top, rgba(37, 99, 235, 0.16), transparent 28%),
    rgba(7, 14, 24, 0.9);
}

.home-promo-cta__content {
  max-width: 780px;
}

.home-promo-cta__eyebrow {
  margin: 0 0 10px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.home-promo-cta__title {
  margin: 0 0 12px;
  color: #f8fafc;
  font-size: clamp(32px, 4vw, 48px);
  line-height: 1.05;
  letter-spacing: -0.04em;
}

.home-promo-cta__text {
  margin: 0;
  color: #94a3b8;
  font-size: 17px;
  line-height: 1.8;
}

.home-promo-cta__button {
  flex: 0 0 auto;
  min-height: 48px;
  padding: 0 18px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  text-decoration: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 900px) {
  .home-promo-cta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>