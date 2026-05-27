<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import HomeHero from '../components/home/HomeHero.vue'
import HomeRecentlyAdded from '../components/home/HomeRecentlyAdded.vue'
import HomePopularFilms from '../components/home/HomePopularFilms.vue'
import HomeForumTopics from '../components/home/HomeForumTopics.vue'
import HomePromoCta from '../components/home/HomePromoCta.vue'
import HomeRecommendedForYou from '../components/home/HomeRecommendedForYou.vue'
import type { RecentlyAddedItem, PopularFilm, HeroAction } from '../types/home'
import type { RecommendationSection } from '../types/recommendations'
import { getHomeShowcaseItems, getPopularMovieItems } from '../services/api'
import { useAuth } from '../services/auth'
import { getRecommendations } from '../services/recommendations'
import { toRecentlyAddedItem, toPopularFilm } from '../utils/home'

const heroActions: HeroAction[] = [
  {
    label: 'Explore Catalog',
    to: '/catalog',
    variant: 'primary',
  },
  {
    label: 'Visit Forum',
    to: '/forum',
    variant: 'secondary',
  },
]

const heroContent = {
  badge: 'MEDIA DISCOVERY PLATFORM',
  title: 'Find your next',
  accentTitle: 'great story',
  description:
    'Explore movies, TV series, and books in one place. Discover something worth your time instead of endlessly scrolling.',
  backgroundImage:
    'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1600&q=80',
  actions: heroActions,
}

const { isLoggedIn } = useAuth()

const recentlyAddedItems = ref<RecentlyAddedItem[]>([])
const recentItemsLoading = ref(true)
const recentItemsNote = ref('')

const popularFilms = ref<PopularFilm[]>([])
const popularFilmsLoading = ref(true)
const popularFilmsNote = ref('')

const homeRecommendationSections = ref<RecommendationSection[]>([])
const homeRecommendationsLoading = ref(false)
const homeRecommendationsNote = ref('')

const homeRecommendedSection = computed(() => {
  const sections = homeRecommendationSections.value

  return (
    sections.find((section) => {
      return section.key === 'based_on_preferences' && section.items.length > 0
    }) ??
    sections.find((section) => {
      return section.key === 'popular_now' && section.items.length > 0
    }) ??
    sections.find((section) => {
      return section.items.length > 0
    }) ??
    null
  )
})

const homeRecommendedItems = computed(() => {
  return homeRecommendedSection.value?.items.slice(0, 4) ?? []
})

const homeRecommendedStatus = computed(() => {
  return homeRecommendedSection.value?.status ?? ''
})

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
      recentItemsNote.value = 'No recent items available yet.'
      recentlyAddedItems.value = []
    }
  } catch {
    recentItemsNote.value = 'Failed to load recent items.'
    recentlyAddedItems.value = []
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
      popularFilmsNote.value = 'No popular movies available yet.'
      popularFilms.value = []
    }
  } catch {
    popularFilmsNote.value = 'Failed to load popular movies.'
    popularFilms.value = []
  } finally {
    popularFilmsLoading.value = false
  }
}

async function loadHomeRecommendations() {
  if (!isLoggedIn.value) {
    homeRecommendationSections.value = []
    homeRecommendationsNote.value = ''
    homeRecommendationsLoading.value = false
    return
  }

  homeRecommendationsLoading.value = true
  homeRecommendationsNote.value = ''

  try {
    const response = await getRecommendations({
      limit: 8,
    })

    homeRecommendationSections.value = response.sections

    if (!response.sections.some((section) => section.items.length > 0)) {
      homeRecommendationsNote.value = 'No recommendation items available yet.'
    }
  } catch {
    homeRecommendationSections.value = []
    homeRecommendationsNote.value = 'Failed to load personal recommendations.'
  } finally {
    homeRecommendationsLoading.value = false
  }
}

onMounted(() => {
  loadRecentItems()
  loadPopularFilms()
})

watch(
  () => isLoggedIn.value,
  (value) => {
    if (value) {
      loadHomeRecommendations()
      return
    }

    homeRecommendationSections.value = []
    homeRecommendationsNote.value = ''
    homeRecommendationsLoading.value = false
  },
  {
    immediate: true,
  },
)

</script>

<template>
  <div class="home-page">
    <HomeHero
      :badge="heroContent.badge"
      :title="heroContent.title"
      :accent-title="heroContent.accentTitle"
      :description="heroContent.description"
      :background-image="heroContent.backgroundImage"
      :actions="heroContent.actions"
    />

    <HomeRecentlyAdded
      :items="recentlyAddedItems"
      :is-loading="recentItemsLoading"
      :note="recentItemsNote"
    />

    <HomeRecommendedForYou
      v-if="isLoggedIn"
      :items="homeRecommendedItems"
      :status="homeRecommendedStatus"
      :is-loading="homeRecommendationsLoading"
      :note="homeRecommendationsNote"
    />

    <section class="home-page__feature-grid">
      <HomePopularFilms
        :films="popularFilms"
        :is-loading="popularFilmsLoading"
        :note="popularFilmsNote"
      />
    </section>

    <section class="home-page__section">
      <HomeForumTopics />
    </section>

    <section class="home-page__section">
      <HomePromoCta />
    </section>
  </div>
</template>

<style scoped>
.home-page {
  width: 100%;
  padding-bottom: 32px;
}

.home-page__feature-grid,
.home-page__section {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
}

.home-page__feature-grid {
  padding: 12px 0 28px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 22px;
}

.home-page__section {
  padding: 0 0 28px;
}

@media (max-width: 900px) {
  .home-page__feature-grid,
  .home-page__section {
    width: min(100%, calc(100% - 32px));
  }
}
</style>