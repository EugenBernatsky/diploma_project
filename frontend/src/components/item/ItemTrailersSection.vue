<script setup lang="ts">
import { useAuth } from '../../services/auth'
import { createInteraction } from '../../services/interactions'
import type { MediaTrailer } from '../../types/media'

const props = defineProps<{
  itemId: string
  trailers: MediaTrailer[]
}>()

const { isLoggedIn } = useAuth()

function extractYouTubeVideoId(url: string): string | null {
  try {
    const parsedUrl = new URL(url)

    if (parsedUrl.hostname.includes('youtu.be')) {
      return parsedUrl.pathname.replace('/', '') || null
    }

    if (parsedUrl.hostname.includes('youtube.com')) {
      if (parsedUrl.pathname === '/watch') {
        return parsedUrl.searchParams.get('v')
      }

      if (parsedUrl.pathname.startsWith('/embed/')) {
        return parsedUrl.pathname.split('/embed/')[1] || null
      }

      if (parsedUrl.pathname.startsWith('/shorts/')) {
        return parsedUrl.pathname.split('/shorts/')[1] || null
      }
    }

    return null
  } catch {
    return null
  }
}

function getEmbedUrl(url: string): string | null {
  const videoId = extractYouTubeVideoId(url)
  if (!videoId) return null

  return `https://www.youtube.com/embed/${videoId}`
}

function trackTrailerClick() {
  if (!isLoggedIn.value) {
    return
  }

  void createInteraction({
    item_id: props.itemId,
    interaction_type: 'trailer_click',
    source: 'item_page',
  }).catch(() => {
    // interaction logging should not block user navigation
  })
}
</script>

<template>
  <section class="item-trailers">
    <div class="item-trailers__header">
      <h2 class="item-trailers__title">Trailers</h2>
      <p class="item-trailers__count">{{ trailers.length }} available</p>
    </div>

    <div v-if="trailers.length" class="item-trailers__grid">
      <article
        v-for="trailer in trailers"
        :key="`${trailer.name}-${trailer.url}`"
        class="item-trailers__card"
      >
        <div class="item-trailers__card-top">
          <div>
            <h3 class="item-trailers__card-title">{{ trailer.name }}</h3>
            <p class="item-trailers__meta">
              <span>{{ trailer.site }}</span>
              <span v-if="trailer.language">• {{ trailer.language.toUpperCase() }}</span>
            </p>
          </div>

          <a
            :href="trailer.url"
            target="_blank"
            rel="noreferrer"
            class="item-trailers__open-link"
            @click="trackTrailerClick"
          >
            Open
          </a>
        </div>

        <div v-if="getEmbedUrl(trailer.url)" class="item-trailers__player-wrap" @click.capture="trackTrailerClick">
          <iframe
            class="item-trailers__player"
            :src="getEmbedUrl(trailer.url) || undefined"
            :title="trailer.name"
            loading="lazy"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
          />
        </div>

        <div v-else class="item-trailers__fallback">
          <p>This trailer cannot be embedded here.</p>
        </div>
      </article>
    </div>

    <div v-else class="item-trailers__empty">
      No trailers available yet.
    </div>
  </section>
</template>

<style scoped>
.item-trailers {
  display: grid;
  gap: 18px;
}

.item-trailers__header {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 16px;
}

.item-trailers__title {
  margin: 0;
  color: #f8fafc;
  font-size: 36px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.item-trailers__count {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

.item-trailers__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.item-trailers__card {
  padding: 20px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
}

.item-trailers__card-top {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
  margin-bottom: 14px;
}

.item-trailers__card-title {
  margin: 0 0 6px;
  color: #f8fafc;
  font-size: 20px;
  line-height: 1.3;
}

.item-trailers__meta {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

.item-trailers__open-link {
  flex: 0 0 auto;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #e2e8f0;
  text-decoration: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.item-trailers__player-wrap {
  overflow: hidden;
  border-radius: 18px;
  background: #020617;
  aspect-ratio: 16 / 9;
}

.item-trailers__player {
  width: 100%;
  height: 100%;
  border: 0;
  display: block;
}

.item-trailers__fallback,
.item-trailers__empty {
  padding: 20px;
  border-radius: 18px;
  border: 1px dashed rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.45);
  color: #94a3b8;
}

@media (max-width: 980px) {
  .item-trailers__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .item-trailers__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .item-trailers__card-top {
    flex-direction: column;
  }
}
</style>