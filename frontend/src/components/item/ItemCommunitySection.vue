<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useAuth } from '../../services/auth'
import type { Comment, CommentBase } from '../../types/comment'
import ItemCommentCard from './ItemCommentCard.vue'
import ConfirmModal from '../common/ConfirmModal.vue'
import ForumPagination from '../forum/ForumPagination.vue'
import {
  createItemComment,
  deleteItemComment,
  getItemComments,
  updateItemComment,
} from '../../services/comments'
import { deleteAdminComment } from '../../services/admin'
import { parseApiDate } from '../../utils/forumTime'
import { useRoute } from 'vue-router'

const props = defineProps<{
  itemId: string
}>()

const emit = defineEmits<{
  (e: 'changed'): void
}>()

const { authState, isLoggedIn } = useAuth()
const route = useRoute()

const comments = ref<Comment[]>([])
const isLoading = ref(true)
const errorText = ref('')
const commentText = ref('')
const isSubmitting = ref(false)
const replyTarget = ref<{ id: string; username: string } | null>(null)
const composerTextarea = ref<HTMLTextAreaElement | null>(null)
const commentToDelete = ref<CommentBase | null>(null)
const isDeletingComment = ref(false)

const openReplyGroups = ref<string[]>([])
const currentCommentsPage = ref(1)
const commentsPerPage = 15
const commentSort = ref<'oldest' | 'newest'>('oldest')

const topLevelCount = computed(() => comments.value.length)
const isAdmin = computed(() => authState.user?.role === 'admin')

async function loadComments() {
  isLoading.value = true
  errorText.value = ''

  let shouldScrollToRouteComment = false

  try {
    comments.value = await getItemComments(props.itemId, 100)
    openReplyGroups.value = []
    shouldScrollToRouteComment = true
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load comments.'
    comments.value = []
  } finally {
    isLoading.value = false
  }

  if (shouldScrollToRouteComment) {
    await scrollToCommentFromRoute()
  }
}

function isRepliesOpen(commentId: string): boolean {
  return openReplyGroups.value.includes(commentId)
}

function toggleReplies(commentId: string) {
  if (isRepliesOpen(commentId)) {
    openReplyGroups.value = openReplyGroups.value.filter((id) => id !== commentId)
    return
  }

  openReplyGroups.value = [...openReplyGroups.value, commentId]
}

function wait(ms: number) {
  return new Promise<void>((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

async function waitForElementById(
  elementId: string,
  attempts = 14,
): Promise<HTMLElement | null> {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    await nextTick()

    const element = document.getElementById(elementId)

    if (element) {
      return element
    }

    await wait(60)
  }

  return null
}

function findParentCommentId(targetCommentId: string): string | null {
  for (const comment of comments.value) {
    if (comment.id === targetCommentId) {
      return comment.id
    }

    if (comment.replies.some((reply) => reply.id === targetCommentId)) {
      return comment.id
    }
  }

  return null
}

function findTopLevelCommentPage(commentId: string): number {
  const index = sortedComments.value.findIndex((comment) => comment.id === commentId)

  if (index === -1) {
    return currentCommentsPage.value
  }

  return Math.floor(index / commentsPerPage) + 1
}

async function scrollToCommentFromRoute() {
  const commentId = route.query.commentId

  if (typeof commentId !== 'string' || !commentId.trim()) {
    return
  }

  const parentCommentId = findParentCommentId(commentId)

  if (!parentCommentId) {
    return
  }

  currentCommentsPage.value = findTopLevelCommentPage(parentCommentId)

  if (!isRepliesOpen(parentCommentId)) {
    openReplyGroups.value = [...openReplyGroups.value, parentCommentId]
  }

  const target = await waitForElementById(`comment-${commentId}`)

  if (!target) {
    return
  }

  target.scrollIntoView({
    behavior: 'smooth',
    block: 'center',
  })

  target.classList.add('item-community__highlighted-comment')

  window.setTimeout(() => {
    target.classList.remove('item-community__highlighted-comment')
  }, 2400)
}

const sortedComments = computed(() => {
  const items = [...comments.value]

  items.sort((a, b) => {
    const timeA = parseApiDate(a.created_at).getTime()
    const timeB = parseApiDate(b.created_at).getTime()

    if (commentSort.value === 'newest') {
      return timeB - timeA
    }

    return timeA - timeB
  })

  return items
})

const totalCommentPages = computed(() => {
  return Math.max(1, Math.ceil(sortedComments.value.length / commentsPerPage))
})

const paginatedComments = computed(() => {
  const start = (currentCommentsPage.value - 1) * commentsPerPage
  return sortedComments.value.slice(start, start + commentsPerPage)
})

function startReply(comment: CommentBase) {
  replyTarget.value = {
    id: comment.id,
    username: comment.author_username,
  }

  composerTextarea.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'center',
  })

  composerTextarea.value?.focus()
}

function cancelReply() {
  replyTarget.value = null
}

async function handleSubmitComment() {
  errorText.value = ''

  if (!isLoggedIn.value) {
    errorText.value = 'You need to log in to comment.'
    return
  }

  if (!commentText.value.trim()) {
    return
  }

  isSubmitting.value = true

  try {
    const payload: {
      text: string
      reply_to_comment_id?: string
    } = {
      text: commentText.value.trim(),
    }

    if (replyTarget.value) {
      payload.reply_to_comment_id = replyTarget.value.id
    }

    await createItemComment(props.itemId, payload)

    commentText.value = ''
    replyTarget.value = null
    await loadComments()
    currentCommentsPage.value = 1
    emit('changed')
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to create comment.'
  } finally {
    isSubmitting.value = false
  }
}

async function handleSaveEdit(payload: { commentId: string; text: string }) {
  try {
    await updateItemComment(payload.commentId, {
      text: payload.text,
    })

    await loadComments()
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to update comment.'
  }
}

function findCommentById(commentId: string): CommentBase | null {
  for (const comment of comments.value) {
    if (comment.id === commentId) {
      return comment
    }

    const reply = comment.replies.find((item) => item.id === commentId)

    if (reply) {
      return reply
    }
  }

  return null
}

function handleDeleteComment(commentId: string) {
  const targetComment = findCommentById(commentId)

  if (!targetComment) {
    errorText.value = 'Comment was not found.'
    return
  }

  commentToDelete.value = targetComment
}

function cancelDeleteComment() {
  if (isDeletingComment.value) {
    return
  }

  commentToDelete.value = null
}

async function confirmDeleteComment() {
  if (!commentToDelete.value) {
    return
  }

  isDeletingComment.value = true
  errorText.value = ''

  try {
    if (isAdmin.value) {
      await deleteAdminComment(commentToDelete.value.id)
    } else {
      await deleteItemComment(commentToDelete.value.id)
    }

    commentToDelete.value = null
    await loadComments()
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to delete comment.'
  } finally {
    isDeletingComment.value = false
  }
}

watch(
  () => props.itemId,
  () => {
    currentCommentsPage.value = 1
    loadComments()
  },
)

watch(
  () => [route.query.commentId, route.query.focus],
  async () => {
    if (isLoading.value || !comments.value.length) {
      return
    }

    await scrollToCommentFromRoute()
  },
)

watch(commentSort, () => {
  currentCommentsPage.value = 1
})

watch(totalCommentPages, (pages) => {
  if (currentCommentsPage.value > pages) {
    currentCommentsPage.value = pages
  }
})

onMounted(() => {
  loadComments()
})
</script>

<template>
  <section class="item-community">
    <div class="item-community__head">
      <div>
        <h2 class="item-community__title">Community Discussion</h2>
        <p class="item-community__subtitle">
          {{ topLevelCount }} top-level comments
        </p>
      </div>

      <label class="item-community__sort">
        <span>Sort by</span>
        <select v-model="commentSort">
          <option value="oldest">Oldest first</option>
          <option value="newest">Newest first</option>
        </select>
      </label>
    </div>

    <section class="item-community__composer">
      <div class="item-community__composer-head">
        <h3>Write a Comment</h3>
        <span v-if="authState.user">Posting as {{ authState.user.username }}</span>
      </div>

      <p v-if="!isLoggedIn" class="item-community__login-note">
        Log in to join the discussion.
      </p>

      <div v-if="replyTarget" class="item-community__reply-target">
        <span>Replying to @{{ replyTarget.username }}</span>
        <button type="button" @click="cancelReply">Cancel</button>
      </div>

      <textarea
        ref="composerTextarea"
        v-model="commentText"
        rows="5"
        placeholder="Share your thoughts about this item..."
      />

      <div class="item-community__composer-footer">
        <p v-if="errorText" class="item-community__error">
          {{ errorText }}
        </p>

        <button
          type="button"
          class="item-community__submit"
          :disabled="isSubmitting || !isLoggedIn"
          @click="handleSubmitComment"
        >
          {{ isSubmitting ? 'Posting...' : 'Post Comment' }}
        </button>
      </div>
    </section>

    <div v-if="isLoading" class="item-community__state">
      Loading comments...
    </div>

    <div
      v-else-if="!isLoading && !comments.length"
      class="item-community__state"
    >
      No comments yet. Be the first to start the discussion.
    </div>

    <div v-else class="item-community__list">
        <div
          v-for="comment in paginatedComments"
          :id="`comment-${comment.id}`"
          :key="comment.id"
          class="item-community__thread"
        >
        <ItemCommentCard
          :comment="comment"
          @reply="startReply"
          @save-edit="handleSaveEdit"
          @delete="handleDeleteComment"
        />

        <button
          v-if="comment.replies.length"
          type="button"
          class="item-community__toggle-replies"
          @click="toggleReplies(comment.id)"
        >
          {{
            isRepliesOpen(comment.id)
              ? `Hide replies (${comment.replies.length})`
              : `Show replies (${comment.replies.length})`
          }}
        </button>

        <div
          v-if="comment.replies.length && isRepliesOpen(comment.id)"
          class="item-community__replies"
        >
        <div
          v-for="reply in comment.replies"
          :id="`comment-${reply.id}`"
          :key="reply.id"
        >
          <ItemCommentCard
            :comment="reply"
            is-reply
            @reply="startReply"
            @save-edit="handleSaveEdit"
            @delete="handleDeleteComment"
          />
        </div>
        </div>
      </div>

      <div v-if="totalCommentPages > 1" class="item-community__pagination">
        <ForumPagination
          :current-page="currentCommentsPage"
          :total-pages="totalCommentPages"
          @update:page="currentCommentsPage = $event"
        />
      </div>
    </div>

    <ConfirmModal
      :open="Boolean(commentToDelete)"
      title="Delete comment?"
      :message="`This will permanently delete the comment by ${commentToDelete?.author_username || 'this user'}. This action cannot be undone.`"
      confirm-label="Delete comment"
      cancel-label="Cancel"
      :is-busy="isDeletingComment"
      @confirm="confirmDeleteComment"
      @cancel="cancelDeleteComment"
    />

  </section>
</template>

<style scoped>
.item-community {
  display: grid;
  gap: 22px;
}

.item-community__head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.item-community__title {
  margin: 0 0 6px;
  color: #f8fafc;
  font-size: 34px;
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.item-community__subtitle {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

.item-community__sort {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-community__sort span {
  color: #94a3b8;
  font-size: 13px;
}

.item-community__sort select {
  min-width: 150px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  padding: 0 12px;
  outline: none;
}

.item-community__composer {
  display: grid;
  gap: 14px;
  padding: 22px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
}

.item-community__composer-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.item-community__composer-head h3 {
  margin: 0;
  color: #f8fafc;
  font-size: 24px;
}

.item-community__composer-head span,
.item-community__login-note {
  color: #94a3b8;
  font-size: 14px;
}

.item-community__reply-target {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
  color: #60a5fa;
  font-size: 14px;
}

.item-community__reply-target button {
  border: none;
  background: transparent;
  color: #cbd5e1;
  cursor: pointer;
  font-weight: 700;
}

.item-community__composer textarea {
  width: 100%;
  min-height: 170px;
  resize: vertical;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  outline: none;
}

.item-community__composer-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.item-community__error {
  margin: 0;
  color: #fca5a5;
  font-size: 14px;
}

.item-community__submit {
  min-height: 44px;
  padding: 0 18px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
}

.item-community__submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.item-community__state {
  padding: 24px;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
  color: #94a3b8;
}

.item-community__list,
.item-community__thread,
.item-community__replies {
  display: grid;
}

.item-community__thread,
.item-community__replies > div {
  scroll-margin-top: 120px;
}

.item-community__toggle-replies {
  justify-self: start;
  margin: -2px 0 8px 0;
  border: none;
  background: transparent;
  color: #60a5fa;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  padding: 0;
}

.item-community__pagination {
  padding-top: 12px;
}

.item-community__highlighted-comment {
  border-radius: 18px;
  outline: 2px solid rgba(96, 165, 250, 0.65);
  outline-offset: 8px;
  transition: outline-color 0.25s ease;
}
@media (max-width: 700px) {
  .item-community__head,
  .item-community__composer-head,
  .item-community__composer-footer,
  .item-community__reply-target {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>