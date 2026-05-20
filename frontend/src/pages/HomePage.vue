<script setup lang="ts">
import { onMounted, ref } from 'vue'
import HomeHero from '../components/home/HomeHero.vue'
import HomeRecentlyAdded from '../components/home/HomeRecentlyAdded.vue'
import HomePopularFilms from '../components/home/HomePopularFilms.vue'
import HomeForumTopics from '../components/home/HomeForumTopics.vue'
import HomePromoSection from '../components/home/HomePromoSection.vue'
import { homePageData } from '../mocks/home'
import type { RecentlyAddedItem, PopularFilm } from '../types/home'
import { getHomeShowcaseItems, getPopularMovieItems } from '../services/api'
import { toRecentlyAddedItem, toPopularFilm } from '../utils/home'

const recentlyAddedItems = ref<RecentlyAddedItem[]>(homePageData.recentlyAdded)
const recentItemsLoading = ref(true)
const recentItemsNote = ref('')

const popularFilms = ref<PopularFilm[]>(homePageData.popularFilms)
const popularFilmsLoading = ref(true)
const popularFilmsNote = ref('')

async function loadRecentItems() {
  recentItemsLoading.value = true
  recentItemsNote.value = ''

  try {
    const items = await getHomeShowcaseItems(5)

    if (items.length > 0) {
      recentlyAddedItems.value = items.map((item, index) =>
        toRecentlyAddedItem(item, index),
      )
    } else {
      recentItemsNote.value = 'No recent items came from the API, so demo content is shown.'
    }
  } catch {
    recentItemsNote.value = 'API is unavailable right now, so demo content is shown.'
  } finally {
    recentItemsLoading.value = false
  }
}

async function loadPopularFilms() {
  popularFilmsLoading.value = true
  popularFilmsNote.value = ''

  try {
    const items = await getPopularMovieItems(4)

    if (items.length > 0) {
      popularFilms.value = items.map((item, index) => toPopularFilm(item, index))
    } else {
      popularFilmsNote.value = 'No movie data came from the API, so demo content is shown.'
    }
  } catch {
    popularFilmsNote.value = 'API is unavailable right now, so demo content is shown.'
  } finally {
    popularFilmsLoading.value = false
  }
}

onMounted(() => {
  loadRecentItems()
  loadPopularFilms()
})
</script>

<template>
  <div class="home-page">
    <HomeHero
      :badge="homePageData.hero.badge"
      :title="homePageData.hero.title"
      :accent-title="homePageData.hero.accentTitle"
      :description="homePageData.hero.description"
      :background-image="homePageData.hero.backgroundImage"
      :actions="homePageData.hero.actions"
    />

    <HomeRecentlyAdded
      :items="recentlyAddedItems"
      :is-loading="recentItemsLoading"
      :note="recentItemsNote"
    />

    <section class="home-page__feature-grid">
      <HomePopularFilms
        :films="popularFilms"
        :is-loading="popularFilmsLoading"
        :note="popularFilmsNote"
      />
      <HomeForumTopics :topics="homePageData.hotTopics" />
    </section>

    <HomePromoSection :tiles="homePageData.promoTiles" />
  </div>
</template>

<style scoped>
.home-page {
  width: 100%;
  padding-bottom: 32px;
}

.home-page__feature-grid {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding: 12px 0 28px;
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 22px;
}

@media (max-width: 1100px) {
  .home-page__feature-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .home-page__feature-grid {
    width: min(100%, calc(100% - 32px));
  }
}
</style>