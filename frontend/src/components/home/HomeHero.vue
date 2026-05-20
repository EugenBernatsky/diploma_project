<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { HeroAction } from '../../types/home'

defineProps<{
  badge: string
  title: string
  accentTitle: string
  description: string
  backgroundImage: string
  actions: HeroAction[]
}>()
</script>

<template>
  <section
    class="home-hero"
    :style="{
      backgroundImage: `linear-gradient(90deg, rgba(2, 6, 23, 0.96) 0%, rgba(2, 6, 23, 0.8) 42%, rgba(2, 6, 23, 0.55) 70%, rgba(2, 6, 23, 0.35) 100%), url(${backgroundImage})`,
    }"
  >
    <div class="home-hero__content">
      <p class="home-hero__badge">{{ badge }}</p>

      <h1 class="home-hero__title">
        <span>{{ title }}</span>
        <span class="home-hero__title-accent">{{ accentTitle }}</span>
      </h1>

      <p class="home-hero__description">
        {{ description }}
      </p>

      <div class="home-hero__actions">
        <RouterLink
          v-for="action in actions"
          :key="action.label"
          :to="action.to"
          class="home-hero__button"
          :class="{
            'home-hero__button--primary': action.variant === 'primary',
            'home-hero__button--secondary': action.variant === 'secondary',
          }"
        >
          <span>{{ action.label }}</span>
          <span v-if="action.variant === 'primary'" class="home-hero__button-arrow">›</span>
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.home-hero {
  min-height: 620px;
  border: 1px solid rgba(96, 165, 250, 0.12);
  border-radius: 0 0 28px 28px;
  background-position: center;
  background-size: cover;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.home-hero__content {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding: 72px 0 92px;
}

.home-hero__badge {
  display: inline-flex;
  align-items: center;
  margin: 0 0 28px;
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid rgba(59, 130, 246, 0.28);
  background: rgba(30, 64, 175, 0.22);
  color: #bfdbfe;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.home-hero__title {
  max-width: 760px;
  margin: 0 0 20px;
  display: flex;
  flex-direction: column;
  font-size: clamp(52px, 7vw, 96px);
  line-height: 0.93;
  letter-spacing: -0.04em;
  color: #ffffff;
}

.home-hero__title-accent {
  color: #3b82f6;
}

.home-hero__description {
  max-width: 620px;
  margin: 0 0 36px;
  color: #dbe5f5;
  font-size: 20px;
  line-height: 1.7;
}

.home-hero__actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.home-hero__button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 54px;
  padding: 0 22px;
  border-radius: 14px;
  text-decoration: none;
  font-weight: 700;
  transition:
    transform 0.18s ease,
    border-color 0.18s ease,
    background 0.18s ease;
}

.home-hero__button:hover {
  transform: translateY(-1px);
}

.home-hero__button--primary {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  color: #ffffff;
  box-shadow: 0 12px 30px rgba(37, 99, 235, 0.25);
}

.home-hero__button--secondary {
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(2, 6, 23, 0.72);
  color: #ffffff;
}

.home-hero__button-arrow {
  font-size: 20px;
  line-height: 1;
}

@media (max-width: 900px) {
  .home-hero {
    min-height: 540px;
    border-radius: 0 0 22px 22px;
  }

  .home-hero__content {
    width: min(100%, calc(100% - 32px));
    padding: 56px 0 64px;
  }

  .home-hero__description {
    font-size: 17px;
  }
}

@media (max-width: 640px) {
  .home-hero__actions {
    flex-direction: column;
    align-items: stretch;
  }

  .home-hero__button {
    justify-content: center;
  }
}
</style>