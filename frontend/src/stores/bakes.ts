import { defineStore } from 'pinia'
import { ref } from 'vue'
import { bakesApi } from '@/api/bakes'
import type { Bake } from '@/types'

export const useBakesStore = defineStore('bakes', () => {
  const bakes = ref<Bake[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      bakes.value = await bakesApi.list()
    } finally {
      loading.value = false
    }
  }

  async function create(data: Partial<Bake>) {
    const bake = await bakesApi.create(data)
    bakes.value = [bake, ...bakes.value]
    return bake
  }

  async function remove(id: number) {
    await bakesApi.remove(id)
    bakes.value = bakes.value.filter((b) => b.id !== id)
  }

  return { bakes, loading, fetchAll, create, remove }
})
