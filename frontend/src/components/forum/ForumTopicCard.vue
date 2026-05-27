<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { ForumThreadResponse } from '../../types/forum'
import { formatRelativeTime } from '../../utils/forumTime'
import { getAvatarImageUrl } from '../../utils/avatars'

const props = defineProps<{
  thread: ForumThreadResponse
}>()

function formatCategoryLabel(thread: ForumThreadResponse): string {
  if (thread.category_type === 'movie') return 'Movies'
  if (thread.category_type === 'series') return 'TV Series'
  if (thread.category_type === 'book') return 'Books'
  return thread.custom_category?.trim() || 'Custom'
}

function getAuthorInitial(name: string): string {
  return name.trim().charAt(0).toUpperCase() || 'U'
}

const threadLink = computed(() => `/forum/threads/${props.thread.id}`)

const authorAvatarUrl = computed(() => {
  return getAvatarImageUrl(props.thread.author_avatar_id)
})

</script>

<template>
  <RouterLink :to="threadLink" class="forum-topic-card">
    <div class="forum-topic-card__score">
      <span class="forum-topic-card__score-value">{{ thread.score }}</span>
      <span class="forum-topic-card__score-label">Score</span>
    </div>

    <div class="forum-topic-card__content">
      <div class="forum-topic-card__top">
        <h3 class="forum-topic-card__title">{{ thread.title }}</h3>
      </div>

      <p class="forum-topic-card__text">
        {{ thread.text }}
      </p>

      <div class="forum-topic-card__meta">
        <div class="forum-topic-card__author">
          <span class="forum-topic-card__avatar">
            <img
              v-if="authorAvatarUrl"
              :src="authorAvatarUrl"
              :alt="thread.author_username"
            />

            <span v-else>{{ getAuthorInitial(thread.author_username) }}</span>
          </span>

          <span class="forum-topic-card__username">{{ thread.author_username }}</span>
        </div>

        <span class="forum-topic-card__pill">
          {{ formatCategoryLabel(thread) }}
        </span>

        <span class="forum-topic-card__time">
          Last active {{ formatRelativeTime(thread.last_activity_at) }}
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
    </div>
  </RouterLink>
</template>

<style scoped>
.forum-topic-card {
  display: grid;
  grid-template-columns: 88px minmax(0, 1fr) 110px;
  gap: 18px;
  padding: 18px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.66);
  text-decoration: none;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease;
}

.forum-topic-card:hover {
  transform: translateY(-2px);
  border-color: rgba(96, 165, 250, 0.22);
}

.forum-topic-card__score {
  display: grid;
  justify-items: center;
  align-content: center;
  gap: 4px;
  padding: 12px;
  border-radius: 16px;
  background: rgba(8, 14, 24, 0.72);
}

.forum-topic-card__score-value {
  color: #60a5fa;
  font-size: 24px;
  font-weight: 800;
}

.forum-topic-card__score-label {
  color: #64748b;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
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
  font-size: 24px;
  line-height: 1.2;
  letter-spacing: -0.03em;
}

.forum-topic-card__text {
  margin: 0 0 14px;
  color: #94a3b8;
  line-height: 1.7;
  font-size: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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

.forum-topic-card__avatar img {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: inherit;
  object-fit: cover;
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
    grid-template-columns: 88px 1fr;
  }

  .forum-topic-card__engagement {
    grid-column: 1 / -1;
  }

  .forum-topic-card__stat {
    justify-items: start;
  }
}

@media (max-width: 640px) {
  .forum-topic-card {
    grid-template-columns: 1fr;
  }

  .forum-topic-card__title {
    font-size: 21px;
  }
}
</style>