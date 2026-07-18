import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ollamaApi } from '@/api/ollama'
import type { OllamaConfig, OllamaModel } from '@/types'

export const useOllamaStore = defineStore('ollama', () => {
  const models = ref<OllamaModel[]>([])
  const config = ref<OllamaConfig | null>(null)
  const pullLog = ref<string[]>([])
  const pulling = ref(false)
  const loading = ref(false)

  async function fetchConfig() {
    config.value = await ollamaApi.getConfig()
  }

  async function fetchModels() {
    loading.value = true
    try {
      models.value = await ollamaApi.listModels()
    } finally {
      loading.value = false
    }
  }

  async function updateConfig(data: Partial<OllamaConfig>) {
    config.value = await ollamaApi.updateConfig(data)
  }

  async function pullModel(model: string) {
    pulling.value = true
    pullLog.value = []
    try {
      await ollamaApi.pullModel(model, (chunk) => {
        pullLog.value = [...pullLog.value, chunk]
      })
      await fetchModels()
    } finally {
      pulling.value = false
    }
  }

  return { models, config, pullLog, pulling, loading, fetchConfig, fetchModels, updateConfig, pullModel }
})
