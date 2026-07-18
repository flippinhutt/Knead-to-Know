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
      <RecipeCard
        v-for="recipe in store.recipes"
        :key="recipe.id"
        :recipe="recipe"
        @deleted="store.remove(recipe.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRecipesStore } from '@/stores/recipes'
import RecipeImporter from '@/components/RecipeImporter.vue'
import RecipeCard from '@/components/RecipeCard.vue'

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
.list { display: flex; flex-direction: column; gap: 1rem; }
.muted { color: var(--text-muted); }
</style>
