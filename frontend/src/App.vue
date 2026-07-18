<template>
  <div class="layout">
    <nav class="nav">
      <span class="nav-brand">Knead to Know</span>
      <RouterLink to="/" :class="{ active: route.path === '/' }">Starters</RouterLink>
      <RouterLink to="/recipes" :class="{ active: route.path === '/recipes' }">Recipes</RouterLink>
      <RouterLink to="/timers" :class="{ active: route.path === '/timers' }">Timers</RouterLink>
      <RouterLink to="/bakes" :class="{ active: route.path === '/bakes' }">Bakes</RouterLink>
      <RouterLink to="/chat" :class="{ active: route.path === '/chat' }">Chat</RouterLink>
      <RouterLink to="/hydration" :class="{ active: route.path === '/hydration' }">Hydration</RouterLink>
      <RouterLink to="/settings" :class="{ active: route.path === '/settings' }">Settings</RouterLink>
      <button class="theme-toggle" @click="theme.toggle" :title="theme.dark ? 'Light mode' : 'Dark mode'">
        {{ theme.dark ? '☀' : '◑' }}
      </button>
    </nav>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
const route = useRoute()
const theme = useThemeStore()
</script>

<style scoped>
.layout { display: flex; flex-direction: column; min-height: 100vh; }

.nav {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.nav-brand { font-weight: 700; color: var(--accent); margin-right: auto; font-size: 1.1rem; }
.theme-toggle { background: none; border: 1px solid var(--border); color: var(--text-muted); padding: 0.2rem 0.5rem; border-radius: var(--radius); cursor: pointer; font-size: 1rem; line-height: 1; }

.nav a { color: var(--text-muted); font-size: 0.9rem; font-weight: 500; }
.nav a.active, .nav a:hover { color: var(--accent); }

.main { max-width: 960px; width: 100%; margin: 0 auto; padding: 1.5rem; }
</style>
