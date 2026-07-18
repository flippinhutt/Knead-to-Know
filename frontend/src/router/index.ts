import { createRouter, createWebHistory } from 'vue-router'
import StartersView from '@/views/StartersView.vue'
import RecipesView from '@/views/RecipesView.vue'
import TimersView from '@/views/TimersView.vue'
import SettingsView from '@/views/SettingsView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: StartersView },
    { path: '/recipes', component: RecipesView },
    { path: '/timers', component: TimersView },
    { path: '/settings', component: SettingsView },
  ],
})
