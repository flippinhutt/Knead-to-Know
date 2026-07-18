import { defineStore } from 'pinia'
import { ref } from 'vue'
import { startersApi } from '@/api/starters'
import type { Feeding, Starter } from '@/types'

export const useStartersStore = defineStore('starters', () => {
  const starters = ref<Starter[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      starters.value = await startersApi.list()
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function create(data: { name: string; description?: string; hydration_percent?: number }) {
    const starter = await startersApi.create(data)
    starters.value = [...starters.value, starter]
    return starter
  }

  async function update(id: number, data: Partial<{ name: string; description: string; hydration_percent: number; feed_interval_hours: number }>) {
    const updated = await startersApi.update(id, data)
    starters.value = starters.value.map((s) => (s.id === id ? updated : s))
    return updated
  }

  async function remove(id: number) {
    await startersApi.remove(id)
    starters.value = starters.value.filter((s) => s.id !== id)
  }

  async function addFeeding(starterId: number, data: { flour_grams?: number; water_grams?: number; starter_grams?: number; height_mm?: number; notes?: string }): Promise<Feeding> {
    const feeding = await startersApi.addFeeding(starterId, data)
    starters.value = starters.value.map((s) =>
      s.id === starterId ? { ...s, feedings: [feeding, ...s.feedings] } : s,
    )
    return feeding
  }

  return { starters, loading, error, fetchAll, create, update, remove, addFeeding }
})
