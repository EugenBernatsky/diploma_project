<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useAuth } from '../../services/auth'
import type { CommentBase } from '../../types/comment'
import { formatRelativeTime } from '../../utils/forumTime'
import { getAvatarImageUrl } from '../../utils/avatars'

const props = withDefaults(
  defineProps<{
    comment: CommentBase
    isReply?: boolean
  }>(),
  {
    isReply: false,
  },
)

const emit = defineEmits<{
  (e: 'reply', value: CommentBase): void
  (e: 'save-edit', value: { commentId: string; text: string }): void
  (e: 'delete', value: string): void
}>()

const { authState } = useAuth()

const isEditing = ref(false)
const editText = ref(props.comment.text)

watch(
  () => props.comment.text,
  (value) => {
    if (!isEditing.value) {
      editText.value = value
    }
  },
)

const canManage = computed(() => authState.user?.id === props.comment.user_id)

const isAdmin = computed(() => authState.user?.role === 'admin')

const canDelete = computed(() => {
  return canManage.value || isAdmin.value
})

const isAdminDeleteAction = computed(() => {
  return isAdmin.value && !canManage.value
})

const authorAvatarUrl = computed(() => {
  return getAvatarImageUrl(props.comment.author_avatar_id)
})

function getAuthorInitial(name: string): string {
  return name.trim().charAt(0).toUpperCase() || 'U'
}

function startEdit() {
  editText.value = props.comment.text
  isEditing.value = true
}

function cancelEdit() {
  editText.value = props.comment.text
  isEditing.value = false
}

function saveEdit() {
  const trimmed = editText.value.trim()

  if (!trimmed || trimmed === props.comment.text) {
    isEditing.value = false
    return
  }

  emit('save-edit', {
    commentId: props.comment.id,
    text: trimmed,
  })

  isEditing.value = false
}
</script>

<template>
  <article class="item-comment-card" :class="{ 'item-comment-card--reply': isReply }">
    <div class="item-comment-card__top">
      <div class="item-comment-card__author-wrap">
        <span class="item-comment-card__avatar">
          <img
            v-if="authorAvatarUrl"
            :src="authorAvatarUrl"
            :alt="comment.author_username"
          />

          <span v-else>{{ getAuthorInitial(comment.author_username) }}</span>
        </span>

        <div class="item-comment-card__author-meta">
          <h3 class="item-comment-card__author">{{ comment.author_username }}</h3>
          <p class="item-comment-card__time">
            {{ formatRelativeTime(comment.created_at) }}
            <span v-if="comment.edited">• edited</span>
          </p>
        </div>
      </div>
    </div>

    <p v-if="comment.reply_to_username" class="item-comment-card__reply-target">
      Replying to @{{ comment.reply_to_username }}
    </p>

    <template v-if="isEditing">
      <textarea
        v-model="editText"
        class="item-comment-card__editor"
        rows="4"
      />

      <div class="item-comment-card__actions">
        <button type="button" class="item-comment-card__action" @click="saveEdit">
          Save
        </button>

        <button type="button" class="item-comment-card__action" @click="cancelEdit">
          Cancel
        </button>
      </div>
    </template>

    <template v-else>
      <p class="item-comment-card__text">
        {{ comment.text }}
      </p>

      <div class="item-comment-card__actions">
        <button type="button" class="item-comment-card__action" @click="$emit('reply', comment)">
          Reply
        </button>

        <button
          v-if="canManage"
          type="button"
          class="item-comment-card__action"
          @click="startEdit"
        >
          Edit
        </button>

        <button
          v-if="canDelete"
          type="button"
          class="item-comment-card__action item-comment-card__action--danger"
          @click="$emit('delete', comment.id)"
        >
          Delete
        </button>

        <span v-if="canManage" class="item-comment-card__owner-mark">
          Your comment
        </span>

        <span v-if="isAdminDeleteAction" class="item-comment-card__admin-mark">
          Admin action
        </span>
      </div>
    </template>
  </article>
</template>

<style scoped>
.item-comment-card {
  display: grid;
  gap: 12px;
  padding: 18px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
}

.item-comment-card--reply {
  margin-left: 28px;
  padding-left: 18px;
  border-left: 2px solid rgba(37, 99, 235, 0.18);
}

.item-comment-card__author-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-comment-card__avatar {
  width: 36px;
  height: 36px;
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

.item-comment-card__avatar img {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: inherit;
  object-fit: cover;
}

.item-comment-card__author {
  margin: 0 0 2px;
  color: #f8fafc;
  font-size: 15px;
  line-height: 1.2;
}

.item-comment-card__time {
  margin: 0;
  color: #64748b;
  font-size: 12px;
}

.item-comment-card__reply-target {
  margin: 0;
  color: #60a5fa;
  font-size: 13px;
  font-weight: 600;
}

.item-comment-card__text {
  margin: 0;
  color: #cbd5e1;
  font-size: 15px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.item-comment-card__editor {
  width: 100%;
  min-height: 110px;
  resize: vertical;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  outline: none;
}

.item-comment-card__actions {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.item-comment-card__action {
  border: none;
  background: transparent;
  color: #60a5fa;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  padding: 0;
}

.item-comment-card__action--danger {
  color: #fca5a5;
}

.item-comment-card__owner-mark {
  color: #64748b;
  font-size: 12px;
}

.item-comment-card__admin-mark {
  color: #fca5a5;
  font-size: 12px;
  font-weight: 700;
}

@media (max-width: 640px) {
  .item-comment-card--reply {
    margin-left: 14px;
    padding-left: 12px;
  }
}
</style>