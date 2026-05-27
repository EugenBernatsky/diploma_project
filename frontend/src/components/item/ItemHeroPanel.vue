<script setup lang="ts">
import type { MediaItem } from '../../types/media'
import {
  getHeroChips,
  getHeroFacts,
  getItemActions,
  getItemSubtitle,
  getOriginalDisplayTitle,
} from '../../utils/itemDetails'
import { getItemImage } from '../../utils/catalog'
import ItemQuickActions from './ItemQuickActions.vue'
import { useAuth } from '../../services/auth'
import { createInteraction } from '../../services/interactions'

const props = defineProps<{
  item: MediaItem
  source?: string | null
}>()

const emit = defineEmits<{
  (e: 'stats-changed'): void
}>()

const { isLoggedIn } = useAuth()

const posterImage = getItemImage(props.item)
const subtitle = getItemSubtitle(props.item)
const originalDisplayTitle = getOriginalDisplayTitle(props.item)
const heroChips = getHeroChips(props.item)
const heroFacts = getHeroFacts(props.item)
const actions = getItemActions(props.item).filter((action) => {
  const label = action.label.toLowerCase()
  const homepage = props.item.homepage?.trim()

  if (homepage && action.href === homepage) {
    return false
  }

  if (label.includes('homepage')) {
    return false
  }

  return true
})

function trackExternalActionClick() {
  if (!isLoggedIn.value) {
    return
  }

  void createInteraction({
    item_id: props.item.id,
    interaction_type: 'external_link_click',
    source: 'item_page',
  }).catch(() => {
    // external links should stay fast even if tracking fails
  })
}
</script>

<template>
  <section class="item-hero">
    <div class="item-hero__heading">
      <h1 class="item-hero__title">{{ item.title }}</h1>

      <p v-if="originalDisplayTitle" class="item-hero__original-title">
        {{ originalDisplayTitle }}
      </p>

      <p v-if="subtitle" class="item-hero__subtitle">{{ subtitle }}</p>
    </div>

    <div class="item-hero__layout">
        <div class="item-hero__poster-column">
            <div class="item-hero__poster">
              <img :src="posterImage" :alt="item.title" />
            </div>

            <ItemQuickActions
              :item-id="item.id"
              :homepage-url="item.homepage"
              :source="source"
              @changed="emit('stats-changed')"
            />

            <div v-if="actions.length" class="item-hero__actions">
              <a
                v-for="action in actions"
                :key="`${action.label}-${action.href}`"
                :href="action.href"
                target="_blank"
                rel="noreferrer"
                class="item-hero__action"
                :class="{
                  'item-hero__action--primary': action.variant === 'primary',
                  'item-hero__action--secondary': action.variant === 'secondary',
                }"
                @click="trackExternalActionClick"
              >
                {{ action.label }}
              </a>
            </div>
          </div>

      <div class="item-hero__content">
        <div v-if="heroChips.length" class="item-hero__chips">
          <div
            v-for="chip in heroChips"
            :key="`${chip.label}-${chip.value}`"
            class="item-hero__chip"
          >
            <span class="item-hero__chip-label">{{ chip.label }}</span>
            <span class="item-hero__chip-value">{{ chip.value }}</span>
          </div>
        </div>

        <div v-if="item.genres.length" class="item-hero__genres">
          <span
            v-for="genre in item.genres"
            :key="genre"
            class="item-hero__genre"
          >
            {{ genre }}
          </span>
        </div>

        <div v-if="heroFacts.length" class="item-hero__facts">
          <div
            v-for="fact in heroFacts"
            :key="`${fact.label}-${fact.value}`"
            class="item-hero__fact"
          >
            <p class="item-hero__fact-label">{{ fact.label }}</p>

            <a
              v-if="fact.href"
              :href="fact.href"
              target="_blank"
              rel="noreferrer"
              class="item-hero__fact-link"
            >
              {{ fact.value }}
            </a>

            <p v-else class="item-hero__fact-value">
              {{ fact.value }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.item-hero {
  display: grid;
  gap: 24px;
  padding-top: 8px;
}

.item-hero__heading {
  display: grid;
  gap: 8px;
}

.item-hero__title {
  margin: 0;
  color: #f8fafc;
  font-size: clamp(42px, 5vw, 68px);
  line-height: 0.95;
  letter-spacing: -0.04em;
}

.item-hero__original-title {
  margin: 0;
  color: #94a3b8;
  font-size: 24px;
  line-height: 1.35;
  font-weight: 500;
}

.item-hero__subtitle {
  margin: 0;
  color: #60a5fa;
  font-size: 22px;
  line-height: 1.5;
  font-style: italic;
}

.item-hero__layout {
  display: grid;
  grid-template-columns: 290px minmax(0, 1fr);
  gap: 30px;
}

.item-hero__poster-column {
  display: grid;
  align-content: start;
  gap: 16px;
}

.item-hero__poster {
  overflow: hidden;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.72);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
}

.item-hero__poster img {
  width: 100%;
  display: block;
  aspect-ratio: 0.74 / 1;
  object-fit: cover;
}

.item-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.item-hero__action {
  flex: 1 1 140px;
  min-height: 48px;
  border-radius: 14px;
  text-decoration: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  transition:
    transform 0.18s ease,
    border-color 0.18s ease;
}

.item-hero__action:hover {
  transform: translateY(-1px);
}

.item-hero__action--primary {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
}

.item-hero__action--secondary {
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(15, 23, 42, 0.8);
  color: #f8fafc;
}

.item-hero__content {
  min-width: 0;
}

.item-hero__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
}

.item-hero__chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(15, 23, 42, 0.72);
}

.item-hero__chip-label {
  color: #64748b;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
}

.item-hero__chip-value {
  color: #f8fafc;
  font-size: 14px;
  font-weight: 700;
}

.item-hero__genres {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 26px;
}

.item-hero__genre {
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.12);
  border: 1px solid rgba(96, 165, 250, 0.18);
  color: #dbeafe;
  font-size: 13px;
  font-weight: 600;
}

.item-hero__facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px 28px;
  padding-top: 22px;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
}

.item-hero__fact-label {
  margin: 0 0 6px;
  color: #64748b;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
}

.item-hero__fact-value,
.item-hero__fact-link {
  margin: 0;
  color: #f8fafc;
  font-size: 18px;
  line-height: 1.5;
  text-decoration: none;
  font-weight: 600;
  word-break: break-word;
}

.item-hero__fact-link:hover {
  color: #60a5fa;
}

@media (max-width: 980px) {
  .item-hero__layout {
    grid-template-columns: 1fr;
  }

  .item-hero__poster-column {
    max-width: 340px;
  }
}

@media (max-width: 640px) {
  .item-hero__facts {
    grid-template-columns: 1fr;
  }

  .item-hero__subtitle {
    font-size: 18px;
  }

  .item-hero__original-title {
    font-size: 18px;
  }
}
</style>