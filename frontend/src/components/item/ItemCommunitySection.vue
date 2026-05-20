<script setup lang="ts">
import { computed, ref } from 'vue'
import type { MediaItem } from '../../types/media'
import type { MockReview } from '../../mocks/itemDetails'
import { getQuickFacts } from '../../utils/itemDetails'

const props = defineProps<{
  item: MediaItem
  reviews: MockReview[]
}>()

const sortMode = ref<'recent' | 'rated'>('recent')

const sortedReviews = computed(() => {
  if (sortMode.value === 'rated') {
    return [...props.reviews].sort((a, b) => b.rating - a.rating)
  }

  return props.reviews
})

const quickFacts = computed(() => getQuickFacts(props.item))
</script>

<template>
  <section class="item-community">
    <div class="item-community__header">
      <h2 class="item-community__title">
        Community Reviews
        <span class="item-community__count">{{ reviews.length }}</span>
      </h2>

      <div class="item-community__sort">
        <button
          type="button"
          class="item-community__sort-btn"
          :class="{ 'item-community__sort-btn--active': sortMode === 'recent' }"
          @click="sortMode = 'recent'"
        >
          Most Recent
        </button>

        <button
          type="button"
          class="item-community__sort-btn"
          :class="{ 'item-community__sort-btn--active': sortMode === 'rated' }"
          @click="sortMode = 'rated'"
        >
          Highest Rated
        </button>
      </div>
    </div>

    <div class="item-community__content">
      <div class="item-community__reviews">
        <article
          v-for="review in sortedReviews"
          :key="review.id"
          class="item-community__review"
        >
          <div class="item-community__review-top">
            <div>
              <h3 class="item-community__author">{{ review.author }}</h3>
              <p class="item-community__stars">★ {{ review.rating.toFixed(1) }}</p>
            </div>

            <span class="item-community__time">{{ review.timeAgo }}</span>
          </div>

          <p class="item-community__text">
            {{ review.text }}
          </p>

          <div class="item-community__review-actions">
            <span>{{ review.helpful }} helpful</span>
            <span>Reply</span>
            <span>Share</span>
          </div>
        </article>
      </div>

      <aside class="item-community__sidebar">
        <div class="item-community__card">
          <h3 class="item-community__card-title">Write a Review</h3>
          <p class="item-community__card-text">
            UI block for now. Real review API can be wired next.
          </p>

          <div class="item-community__rating-row">
            <span>★</span><span>★</span><span>★</span><span>★</span><span>★</span>
          </div>

          <textarea
            class="item-community__textarea"
            placeholder="Share your thoughts about this item..."
            disabled
          />

          <button type="button" class="item-community__post-btn" disabled>
            Post Review
          </button>
        </div>

        <div class="item-community__card">
          <h3 class="item-community__card-title">Quick Facts</h3>

          <div class="item-community__facts">
            <div
              v-for="fact in quickFacts"
              :key="`${fact.label}-${fact.value}`"
              class="item-community__fact"
            >
              <span class="item-community__fact-label">{{ fact.label }}</span>
              <span class="item-community__fact-value">{{ fact.value }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.item-community {
  padding-top: 6px;
}

.item-community__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 18px;
}

.item-community__title {
  margin: 0;
  color: #f8fafc;
  font-size: 36px;
  line-height: 1;
  letter-spacing: -0.03em;
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-community__count {
  min-width: 30px;
  height: 30px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.8);
  color: #94a3b8;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.item-community__sort {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.item-community__sort-btn {
  min-height: 40px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.72);
  color: #cbd5e1;
  cursor: pointer;
  font-weight: 600;
}

.item-community__sort-btn--active {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  border-color: transparent;
}

.item-community__content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 26px;
}

.item-community__reviews {
  display: grid;
  gap: 18px;
}

.item-community__review {
  padding: 24px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
}

.item-community__review-top {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.item-community__author {
  margin: 0 0 4px;
  color: #f8fafc;
  font-size: 18px;
}

.item-community__stars {
  margin: 0;
  color: #60a5fa;
  font-size: 14px;
  font-weight: 700;
}

.item-community__time {
  color: #64748b;
  font-size: 13px;
}

.item-community__text {
  margin: 0 0 16px;
  color: #cbd5e1;
  line-height: 1.8;
  font-size: 16px;
}

.item-community__review-actions {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  color: #64748b;
  font-size: 13px;
}

.item-community__sidebar {
  display: grid;
  align-content: start;
  gap: 18px;
}

.item-community__card {
  padding: 22px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.72);
}

.item-community__card-title {
  margin: 0 0 12px;
  color: #f8fafc;
  font-size: 26px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.item-community__card-text {
  margin: 0 0 16px;
  color: #94a3b8;
  line-height: 1.7;
}

.item-community__rating-row {
  display: flex;
  gap: 6px;
  margin-bottom: 14px;
  color: #64748b;
  font-size: 22px;
}

.item-community__textarea {
  width: 100%;
  min-height: 130px;
  margin-bottom: 12px;
  padding: 14px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 14px;
  background: rgba(2, 6, 23, 0.7);
  color: #e2e8f0;
  resize: vertical;
}

.item-community__post-btn {
  width: 100%;
  min-height: 46px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 700;
  opacity: 0.7;
}

.item-community__facts {
  display: grid;
  gap: 14px;
}

.item-community__fact {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
}

.item-community__fact-label {
  color: #64748b;
  font-size: 13px;
}

.item-community__fact-value {
  color: #f8fafc;
  font-size: 14px;
  text-align: right;
  font-weight: 600;
}

@media (max-width: 980px) {
  .item-community__content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 680px) {
  .item-community__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .item-community__review-top {
    flex-direction: column;
  }
}
</style>