import { createRouter, createWebHistory } from 'vue-router'
import StartersView from '@/views/StartersView.vue'
import RecipesView from '@/views/RecipesView.vue'
import RecipeDetailView from '@/views/RecipeDetailView.vue'
import TimersView from '@/views/TimersView.vue'
import BakesView from '@/views/BakesView.vue'
import ChatView from '@/views/ChatView.vue'
import CalculatorsView from '@/views/CalculatorsView.vue'
import SettingsView from '@/views/SettingsView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: StartersView },
    { path: '/recipes', component: RecipesView },
    { path: '/recipes/:id', component: RecipeDetailView },
    { path: '/timers', component: TimersView },
    { path: '/bakes', component: BakesView },
    { path: '/chat', component: ChatView },
    { path: '/calculators', component: CalculatorsView },
    { path: '/hydration', redirect: '/calculators' },
    { path: '/settings', component: SettingsView },
  ],
})
