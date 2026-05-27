<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { ForumPostBaseResponse } from '../../types/forum'
import { useAuth } from '../../services/auth'
import { formatRelativeTime } from '../../utils/forumTime'
import { getAvatarImageUrl } from '../../utils/avatars'

const props = withDefaults(
  defineProps<{
    post: ForumPostBaseResponse
    isReply?: boolean
    myVote?: 1 | -1 | 0
    canInteract?: boolean
  }>(),
  {
    isReply: false,
    myVote: 0,
    canInteract: true,
  },
)

const emit = defineEmits<{
  (e: 'reply', value: ForumPostBaseResponse): void
  (e: 'vote', value: { postId: string; value: 1 | -1 }): void
  (e: 'save-edit', value: { postId: string; text: string }): void
  (e: 'delete', value: string): void
}>()

const { authState } = useAuth()
const isVoting = ref(false)
const isEditing = ref(false)
const editText = ref(props.post.text)

watch(
  () => props.post.text,
  (value) => {
    if (!isEditing.value) {
      editText.value = value
    }
  },
)

function getAuthorInitial(name: string): string {
  return name.trim().charAt(0).toUpperCase() || 'U'
}

const canManage = computed(() => authState.user?.id === props.post.user_id)

const isAdmin = computed(() => authState.user?.role === 'admin')

const canDelete = computed(() => {
  return canManage.value || isAdmin.value
})

const isAdminDeleteAction = computed(() => {
  return isAdmin.value && !canManage.value
})

const authorAvatarUrl = computed(() => {
  return getAvatarImageUrl(props.post.author_avatar_id)
})

async function handleVote(value: 1 | -1) {
  if (isVoting.value || !props.canInteract) return
  isVoting.value = true

  try {
    emit('vote', {
      postId: props.post.id,
      value,
    })
  } finally {
    isVoting.value = false
  }
}

function startEdit() {
  editText.value = props.post.text
  isEditing.value = true
}

function cancelEdit() {
  editText.value = props.post.text
  isEditing.value = false
}

function saveEdit() {
  const trimmed = editText.value.trim()
  if (!trimmed || trimmed === props.post.text) {
    isEditing.value = false
    return
  }

  emit('save-edit', {
    postId: props.post.id,
    text: trimmed,
  })

  isEditing.value = false
}
</script>

<template>
  <article class="forum-post-card" :class="{ 'forum-post-card--reply': isReply }">
    <div class="forum-post-card__vote">
      <button
        type="button"
        class="forum-post-card__vote-btn"
        :class="{ 'forum-post-card__vote-btn--active': myVote === 1 }"
        :disabled="!canInteract || isVoting"
        @click="handleVote(1)"
      >
        ⌃
      </button>

      <span class="forum-post-card__score">{{ post.score }}</span>

      <button
        type="button"
        class="forum-post-card__vote-btn"
        :class="{ 'forum-post-card__vote-btn--active': myVote === -1 }"
        :disabled="!canInteract || isVoting"
        @click="handleVote(-1)"
      >
        ⌄
      </button>
    </div>

    <div class="forum-post-card__body">
      <div class="forum-post-card__top">
        <div class="forum-post-card__author-wrap">
          <span class="forum-post-card__avatar">
            <img
              v-if="authorAvatarUrl"
              :src="authorAvatarUrl"
              :alt="post.author_username"
            />

            <span v-else>{{ getAuthorInitial(post.author_username) }}</span>
          </span>

          <div class="forum-post-card__author-meta">
            <h3 class="forum-post-card__author">{{ post.author_username }}</h3>
            <p class="forum-post-card__time">
              {{ formatRelativeTime(post.created_at) }}
              <span v-if="post.edited">• edited</span>
            </p>
          </div>
        </div>
      </div>

      <p v-if="post.reply_to_username" class="forum-post-card__reply-target">
        Replying to @{{ post.reply_to_username }}
      </p>

      <template v-if="isEditing">
        <textarea
          v-model="editText"
          class="forum-post-card__editor"
          rows="4"
        />

        <div class="forum-post-card__actions">
          <button type="button" class="forum-post-card__action" @click="saveEdit">
            Save
          </button>

          <button type="button" class="forum-post-card__action" @click="cancelEdit">
            Cancel
          </button>
        </div>
      </template>

      <template v-else>
        <p class="forum-post-card__text">
          {{ post.text }}
        </p>

        <div class="forum-post-card__actions">
          <button
            v-if="canInteract"
            type="button"
            class="forum-post-card__action"
            @click="$emit('reply', post)"
          >
            Reply
          </button>

          <button
            v-if="canManage"
            type="button"
            class="forum-post-card__action"
            @click="startEdit"
          >
            Edit
          </button>

          <button
            v-if="canDelete"
            type="button"
            class="forum-post-card__action forum-post-card__action--danger"
            @click="$emit('delete', post.id)"
          >
            Delete
          </button>

          <span v-if="canManage" class="forum-post-card__owner-mark">
            Your post
          </span>

          <span v-if="isAdminDeleteAction" class="forum-post-card__admin-mark">
            Admin action
          </span>
        </div>
      </template>
    </div>
  </article>
</template>

<style scoped>
.forum-post-card {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 18px;
  padding: 18px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
}

.forum-post-card--reply {
  margin-left: 44px;
  padding-left: 18px;
  border-left: 2px solid rgba(37, 99, 235, 0.2);
}

.forum-post-card__vote {
  display: grid;
  justify-items: center;
  align-content: start;
  gap: 8px;
  padding-top: 2px;
}

.forum-post-card__vote-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #cbd5e1;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  border-radius: 8px;
}

.forum-post-card__vote-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.forum-post-card__vote-btn--active {
  color: #60a5fa;
  background: rgba(37, 99, 235, 0.12);
}

.forum-post-card__score {
  color: #f8fafc;
  font-size: 18px;
  font-weight: 700;
  line-height: 1;
}

.forum-post-card__body {
  min-width: 0;
}

.forum-post-card__top {
  margin-bottom: 10px;
}

.forum-post-card__author-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.forum-post-card__avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  background: linear-gradient(135deg, #f8fafc 0%, #dbeafe 100%);
  color: #0f172a;
  font-size: 13px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}

.forum-post-card__avatar img {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: inherit;
  object-fit: cover;
}

.forum-post-card__author-meta {
  min-width: 0;
}

.forum-post-card__author {
  margin: 0 0 2px;
  color: #f8fafc;
  font-size: 15px;
  line-height: 1.2;
}

.forum-post-card__time {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.4;
}

.forum-post-card__reply-target {
  margin: 0 0 10px;
  color: #60a5fa;
  font-size: 13px;
  font-weight: 600;
}

.forum-post-card__text {
  margin: 0 0 14px;
  color: #cbd5e1;
  font-size: 15px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.forum-post-card__editor {
  width: 100%;
  min-height: 110px;
  resize: vertical;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  outline: none;
  margin-bottom: 12px;
}

.forum-post-card__actions {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.forum-post-card__action {
  border: none;
  background: transparent;
  color: #60a5fa;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  padding: 0;
}

.forum-post-card__action--danger {
  color: #fca5a5;
}

.forum-post-card__owner-mark {
  color: #64748b;
  font-size: 12px;
}

.forum-post-card__admin-mark {
  color: #fca5a5;
  font-size: 12px;
  font-weight: 700;
}

@media (max-width: 700px) {
  .forum-post-card {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .forum-post-card--reply {
    margin-left: 18px;
    padding-left: 14px;
  }

  .forum-post-card__vote {
    grid-auto-flow: column;
    justify-content: start;
    gap: 12px;
  }
}
</style>