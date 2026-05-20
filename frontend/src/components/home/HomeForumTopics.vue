<script setup lang="ts">
import type { ForumTopic } from '../../types/home'

defineProps<{
  topics: ForumTopic[]
}>()
</script>

<template>
  <section class="forum-panel">
    <div class="forum-panel__header">
      <div class="forum-panel__title-wrap">
        <span class="forum-panel__icon">◌</span>
        <h2 class="forum-panel__title">Hot Forum Topics</h2>
      </div>

      <a href="#" class="forum-panel__link">View discussions</a>
    </div>

    <div class="forum-list">
      <article v-for="topic in topics" :key="topic.id" class="forum-item">
        <div class="forum-item__stats">
          <span class="forum-item__views">{{ topic.views >= 1000 ? `${(topic.views / 1000).toFixed(1)}k` : topic.views }}</span>
          <span class="forum-item__label">views</span>
        </div>

        <div class="forum-item__content">
          <h3 class="forum-item__title">{{ topic.title }}</h3>

          <p class="forum-item__meta">
            <span>{{ topic.replies }} replies</span>
            <span>{{ topic.timeAgo }}</span>
            <span>by {{ topic.author }}</span>
          </p>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.forum-panel {
  padding: 30px;
  border: 1px solid rgba(96, 165, 250, 0.1);
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.12), transparent 32%),
    rgba(5, 11, 23, 0.9);
}

.forum-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.forum-panel__title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.forum-panel__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.14);
  color: #60a5fa;
  font-size: 18px;
}

.forum-panel__title {
  margin: 0;
  color: #f8fafc;
  font-size: 30px;
  letter-spacing: -0.03em;
}

.forum-panel__link {
  color: #60a5fa;
  text-decoration: none;
  font-weight: 600;
}

.forum-list {
  display: grid;
}

.forum-item {
  display: grid;
  grid-template-columns: 70px 1fr;
  gap: 18px;
  padding: 18px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.12);
}

.forum-item:first-child {
  border-top: none;
  padding-top: 0;
}

.forum-item__stats {
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: center;
  justify-content: center;
  padding-top: 2px;
}

.forum-item__views {
  color: #60a5fa;
  font-weight: 800;
  font-size: 18px;
}

.forum-item__label {
  color: #64748b;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.1em;
}

.forum-item__title {
  margin: 0 0 10px;
  color: #f8fafc;
  font-size: 18px;
  line-height: 1.4;
}

.forum-item__meta {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  color: #94a3b8;
  font-size: 13px;
}

@media (max-width: 700px) {
  .forum-panel {
    padding: 22px;
  }

  .forum-item {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .forum-item__stats {
    align-items: start;
  }
}
</style>