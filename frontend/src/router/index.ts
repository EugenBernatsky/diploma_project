import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../pages/HomePage.vue'
import CatalogPage from '../pages/CatalogPage.vue'
import ItemDetailsPage from '../pages/ItemDetailsPage.vue'
import RecommendationsPage from '../pages/RecommendationsPage.vue'
import ForumPage from '../pages/ForumPage.vue'
import ProfilePage from '../pages/ProfilePage.vue'
import LoginPage from '../pages/LoginPage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import { isAuthenticated } from '../services/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/catalog', name: 'catalog', component: CatalogPage },
    { path: '/items/:id', name: 'item-details', component: ItemDetailsPage },
    {
      path: '/recommendations',
      name: 'recommendations',
      component: RecommendationsPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/forum',
      name: 'forum',
      component: ForumPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfilePage,
      meta: { requiresAuth: true },
    },
    { path: '/login', name: 'login', component: LoginPage },
    { path: '/register', name: 'register', component: RegisterPage },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach((to) => {
  const loggedIn = isAuthenticated()

  if (to.meta.requiresAuth && !loggedIn) {
    return { name: 'login' }
  }

  if ((to.name === 'login' || to.name === 'register') && loggedIn) {
    return { name: 'profile' }
  }
})

export default router