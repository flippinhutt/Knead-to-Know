<template>
  <div class="card" style="margin-bottom:1rem">
    <h2 style="margin-bottom:0.75rem;font-size:1rem">Import Recipe via Ollama</h2>

    <div v-if="!preview">
      <div style="margin-bottom:0.5rem">
        <label>Model</label>
        <select v-model="selectedModel">
          <option v-for="m in ollamaStore.models" :key="m.name" :value="m.name">{{ m.name }}</option>
        </select>
      </div>
      <div class="mode-toggle" style="margin-bottom:0.75rem">
        <button :class="['mode-btn', mode === 'text' && 'active']" @click="mode = 'text'">Paste text</button>
        <button :class="['mode-btn', mode === 'url' && 'active']" @click="mode = 'url'">From URL</button>
      </div>
      <template v-if="mode === 'text'">
        <label>Paste recipe text</label>
        <textarea v-model="rawText" rows="8" placeholder="Paste your sourdough recipe here..." style="margin-bottom:0.5rem" />
      </template>
      <template v-else>
        <label>Recipe URL</label>
        <input v-model="url" type="url" placeholder="https://www.example.com/sourdough-recipe" style="margin-bottom:0.5rem" />
        <p class="hint">The page will be fetched on the server and parsed by Ollama.</p>
      </template>
      <div class="btn-row">
        <button class="btn-secondary" @click="$emit('saved')">Cancel</button>
        <button class="btn-primary" :disabled="!canImport || loading" @click="doImport">
          {{ loading ? 'Fetching & parsing…' : 'Parse Recipe' }}
        </button>
      </div>
      <p v-if="error" class="error" style="margin-top:0.5rem">{{ error }}</p>
    </div>

    <div v-else>
      <h3 style="margin-bottom:0.25rem">{{ preview.name }}</h3>
      <p v-if="preview.description" class="meta" style="margin-bottom:0.75rem">{{ preview.description }}</p>
      <div class="steps">
        <div v-for="step in preview.steps" :key="step.order" class="step">
          <span class="step-num">{{ step.order }}</span>
          <span class="step-text">{{ step.description }}</span>
          <span v-if="step.duration_minutes" class="tag">{{ step.duration_minutes }}m</span>
        </div>
      </div>
      <div class="btn-row" style="margin-top:0.75rem">
        <button class="btn-secondary" @click="preview = null">Back</button>
        <button class="btn-primary" @click="save">Save Recipe</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRecipesStore } from '@/stores/recipes'
import { useOllamaStore } from '@/stores/ollama'
import type { RecipeImportPreview } from '@/types'

const emit = defineEmits<{ saved: [] }>()

const recipesStore = useRecipesStore()
const ollamaStore = useOllamaStore()

const mode = ref<'text' | 'url'>('text')
const rawText = ref('')
const url = ref('')
const selectedModel = ref('')
const loading = ref(false)
const error = ref<string | null>(null)
const preview = ref<RecipeImportPreview | null>(null)

const canImport = computed(() =>
  mode.value === 'text' ? rawText.value.trim().length > 0 : url.value.trim().length > 0
)

onMounted(async () => {
  await ollamaStore.fetchConfig()
  await ollamaStore.fetchModels()
  selectedModel.value = ollamaStore.config?.ollama_model ?? ''
})

async function doImport() {
  loading.value = true
  error.value = null
  try {
    const params = mode.value === 'url'
      ? { url: url.value.trim(), model: selectedModel.value || undefined }
      : { raw_text: rawText.value, model: selectedModel.value || undefined }
    preview.value = await recipesStore.importRecipe(params)
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!preview.value) return
  await recipesStore.create({
    name: preview.value.name,
    description: preview.value.description ?? undefined,
    steps: preview.value.steps,
    source: mode.value === 'url' ? url.value.trim() : undefined,
  })
  emit('saved')
}
</script>

<style scoped>
.btn-row { display: flex; gap: 0.5rem; justify-content: flex-end; }
.meta { font-size: 0.85rem; color: var(--text-muted); }
.steps { display: flex; flex-direction: column; gap: 0.4rem; }
.step { display: flex; align-items: flex-start; gap: 0.6rem; font-size: 0.875rem; }
.step-num { background: var(--accent); color: #fff; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; flex-shrink: 0; }
.step-text { flex: 1; }
textarea { width: 100%; resize: vertical; }
.mode-toggle { display: flex; gap: 0; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; width: fit-content; }
.mode-btn { padding: 0.3rem 0.85rem; font-size: 0.82rem; background: none; border: none; cursor: pointer; color: var(--text-muted); }
.mode-btn.active { background: var(--accent); color: #fff; }
.hint { font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.5rem; }
</style>
