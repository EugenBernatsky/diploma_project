<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { deleteAdminComment, getAdminComments } from '../../services/admin'
import type { AdminComment } from '../../types/admin'
import { getAvatarImageUrl } from '../../utils/avatars'
import ConfirmModal from '../common/ConfirmModal.vue'

const emit = defineEmits<{
  (event: 'close'): void
}>()

const router = useRouter()

const PAGE_SIZE = 20
const SEARCH_DEBOUNCE_MS = 450

const comments = ref<AdminComment[]>([])
const searchInput = ref('')
const skip = ref(0)
const total = ref(0)

const isLoading = ref(false)
const isDeleting = ref(false)
const errorText = ref('')
const successText = ref('')

const commentToDelete = ref<AdminComment | null>(null)

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

function getCommentPreview(comment: AdminComment): string {
  const content = comment.content.trim()

  if (!content) {
    return 'No content.'
  }

  return content
}

async function loadComments() {
  isLoading.value = true
  errorText.value = ''

  try {
    const response = await getAdminComments({
      search: searchTerm.value || undefined,
      limit: PAGE_SIZE,
      skip: skip.value,
    })

    comments.value = response.results
    total.value = response.total
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load admin comments.'
    comments.value = []
    total.value = 0
  } finally {
    isLoading.value = false
  }
}

function scheduleReload() {
  window.clearTimeout(searchTimeoutId)

  searchTimeoutId = window.setTimeout(() => {
    skip.value = 0
    loadComments()
  }, SEARCH_DEBOUNCE_MS)
}

function goToPage(page: number) {
  const safePage = Math.min(Math.max(page, 1), totalPages.value)
  skip.value = (safePage - 1) * PAGE_SIZE
  loadComments()
}

function openComment(comment: AdminComment) {
  emit('close')

  router.push({
    path: `/items/${comment.item_id}`,
    query: {
      commentId: comment.id,
      focus: String(Date.now()),
    },
  })
}

function requestDelete(comment: AdminComment) {
  successText.value = ''
  errorText.value = ''
  commentToDelete.value = comment
}

function cancelDelete() {
  if (isDeleting.value) {
    return
  }

  commentToDelete.value = null
}

async function confirmDelete() {
  if (!commentToDelete.value) {
    return
  }

  isDeleting.value = true
  errorText.value = ''
  successText.value = ''

  try {
    await deleteAdminComment(commentToDelete.value.id)

    successText.value = 'Comment deleted.'
    commentToDelete.value = null

    const isLastItemOnPage = comments.value.length === 1 && skip.value > 0

    if (isLastItemOnPage) {
      skip.value = Math.max(0, skip.value - PAGE_SIZE)
    }

    await loadComments()
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to delete comment.'
  } finally {
    isDeleting.value = false
  }
}

watch(searchInput, () => {
  scheduleReload()
})

onMounted(() => {
  loadComments()
})
</script>

<template>
  <section class="admin-comments-tab">
    <header class="admin-comments-tab__header">
      <div>
        <p class="admin-comments-tab__eyebrow">Comments</p>
        <h3>Item Comments</h3>
        <span>
          Search comments across all item pages and moderate inappropriate content.
        </span>
      </div>

      <button
        type="button"
        class="admin-comments-tab__refresh"
        :disabled="isLoading"
        @click="loadComments"
      >
        {{ isLoading ? 'Loading...' : 'Refresh' }}
      </button>
    </header>

    <div class="admin-comments-tab__filters">
      <label class="admin-comments-tab__field">
        <span>Search</span>
        <input
          v-model="searchInput"
          type="search"
          placeholder="Search by comment text or username..."
          autocomplete="off"
        />
      </label>
    </div>

    <p v-if="searchHint" class="admin-comments-tab__hint">
      {{ searchHint }}
    </p>

    <p v-if="errorText" class="admin-comments-tab__error">
      {{ errorText }}
    </p>

    <p v-if="successText" class="admin-comments-tab__success">
      {{ successText }}
    </p>

    <div class="admin-comments-tab__summary">
      <span>
        Page {{ currentPage }} of {{ totalPages }}
      </span>

      <strong>
        {{ total }} total comments
      </strong>
    </div>

    <div v-if="isLoading" class="admin-comments-tab__state">
      Loading comments...
    </div>

    <div v-else-if="comments.length === 0" class="admin-comments-tab__state">
      No comments found.
    </div>

    <div v-else class="admin-comments-tab__list">
      <article
        v-for="comment in comments"
        :key="comment.id"
        class="admin-comment-card"
      >
        <div class="admin-comment-card__avatar">
          <img
            v-if="getAvatarImageUrl(comment.author_avatar_id)"
            :src="getAvatarImageUrl(comment.author_avatar_id) || undefined"
            :alt="comment.author_username"
          />

          <span v-else>{{ getAuthorInitial(comment.author_username) }}</span>
        </div>

        <div class="admin-comment-card__body">
          <div class="admin-comment-card__top">
            <div>
              <h4>{{ comment.author_username }}</h4>

              <p>
                {{ comment.item_title || 'Unknown item' }}
                <span>•</span>
                {{ formatDate(comment.created_at) }}
              </p>
            </div>

            <span
              v-if="comment.parent_comment_id"
              class="admin-comment-card__badge"
            >
              Reply
            </span>
          </div>

          <p
            v-if="comment.reply_to_username"
            class="admin-comment-card__reply-to"
          >
            Reply to @{{ comment.reply_to_username }}
          </p>

          <p class="admin-comment-card__content">
            {{ getCommentPreview(comment) }}
          </p>

          <div class="admin-comment-card__meta">
            <span>Comment ID: {{ comment.id }}</span>
            <span>User ID: {{ comment.user_id }}</span>
            <span>Item ID: {{ comment.item_id }}</span>
          </div>
        </div>

        <div class="admin-comment-card__actions">
          <button
            type="button"
            class="admin-comment-card__button"
            @click="openComment(comment)"
          >
            Open
          </button>

          <button
            type="button"
            class="admin-comment-card__button admin-comment-card__button--danger"
            @click="requestDelete(comment)"
          >
            Delete
          </button>
        </div>
      </article>
    </div>

    <footer class="admin-comments-tab__pagination">
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
      :open="Boolean(commentToDelete)"
      title="Delete comment?"
      :message="`This will permanently delete the comment by ${commentToDelete?.author_username || 'this user'}. This action cannot be undone.`"
      confirm-label="Delete comment"
      cancel-label="Cancel"
      :is-busy="isDeleting"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </section>
</template>

<style scoped>
.admin-comments-tab {
  display: grid;
  gap: 18px;
}

.admin-comments-tab__header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: start;
}

.admin-comments-tab__eyebrow {
  margin: 0 0 8px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.admin-comments-tab__header h3 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 30px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.admin-comments-tab__header span,
.admin-comments-tab__hint,
.admin-comments-tab__summary span {
  color: #94a3b8;
  line-height: 1.6;
}

.admin-comments-tab__refresh,
.admin-comment-card__button,
.admin-comments-tab__pagination button {
  min-height: 40px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #ffffff;
  font-weight: 800;
  cursor: pointer;
}

.admin-comments-tab__refresh:disabled,
.admin-comments-tab__pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.admin-comments-tab__filters {
  display: grid;
  gap: 14px;
}

.admin-comments-tab__field {
  display: grid;
  gap: 8px;
}

.admin-comments-tab__field span {
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 800;
}

.admin-comments-tab__field input {
  width: 100%;
  min-height: 44px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  outline: none;
}

.admin-comments-tab__field input:focus {
  border-color: rgba(96, 165, 250, 0.55);
}

.admin-comments-tab__error,
.admin-comments-tab__success {
  margin: 0;
  padding: 14px 16px;
  border-radius: 14px;
  font-weight: 700;
}

.admin-comments-tab__error {
  background: rgba(239, 68, 68, 0.12);
  color: #fca5a5;
}

.admin-comments-tab__success {
  background: rgba(34, 197, 94, 0.12);
  color: #86efac;
}

.admin-comments-tab__summary {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.48);
}

.admin-comments-tab__summary strong {
  color: #f8fafc;
}

.admin-comments-tab__state {
  padding: 26px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.48);
  color: #94a3b8;
}

.admin-comments-tab__list {
  display: grid;
  gap: 12px;
}

.admin-comment-card {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr) auto;
  gap: 16px;
  align-items: start;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.48);
}

.admin-comment-card__avatar {
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

.admin-comment-card__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.admin-comment-card__body {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.admin-comment-card__top {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: start;
}

.admin-comment-card h4 {
  margin: 0 0 5px;
  color: #f8fafc;
  font-size: 17px;
}

.admin-comment-card p {
  margin: 0;
}

.admin-comment-card__top p,
.admin-comment-card__content,
.admin-comment-card__reply-to,
.admin-comment-card__meta {
  color: #94a3b8;
  line-height: 1.5;
}

.admin-comment-card__top p span {
  margin: 0 6px;
  color: #475569;
}

.admin-comment-card__badge {
  flex: 0 0 auto;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.16);
  color: #93c5fd;
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
}

.admin-comment-card__reply-to {
  font-size: 13px;
  color: #bfdbfe;
}

.admin-comment-card__content {
  white-space: pre-wrap;
}

.admin-comment-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  font-size: 12px;
  color: #64748b;
}

.admin-comment-card__actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.admin-comment-card__button {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  border: none;
}

.admin-comment-card__button--danger {
  background: linear-gradient(135deg, #dc2626 0%, #f97316 100%);
}

.admin-comments-tab__pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 14px;
}

.admin-comments-tab__pagination span {
  color: #cbd5e1;
  font-weight: 800;
}

@media (max-width: 860px) {
  .admin-comments-tab__header,
  .admin-comments-tab__summary,
  .admin-comment-card__top {
    flex-direction: column;
    align-items: flex-start;
  }

  .admin-comment-card {
    grid-template-columns: 52px minmax(0, 1fr);
  }

  .admin-comment-card__actions {
    grid-column: 1 / -1;
    justify-content: stretch;
  }

  .admin-comment-card__button {
    width: 100%;
  }
}

@media (max-width: 560px) {
  .admin-comment-card {
    grid-template-columns: 1fr;
  }

  .admin-comment-card__actions,
  .admin-comments-tab__pagination {
    display: grid;
    grid-template-columns: 1fr;
  }

  .admin-comments-tab__pagination button {
    width: 100%;
  }
}
</style>