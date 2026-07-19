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
      <label>Name</label>
      <input v-model="preview.name" style="margin-bottom:0.5rem" />
      <label>Description</label>
      <textarea v-model="preview.description" rows="2" style="margin-bottom:0.75rem" />
      <div class="step-editor">
        <div v-for="(step, i) in preview.steps" :key="i" class="draft-step">
          <span class="step-num">{{ step.order }}</span>
          <div class="draft-body">
            <input v-model="preview.steps[i].title" placeholder="Title (optional)" class="draft-title" />
            <textarea v-model="preview.steps[i].description" rows="2" class="draft-desc" />
          </div>
          <input v-model.number="preview.steps[i].duration_minutes" type="number" min="0" placeholder="min" class="draft-dur" />
          <button class="btn-sm btn-ghost" @click="removeStep(i)" title="Remove step">×</button>
        </div>
        <button class="btn-sm btn-ghost" style="margin-top:0.4rem" @click="addStep">+ Add step</button>
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

function addStep() {
  if (!preview.value) return
  const steps = preview.value.steps
  const nextOrder = steps.length ? Math.max(...steps.map((s) => s.order)) + 1 : 1
  preview.value = { ...preview.value, steps: [...steps, { order: nextOrder, title: null, description: '', duration_minutes: null }] }
}

function removeStep(i: number) {
  if (!preview.value) return
  const steps = preview.value.steps.filter((_, idx) => idx !== i).map((s, idx) => ({ ...s, order: idx + 1 }))
  preview.value = { ...preview.value, steps }
}

async function save() {
  if (!preview.value) return
  await recipesStore.create({
    name: preview.value.name,
    description: preview.value.description?.trim() || undefined,
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
.step-editor { display: flex; flex-direction: column; gap: 0.5rem; }
.draft-step { display: flex; align-items: flex-start; gap: 0.5rem; }
.draft-body { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; }
.draft-title { font-size: 0.875rem; font-weight: 600; }
.draft-desc { flex: 1; resize: vertical; font-size: 0.875rem; }
.draft-dur { width: 60px; font-size: 0.875rem; }
.btn-ghost { background: none; border: 1px solid var(--border, #ccc); color: var(--text-muted); border-radius: 4px; padding: 0.2rem 0.5rem; cursor: pointer; font-size: 0.75rem; }
</style>
