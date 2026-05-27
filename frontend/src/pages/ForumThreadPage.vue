<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import ForumPagination from '../components/forum/ForumPagination.vue'
import ForumPostCard from '../components/forum/ForumPostCard.vue'
import { useAuth } from '../services/auth'
import {
  createForumPost,
  deleteForumPost,
  deleteForumThread,
  getForumPosts,
  getForumThread,
  getMyPostVote,
  getMyThreadVote,
  updateForumPost,
  updateForumThread,
  voteForumPost,
  voteForumThread,
} from '../services/forum'
import type { ForumPostBaseResponse, ForumPostResponse, ForumThreadResponse } from '../types/forum'
import { formatRelativeTime, parseApiDate } from '../utils/forumTime'
import ConfirmModal from '../components/common/ConfirmModal.vue'
import {
  deleteAdminForumPost,
  deleteAdminForumThread,
} from '../services/admin'

const route = useRoute()
const router = useRouter()
const { authState, isLoggedIn } = useAuth()

const thread = ref<ForumThreadResponse | null>(null)
const posts = ref<ForumPostResponse[]>([])
const isLoading = ref(true)
const errorText = ref('')

const isThreadDeleteRequested = ref(false)
const postToDelete = ref<{
  id: string
  authorUsername: string
} | null>(null)

const isDeletingThread = ref(false)
const isDeletingPost = ref(false)

const composerText = ref('')
const replyTarget = ref<{ id: string; username: string } | null>(null)
const isSubmitting = ref(false)
const isThreadVoting = ref(false)
const openReplyGroups = ref<string[]>([])
const currentPostsPage = ref(1)
const composerTextarea = ref<HTMLTextAreaElement | null>(null)

const threadMyVote = ref<1 | -1 | 0>(0)
const postVoteMap = ref<Record<string, 1 | -1 | 0>>({})

const postSort = ref<'oldest' | 'newest'>('oldest')

const isEditingThread = ref(false)
const threadEditTitle = ref('')
const threadEditText = ref('')

const threadId = computed(() => String(route.params.id ?? ''))
const postsPerPage = 20

function formatCategoryLabel(thread: ForumThreadResponse): string {
  if (thread.category_type === 'movie') return 'Movies'
  if (thread.category_type === 'series') return 'TV Series'
  if (thread.category_type === 'book') return 'Books'
  return thread.custom_category?.trim() || 'Custom'
}

function getAuthorInitial(name: string): string {
  return name.trim().charAt(0).toUpperCase() || 'U'
}

const canManageThread = computed(() => {
  return Boolean(thread.value && authState.user?.id === thread.value.user_id)
})

const isAdmin = computed(() => {
  return authState.user?.role === 'admin'
})

const canDeleteThread = computed(() => {
  return canManageThread.value || isAdmin.value
})

const isAdminThreadAction = computed(() => {
  return isAdmin.value && !canManageThread.value
})

function startReplyToPost(post: ForumPostBaseResponse) {
  if (!isLoggedIn.value) {
    errorText.value = 'Log in to reply to posts.'
    return
  }

  replyTarget.value = {
    id: post.id,
    username: post.author_username,
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

function handleReplyToTopic() {
  if (!isLoggedIn.value) {
    errorText.value = 'Log in to reply to this topic.'
    return
  }

  replyTarget.value = null

  composerTextarea.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'center',
  })

  composerTextarea.value?.focus()
}

function isRepliesOpen(postId: string): boolean {
  return openReplyGroups.value.includes(postId)
}

function toggleReplies(postId: string) {
  if (isRepliesOpen(postId)) {
    openReplyGroups.value = openReplyGroups.value.filter((id) => id !== postId)
    return
  }

  openReplyGroups.value = [...openReplyGroups.value, postId]
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

function findParentPostId(targetPostId: string): string | null {
  for (const post of posts.value) {
    if (post.id === targetPostId) {
      return post.id
    }

    if (post.replies.some((reply) => reply.id === targetPostId)) {
      return post.id
    }
  }

  return null
}

function findTopLevelPostPage(postId: string): number {
  const index = sortedTopLevelPosts.value.findIndex((post) => post.id === postId)

  if (index === -1) {
    return currentPostsPage.value
  }

  return Math.floor(index / postsPerPage) + 1
}

async function scrollToPostFromRoute() {
  const postId = route.query.postId

  if (typeof postId !== 'string' || !postId.trim()) {
    return
  }

  const parentPostId = findParentPostId(postId)

  if (!parentPostId) {
    return
  }

  currentPostsPage.value = findTopLevelPostPage(parentPostId)

  if (!isRepliesOpen(parentPostId)) {
    openReplyGroups.value = [...openReplyGroups.value, parentPostId]
  }

  const target = await waitForElementById(`post-${postId}`)

  if (!target) {
    return
  }

  target.scrollIntoView({
    behavior: 'smooth',
    block: 'center',
  })

  target.classList.add('forum-thread-page__highlighted-post')

  window.setTimeout(() => {
    target.classList.remove('forum-thread-page__highlighted-post')
  }, 2400)
}

function getVoteDelta(
  currentVote: 1 | -1 | 0,
  clickedVote: 1 | -1,
): { nextVote: 1 | -1 | 0; delta: number } {
  if (currentVote === clickedVote) {
    return {
      nextVote: 0,
      delta: -currentVote,
    }
  }

  return {
    nextVote: clickedVote,
    delta: clickedVote - currentVote,
  }
}

function patchPostScore(postId: string, delta: number) {
  if (!delta) return

  posts.value = posts.value.map((post) => {
    if (post.id === postId) {
      return {
        ...post,
        score: post.score + delta,
      }
    }

    const hasReply = post.replies.some((reply) => reply.id === postId)
    if (!hasReply) {
      return post
    }

    return {
      ...post,
      replies: post.replies.map((reply) =>
        reply.id === postId
          ? {
              ...reply,
              score: reply.score + delta,
            }
          : reply,
      ),
    }
  })
}

async function loadThreadVoteState() {
  if (!authState.user || !thread.value) {
    threadMyVote.value = 0
    return
  }

  try {
    const result = await getMyThreadVote(thread.value.id)
    threadMyVote.value = result.current_vote ?? 0
  } catch {
    threadMyVote.value = 0
  }
}

const sortedTopLevelPosts = computed(() => {
  const items = [...posts.value]

  items.sort((a, b) => {
    const timeA = parseApiDate(a.created_at).getTime()
    const timeB = parseApiDate(b.created_at).getTime()

    if (postSort.value === 'newest') {
      return timeB - timeA
    }

    return timeA - timeB
  })

  return items
})

const totalPostPages = computed(() => {
  return Math.max(1, Math.ceil(sortedTopLevelPosts.value.length / postsPerPage))
})

const paginatedPosts = computed(() => {
  const start = (currentPostsPage.value - 1) * postsPerPage
  return sortedTopLevelPosts.value.slice(start, start + postsPerPage)
})

const visibleVoteTargetIds = computed(() => {
  const ids: string[] = []

  for (const post of paginatedPosts.value) {
    ids.push(post.id)

    if (isRepliesOpen(post.id)) {
      for (const reply of post.replies) {
        ids.push(reply.id)
      }
    }
  }

  return [...new Set(ids)]
})

async function loadVisiblePostVotes(reset = false) {
  if (reset) {
    postVoteMap.value = {}
  }

  if (!authState.user) {
    postVoteMap.value = {}
    return
  }

  const missingIds = visibleVoteTargetIds.value.filter(
    (id) => !(id in postVoteMap.value),
  )

  if (!missingIds.length) {
    return
  }

  const results = await Promise.allSettled(
    missingIds.map((id) => getMyPostVote(id)),
  )

  const next = { ...postVoteMap.value }

  results.forEach((result, index) => {
    next[missingIds[index]] =
        result.status === 'fulfilled' ? (result.value.current_vote ?? 0) : 0
  })

  postVoteMap.value = next
}

async function loadThreadPage() {
  isLoading.value = true
  errorText.value = ''

  let shouldScrollToRoutePost = false

  try {
    const [threadData, postsData] = await Promise.all([
      getForumThread(threadId.value),
      getForumPosts(threadId.value, 200),
    ])

    thread.value = threadData
    posts.value = postsData
    openReplyGroups.value = []
    postVoteMap.value = {}

    shouldScrollToRoutePost = true

    await loadThreadVoteState()
    await loadVisiblePostVotes(true)
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load thread.'
    thread.value = null
    posts.value = []
  } finally {
    isLoading.value = false
  }

  if (shouldScrollToRoutePost) {
    await scrollToPostFromRoute()
  }
}

async function handleSubmitPost() {
  errorText.value = ''

  if (!isLoggedIn.value) {
    errorText.value = 'Log in to post a reply.'
    return
  }

  if (!composerText.value.trim()) {
    return
  }

  isSubmitting.value = true

  try {
    const payload: { text: string; reply_to_post_id?: string } = {
      text: composerText.value.trim(),
    }

    if (replyTarget.value) {
      payload.reply_to_post_id = replyTarget.value.id
    }

    await createForumPost(threadId.value, payload)

    composerText.value = ''
    replyTarget.value = null
    await loadThreadPage()
    currentPostsPage.value = 1
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to create post.'
  } finally {
    isSubmitting.value = false
  }
}

async function handleVoteThread(value: 1 | -1) {
  if (!thread.value || isThreadVoting.value) return

  if (!isLoggedIn.value) {
    errorText.value = 'Log in to vote.'
    return
  }
  const previousVote = threadMyVote.value
  const { nextVote, delta } = getVoteDelta(previousVote, value)

  isThreadVoting.value = true
  thread.value = {
    ...thread.value,
    score: thread.value.score + delta,
  }
  threadMyVote.value = nextVote

  try {
    const response = await voteForumThread(thread.value.id, { value })
    threadMyVote.value = response.current_vote ?? 0
    thread.value = {
      ...thread.value,
      score: response.score,
    }
  } catch (error) {
    thread.value = {
      ...thread.value,
      score: thread.value.score - delta,
    }
    threadMyVote.value = previousVote
    errorText.value =
      error instanceof Error ? error.message : 'Failed to vote thread.'
  } finally {
    isThreadVoting.value = false
  }
}

async function handleVotePost(payload: { postId: string; value: 1 | -1 }) {
  if (!isLoggedIn.value) {
    errorText.value = 'Log in to vote.'
    return
  }

  const previousVote = postVoteMap.value[payload.postId] ?? 0
  const { nextVote, delta } = getVoteDelta(previousVote, payload.value)

  patchPostScore(payload.postId, delta)
  postVoteMap.value = {
    ...postVoteMap.value,
    [payload.postId]: nextVote,
  }

  try {
    const response = await voteForumPost(payload.postId, { value: payload.value })

    postVoteMap.value = {
      ...postVoteMap.value,
      [payload.postId]: response.current_vote ?? 0,
    }

    // score уже оновили оптимістично, але краще синхронізувати точно
    const actualScore = response.score
    const currentLocalScore = (() => {
      for (const post of posts.value) {
        if (post.id === payload.postId) return post.score
        for (const reply of post.replies) {
          if (reply.id === payload.postId) return reply.score
        }
      }
      return actualScore
    })()

    patchPostScore(payload.postId, actualScore - currentLocalScore)
  } catch (error) {
    patchPostScore(payload.postId, -delta)
    postVoteMap.value = {
      ...postVoteMap.value,
      [payload.postId]: previousVote,
    }
    errorText.value =
      error instanceof Error ? error.message : 'Failed to vote post.'
  }
}

function startThreadEdit() {
  if (!thread.value) return

  threadEditTitle.value = thread.value.title
  threadEditText.value = thread.value.text
  isEditingThread.value = true
}

function cancelThreadEdit() {
  isEditingThread.value = false
  threadEditTitle.value = ''
  threadEditText.value = ''
}

async function saveThreadEdit() {
  if (!thread.value) return

  const nextTitle = threadEditTitle.value.trim()
  const nextText = threadEditText.value.trim()

  if (nextTitle.length < 3) {
    errorText.value = 'Thread title must be at least 3 characters long.'
    return
  }

  if (!nextText) {
    errorText.value = 'Thread text cannot be empty.'
    return
  }

  try {
    const updated = await updateForumThread(thread.value.id, {
      title: nextTitle,
      text: nextText,
      category_type: thread.value.category_type,
      custom_category: thread.value.custom_category,
    })

    thread.value = updated
    isEditingThread.value = false
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to update thread.'
  }
}

function handleDeleteThread() {
  if (!thread.value) {
    return
  }

  isThreadDeleteRequested.value = true
}

function cancelDeleteThread() {
  if (isDeletingThread.value) {
    return
  }

  isThreadDeleteRequested.value = false
}

async function confirmDeleteThread() {
  if (!thread.value) {
    return
  }

  isDeletingThread.value = true
  errorText.value = ''

  try {
    if (isAdmin.value) {
      await deleteAdminForumThread(thread.value.id)
    } else {
      await deleteForumThread(thread.value.id)
    }

    isThreadDeleteRequested.value = false
    await router.push('/forum')
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to delete thread.'
  } finally {
    isDeletingThread.value = false
  }
}

async function handleSavePostEdit(payload: { postId: string; text: string }) {
  try {
    await updateForumPost(payload.postId, {
      text: payload.text,
    })

    await loadThreadPage()
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to update post.'
  }
}

function handleDeletePost(postId: string) {
  const targetPost = findPostById(postId)

  if (!targetPost) {
    errorText.value = 'Post was not found.'
    return
  }

  postToDelete.value = {
    id: targetPost.id,
    authorUsername: targetPost.author_username,
  }
}

function cancelDeletePost() {
  if (isDeletingPost.value) {
    return
  }

  postToDelete.value = null
}

async function confirmDeletePost() {
  if (!postToDelete.value) {
    return
  }

  isDeletingPost.value = true
  errorText.value = ''

  try {
    if (isAdmin.value) {
      await deleteAdminForumPost(postToDelete.value.id)
    } else {
      await deleteForumPost(postToDelete.value.id)
    }

    postToDelete.value = null
    await loadThreadPage()
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to delete post.'
  } finally {
    isDeletingPost.value = false
  }
}

function findPostById(postId: string) {
  for (const post of posts.value) {
    if (post.id === postId) {
      return post
    }

    const reply = post.replies.find((item) => item.id === postId)

    if (reply) {
      return reply
    }
  }

  return null
}

watch(
  () => route.params.id,
  () => {
    currentPostsPage.value = 1
    loadThreadPage()
  },
)

watch(
  () => [route.query.postId, route.query.focus],
  async () => {
    if (isLoading.value || !thread.value) {
      return
    }

    await scrollToPostFromRoute()
  },
)

watch(totalPostPages, (pages) => {
  if (currentPostsPage.value > pages) {
    currentPostsPage.value = pages
  }
})

watch(postSort, () => {
  currentPostsPage.value = 1
})

watch([currentPostsPage, openReplyGroups, () => authState.user?.id], () => {
  loadVisiblePostVotes()
}, { deep: true })

onMounted(() => {
  loadThreadPage()
})
</script>

<template>
  <section class="forum-thread-page">
    <div class="forum-thread-page__inner">
      <div class="forum-thread-page__breadcrumbs">
        <RouterLink to="/">Home</RouterLink>
        <span>›</span>
        <RouterLink to="/forum">Forum</RouterLink>
        <span v-if="thread">›</span>
        <span v-if="thread">{{ thread.title }}</span>
      </div>

      <div v-if="isLoading" class="forum-thread-page__state">
        Loading thread...
      </div>

      <div
        v-else-if="errorText && !thread"
        class="forum-thread-page__state forum-thread-page__state--error"
      >
        {{ errorText }}
      </div>

      <template v-else-if="thread">
        <div class="forum-thread-page__back-row">
          <RouterLink to="/forum" class="forum-thread-page__back-link">
            ← Back to Forum Topics
          </RouterLink>
        </div>

        <div class="forum-thread-page__meta-row">
          <span class="forum-thread-page__pill">
            {{ formatCategoryLabel(thread) }}
          </span>
          <span class="forum-thread-page__meta-text">
            {{ thread.replies_count }} replies
          </span>
        </div>

        <header class="forum-thread-page__header">
          <h1 class="forum-thread-page__title">
            {{ thread.title }}
          </h1>

          <p class="forum-thread-page__subtitle">
            Started by
            <span>{{ thread.author_username }}</span>
            • {{ formatRelativeTime(thread.created_at) }}
          </p>
        </header>

        <article class="forum-thread-page__thread-card">
          <aside class="forum-thread-page__author-panel">
            <span class="forum-thread-page__author-avatar">
              {{ getAuthorInitial(thread.author_username) }}
            </span>

            <h2 class="forum-thread-page__author-name">
              {{ thread.author_username }}
            </h2>

            <p class="forum-thread-page__author-role">
              Thread Author
            </p>
          </aside>

          <div class="forum-thread-page__thread-vote">
            <button
              type="button"
              class="forum-thread-page__vote-btn"
              :class="{ 'forum-thread-page__vote-btn--active': threadMyVote === 1 }"
              :disabled="!isLoggedIn || isThreadVoting"
              @click="handleVoteThread(1)"
            >
              ⌃
            </button>

            <strong>{{ thread.score }}</strong>

            <button
              type="button"
              class="forum-thread-page__vote-btn"
              :class="{ 'forum-thread-page__vote-btn--active': threadMyVote === -1 }"
              :disabled="!isLoggedIn || isThreadVoting"
              @click="handleVoteThread(-1)"
            >
              ⌄
            </button>
          </div>

          <div class="forum-thread-page__thread-content">
            <template v-if="isEditingThread">
              <label class="forum-thread-page__edit-field">
                <span>Title</span>
                <input v-model="threadEditTitle" type="text" />
              </label>

              <label class="forum-thread-page__edit-field">
                <span>Text</span>
                <textarea v-model="threadEditText" rows="7" />
              </label>

              <div class="forum-thread-page__thread-actions">
                <button
                  type="button"
                  class="forum-thread-page__thread-action-btn"
                  @click="saveThreadEdit"
                >
                  Save changes
                </button>

                <button
                  type="button"
                  class="forum-thread-page__thread-action-btn forum-thread-page__thread-action-btn--ghost"
                  @click="cancelThreadEdit"
                >
                  Cancel
                </button>
              </div>
            </template>

            <template v-else>
              <p class="forum-thread-page__thread-text">
                {{ thread.text }}
              </p>

              <div class="forum-thread-page__thread-actions">
                <button
                  v-if="isLoggedIn"
                  type="button"
                  class="forum-thread-page__reply-topic-btn"
                  @click="handleReplyToTopic"
                >
                  Reply to Topic
                </button>

                <RouterLink
                  v-else
                  to="/login"
                  class="forum-thread-page__thread-action-btn forum-thread-page__thread-action-btn--ghost"
                >
                  Log in to Reply
                </RouterLink>

                <button
                  v-if="canManageThread"
                  type="button"
                  class="forum-thread-page__thread-action-btn forum-thread-page__thread-action-btn--ghost"
                  @click="startThreadEdit"
                >
                  Edit Thread
                </button>

                <button
                  v-if="canDeleteThread"
                  type="button"
                  class="forum-thread-page__thread-action-btn forum-thread-page__thread-action-btn--danger"
                  @click="handleDeleteThread"
                >
                  Delete Thread
                </button>

                <span
                  v-if="isAdminThreadAction"
                  class="forum-thread-page__admin-mark"
                >
                  Admin action
                </span>
              </div>
            </template>
          </div>
        </article>

        <section class="forum-thread-page__discussion">
          <div class="forum-thread-page__discussion-head">
            <h2>Discussion</h2>

            <div class="forum-thread-page__discussion-controls">
              <label class="forum-thread-page__sort">
                <span>Sort by</span>
                <select v-model="postSort">
                  <option value="oldest">Oldest first</option>
                  <option value="newest">Newest first</option>
                </select>
              </label>
            </div>
          </div>

          <div v-if="paginatedPosts.length" class="forum-thread-page__posts-list">
              <div
                v-for="post in paginatedPosts"
                :id="`post-${post.id}`"
                :key="post.id"
                class="forum-thread-page__post-group"
              >
              <ForumPostCard
                :post="post"
                :my-vote="postVoteMap[post.id] ?? 0"
                :can-interact="isLoggedIn"
                @reply="startReplyToPost"
                @vote="handleVotePost"
                @save-edit="handleSavePostEdit"
                @delete="handleDeletePost"
              />

              <button
                v-if="post.replies.length"
                type="button"
                class="forum-thread-page__toggle-replies"
                @click="toggleReplies(post.id)"
              >
                {{
                  isRepliesOpen(post.id)
                    ? `Hide replies (${post.replies.length})`
                    : `Show replies (${post.replies.length})`
                }}
              </button>

              <div
                v-if="post.replies.length && isRepliesOpen(post.id)"
                class="forum-thread-page__replies"
              >
              <div
                v-for="reply in post.replies"
                :id="`post-${reply.id}`"
                :key="reply.id"
              >
                <ForumPostCard
                  :post="reply"
                  :my-vote="postVoteMap[reply.id] ?? 0"
                  :can-interact="isLoggedIn"
                  is-reply
                  @reply="startReplyToPost"
                  @vote="handleVotePost"
                  @save-edit="handleSavePostEdit"
                  @delete="handleDeletePost"
                />
              </div>
              </div>
            </div>
          </div>

          <div v-else class="forum-thread-page__empty">
            No posts yet. Be the first to reply.
          </div>

          <div v-if="totalPostPages > 1" class="forum-thread-page__posts-pagination">
            <ForumPagination
              :current-page="currentPostsPage"
              :total-pages="totalPostPages"
              @update:page="currentPostsPage = $event"
            />
          </div>
        </section>

        <section class="forum-thread-page__composer">
          <h2 class="forum-thread-page__composer-title">Add Your Reply</h2>

          <div v-if="!isLoggedIn" class="forum-thread-page__login-note">
            <p>Log in to join this discussion, reply to posts, and vote.</p>

            <RouterLink to="/login" class="forum-thread-page__login-link">
              Log in
            </RouterLink>
          </div>

          <template v-else>
            <div v-if="replyTarget" class="forum-thread-page__reply-target">
              <span>
                Replying to @{{ replyTarget.username }}
              </span>

              <button type="button" @click="cancelReply">
                Cancel
              </button>
            </div>

            <textarea
              ref="composerTextarea"
              v-model="composerText"
              rows="6"
              placeholder="What are your thoughts on this discussion? Be respectful and constructive..."
            />

            <div class="forum-thread-page__composer-footer">
              <p v-if="errorText && thread" class="forum-thread-page__inline-error">
                {{ errorText }}
              </p>

              <button
                type="button"
                class="forum-thread-page__composer-submit"
                :disabled="isSubmitting"
                @click="handleSubmitPost"
              >
                {{ isSubmitting ? 'Posting...' : 'Post Reply' }}
              </button>
            </div>
          </template>
        </section>
      </template>
    </div>

    <ConfirmModal
      :open="isThreadDeleteRequested"
      title="Delete forum thread?"
      :message="`This will permanently delete the thread '${thread?.title || 'selected thread'}'. This action cannot be undone.`"
      confirm-label="Delete thread"
      cancel-label="Cancel"
      :is-busy="isDeletingThread"
      @confirm="confirmDeleteThread"
      @cancel="cancelDeleteThread"
    />

    <ConfirmModal
      :open="Boolean(postToDelete)"
      title="Delete forum post?"
      :message="`This will permanently delete the post by ${postToDelete?.authorUsername || 'this user'}. This action cannot be undone.`"
      confirm-label="Delete post"
      cancel-label="Cancel"
      :is-busy="isDeletingPost"
      @confirm="confirmDeletePost"
      @cancel="cancelDeletePost"
    />

  </section>
</template>

<style scoped>
.forum-thread-page {
  width: 100%;
  padding: 26px 0 56px;
}

.forum-thread-page__inner {
  width: min(1120px, calc(100% - 48px));
  margin: 0 auto;
  display: grid;
  gap: 20px;
}

.forum-thread-page__breadcrumbs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  color: #64748b;
  font-size: 13px;
}

.forum-thread-page__breadcrumbs a {
  color: #94a3b8;
  text-decoration: none;
}

.forum-thread-page__back-row {
  display: flex;
  justify-content: flex-start;
}

.forum-thread-page__back-link {
  color: #60a5fa;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
}

.forum-thread-page__meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.forum-thread-page__pill {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.14);
  color: #dbeafe;
  font-size: 12px;
  font-weight: 700;
}

.forum-thread-page__meta-text {
  color: #94a3b8;
  font-size: 14px;
}

.forum-thread-page__header {
  display: grid;
  gap: 10px;
}

.forum-thread-page__title {
  margin: 0;
  color: #f8fafc;
  font-size: clamp(34px, 4.5vw, 58px);
  line-height: 1.08;
  letter-spacing: -0.04em;
  max-width: 900px;
}

.forum-thread-page__subtitle {
  margin: 0;
  color: #94a3b8;
  font-size: 15px;
}

.forum-thread-page__subtitle span {
  color: #60a5fa;
  font-weight: 600;
}

.forum-thread-page__thread-card {
  display: grid;
  grid-template-columns: 150px 52px minmax(0, 1fr);
  gap: 18px;
  padding: 22px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(24, 29, 41, 0.92);
}

.forum-thread-page__author-panel {
  padding-right: 18px;
  border-right: 1px solid rgba(148, 163, 184, 0.08);
  display: grid;
  align-content: center;
  justify-items: center;
  text-align: center;
  gap: 10px;
}

.forum-thread-page__author-avatar {
  width: 56px;
  height: 56px;
  border-radius: 999px;
  background: linear-gradient(135deg, #f8fafc 0%, #dbeafe 100%);
  color: #0f172a;
  font-size: 20px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.forum-thread-page__author-name {
  margin: 0;
  color: #f8fafc;
  font-size: 18px;
  line-height: 1.2;
}

.forum-thread-page__author-role {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.forum-thread-page__thread-vote {
  display: grid;
  justify-items: center;
  align-content: center;
  gap: 10px;
  padding-top: 4px;
}

.forum-thread-page__thread-vote strong {
  color: #f8fafc;
  font-size: 28px;
  line-height: 1;
}

.forum-thread-page__vote-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #e2e8f0;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  border-radius: 8px;
}

.forum-thread-page__vote-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.forum-thread-page__vote-btn--active {
  color: #60a5fa;
  background: rgba(37, 99, 235, 0.12);
}

.forum-thread-page__thread-content {
  min-width: 0;
  display: grid;
  gap: 18px;
}

.forum-thread-page__thread-text {
  margin: 0;
  color: #e2e8f0;
  font-size: 17px;
  line-height: 1.9;
  white-space: pre-wrap;
}

.forum-thread-page__edit-field {
  display: grid;
  gap: 8px;
}

.forum-thread-page__edit-field span {
  color: #cbd5e1;
  font-size: 14px;
  font-weight: 600;
}

.forum-thread-page__edit-field input,
.forum-thread-page__edit-field textarea {
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  padding: 14px;
  outline: none;
}

.forum-thread-page__thread-actions {
  padding-top: 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.forum-thread-page__reply-topic-btn,
.forum-thread-page__thread-action-btn {
  min-height: 40px;
  padding: 0 16px;
  border-radius: 12px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

.forum-thread-page__reply-topic-btn,
.forum-thread-page__thread-action-btn {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
}

.forum-thread-page__thread-action-btn--ghost {
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.12);
  color: #e2e8f0;
}

.forum-thread-page__thread-action-btn--ghost:hover {
  border-color: rgba(96, 165, 250, 0.28);
  color: #ffffff;
  background: rgba(15, 23, 42, 0.95);
}

.forum-thread-page__reply-topic-btn:disabled,
.forum-thread-page__thread-action-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.forum-thread-page__thread-action-btn--danger {
  background: rgba(127, 29, 29, 0.18);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #fecaca;
}

.forum-thread-page__discussion {
  display: grid;
  gap: 10px;
}

.forum-thread-page__discussion-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding-top: 10px;
}

.forum-thread-page__discussion-head h2 {
  margin: 0;
  color: #f8fafc;
  font-size: 28px;
  line-height: 1.1;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.forum-thread-page__discussion-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.forum-thread-page__sort {
  display: flex;
  align-items: center;
  gap: 10px;
}

.forum-thread-page__sort span {
  color: #94a3b8;
  font-size: 13px;
}

.forum-thread-page__sort select {
  min-width: 150px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  padding: 0 12px;
  outline: none;
}

.forum-thread-page__posts-list,
.forum-thread-page__post-group,
.forum-thread-page__replies {
  display: grid;
}

.forum-thread-page__post-group,
.forum-thread-page__replies > div {
  scroll-margin-top: 120px;
}

.forum-thread-page__toggle-replies {
  justify-self: start;
  margin: -4px 0 8px 62px;
  border: none;
  background: transparent;
  color: #60a5fa;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  padding: 0;
}

.forum-thread-page__posts-pagination {
  padding-top: 12px;
}

.forum-thread-page__empty,
.forum-thread-page__state {
  padding: 28px;
  border-radius: 22px;
  background: rgba(8, 14, 24, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.08);
  color: #cbd5e1;
}

.forum-thread-page__state--error {
  color: #fca5a5;
}

.forum-thread-page__composer {
  display: grid;
  gap: 14px;
  padding-top: 8px;
}

.forum-thread-page__composer-title {
  margin: 0;
  color: #f8fafc;
  font-size: 30px;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.forum-thread-page__login-note {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 20px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
}

.forum-thread-page__login-note p {
  margin: 0;
  color: #94a3b8;
  font-size: 15px;
  line-height: 1.7;
}

.forum-thread-page__login-link {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  text-decoration: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}

.forum-thread-page__reply-target {
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

.forum-thread-page__reply-target button {
  border: none;
  background: transparent;
  color: #cbd5e1;
  cursor: pointer;
  font-weight: 700;
}

.forum-thread-page__composer textarea {
  width: 100%;
  min-height: 220px;
  resize: vertical;
  padding: 16px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(9, 18, 38, 0.9);
  color: #f8fafc;
  outline: none;
}

.forum-thread-page__composer-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.forum-thread-page__inline-error {
  margin: 0;
  color: #fca5a5;
  font-size: 14px;
}

.forum-thread-page__composer-submit {
  min-height: 44px;
  padding: 0 18px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
}

.forum-thread-page__highlighted-post {
  border-radius: 18px;
  outline: 2px solid rgba(96, 165, 250, 0.65);
  outline-offset: 8px;
  transition: outline-color 0.25s ease;
}

.forum-thread-page__admin-mark {
  color: #fca5a5;
  font-size: 12px;
  font-weight: 800;
  align-self: center;
}

@media (max-width: 900px) {
  .forum-thread-page__inner {
    width: min(100%, calc(100% - 32px));
  }

  .forum-thread-page__thread-card {
    grid-template-columns: 1fr;
  }

  .forum-thread-page__author-panel {
    border-right: none;
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
    padding-right: 0;
    padding-bottom: 16px;
  }

  .forum-thread-page__thread-vote {
    grid-auto-flow: column;
    justify-content: center;
  }

  .forum-thread-page__toggle-replies {
    margin-left: 0;
  }
}

@media (max-width: 700px) {
  .forum-thread-page__discussion-head,
  .forum-thread-page__composer-footer,
  .forum-thread-page__reply-target,
  .forum-thread-page__login-note {
    flex-direction: column;
    align-items: flex-start;
  }

  .forum-thread-page__thread-actions {
    justify-content: flex-start;
  }
}
</style>