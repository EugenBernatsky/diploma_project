<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import ForumToolbar from '../components/forum/ForumToolbar.vue'
import ForumTopicCard from '../components/forum/ForumTopicCard.vue'
import ForumPagination from '../components/forum/ForumPagination.vue'
import { getForumThreads } from '../services/forum'
import type { ForumCategoryType, ForumThreadResponse, ForumThreadSort } from '../types/forum'

type ForumCategoryFilter = 'all' | ForumCategoryType

const threads = ref<ForumThreadResponse[]>([])
const isLoading = ref(true)
const errorText = ref('')

const currentCategory = ref<ForumCategoryFilter>('all')
const searchQuery = ref('')
const sortBy = ref<ForumThreadSort>('activity')
const currentPage = ref(1)

const itemsPerPage = 10

async function loadThreads() {
  isLoading.value = true
  errorText.value = ''

  try {
    threads.value = await getForumThreads({
      limit: 100,
      sort: sortBy.value,
      category_type: currentCategory.value === 'all' ? undefined : currentCategory.value,
    })
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load forum threads.'
    threads.value = []
  } finally {
    isLoading.value = false
  }
}

const filteredThreads = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  if (!query) return threads.value

  return threads.value.filter((thread) => {
    return (
      thread.title.toLowerCase().includes(query) ||
      thread.text.toLowerCase().includes(query) ||
      thread.author_username.toLowerCase().includes(query) ||
      (thread.custom_category || '').toLowerCase().includes(query)
    )
  })
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredThreads.value.length / itemsPerPage)),
)

const paginatedThreads = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredThreads.value.slice(start, start + itemsPerPage)
})

const todayTopicsCount = computed(() => {
  const now = new Date()

  return threads.value.filter((thread) => {
    const created = new Date(thread.created_at)
    return (
      created.getFullYear() === now.getFullYear() &&
      created.getMonth() === now.getMonth() &&
      created.getDate() === now.getDate()
    )
  }).length
})

const summaryLabel = computed(() => {
  if (!filteredThreads.value.length) return 'Showing 0 topics'

  const start = (currentPage.value - 1) * itemsPerPage + 1
  const end = Math.min(currentPage.value * itemsPerPage, filteredThreads.value.length)
  return `Showing ${start}-${end} of ${filteredThreads.value.length} topics`
})

watch([currentCategory, sortBy], async () => {
  currentPage.value = 1
  await loadThreads()
})

watch(searchQuery, () => {
  currentPage.value = 1
})

watch(totalPages, (pages) => {
  if (currentPage.value > pages) {
    currentPage.value = pages
  }
})

onMounted(() => {
  loadThreads()
})
</script>

<template>
  <section class="forum-page">
    <div class="forum-page__inner">
      <header class="forum-page__hero">
        <div class="forum-page__hero-copy">
          <h1 class="forum-page__title">Community Forum</h1>
          <p class="forum-page__text">
            Start real discussions, vote on topics, and reply with the new flat reply
            model. This page now works against the real forum API.
          </p>

          <div class="forum-page__stats">
            <div class="forum-page__stat-card">
              <span class="forum-page__stat-label">Today’s topics</span>
              <strong class="forum-page__stat-value">{{ todayTopicsCount }}</strong>
            </div>

            <div class="forum-page__stat-card">
              <span class="forum-page__stat-label">Loaded topics</span>
              <strong class="forum-page__stat-value">{{ threads.length }}</strong>
            </div>
          </div>
        </div>

        <RouterLink to="/forum/new" class="forum-page__new-topic-btn">
          + New Discussion
        </RouterLink>
      </header>

      <ForumToolbar
        :category="currentCategory"
        :search-query="searchQuery"
        :sort-by="sortBy"
        @update:category="currentCategory = $event"
        @update:searchQuery="searchQuery = $event"
        @update:sortBy="sortBy = $event"
      />

      <div class="forum-page__list-head">
        <p class="forum-page__summary">{{ summaryLabel }}</p>
      </div>

      <div v-if="isLoading" class="forum-page__state">
        Loading forum threads...
      </div>

      <div
        v-else-if="errorText"
        class="forum-page__state forum-page__state--error"
      >
        {{ errorText }}
      </div>

      <div v-else-if="paginatedThreads.length" class="forum-page__topics">
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
  text-decoration: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.forum-page__state,
.forum-page__empty {
  padding: 32px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(9, 14, 25, 0.7);
  color: #94a3b8;
}

.forum-page__state--error {
  color: #fca5a5;
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