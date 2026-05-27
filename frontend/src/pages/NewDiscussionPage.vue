<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { createForumThread } from '../services/forum'
import type { ForumCategoryType } from '../types/forum'

const router = useRouter()

const title = ref('')
const text = ref('')
const categoryType = ref<ForumCategoryType>('movie')
const customCategory = ref('')
const isSubmitting = ref(false)
const errorText = ref('')

const isCustom = computed(() => categoryType.value === 'custom')

async function handleSubmit() {
  errorText.value = ''

  if (title.value.trim().length < 3) {
    errorText.value = 'Title must be at least 3 characters long.'
    return
  }

  if (text.value.trim().length < 1) {
    errorText.value = 'Text is required.'
    return
  }

  if (isCustom.value && customCategory.value.trim().length < 2) {
    errorText.value = 'Custom category must be at least 2 characters long.'
    return
  }

  isSubmitting.value = true

  try {
    const thread = await createForumThread({
      title: title.value.trim(),
      text: text.value.trim(),
      category_type: categoryType.value,
      custom_category: isCustom.value ? customCategory.value.trim() : null,
    })

    await router.push(`/forum/threads/${thread.id}`)
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to create discussion.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="new-thread-page">
    <div class="new-thread-page__inner">
      <div class="new-thread-page__top">
        <div>
          <p class="new-thread-page__eyebrow">FORUM</p>
          <h1 class="new-thread-page__title">Create New Discussion</h1>
          <p class="new-thread-page__text">
            Start a real topic in the forum and test the full thread flow.
          </p>
        </div>

        <RouterLink to="/forum" class="new-thread-page__back">
          Back to Forum
        </RouterLink>
      </div>

      <form class="new-thread-form" @submit.prevent="handleSubmit">
        <label class="new-thread-form__field">
          <span>Title</span>
          <input v-model="title" type="text" placeholder="Enter discussion title" />
        </label>

        <label class="new-thread-form__field">
          <span>Category</span>
          <select v-model="categoryType">
            <option value="movie">Movies</option>
            <option value="series">TV Series</option>
            <option value="book">Books</option>
            <option value="custom">Custom</option>
          </select>
        </label>

        <label v-if="isCustom" class="new-thread-form__field">
          <span>Custom Category</span>
          <input
            v-model="customCategory"
            type="text"
            placeholder="For example: General"
          />
        </label>

        <label class="new-thread-form__field">
          <span>Text</span>
          <textarea
            v-model="text"
            rows="8"
            placeholder="Write your discussion text..."
          />
        </label>

        <p v-if="errorText" class="new-thread-form__error">
          {{ errorText }}
        </p>

        <button type="submit" class="new-thread-form__submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Creating...' : 'Create Discussion' }}
        </button>
      </form>
    </div>
  </section>
</template>

<style scoped>
.new-thread-page {
  width: 100%;
  padding: 30px 0 56px;
}

.new-thread-page__inner {
  width: min(980px, calc(100% - 48px));
  margin: 0 auto;
  display: grid;
  gap: 24px;
}

.new-thread-page__top {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: start;
}

.new-thread-page__eyebrow {
  margin: 0 0 10px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.new-thread-page__title {
  margin: 0 0 12px;
  color: #f8fafc;
  font-size: clamp(34px, 4vw, 50px);
  line-height: 1.02;
  letter-spacing: -0.04em;
}

.new-thread-page__text {
  margin: 0;
  color: #94a3b8;
  line-height: 1.75;
}

.new-thread-page__back {
  min-height: 44px;
  padding: 0 16px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.12);
  color: #f8fafc;
  text-decoration: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
}

.new-thread-form {
  display: grid;
  gap: 16px;
  padding: 26px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.92);
}

.new-thread-form__field {
  display: grid;
  gap: 8px;
}

.new-thread-form__field span {
  color: #cbd5e1;
  font-size: 14px;
  font-weight: 600;
}

.new-thread-form__field input,
.new-thread-form__field select,
.new-thread-form__field textarea {
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  padding: 14px;
  outline: none;
}

.new-thread-form__field textarea {
  resize: vertical;
  min-height: 180px;
}

.new-thread-form__error {
  margin: 0;
  color: #fca5a5;
  font-size: 14px;
}

.new-thread-form__submit {
  min-height: 50px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
}

.new-thread-form__submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .new-thread-page__inner {
    width: min(100%, calc(100% - 32px));
  }

  .new-thread-page__top {
    flex-direction: column;
  }
}
</style>