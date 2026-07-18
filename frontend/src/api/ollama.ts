import type { OllamaConfig, OllamaModel } from '@/types'
import { apiFetch } from './index'

export const ollamaApi = {
  getConfig: () => apiFetch<OllamaConfig>('/ollama/config'),
  updateConfig: (data: Partial<OllamaConfig>) =>
    apiFetch<OllamaConfig>('/ollama/config', { method: 'PATCH', body: JSON.stringify(data) }),
  listModels: () => apiFetch<OllamaModel[]>('/ollama/models'),
  pullModel: async (model: string, onChunk: (chunk: string) => void): Promise<void> => {
    const res = await fetch('/api/ollama/pull', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model }),
    })
    if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`)
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      onChunk(decoder.decode(value, { stream: true }))
    }
  },
}
