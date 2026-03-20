<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { getItemById } from '../services/api'
import type { MediaItem } from '../types/media'

const route = useRoute()
const router = useRouter()

const item = ref<MediaItem | null>(null)
const isLoading = ref(true)
const errorText = ref('')

const itemId = computed(() => Number(route.params.id))

async function loadItem() {
  isLoading.value = true
  errorText.value = ''

  try {
    if (Number.isNaN(itemId.value)) {
      throw new Error('Некоректний id айтема')
    }

    const data = await getItemById(itemId.value)
    item.value = data
  } catch (error) {
    item.value = null
    errorText.value =
      error instanceof Error ? error.message : 'Невідома помилка'
  } finally {
    isLoading.value = false
  }
}

watch(
  () => route.params.id,
  () => {
    loadItem()
  }
)

onMounted(() => {
  loadItem()
})
</script>

<template>
  <section class="item-details-page">
    <div class="item-details-page__inner">
      <div class="item-details-page__topbar">
        <RouterLink to="/catalog" class="back-link">
          ← Назад до каталогу
        </RouterLink>

        <button class="secondary-button" @click="router.back()">
          Назад
        </button>
      </div>

      <div v-if="isLoading" class="state-card">
        Завантаження айтема...
      </div>

      <div v-else-if="errorText" class="state-card state-card--error">
        Помилка: {{ errorText }}
      </div>

      <article v-else-if="item" class="details-card">
        <p class="details-card__tag">Media Item</p>
        <h2 class="details-card__title">{{ item.title }}</h2>

        <div class="details-card__meta">
          <span>Категорія: {{ item.category }}</span>
          <span>Рік: {{ item.year }}</span>
          <span>ID: {{ item.id }}</span>
        </div>

        <div class="details-card__genres">
          <span
            v-for="genre in item.genres"
            :key="genre"
            class="genre-badge"
          >
            {{ genre }}
          </span>
        </div>

        <p class="details-card__description">
          {{ item.description }}
        </p>

        <div class="details-card__actions">
          <button class="primary-button">
            Додати в обране
          </button>

          <button class="secondary-button">
            Оцінити
          </button>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.item-details-page {
  padding: 40px 16px 56px;
}

.item-details-page__inner {
  width: min(920px, 100%);
  margin: 0 auto;
  display: grid;
  gap: 20px;
}

.item-details-page__topbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.back-link {
  color: #93c5fd;
  text-decoration: none;
  font-weight: 600;
}

.back-link:hover {
  color: #bfdbfe;
}

.state-card,
.details-card {
  padding: 32px;
  border-radius: 24px;
  background: #071533;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
}

.state-card--error {
  color: #fca5a5;
}

.details-card__tag {
  margin: 0 0 12px;
  color: #60a5fa;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 14px;
}

.details-card__title {
  margin: 0 0 16px;
  font-size: 42px;
  line-height: 1.1;
  color: #f8fafc;
}

.details-card__meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin: 0 0 16px;
  color: #cbd5e1;
}

.details-card__genres {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.genre-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: #0f172a;
  border: 1px solid #374151;
  color: #93c5fd;
  font-size: 14px;
}

.details-card__description {
  margin: 0 0 24px;
  color: #cbd5e1;
  line-height: 1.7;
  font-size: 18px;
}

.details-card__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-button {
  border: none;
  border-radius: 12px;
  padding: 12px 18px;
  background: #2563eb;
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.primary-button:hover {
  background: #1d4ed8;
}

.secondary-button {
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 12px 18px;
  background: transparent;
  color: #e5e7eb;
  cursor: pointer;
  font-weight: 600;
}

.secondary-button:hover {
  border-color: #60a5fa;
}
</style>