<template>
  <div>
    <RouterLink to="/recipes" class="back-link">&larr; Back to recipes</RouterLink>

    <p v-if="store.loading" class="muted">Loading...</p>
    <p v-else-if="!recipe" class="muted">Recipe not found.</p>
    <RecipeCard v-else :recipe="recipe" @deleted="onDeleted" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecipesStore } from '@/stores/recipes'
import RecipeCard from '@/components/RecipeCard.vue'

const route = useRoute()
const router = useRouter()
const store = useRecipesStore()

const recipe = computed(() =>
  store.recipes.find((r) => r.id === Number(route.params.id))
)

onMounted(() => {
  if (!store.recipes.length) store.fetchAll()
})

async function onDeleted() {
  if (!recipe.value) return
  await store.remove(recipe.value.id)
  router.push('/recipes')
}
</script>

<style scoped>
.back-link { display: inline-block; margin-bottom: 1rem; color: var(--text-muted); text-decoration: none; font-size: 0.875rem; }
.back-link:hover { color: var(--accent); }
.muted { color: var(--text-muted); }
</style>
