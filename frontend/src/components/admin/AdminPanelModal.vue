<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { getAdminDashboardStats } from '../../services/admin'
import type { AdminDashboardStats } from '../../types/admin'
import AdminItemsTab from './AdminItemsTab.vue'
import AdminCommentsTab from './AdminCommentsTab.vue'
import AdminForumThreadsTab from './AdminForumThreadsTab.vue'
import AdminForumPostsTab from './AdminForumPostsTab.vue'

type AdminTab = 'items' | 'comments' | 'threads' | 'posts'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  (event: 'close'): void
}>()

const activeTab = ref<AdminTab>('items')
const stats = ref<AdminDashboardStats | null>(null)
const isLoadingStats = ref(false)
const errorText = ref('')

const tabs: Array<{
  value: AdminTab
  label: string
  description: string
}> = [
  {
    value: 'items',
    label: 'Items',
    description: 'Search, open and edit media items.',
  },
  {
    value: 'comments',
    label: 'Comments',
    description: 'Moderate comments from item pages.',
  },
  {
    value: 'threads',
    label: 'Forum Threads',
    description: 'Open or remove forum topics.',
  },
  {
    value: 'posts',
    label: 'Forum Posts',
    description: 'Moderate forum posts and replies.',
  },
]

const statCards = computed(() => {
  if (!stats.value) {
    return []
  }

  return [
    {
      label: 'Users',
      value: stats.value.users_count,
    },
    {
      label: 'Items',
      value: stats.value.items_count,
    },
    {
      label: 'Comments',
      value: stats.value.comments_count,
    },
    {
      label: 'Threads',
      value: stats.value.forum_threads_count,
    },
    {
      label: 'Posts',
      value: stats.value.forum_posts_count,
    },
    {
      label: 'Unread Notifications',
      value: stats.value.unread_notifications_count,
    },
  ]
})

const activeTabInfo = computed(() => {
  return tabs.find((tab) => tab.value === activeTab.value) ?? tabs[0]
})

function closeModal() {
  emit('close')
}

function handleKeydown(event: KeyboardEvent) {
  const hasNestedModal = Boolean(document.querySelector('.confirm-modal'))

  if (hasNestedModal) {
    return
  }

  if (event.key === 'Escape' && props.open) {
    closeModal()
  }
}

async function loadStats() {
  isLoadingStats.value = true
  errorText.value = ''

  try {
    stats.value = await getAdminDashboardStats()
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to load admin stats.'
  } finally {
    isLoadingStats.value = false
  }
}

watch(
  () => props.open,
  (value) => {
    document.body.style.overflow = value ? 'hidden' : ''

    if (value) {
      loadStats()
    }
  },
)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)

  if (props.open) {
    loadStats()
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="admin-panel"
      @click.self="closeModal"
    >
      <section class="admin-panel__dialog">
        <header class="admin-panel__header">
          <div>
            <p class="admin-panel__eyebrow">Admin Area</p>
            <h2>Admin Panel</h2>
            <span>Manage media items, comments and forum content.</span>
          </div>

          <button
            type="button"
            class="admin-panel__close"
            aria-label="Close admin panel"
            @click="closeModal"
          >
            ✕
          </button>
        </header>

        <div v-if="errorText" class="admin-panel__error">
          {{ errorText }}
        </div>

        <section class="admin-panel__stats">
          <div v-if="isLoadingStats" class="admin-panel__state">
            Loading dashboard stats...
          </div>

          <article
            v-for="card in statCards"
            v-else
            :key="card.label"
            class="admin-panel__stat-card"
          >
            <span>{{ card.label }}</span>
            <strong>{{ card.value }}</strong>
          </article>
        </section>

        <div class="admin-panel__body">
          <aside class="admin-panel__tabs">
            <button
              v-for="tab in tabs"
              :key="tab.value"
              type="button"
              class="admin-panel__tab"
              :class="{ 'admin-panel__tab--active': activeTab === tab.value }"
              @click="activeTab = tab.value"
            >
              <strong>{{ tab.label }}</strong>
              <span>{{ tab.description }}</span>
            </button>
          </aside>

        <main class="admin-panel__content">
            <AdminItemsTab
                v-if="activeTab === 'items'"
                @close="closeModal"
            />

            <AdminCommentsTab
                v-else-if="activeTab === 'comments'"
                @close="closeModal"
            />

            <AdminForumThreadsTab
                v-else-if="activeTab === 'threads'"
                @close="closeModal"
            />

            <AdminForumPostsTab
                v-else-if="activeTab === 'posts'"
                @close="closeModal"
            />

            <div v-else class="admin-panel__placeholder">
                <p class="admin-panel__eyebrow">{{ activeTabInfo.label }}</p>
                <h3>{{ activeTabInfo.label }} tab</h3>
                <span>
                Unknown admin tab.
                </span>
            </div>
        </main>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.admin-panel {
  position: fixed;
  inset: 0;
  z-index: 240;
  padding: 24px;
  background: rgba(2, 6, 23, 0.78);
  display: flex;
  align-items: center;
  justify-content: center;
}

.admin-panel__dialog {
  width: min(1380px, 100%);
  max-height: 90vh;
  overflow: hidden;
  display: grid;
  grid-template-rows: auto auto auto minmax(0, 1fr);
  border-radius: 26px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(8, 14, 24, 0.98);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.42);
}

.admin-panel__header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: start;
  padding: 24px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

.admin-panel__eyebrow {
  margin: 0 0 8px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.admin-panel__header h2,
.admin-panel__placeholder h3 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 34px;
  line-height: 1;
  letter-spacing: -0.04em;
}

.admin-panel__header span,
.admin-panel__placeholder span {
  color: #94a3b8;
  line-height: 1.7;
}

.admin-panel__close {
  width: 42px;
  height: 42px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
  color: #ffffff;
  font-size: 18px;
  cursor: pointer;
  flex: 0 0 auto;
}

.admin-panel__error {
  margin: 16px 24px 0;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(239, 68, 68, 0.12);
  color: #fca5a5;
  font-weight: 700;
}

.admin-panel__stats {
  padding: 18px 24px;
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

.admin-panel__state {
  grid-column: 1 / -1;
  color: #94a3b8;
}

.admin-panel__stat-card {
  padding: 16px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(148, 163, 184, 0.08);
  display: grid;
  gap: 8px;
}

.admin-panel__stat-card span {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 800;
}

.admin-panel__stat-card strong {
  color: #f8fafc;
  font-size: 26px;
  line-height: 1;
}

.admin-panel__body {
  min-height: 0;
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
}

.admin-panel__tabs {
  min-height: 0;
  padding: 18px;
  border-right: 1px solid rgba(148, 163, 184, 0.08);
  display: grid;
  align-content: start;
  gap: 10px;
  overflow-y: auto;
}

.admin-panel__tab {
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.46);
  color: #94a3b8;
  text-align: left;
  cursor: pointer;
  display: grid;
  gap: 6px;
}

.admin-panel__tab strong {
  color: #f8fafc;
}

.admin-panel__tab span {
  line-height: 1.5;
}

.admin-panel__tab--active {
  border-color: rgba(96, 165, 250, 0.42);
  background: rgba(37, 99, 235, 0.16);
}

.admin-panel__content {
  min-height: 0;
  overflow-y: auto;
  padding: 24px;
}

.admin-panel__placeholder {
  min-height: 360px;
  border-radius: 22px;
  border: 1px dashed rgba(148, 163, 184, 0.22);
  background: rgba(15, 23, 42, 0.42);
  display: grid;
  place-content: center;
  justify-items: center;
  text-align: center;
  padding: 32px;
}

@media (max-width: 1080px) {
  .admin-panel__stats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .admin-panel__body {
    grid-template-columns: 1fr;
  }

  .admin-panel__tabs {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    border-right: none;
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
  }
}

@media (max-width: 720px) {
  .admin-panel {
    padding: 12px;
  }

  .admin-panel__dialog {
    max-height: 94vh;
  }

  .admin-panel__header {
    flex-direction: column;
  }

  .admin-panel__stats,
  .admin-panel__tabs {
    grid-template-columns: 1fr;
  }

  .admin-panel__content,
  .admin-panel__header,
  .admin-panel__stats {
    padding: 16px;
  }
}
</style>