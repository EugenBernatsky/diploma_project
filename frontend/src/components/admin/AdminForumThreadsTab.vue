<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  deleteAdminForumThread,
  getAdminForumThreads,
} from '../../services/admin'
import type { AdminForumThread } from '../../types/admin'
import { getAvatarImageUrl } from '../../utils/avatars'
import ConfirmModal from '../common/ConfirmModal.vue'

const emit = defineEmits<{
  (event: 'close'): void
}>()

const router = useRouter()

const PAGE_SIZE = 20
const SEARCH_DEBOUNCE_MS = 450

const threads = ref<AdminForumThread[]>([])
const searchInput = ref('')
const categoryFilter = ref<AdminForumThread['category'] | ''>('')
const skip = ref(0)
const total = ref(0)

const isLoading = ref(false)
const isDeleting = ref(false)
const errorText = ref('')
const successText = ref('')

const threadToDelete = ref<AdminForumThread | null>(null)

let searchTimeoutId: number | undefined

const currentPage = computed(() => {
  return Math.floor(skip.value / PAGE_SIZE) + 1
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(total.value / PAGE_SIZE))
})

const searchTerm = computed(() => {
  const value = searchInput.value.trim()

  if (value.length >= 3) {
    return value
  }

  return ''
})

const searchHint = computed(() => {
  const value = searchInput.value.trim()

  if (value.length > 0 && value.length < 3) {
    return 'Enter at least 3 characters to search.'
  }

  return ''
})

function formatDate(value: string | null): string {
  if (!value) {
    return '—'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '—'
  }

  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function getAuthorInitial(username: string): string {
  return username.trim().charAt(0).toUpperCase() || 'U'
}

function getThreadCategoryLabel(thread: AdminForumThread): string {
  if (thread.category === 'custom') {
    return thread.custom_category || 'Custom'
  }

  return thread.category
}

function getThreadPreview(thread: AdminForumThread): string {
  const content = thread.content?.trim()

  if (!content) {
    return 'No content.'
  }

  return content
}

async function loadThreads() {
  isLoading.value = true
  errorText.value = ''

  try {
    const response = await getAdminForumThreads({
      search: searchTerm.value || undefined,
      category: categoryFilter.value || undefined,
      limit: PAGE_SIZE,
      skip: skip.value,
    })

    threads.value = response.results
    total.value = response.total
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load forum threads.'
    threads.value = []
    total.value = 0
  } finally {
    isLoading.value = false
  }
}

function scheduleReload() {
  window.clearTimeout(searchTimeoutId)

  searchTimeoutId = window.setTimeout(() => {
    skip.value = 0
    loadThreads()
  }, SEARCH_DEBOUNCE_MS)
}

function goToPage(page: number) {
  const safePage = Math.min(Math.max(page, 1), totalPages.value)
  skip.value = (safePage - 1) * PAGE_SIZE
  loadThreads()
}

function openThread(threadId: string) {
  emit('close')
  router.push(`/forum/threads/${threadId}`)
}

function requestDelete(thread: AdminForumThread) {
  successText.value = ''
  errorText.value = ''
  threadToDelete.value = thread
}

function cancelDelete() {
  if (isDeleting.value) {
    return
  }

  threadToDelete.value = null
}

async function confirmDelete() {
  if (!threadToDelete.value) {
    return
  }

  isDeleting.value = true
  errorText.value = ''
  successText.value = ''

  try {
    await deleteAdminForumThread(threadToDelete.value.id)

    successText.value = 'Forum thread deleted.'
    threadToDelete.value = null

    const isLastItemOnPage = threads.value.length === 1 && skip.value > 0

    if (isLastItemOnPage) {
      skip.value = Math.max(0, skip.value - PAGE_SIZE)
    }

    await loadThreads()
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to delete forum thread.'
  } finally {
    isDeleting.value = false
  }
}

watch(searchInput, () => {
  scheduleReload()
})

watch(categoryFilter, () => {
  skip.value = 0
  loadThreads()
})

onMounted(() => {
  loadThreads()
})
</script>

<template>
  <section class="admin-threads-tab">
    <header class="admin-threads-tab__header">
      <div>
        <p class="admin-threads-tab__eyebrow">Forum Threads</p>
        <h3>Forum Topics</h3>
        <span>
          Search forum topics, filter by category and remove inappropriate threads.
        </span>
      </div>

      <button
        type="button"
        class="admin-threads-tab__refresh"
        :disabled="isLoading"
        @click="loadThreads"
      >
        {{ isLoading ? 'Loading...' : 'Refresh' }}
      </button>
    </header>

    <div class="admin-threads-tab__filters">
      <label class="admin-threads-tab__field">
        <span>Search</span>
        <input
          v-model="searchInput"
          type="search"
          placeholder="Search by title, text, username..."
          autocomplete="off"
        />
      </label>

      <label class="admin-threads-tab__field admin-threads-tab__field--select">
        <span>Category</span>
        <select v-model="categoryFilter">
          <option value="">All categories</option>
          <option value="movie">Movies</option>
          <option value="series">Series</option>
          <option value="book">Books</option>
          <option value="custom">Custom</option>
        </select>
      </label>
    </div>

    <p v-if="searchHint" class="admin-threads-tab__hint">
      {{ searchHint }}
    </p>

    <p v-if="errorText" class="admin-threads-tab__error">
      {{ errorText }}
    </p>

    <p v-if="successText" class="admin-threads-tab__success">
      {{ successText }}
    </p>

    <div class="admin-threads-tab__summary">
      <span>
        Page {{ currentPage }} of {{ totalPages }}
      </span>

      <strong>
        {{ total }} total threads
      </strong>
    </div>

    <div v-if="isLoading" class="admin-threads-tab__state">
      Loading forum threads...
    </div>

    <div v-else-if="threads.length === 0" class="admin-threads-tab__state">
      No forum threads found.
    </div>

    <div v-else class="admin-threads-tab__list">
      <article
        v-for="thread in threads"
        :key="thread.id"
        class="admin-thread-card"
      >
        <div class="admin-thread-card__avatar">
          <img
            v-if="getAvatarImageUrl(thread.author_avatar_id)"
            :src="getAvatarImageUrl(thread.author_avatar_id) || undefined"
            :alt="thread.author_username"
          />

          <span v-else>{{ getAuthorInitial(thread.author_username) }}</span>
        </div>

        <div class="admin-thread-card__body">
          <div class="admin-thread-card__top">
            <div>
              <h4>{{ thread.title }}</h4>

              <p>
                by {{ thread.author_username }}
                <span>•</span>
                {{ formatDate(thread.created_at) }}
              </p>
            </div>

            <span class="admin-thread-card__badge">
              {{ getThreadCategoryLabel(thread) }}
            </span>
          </div>

          <p class="admin-thread-card__content">
            {{ getThreadPreview(thread) }}
          </p>

          <div class="admin-thread-card__meta">
            <span>Thread ID: {{ thread.id }}</span>
            <span>User ID: {{ thread.user_id }}</span>
            <span>Posts: {{ thread.posts_count }}</span>
            <span>Votes: {{ thread.votes_count }}</span>
          </div>
        </div>

        <div class="admin-thread-card__actions">
          <button
            type="button"
            class="admin-thread-card__button"
            @click="openThread(thread.id)"
          >
            Open
          </button>

          <button
            type="button"
            class="admin-thread-card__button admin-thread-card__button--danger"
            @click="requestDelete(thread)"
          >
            Delete
          </button>
        </div>
      </article>
    </div>

    <footer class="admin-threads-tab__pagination">
      <button
        type="button"
        :disabled="isLoading || currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        Previous
      </button>

      <span>
        {{ currentPage }} / {{ totalPages }}
      </span>

      <button
        type="button"
        :disabled="isLoading || currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        Next
      </button>
    </footer>

    <ConfirmModal
      :open="Boolean(threadToDelete)"
      title="Delete forum thread?"
      :message="`This will permanently delete the thread '${threadToDelete?.title || 'selected thread'}' and its discussion. This action cannot be undone.`"
      confirm-label="Delete thread"
      cancel-label="Cancel"
      :is-busy="isDeleting"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </section>
</template>

<style scoped>
.admin-threads-tab {
  display: grid;
  gap: 18px;
}

.admin-threads-tab__header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: start;
}

.admin-threads-tab__eyebrow {
  margin: 0 0 8px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.admin-threads-tab__header h3 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 30px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.admin-threads-tab__header span,
.admin-threads-tab__hint,
.admin-threads-tab__summary span {
  color: #94a3b8;
  line-height: 1.6;
}

.admin-threads-tab__refresh,
.admin-thread-card__button,
.admin-threads-tab__pagination button {
  min-height: 40px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #ffffff;
  font-weight: 800;
  cursor: pointer;
}

.admin-threads-tab__refresh:disabled,
.admin-threads-tab__pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.admin-threads-tab__filters {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  gap: 14px;
}

.admin-threads-tab__field {
  display: grid;
  gap: 8px;
}

.admin-threads-tab__field span {
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 800;
}

.admin-threads-tab__field input,
.admin-threads-tab__field select {
  width: 100%;
  min-height: 44px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  outline: none;
}

.admin-threads-tab__field input:focus,
.admin-threads-tab__field select:focus {
  border-color: rgba(96, 165, 250, 0.55);
}

.admin-threads-tab__error,
.admin-threads-tab__success {
  margin: 0;
  padding: 14px 16px;
  border-radius: 14px;
  font-weight: 700;
}

.admin-threads-tab__error {
  background: rgba(239, 68, 68, 0.12);
  color: #fca5a5;
}

.admin-threads-tab__success {
  background: rgba(34, 197, 94, 0.12);
  color: #86efac;
}

.admin-threads-tab__summary {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.48);
}

.admin-threads-tab__summary strong {
  color: #f8fafc;
}

.admin-threads-tab__state {
  padding: 26px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.48);
  color: #94a3b8;
}

.admin-threads-tab__list {
  display: grid;
  gap: 12px;
}

.admin-thread-card {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr) auto;
  gap: 16px;
  align-items: start;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.48);
}

.admin-thread-card__avatar {
  width: 52px;
  height: 52px;
  overflow: hidden;
  border-radius: 16px;
  background: rgba(37, 99, 235, 0.16);
  color: #bfdbfe;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 900;
}

.admin-thread-card__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.admin-thread-card__body {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.admin-thread-card__top {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: start;
}

.admin-thread-card h4 {
  margin: 0 0 5px;
  color: #f8fafc;
  font-size: 17px;
}

.admin-thread-card p {
  margin: 0;
}

.admin-thread-card__top p,
.admin-thread-card__content,
.admin-thread-card__meta {
  color: #94a3b8;
  line-height: 1.5;
}

.admin-thread-card__top p span {
  margin: 0 6px;
  color: #475569;
}

.admin-thread-card__badge {
  flex: 0 0 auto;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.16);
  color: #93c5fd;
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
}

.admin-thread-card__content {
  display: -webkit-box;
  overflow: hidden;
  white-space: pre-wrap;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.admin-thread-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  font-size: 12px;
  color: #64748b;
}

.admin-thread-card__actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.admin-thread-card__button {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  border: none;
}

.admin-thread-card__button--danger {
  background: linear-gradient(135deg, #dc2626 0%, #f97316 100%);
}

.admin-threads-tab__pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 14px;
}

.admin-threads-tab__pagination span {
  color: #cbd5e1;
  font-weight: 800;
}

@media (max-width: 860px) {
  .admin-threads-tab__header,
  .admin-threads-tab__summary,
  .admin-thread-card__top {
    flex-direction: column;
    align-items: flex-start;
  }

  .admin-threads-tab__filters {
    grid-template-columns: 1fr;
  }

  .admin-thread-card {
    grid-template-columns: 52px minmax(0, 1fr);
  }

  .admin-thread-card__actions {
    grid-column: 1 / -1;
    justify-content: stretch;
  }

  .admin-thread-card__button {
    width: 100%;
  }
}

@media (max-width: 560px) {
  .admin-thread-card {
    grid-template-columns: 1fr;
  }

  .admin-thread-card__actions,
  .admin-threads-tab__pagination {
    display: grid;
    grid-template-columns: 1fr;
  }

  .admin-threads-tab__pagination button {
    width: 100%;
  }
}
</style>