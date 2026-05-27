<script setup lang="ts">
import type { MediaItemStats } from '../../types/media'

defineProps<{
  stats: MediaItemStats
}>()

function formatRating(value: number | null | undefined): string {
  if (typeof value !== 'number') {
    return '—'
  }

  return value.toFixed(1)
}

function formatCount(value: number | null | undefined): string {
  if (typeof value !== 'number') {
    return '0'
  }

  return new Intl.NumberFormat('en-US').format(value)
}
</script>

<template>
  <section class="item-stats">
    <div class="item-stats__header">
      <div>
        <h2 class="item-stats__title">MediaCompass User Statistics</h2>
        <p class="item-stats__subtitle">
          Ratings and activity from users of this platform.
        </p>
      </div>
    </div>

    <div class="item-stats__grid">
      <article class="item-stats__card">
        <p class="item-stats__label">Site Rating</p>
        <strong class="item-stats__value">
          {{ formatRating(stats.user_rating_average) }}
        </strong>
        <span class="item-stats__meta">
          {{ formatCount(stats.user_ratings_count) }} user ratings
        </span>
      </article>

      <article class="item-stats__card">
        <p class="item-stats__label">Favorites</p>
        <strong class="item-stats__value">
          {{ formatCount(stats.favorites_count) }}
        </strong>
        <span class="item-stats__meta">users saved this item</span>
      </article>

      <article class="item-stats__card">
        <p class="item-stats__label">Statuses</p>
        <strong class="item-stats__value">
          {{ formatCount(stats.statuses_total_count) }}
        </strong>

        <div class="item-stats__status-list">
          <span>Planned: {{ stats.status_counts.planned }}</span>
          <span>In progress: {{ stats.status_counts.in_progress }}</span>
          <span>Completed: {{ stats.status_counts.completed }}</span>
          <span>Dropped: {{ stats.status_counts.dropped }}</span>
        </div>
      </article>

      <article class="item-stats__card">
        <p class="item-stats__label">Comments</p>
        <strong class="item-stats__value">
          {{ formatCount(stats.comments_count) }}
        </strong>
        <span class="item-stats__meta">community messages</span>
      </article>
    </div>
  </section>
</template>

<style scoped>
.item-stats {
  display: grid;
  gap: 18px;
  padding: 24px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.1), transparent 30%),
    rgba(8, 14, 24, 0.9);
}

.item-stats__header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: end;
}

.item-stats__title {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 34px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.item-stats__subtitle {
  margin: 0;
  color: #94a3b8;
  font-size: 15px;
  line-height: 1.7;
}

.item-stats__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.item-stats__card {
  min-width: 0;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.68);
}

.item-stats__label {
  margin: 0 0 10px;
  color: #64748b;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 800;
}

.item-stats__value {
  display: block;
  margin-bottom: 8px;
  color: #f8fafc;
  font-size: 32px;
  line-height: 1;
  letter-spacing: -0.04em;
}

.item-stats__meta {
  color: #94a3b8;
  font-size: 13px;
  line-height: 1.5;
}

.item-stats__status-list {
  display: grid;
  gap: 5px;
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.4;
}

@media (max-width: 1200px) {
  .item-stats__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .item-stats__grid {
    grid-template-columns: 1fr;
  }

  .item-stats__title {
    font-size: 28px;
  }
}
</style>