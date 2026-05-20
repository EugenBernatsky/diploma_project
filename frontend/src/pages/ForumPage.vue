<script setup lang="ts">
import { computed, ref } from 'vue'
import ForumToolbar from '../components/forum/ForumToolbar.vue'
import ForumTopicCard from '../components/forum/ForumTopicCard.vue'
import ForumPagination from '../components/forum/ForumPagination.vue'
import ForumCta from '../components/forum/ForumCta.vue'
import { forumMockData } from '../mocks/forum'
import type {
  ForumCategoryType,
  ForumMockThread,
  ForumSortOption,
} from '../types/forum'
import {
  countTodayThreads,
  formatCompactNumber,
  sortForumThreads,
} from '../utils/forum'

type ForumCategoryFilter = 'all' | ForumCategoryType

const currentCategory = ref<ForumCategoryFilter>('all')
const searchQuery = ref('')
const sortBy = ref<ForumSortOption>('active')
const currentPage = ref(1)

const itemsPerPage = 10

const threads = computed(() => forumMockData.threads)
const todayTopicsCount = computed(() => countTodayThreads(threads.value))

const filteredThreads = computed<ForumMockThread[]>(() => {
  const query = searchQuery.value.trim().toLowerCase()

  return threads.value.filter((thread) => {
    const matchesCategory =
      currentCategory.value === 'all' ||
      thread.category_type === currentCategory.value

    const matchesSearch =
      !query ||
      thread.title.toLowerCase().includes(query) ||
      thread.text.toLowerCase().includes(query) ||
      thread.author_username.toLowerCase().includes(query) ||
      (thread.custom_category || '').toLowerCase().includes(query)

    return matchesCategory && matchesSearch
  })
})

const sortedThreads = computed(() =>
  sortForumThreads(filteredThreads.value, sortBy.value),
)

const totalPages = computed(() =>
  Math.max(1, Math.ceil(sortedThreads.value.length / itemsPerPage)),
)

const paginatedThreads = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return sortedThreads.value.slice(start, start + itemsPerPage)
})

const listSummary = computed(() => {
  if (!sortedThreads.value.length) {
    return 'Showing 0 topics'
  }

  const start = (currentPage.value - 1) * itemsPerPage + 1
  const end = Math.min(currentPage.value * itemsPerPage, sortedThreads.value.length)

  return `Showing ${start}-${end} of ${sortedThreads.value.length} topics`
})

function handleCategoryChange(value: ForumCategoryFilter) {
  currentCategory.value = value
}

watchFilters()

function watchFilters() {
  const sync = () => {
    currentPage.value = 1
  }

  ;[currentCategory, searchQuery, sortBy].forEach((source) => {
    source.value
  })

  // Vue reactivity via computed watchers below
}

import { watch } from 'vue'

watch([currentCategory, searchQuery, sortBy], () => {
  currentPage.value = 1
})

watch(totalPages, (pages) => {
  if (currentPage.value > pages) {
    currentPage.value = pages
  }
})
</script>

<template>
  <section class="forum-page">
    <div class="forum-page__inner">
      <header class="forum-page__hero">
        <div class="forum-page__hero-copy">
          <h1 class="forum-page__title">Community Forum</h1>
          <p class="forum-page__text">
            Connect with fellow enthusiasts, share your latest discoveries, and dive
            deep into the media you love. This mock forum uses data shaped close to
            the backend schema, so switching to real API data later will be much
            easier.
          </p>

          <div class="forum-page__stats">
            <div class="forum-page__stat-card">
              <span class="forum-page__stat-label">Today’s topics</span>
              <strong class="forum-page__stat-value">{{ todayTopicsCount }}</strong>
            </div>

            <div class="forum-page__stat-card">
              <span class="forum-page__stat-label">Total threads views</span>
              <strong class="forum-page__stat-value">
                {{
                  formatCompactNumber(
                    threads.reduce((acc, thread) => acc + thread.views, 0),
                  )
                }}
              </strong>
            </div>
          </div>
        </div>

        <button type="button" class="forum-page__new-topic-btn">
          + New Discussion
        </button>
      </header>

      <ForumToolbar
        :category="currentCategory"
        :search-query="searchQuery"
        :sort-by="sortBy"
        @update:category="handleCategoryChange"
        @update:searchQuery="searchQuery = $event"
        @update:sortBy="sortBy = $event"
      />

      <div class="forum-page__list-head">
        <p class="forum-page__summary">{{ listSummary }}</p>
      </div>

      <div v-if="paginatedThreads.length" class="forum-page__topics">
        <ForumTopicCard
          v-for="thread in paginatedThreads"
          :key="thread.id"
          :thread="thread"
        />
      </div>

      <div v-else class="forum-page__empty">
        No discussions match the current filters.
      </div>

      <div class="forum-page__pagination-wrap">
        <ForumPagination
          :current-page="currentPage"
          :total-pages="totalPages"
          @update:page="currentPage = $event"
        />
      </div>

      <ForumCta />
    </div>
  </section>
</template>

<style scoped>
.forum-page {
  width: 100%;
  padding: 30px 0 56px;
}

.forum-page__inner {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  display: grid;
  gap: 24px;
}

.forum-page__hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: start;
  padding: 34px 28px 30px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  border-radius: 0 0 24px 24px;
  background:
    radial-gradient(circle at left top, rgba(37, 99, 235, 0.16), transparent 36%),
    rgba(7, 14, 24, 0.9);
}

.forum-page__hero-copy {
  max-width: 820px;
}

.forum-page__title {
  margin: 0 0 12px;
  color: #f8fafc;
  font-size: clamp(42px, 5vw, 64px);
  line-height: 1;
  letter-spacing: -0.04em;
}

.forum-page__text {
  max-width: 760px;
  margin: 0 0 20px;
  color: #94a3b8;
  font-size: 18px;
  line-height: 1.7;
}

.forum-page__stats {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.forum-page__stat-card {
  min-width: 170px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.55);
}

.forum-page__stat-label {
  display: block;
  margin-bottom: 6px;
  color: #64748b;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
}

.forum-page__stat-value {
  color: #f8fafc;
  font-size: 32px;
  line-height: 1;
}

.forum-page__new-topic-btn {
  min-height: 50px;
  padding: 0 20px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
}

.forum-page__list-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.forum-page__summary {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

.forum-page__topics {
  display: grid;
  gap: 14px;
}

.forum-page__empty {
  padding: 32px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(9, 14, 25, 0.7);
  color: #94a3b8;
  text-align: center;
}

.forum-page__pagination-wrap {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 900px) {
  .forum-page__inner {
    width: min(100%, calc(100% - 32px));
  }

  .forum-page__hero {
    flex-direction: column;
  }
}
</style>