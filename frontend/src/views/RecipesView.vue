<template>
  <div>
    <div class="header">
      <h1>Recipes</h1>
      <button class="btn-primary" @click="showImporter = !showImporter">
        {{ showImporter ? 'Cancel' : '+ Import via Ollama' }}
      </button>
    </div>

    <RecipeImporter v-if="showImporter" @saved="onSaved" />

    <p v-if="!store.loading && !store.recipes.length && !showImporter" class="muted">
      No recipes yet. Import one via Ollama.
    </p>

    <div class="list">
      <RouterLink
        v-for="recipe in store.recipes"
        :key="recipe.id"
        :to="`/recipes/${recipe.id}`"
        class="recipe-link"
      >
        <img v-if="recipe.image_url" :src="recipe.image_url" class="recipe-photo" alt="" />
        <div class="recipe-info">
          <h3>{{ recipe.name }}</h3>
          <p v-if="recipe.description" class="meta">{{ recipe.description }}</p>
          <p v-if="recipe.source" class="meta source">Source: {{ recipe.source }}</p>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRecipesStore } from '@/stores/recipes'
import RecipeImporter from '@/components/RecipeImporter.vue'

const store = useRecipesStore()
const showImporter = ref(false)

onMounted(() => store.fetchAll())

function onSaved() {
  showImporter.value = false
  store.fetchAll()
}
</script>

<style scoped>
.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
h1 { font-size: 1.4rem; }
.list { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; align-items: start; }
.muted { color: var(--text-muted); }
.recipe-link {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  padding: 0.9rem;
  border: 1px solid var(--border, #ccc);
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  background: var(--card-bg, transparent);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.recipe-link:hover {
  border-color: var(--accent);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.recipe-photo { width: 56px; height: 56px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }
.recipe-info { min-width: 0; }
h3 { font-size: 1rem; font-weight: 600; }
.meta { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.15rem; }
.source { font-style: italic; }
</style>
