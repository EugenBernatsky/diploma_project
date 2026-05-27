<script setup lang="ts">
withDefaults(
  defineProps<{
    totalItems: number
    sectionsCount: number
    lastUpdatedLabel: string
    isRefreshing?: boolean
  }>(),
  {
    isRefreshing: false,
  },
)

const emit = defineEmits<{
  (event: 'refresh'): void
}>()
</script>

<template>
  <section class="recommendations-hero">
    <div class="recommendations-hero__badge">HYBRID RECOMMENDATION ENGINE</div>

    <div class="recommendations-hero__content">
      <div class="recommendations-hero__copy">
        <h1 class="recommendations-hero__title">
          Crafted for Your Taste
          <span>Profile.</span>
        </h1>

        <p class="recommendations-hero__text">
          Personal recommendations are loaded from the production backend API.
          The page shows hybrid, popularity-based and collaborative-ready sections
          with clear fallback statuses.
        </p>

        <div class="recommendations-hero__stats">
          <span>{{ totalItems }} recommendations loaded</span>
          <span>{{ sectionsCount }} recommendation sections</span>
          <span>{{ lastUpdatedLabel }}</span>
        </div>
      </div>

      <button
        type="button"
        class="recommendations-hero__button"
        :disabled="isRefreshing"
        @click="emit('refresh')"
      >
        {{ isRefreshing ? 'Refreshing...' : 'Refresh My Recommendations' }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.recommendations-hero {
  padding: 28px 28px 26px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background:
    radial-gradient(circle at right top, rgba(37, 99, 235, 0.16), transparent 28%),
    radial-gradient(circle at left top, rgba(37, 99, 235, 0.12), transparent 26%),
    rgba(7, 14, 24, 0.9);
}

.recommendations-hero__badge {
  display: inline-flex;
  margin-bottom: 18px;
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.12);
  border: 1px solid rgba(96, 165, 250, 0.18);
  color: #bfdbfe;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.recommendations-hero__content {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: end;
}

.recommendations-hero__copy {
  max-width: 840px;
}

.recommendations-hero__title {
  margin: 0 0 14px;
  color: #f8fafc;
  font-size: clamp(42px, 5vw, 62px);
  line-height: 0.96;
  letter-spacing: -0.04em;
}

.recommendations-hero__title span {
  color: #3b82f6;
}

.recommendations-hero__text {
  max-width: 760px;
  margin: 0 0 18px;
  color: #94a3b8;
  font-size: 17px;
  line-height: 1.8;
}

.recommendations-hero__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #64748b;
  font-size: 13px;
}

.recommendations-hero__button {
  flex: 0 0 auto;
  min-height: 48px;
  padding: 0 18px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
}

.recommendations-hero__button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .recommendations-hero__content {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>