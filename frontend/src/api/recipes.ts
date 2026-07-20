import type { Recipe, RecipeImportPreview, RecipeIngredient, RecipeStep } from '@/types'
import { apiFetch } from './index'

export const recipesApi = {
  list: () => apiFetch<Recipe[]>('/recipes/'),
  get: (id: number) => apiFetch<Recipe>(`/recipes/${id}`),
  create: (data: { name: string; description?: string; source?: string; image_url?: string; steps?: RecipeStep[]; ingredients?: RecipeIngredient[] }) =>
    apiFetch<Recipe>('/recipes/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: Partial<{ name: string; description: string; source: string; image_url: string }>) =>
    apiFetch<Recipe>(`/recipes/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  remove: (id: number) => apiFetch<void>(`/recipes/${id}`, { method: 'DELETE' }),
  replaceSteps: (id: number, steps: Array<{ order: number; description: string; duration_minutes?: number | null }>) =>
    apiFetch<Recipe>(`/recipes/${id}/steps`, { method: 'PUT', body: JSON.stringify({ steps }) }),
  replaceIngredients: (id: number, ingredients: Array<{ order: number; name: string; amount?: string | null }>) =>
    apiFetch<Recipe>(`/recipes/${id}/ingredients`, { method: 'PUT', body: JSON.stringify({ ingredients }) }),
  import: (params: { raw_text?: string; url?: string; model?: string }) =>
    apiFetch<RecipeImportPreview>('/recipes/import', {
      method: 'POST',
      body: JSON.stringify(params),
    }),
}
