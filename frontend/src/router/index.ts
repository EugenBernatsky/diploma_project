import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import CatalogPage from '../pages/CatalogPage.vue'
import ItemDetailsPage from '../pages/ItemDetailsPage.vue'
import RecommendationsPage from '../pages/RecommendationsPage.vue'
import ForumPage from '../pages/ForumPage.vue'
import ProfilePage from '../pages/ProfilePage.vue'
import LoginPage from '../pages/LoginPage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import { useAuth } from '../services/auth'
import ForumThreadPage from '../pages/ForumThreadPage.vue'
import NewDiscussionPage from '../pages/NewDiscussionPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomePage },
    { path: '/catalog', component: CatalogPage },
    { path: '/items/:id', component: ItemDetailsPage },
    {
      path: '/recommendations',
      component: RecommendationsPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/forum',
      component: ForumPage,
    },
    {
      path: '/profile',
      component: ProfilePage,
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      component: LoginPage,
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      component: RegisterPage,
      meta: { guestOnly: true },
    },
    {
      path: '/forum/new',
      component: NewDiscussionPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/forum/threads/:id',
      component: ForumThreadPage,
    },
  ],
})

router.beforeEach(async (to) => {
  const { initializeAuth, isLoggedIn } = useAuth()

  await initializeAuth()

  if (to.meta.requiresAuth && !isLoggedIn.value) {
    return {
      path: '/login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (to.meta.guestOnly && isLoggedIn.value) {
    return { path: '/' }
  }

  return true
})

export default router