<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  deleteAdminForumPost,
  getAdminForumPosts,
} from '../../services/admin'
import type { AdminForumPost } from '../../types/admin'
import { getAvatarImageUrl } from '../../utils/avatars'
import ConfirmModal from '../common/ConfirmModal.vue'

const emit = defineEmits<{
  (event: 'close'): void
}>()

const router = useRouter()

const PAGE_SIZE = 20
const SEARCH_DEBOUNCE_MS = 450

const posts = ref<AdminForumPost[]>([])
const searchInput = ref('')
const skip = ref(0)
const total = ref(0)

const isLoading = ref(false)
const isDeleting = ref(false)
const errorText = ref('')
const successText = ref('')

const postToDelete = ref<AdminForumPost | null>(null)

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

function getPostPreview(post: AdminForumPost): string {
  const content = post.content.trim()

  if (!content) {
    return 'No content.'
  }

  return content
}

async function loadPosts() {
  isLoading.value = true
  errorText.value = ''

  try {
    const response = await getAdminForumPosts({
      search: searchTerm.value || undefined,
      limit: PAGE_SIZE,
      skip: skip.value,
    })

    posts.value = response.results
    total.value = response.total
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load forum posts.'
    posts.value = []
    total.value = 0
  } finally {
    isLoading.value = false
  }
}

function scheduleReload() {
  window.clearTimeout(searchTimeoutId)

  searchTimeoutId = window.setTimeout(() => {
    skip.value = 0
    loadPosts()
  }, SEARCH_DEBOUNCE_MS)
}

function goToPage(page: number) {
  const safePage = Math.min(Math.max(page, 1), totalPages.value)
  skip.value = (safePage - 1) * PAGE_SIZE
  loadPosts()
}

function openPost(post: AdminForumPost) {
  emit('close')

  router.push({
    path: `/forum/threads/${post.thread_id}`,
    query: {
      postId: post.id,
      focus: String(Date.now()),
    },
  })
}

function requestDelete(post: AdminForumPost) {
  successText.value = ''
  errorText.value = ''
  postToDelete.value = post
}

function cancelDelete() {
  if (isDeleting.value) {
    return
  }

  postToDelete.value = null
}

async function confirmDelete() {
  if (!postToDelete.value) {
    return
  }

  isDeleting.value = true
  errorText.value = ''
  successText.value = ''

  try {
    await deleteAdminForumPost(postToDelete.value.id)

    successText.value = 'Forum post deleted.'
    postToDelete.value = null

    const isLastItemOnPage = posts.value.length === 1 && skip.value > 0

    if (isLastItemOnPage) {
      skip.value = Math.max(0, skip.value - PAGE_SIZE)
    }

    await loadPosts()
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to delete forum post.'
  } finally {
    isDeleting.value = false
  }
}

watch(searchInput, () => {
  scheduleReload()
})

onMounted(() => {
  loadPosts()
})
</script>

<template>
  <section class="admin-posts-tab">
    <header class="admin-posts-tab__header">
      <div>
        <p class="admin-posts-tab__eyebrow">Forum Posts</p>
        <h3>Forum Posts & Replies</h3>
        <span>
          Search forum posts across all threads and moderate inappropriate replies.
        </span>
      </div>

      <button
        type="button"
        class="admin-posts-tab__refresh"
        :disabled="isLoading"
        @click="loadPosts"
      >
        {{ isLoading ? 'Loading...' : 'Refresh' }}
      </button>
    </header>

    <div class="admin-posts-tab__filters">
      <label class="admin-posts-tab__field">
        <span>Search</span>
        <input
          v-model="searchInput"
          type="search"
          placeholder="Search by post text or username..."
          autocomplete="off"
        />
      </label>
    </div>

    <p v-if="searchHint" class="admin-posts-tab__hint">
      {{ searchHint }}
    </p>

    <p v-if="errorText" class="admin-posts-tab__error">
      {{ errorText }}
    </p>

    <p v-if="successText" class="admin-posts-tab__success">
      {{ successText }}
    </p>

    <div class="admin-posts-tab__summary">
      <span>
        Page {{ currentPage }} of {{ totalPages }}
      </span>

      <strong>
        {{ total }} total posts
      </strong>
    </div>

    <div v-if="isLoading" class="admin-posts-tab__state">
      Loading forum posts...
    </div>

    <div v-else-if="posts.length === 0" class="admin-posts-tab__state">
      No forum posts found.
    </div>

    <div v-else class="admin-posts-tab__list">
      <article
        v-for="post in posts"
        :key="post.id"
        class="admin-post-card"
      >
        <div class="admin-post-card__avatar">
          <img
            v-if="getAvatarImageUrl(post.author_avatar_id)"
            :src="getAvatarImageUrl(post.author_avatar_id) || undefined"
            :alt="post.author_username"
          />

          <span v-else>{{ getAuthorInitial(post.author_username) }}</span>
        </div>

        <div class="admin-post-card__body">
          <div class="admin-post-card__top">
            <div>
              <h4>{{ post.author_username }}</h4>

              <p>
                {{ post.thread_title || 'Unknown thread' }}
                <span>•</span>
                {{ formatDate(post.created_at) }}
              </p>
            </div>

            <span
              v-if="post.parent_post_id"
              class="admin-post-card__badge"
            >
              Reply
            </span>
          </div>

          <p
            v-if="post.reply_to_username"
            class="admin-post-card__reply-to"
          >
            Reply to @{{ post.reply_to_username }}
          </p>

          <p class="admin-post-card__content">
            {{ getPostPreview(post) }}
          </p>

          <div class="admin-post-card__meta">
            <span>Post ID: {{ post.id }}</span>
            <span>Thread ID: {{ post.thread_id }}</span>
            <span>User ID: {{ post.user_id }}</span>
            <span>Votes: {{ post.votes_count }}</span>
          </div>
        </div>

        <div class="admin-post-card__actions">
          <button
            type="button"
            class="admin-post-card__button"
            @click="openPost(post)"
          >
            Open
          </button>

          <button
            type="button"
            class="admin-post-card__button admin-post-card__button--danger"
            @click="requestDelete(post)"
          >
            Delete
          </button>
        </div>
      </article>
    </div>

    <footer class="admin-posts-tab__pagination">
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
      :open="Boolean(postToDelete)"
      title="Delete forum post?"
      :message="`This will permanently delete the post by ${postToDelete?.author_username || 'this user'}. This action cannot be undone.`"
      confirm-label="Delete post"
      cancel-label="Cancel"
      :is-busy="isDeleting"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </section>
</template>

<style scoped>
.admin-posts-tab {
  display: grid;
  gap: 18px;
}

.admin-posts-tab__header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: start;
}

.admin-posts-tab__eyebrow {
  margin: 0 0 8px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.admin-posts-tab__header h3 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 30px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.admin-posts-tab__header span,
.admin-posts-tab__hint,
.admin-posts-tab__summary span {
  color: #94a3b8;
  line-height: 1.6;
}

.admin-posts-tab__refresh,
.admin-post-card__button,
.admin-posts-tab__pagination button {
  min-height: 40px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #ffffff;
  font-weight: 800;
  cursor: pointer;
}

.admin-posts-tab__refresh:disabled,
.admin-posts-tab__pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.admin-posts-tab__filters {
  display: grid;
  gap: 14px;
}

.admin-posts-tab__field {
  display: grid;
  gap: 8px;
}

.admin-posts-tab__field span {
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 800;
}

.admin-posts-tab__field input {
  width: 100%;
  min-height: 44px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  outline: none;
}

.admin-posts-tab__field input:focus {
  border-color: rgba(96, 165, 250, 0.55);
}

.admin-posts-tab__error,
.admin-posts-tab__success {
  margin: 0;
  padding: 14px 16px;
  border-radius: 14px;
  font-weight: 700;
}

.admin-posts-tab__error {
  background: rgba(239, 68, 68, 0.12);
  color: #fca5a5;
}

.admin-posts-tab__success {
  background: rgba(34, 197, 94, 0.12);
  color: #86efac;
}

.admin-posts-tab__summary {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.48);
}

.admin-posts-tab__summary strong {
  color: #f8fafc;
}

.admin-posts-tab__state {
  padding: 26px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.48);
  color: #94a3b8;
}

.admin-posts-tab__list {
  display: grid;
  gap: 12px;
}

.admin-post-card {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr) auto;
  gap: 16px;
  align-items: start;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.48);
}

.admin-post-card__avatar {
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

.admin-post-card__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.admin-post-card__body {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.admin-post-card__top {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: start;
}

.admin-post-card h4 {
  margin: 0 0 5px;
  color: #f8fafc;
  font-size: 17px;
}

.admin-post-card p {
  margin: 0;
}

.admin-post-card__top p,
.admin-post-card__content,
.admin-post-card__reply-to,
.admin-post-card__meta {
  color: #94a3b8;
  line-height: 1.5;
}

.admin-post-card__top p span {
  margin: 0 6px;
  color: #475569;
}

.admin-post-card__badge {
  flex: 0 0 auto;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.16);
  color: #93c5fd;
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
}

.admin-post-card__reply-to {
  font-size: 13px;
  color: #bfdbfe;
}

.admin-post-card__content {
  white-space: pre-wrap;
}

.admin-post-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  font-size: 12px;
  color: #64748b;
}

.admin-post-card__actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.admin-post-card__button {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  border: none;
}

.admin-post-card__button--danger {
  background: linear-gradient(135deg, #dc2626 0%, #f97316 100%);
}

.admin-posts-tab__pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 14px;
}

.admin-posts-tab__pagination span {
  color: #cbd5e1;
  font-weight: 800;
}

@media (max-width: 860px) {
  .admin-posts-tab__header,
  .admin-posts-tab__summary,
  .admin-post-card__top {
    flex-direction: column;
    align-items: flex-start;
  }

  .admin-post-card {
    grid-template-columns: 52px minmax(0, 1fr);
  }

  .admin-post-card__actions {
    grid-column: 1 / -1;
    justify-content: stretch;
  }

  .admin-post-card__button {
    width: 100%;
  }
}

@media (max-width: 560px) {
  .admin-post-card {
    grid-template-columns: 1fr;
  }

  .admin-post-card__actions,
  .admin-posts-tab__pagination {
    display: grid;
    grid-template-columns: 1fr;
  }

  .admin-posts-tab__pagination button {
    width: 100%;
  }
}
</style>