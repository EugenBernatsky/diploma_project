<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { getForumThreads } from '../../services/forum'
import type { ForumThreadResponse } from '../../types/forum'
import { formatRelativeTime } from '../../utils/forumTime'

const threads = ref<ForumThreadResponse[]>([])
const isLoading = ref(true)
const errorText = ref('')

function formatCategoryLabel(thread: ForumThreadResponse): string {
  if (thread.category_type === 'movie') return 'Movies'
  if (thread.category_type === 'series') return 'TV Series'
  if (thread.category_type === 'book') return 'Books'
  return thread.custom_category?.trim() || 'Custom'
}

const visibleThreads = computed(() => threads.value.slice(0, 4))

async function loadThreads() {
  isLoading.value = true
  errorText.value = ''

  try {
    threads.value = await getForumThreads({
      limit: 8,
      sort: 'activity',
    })
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load forum topics.'
    threads.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadThreads()
})
</script>

<template>
  <section class="home-forum-topics">
    <div class="home-forum-topics__header">
      <div>
        <p class="home-forum-topics__eyebrow">COMMUNITY</p>
        <h2 class="home-forum-topics__title">Hot Forum Topics</h2>
        <p class="home-forum-topics__text">
          Real discussions from the forum, sorted by latest activity.
        </p>
      </div>

      <RouterLink to="/forum" class="home-forum-topics__link">
        View All Topics
      </RouterLink>
    </div>

    <div v-if="isLoading" class="home-forum-topics__list">
      <div v-for="index in 4" :key="index" class="home-forum-topics__skeleton"></div>
    </div>

    <div v-else-if="errorText" class="home-forum-topics__state home-forum-topics__state--error">
      {{ errorText }}
    </div>

    <div v-else-if="visibleThreads.length" class="home-forum-topics__list">
      <RouterLink
        v-for="thread in visibleThreads"
        :key="thread.id"
        :to="`/forum/threads/${thread.id}`"
        class="home-forum-topics__card"
      >
        <div class="home-forum-topics__card-top">
          <span class="home-forum-topics__pill">
            {{ formatCategoryLabel(thread) }}
          </span>

          <span class="home-forum-topics__meta">
            {{ thread.replies_count }} replies
          </span>
        </div>

        <h3 class="home-forum-topics__card-title">
          {{ thread.title }}
        </h3>

        <p class="home-forum-topics__card-text">
          {{ thread.text }}
        </p>

        <div class="home-forum-topics__card-footer">
          <span>{{ thread.author_username }}</span>
          <span>•</span>
          <span>{{ formatRelativeTime(thread.last_activity_at) }}</span>
          <span>•</span>
          <span>Score {{ thread.score }}</span>
        </div>
      </RouterLink>
    </div>

    <div v-else class="home-forum-topics__state">
      No forum discussions yet. Start the first one.
    </div>
  </section>
</template>

<style scoped>
.home-forum-topics {
  display: grid;
  gap: 18px;
}

.home-forum-topics__header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: end;
}

.home-forum-topics__eyebrow {
  margin: 0 0 10px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.home-forum-topics__title {
  margin: 0 0 10px;
  color: #f8fafc;
  font-size: clamp(30px, 4vw, 42px);
  line-height: 1.05;
  letter-spacing: -0.04em;
}

.home-forum-topics__text {
  margin: 0;
  color: #94a3b8;
  font-size: 16px;
  line-height: 1.7;
}

.home-forum-topics__link {
  flex: 0 0 auto;
  color: #60a5fa;
  text-decoration: none;
  font-weight: 700;
}

.home-forum-topics__list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.home-forum-topics__card {
  display: block;
  padding: 20px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
  text-decoration: none;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease;
}

.home-forum-topics__card:hover {
  transform: translateY(-3px);
  border-color: rgba(96, 165, 250, 0.22);
}

.home-forum-topics__card-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.home-forum-topics__pill {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.14);
  color: #dbeafe;
  font-size: 12px;
  font-weight: 700;
}

.home-forum-topics__meta {
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.home-forum-topics__card-title {
  margin: 0 0 10px;
  color: #f8fafc;
  font-size: 22px;
  line-height: 1.25;
  letter-spacing: -0.03em;
}

.home-forum-topics__card-text {
  margin: 0 0 16px;
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.75;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.home-forum-topics__card-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: #64748b;
  font-size: 12px;
}

.home-forum-topics__state {
  padding: 24px;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
  color: #94a3b8;
}

.home-forum-topics__state--error {
  color: #fca5a5;
}

.home-forum-topics__skeleton {
  height: 210px;
  border-radius: 22px;
  background: linear-gradient(
    90deg,
    rgba(15, 23, 42, 0.9) 0%,
    rgba(30, 41, 59, 0.95) 50%,
    rgba(15, 23, 42, 0.9) 100%
  );
  background-size: 220% 100%;
  animation: shimmer 1.4s linear infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }

  100% {
    background-position: -20% 0;
  }
}

@media (max-width: 900px) {
  .home-forum-topics__list {
    grid-template-columns: 1fr;
  }

  .home-forum-topics__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>