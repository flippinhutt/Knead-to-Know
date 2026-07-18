import { defineStore } from 'pinia'
import { ref } from 'vue'
import { recipesApi } from '@/api/recipes'
import type { Recipe, RecipeImportPreview, RecipeStep } from '@/types'

export const useRecipesStore = defineStore('recipes', () => {
  const recipes = ref<Recipe[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      recipes.value = await recipesApi.list()
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function create(data: { name: string; description?: string; source?: string; steps?: RecipeStep[] }) {
    const recipe = await recipesApi.create(data)
    recipes.value = [...recipes.value, recipe]
    return recipe
  }

  async function remove(id: number) {
    await recipesApi.remove(id)
    recipes.value = recipes.value.filter((r) => r.id !== id)
  }

  async function importFromText(raw_text: string, model?: string): Promise<RecipeImportPreview> {
    return recipesApi.import(raw_text, model)
  }

  return { recipes, loading, error, fetchAll, create, remove, importFromText }
})
