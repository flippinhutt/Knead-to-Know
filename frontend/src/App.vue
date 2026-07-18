<template>
  <div class="layout">
    <nav class="nav">
      <span class="nav-brand">Sourdough</span>
      <RouterLink to="/" :class="{ active: route.path === '/' }">Starters</RouterLink>
      <RouterLink to="/recipes" :class="{ active: route.path === '/recipes' }">Recipes</RouterLink>
      <RouterLink to="/timers" :class="{ active: route.path === '/timers' }">Timers</RouterLink>
      <RouterLink to="/settings" :class="{ active: route.path === '/settings' }">Settings</RouterLink>
    </nav>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
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

.nav a { color: var(--text-muted); font-size: 0.9rem; font-weight: 500; }
.nav a.active, .nav a:hover { color: var(--accent); }

.main { max-width: 960px; width: 100%; margin: 0 auto; padding: 1.5rem; }
</style>
