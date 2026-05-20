<script setup lang="ts">
import type { ForumMockThread } from '../../types/forum'
import {
  formatCompactNumber,
  formatForumRelativeTime,
  getForumCategoryLabel,
} from '../../utils/forum'

const props = defineProps<{
  thread: ForumMockThread
}>()

function getAuthorInitial(name: string): string {
  return name.trim().charAt(0).toUpperCase() || 'U'
}
</script>

<template>
  <article class="forum-topic-card">
    <div class="forum-topic-card__score">
      <button type="button" class="forum-topic-card__vote-btn" disabled>⌃</button>
      <span class="forum-topic-card__score-value">{{ thread.score }}</span>
      <button type="button" class="forum-topic-card__vote-btn" disabled>⌄</button>
    </div>

    <div class="forum-topic-card__content">
      <div class="forum-topic-card__top">
        <h3 class="forum-topic-card__title">{{ thread.title }}</h3>

        <span v-if="thread.is_trending" class="forum-topic-card__badge">
          Trending
        </span>
      </div>

      <p class="forum-topic-card__text">
        {{ thread.text }}
      </p>

      <div class="forum-topic-card__meta">
        <div class="forum-topic-card__author">
          <span class="forum-topic-card__avatar">
            {{ getAuthorInitial(thread.author_username) }}
          </span>

          <span class="forum-topic-card__username">{{ thread.author_username }}</span>
        </div>

        <span class="forum-topic-card__pill">
          {{ getForumCategoryLabel(thread.category_type, thread.custom_category) }}
        </span>

        <span class="forum-topic-card__time">
          Last active {{ formatForumRelativeTime(thread.last_activity_at) }}
        </span>

        <span v-if="thread.edited" class="forum-topic-card__edited">
          Edited
        </span>
      </div>
    </div>

    <div class="forum-topic-card__engagement">
      <div class="forum-topic-card__stat">
        <strong>{{ thread.replies_count }}</strong>
        <span>Replies</span>
      </div>

      <div class="forum-topic-card__stat">
        <strong>{{ formatCompactNumber(thread.views) }}</strong>
        <span>Views</span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.forum-topic-card {
  display: grid;
  grid-template-columns: 68px minmax(0, 1fr) 120px;
  gap: 18px;
  padding: 18px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.66);
}

.forum-topic-card__score {
  display: grid;
  justify-items: center;
  align-content: center;
  gap: 8px;
  padding: 10px 0;
  border-radius: 16px;
  background: rgba(8, 14, 24, 0.72);
}

.forum-topic-card__vote-btn {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: transparent;
  color: #64748b;
}

.forum-topic-card__score-value {
  color: #60a5fa;
  font-size: 20px;
  font-weight: 800;
}

.forum-topic-card__content {
  min-width: 0;
}

.forum-topic-card__top {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.forum-topic-card__title {
  margin: 0;
  color: #f8fafc;
  font-size: 26px;
  line-height: 1.2;
  letter-spacing: -0.03em;
}

.forum-topic-card__badge {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.18);
  color: #dbeafe;
  font-size: 12px;
  font-weight: 700;
}

.forum-topic-card__text {
  margin: 0 0 14px;
  color: #94a3b8;
  line-height: 1.7;
  font-size: 15px;
}

.forum-topic-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.forum-topic-card__author {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.forum-topic-card__avatar {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  background: linear-gradient(135deg, #f8fafc 0%, #dbeafe 100%);
  color: #0f172a;
  font-size: 12px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.forum-topic-card__username,
.forum-topic-card__time,
.forum-topic-card__edited {
  color: #94a3b8;
  font-size: 13px;
}

.forum-topic-card__pill {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.84);
  border: 1px solid rgba(148, 163, 184, 0.08);
  color: #cbd5e1;
  font-size: 12px;
  font-weight: 700;
}

.forum-topic-card__engagement {
  display: grid;
  align-content: center;
  gap: 12px;
}

.forum-topic-card__stat {
  display: grid;
  justify-items: end;
  gap: 2px;
}

.forum-topic-card__stat strong {
  color: #f8fafc;
  font-size: 18px;
}

.forum-topic-card__stat span {
  color: #64748b;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

@media (max-width: 980px) {
  .forum-topic-card {
    grid-template-columns: 68px 1fr;
  }

  .forum-topic-card__engagement {
    grid-column: 1 / -1;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .forum-topic-card__stat {
    justify-items: start;
  }
}

@media (max-width: 640px) {
  .forum-topic-card {
    grid-template-columns: 1fr;
  }

  .forum-topic-card__score {
    grid-auto-flow: column;
    justify-content: start;
    justify-items: start;
    padding: 12px;
  }

  .forum-topic-card__title {
    font-size: 22px;
  }
}
</style>