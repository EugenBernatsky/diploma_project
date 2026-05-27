<script setup lang="ts">
import { computed } from 'vue'
import { useAuth } from '../../services/auth'
import { createInteraction } from '../../services/interactions'
import type { MediaProviderLink } from '../../types/media'

const props = defineProps<{
  itemId: string
  watchLinks: MediaProviderLink[]
  purchaseLinks: MediaProviderLink[]
}>()

const { isLoggedIn } = useAuth()

function formatProviderType(value: string): string {
  const normalized = value.trim().toLowerCase()

  if (normalized === 'buy') return 'Buy'
  if (normalized === 'rent') return 'Rent'
  if (normalized === 'flatrate') return 'Subscription'
  if (normalized === 'free') return 'Free'
  if (normalized === 'ads') return 'Ads'

  return value
    .trim()
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function trackExternalLinkClick() {
  if (!isLoggedIn.value) {
    return
  }

  void createInteraction({
    item_id: props.itemId,
    interaction_type: 'external_link_click',
    source: 'item_page',
  }).catch(() => {
    // interaction logging should not block user navigation
  })
}

const hasAnyLinks = computed(() => {
  return props.watchLinks.length > 0 || props.purchaseLinks.length > 0
})
</script>

<template>
  <section v-if="hasAnyLinks" class="item-availability">
    <h2 class="item-availability__title">Where to Watch & Buy</h2>

    <div class="item-availability__grid">
  <div v-if="watchLinks.length" class="item-availability__panel">
    <div class="item-availability__panel-head">
      <h3>Watch Links</h3>
      <span>{{ watchLinks.length }}</span>
    </div>

    <div class="item-availability__list">
      <article
        v-for="link in watchLinks"
        :key="`${link.provider_name}-${link.provider_type}-${link.region}-${link.url}`"
        class="item-availability__card"
      >
        <div class="item-availability__card-top">
          <h4 class="item-availability__provider">{{ link.provider_name }}</h4>

          <span class="item-availability__type">
            {{ formatProviderType(link.provider_type) }}
          </span>
        </div>

        <p class="item-availability__meta">
          <span v-if="link.region">Region: {{ link.region }}</span>
        </p>

        <a
          :href="link.url"
          target="_blank"
          rel="noreferrer"
          class="item-availability__button"
          @click="trackExternalLinkClick"
        >
          Open Link
        </a>
      </article>
    </div>
  </div>

  <div v-if="purchaseLinks.length" class="item-availability__panel">
    <div class="item-availability__panel-head">
      <h3>Purchase Links</h3>
      <span>{{ purchaseLinks.length }}</span>
    </div>

    <div class="item-availability__list">
      <article
        v-for="link in purchaseLinks"
        :key="`${link.provider_name}-${link.provider_type}-${link.region}-${link.url}`"
        class="item-availability__card"
      >
        <div class="item-availability__card-top">
          <h4 class="item-availability__provider">{{ link.provider_name }}</h4>

          <span class="item-availability__type">
            {{ formatProviderType(link.provider_type) }}
          </span>
        </div>

        <p class="item-availability__meta">
          <span v-if="link.region">Region: {{ link.region }}</span>
        </p>

        <a
          :href="link.url"
          target="_blank"
          rel="noreferrer"
          class="item-availability__button"
          @click="trackExternalLinkClick"
        >
          Open Link
        </a>
      </article>
    </div>
  </div>
</div>
  </section>
</template>

<style scoped>
.item-availability {
  display: grid;
  gap: 18px;
}

.item-availability__title {
  margin: 0;
  color: #f8fafc;
  font-size: 36px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.item-availability__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 18px;
}

.item-availability__panel {
  padding: 20px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
}

.item-availability__panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.item-availability__panel-head h3 {
  margin: 0;
  color: #f8fafc;
  font-size: 24px;
  line-height: 1;
}

.item-availability__panel-head span {
  min-width: 28px;
  height: 28px;
  padding: 0 8px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.8);
  color: #94a3b8;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.item-availability__list {
  display: grid;
  gap: 12px;
}

.item-availability__card {
  padding: 16px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.65);
}

.item-availability__card-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: start;
  margin-bottom: 10px;
}

.item-availability__provider {
  margin: 0;
  color: #f8fafc;
  font-size: 17px;
  line-height: 1.35;
}

.item-availability__type {
  flex: 0 0 auto;
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.14);
  color: #dbeafe;
  font-size: 12px;
  font-weight: 700;
}

.item-availability__meta {
  margin: 0 0 14px;
  color: #94a3b8;
  font-size: 14px;
}

.item-availability__button {
  min-height: 40px;
  padding: 0 14px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.12);
  color: #f8fafc;
  text-decoration: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}


@media (max-width: 640px) {
  .item-availability__card-top {
    flex-direction: column;
  }
}
</style>