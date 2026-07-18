import { defineStore } from 'pinia'
import { ref } from 'vue'
import { timersApi } from '@/api/timers'
import type { Timer } from '@/types'

export const useTimersStore = defineStore('timers', () => {
  const timers = ref<Timer[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      timers.value = await timersApi.list()
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function create(data: { name: string; duration_minutes: number; recipe_step_id?: number }) {
    const timer = await timersApi.create(data)
    timers.value = [...timers.value, timer]
    return timer
  }

  async function start(id: number) {
    const updated = await timersApi.start(id)
    timers.value = timers.value.map((t) => (t.id === id ? updated : t))
  }

  async function stop(id: number) {
    const updated = await timersApi.stop(id)
    timers.value = timers.value.map((t) => (t.id === id ? updated : t))
  }

  async function remove(id: number) {
    await timersApi.remove(id)
    timers.value = timers.value.filter((t) => t.id !== id)
  }

  return { timers, loading, error, fetchAll, create, start, stop, remove }
})
