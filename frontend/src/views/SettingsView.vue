<template>
  <div>
    <h1 style="margin-bottom:1.25rem">Settings</h1>

    <div class="card" style="margin-bottom:1rem">
      <h2 style="margin-bottom:0.75rem;font-size:1rem">Ollama Connection</h2>
      <div v-if="store.config">
        <div style="margin-bottom:0.5rem">
          <label>Server URL</label>
          <input v-model="urlInput" @blur="saveUrl" />
        </div>
        <div>
          <label>Active Model</label>
          <select v-model="modelInput" @change="saveModel">
            <option v-for="m in store.models" :key="m.name" :value="m.name">{{ m.name }}</option>
            <option v-if="!store.models.length" :value="store.config.ollama_model">{{ store.config.ollama_model }}</option>
          </select>
        </div>
        <p v-if="saved" class="saved-msg">Saved.</p>
      </div>
      <p v-else class="muted">Loading config…</p>
    </div>

    <div class="card" style="margin-bottom:1rem">
      <h2 style="margin-bottom:0.75rem;font-size:1rem">Units</h2>
      <p class="unit-section-label">Weight</p>
      <div class="unit-row">
        <label v-for="u in unitOptions" :key="u.value" class="unit-option">
          <input type="radio" :value="u.value" v-model="selectedUnit" @change="units.setUnit(u.value as any)" />
          {{ u.label }}
        </label>
      </div>
      <p class="muted" style="font-size:0.78rem;margin-top:0.4rem">Cups are approximate (240g = 1 cup). Grams recommended for precision baking.</p>
      <p class="unit-section-label" style="margin-top:0.75rem">Temperature</p>
      <div class="unit-row">
        <label v-for="t in tempOptions" :key="t.value" class="unit-option">
          <input type="radio" :value="t.value" v-model="selectedTempUnit" @change="units.setTempUnit(t.value as any)" />
          {{ t.label }}
        </label>
      </div>
    </div>

    <div class="card" style="margin-bottom:1rem">
      <h2 style="margin-bottom:0.75rem;font-size:1rem">Data</h2>
      <p class="muted" style="margin-bottom:0.75rem;font-size:0.82rem">Download or restore all starters, feedings, recipes, and bakes.</p>
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;align-items:center">
        <a class="btn-primary btn-sm" href="/api/export/" download="knead-to-know-export.json">Download Backup</a>
        <label class="btn-secondary btn-sm" style="cursor:pointer">
          Import Backup
          <input type="file" accept=".json" style="display:none" @change="importFile" />
        </label>
        <span v-if="importMsg" :class="importMsg.ok ? 'ok-msg' : 'error'">{{ importMsg.text }}</span>
      </div>
    </div>

    <div class="card">
      <h2 style="margin-bottom:0.75rem;font-size:1rem">Available Models</h2>
      <button class="btn-secondary btn-sm" style="margin-bottom:0.75rem" :disabled="store.loading" @click="store.fetchModels()">
        {{ store.loading ? 'Loading…' : 'Refresh' }}
      </button>

      <div v-if="store.models.length" class="model-list">
        <div v-for="m in store.models" :key="m.name" class="model-row">
          <span>{{ m.name }}</span>
          <span class="tag">{{ formatSize(m.size) }}</span>
        </div>
      </div>
      <p v-else class="muted">No models found on server.</p>

      <div style="margin-top:1rem;border-top:1px solid var(--border);padding-top:0.75rem">
        <h3 style="font-size:0.9rem;margin-bottom:0.5rem">Pull a Model</h3>
        <div style="display:flex;gap:0.5rem">
          <input v-model="pullName" placeholder="e.g. llama3, mistral" style="flex:1" />
          <button class="btn-primary" :disabled="!pullName || store.pulling" @click="doPull">
            {{ store.pulling ? 'Pulling…' : 'Pull' }}
          </button>
        </div>
        <pre v-if="store.pullLog.length" class="pull-log">{{ store.pullLog.slice(-10).join('') }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useOllamaStore } from '@/stores/ollama'
import { useUnitsStore } from '@/stores/units'
import { apiFetch } from '@/api'

const store = useOllamaStore()
const units = useUnitsStore()
const selectedUnit = ref(units.unit)
const selectedTempUnit = ref(units.tempUnit)
const unitOptions = [
  { value: 'g', label: 'Grams (g)' },
  { value: 'oz', label: 'Ounces (oz)' },
  { value: 'cup', label: 'Cups (approx)' },
]
const tempOptions = [
  { value: 'f', label: 'Fahrenheit (°F)' },
  { value: 'c', label: 'Celsius (°C)' },
]
const importMsg = ref<{ ok: boolean; text: string } | null>(null)

async function importFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  try {
    const json = JSON.parse(await file.text())
    const res = await apiFetch<{ imported: Record<string, number> }>('/import/', {
      method: 'POST',
      body: JSON.stringify(json),
    })
    const i = res.imported
    importMsg.value = { ok: true, text: `Imported: ${i.starters} starters, ${i.recipes} recipes, ${i.bakes} bakes` }
  } catch (err) {
    importMsg.value = { ok: false, text: `Import failed: ${(err as Error).message}` }
  }
  ;(e.target as HTMLInputElement).value = ''
}

const urlInput = ref('')
const modelInput = ref('')
const pullName = ref('')
const saved = ref(false)

onMounted(async () => {
  await store.fetchConfig()
  await store.fetchModels()
  urlInput.value = store.config?.ollama_base_url ?? ''
  modelInput.value = store.config?.ollama_model ?? ''
})

watch(() => store.config, (c) => {
  if (c) { urlInput.value = c.ollama_base_url; modelInput.value = c.ollama_model }
})

async function saveUrl() {
  if (urlInput.value === store.config?.ollama_base_url) return
  await store.updateConfig({ ollama_base_url: urlInput.value })
  flash()
}

async function saveModel() {
  await store.updateConfig({ ollama_model: modelInput.value })
  flash()
}

async function doPull() {
  await store.pullModel(pullName.value)
  pullName.value = ''
}

function flash() { saved.value = true; setTimeout(() => (saved.value = false), 1500) }

function formatSize(bytes: number | null) {
  if (!bytes) return '?'
  return `${(bytes / 1e9).toFixed(1)} GB`
}
</script>

<style scoped>
h1 { font-size: 1.4rem; }
.unit-section-label { font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.3rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.unit-row { display: flex; gap: 1.25rem; }
.unit-option { display: flex; align-items: center; gap: 0.35rem; font-size: 0.875rem; cursor: pointer; }
.unit-option input { width: auto; }
.ok-msg { color: var(--success); font-size: 0.82rem; }
.model-list { display: flex; flex-direction: column; gap: 0.4rem; }
.model-row { display: flex; align-items: center; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid var(--border); }
.muted { color: var(--text-muted); font-size: 0.875rem; }
.saved-msg { color: var(--success); font-size: 0.8rem; margin-top: 0.4rem; }
.pull-log {
  margin-top: 0.5rem;
  background: #1a1a1a;
  color: #d4d4d4;
  padding: 0.6rem;
  border-radius: var(--radius);
  font-size: 0.75rem;
  overflow-x: auto;
  max-height: 150px;
  overflow-y: auto;
}
</style>
