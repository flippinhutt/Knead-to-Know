<template>
  <div class="card">
    <div class="card-header">
      <div>
        <h3>{{ recipe.name }}</h3>
        <p v-if="recipe.description" class="meta">{{ recipe.description }}</p>
        <p v-if="recipe.source" class="meta source">Source: {{ recipe.source }}</p>
      </div>
      <div class="header-actions">
        <div class="scale-control" v-if="!editing">
          <label>Scale</label>
          <input v-model.number="scale" type="number" min="0.25" max="10" step="0.25" style="width:60px" />
          <span>×</span>
        </div>
        <button v-if="anyChecked && !editing" class="btn-sm btn-ghost" @click="clearAll">Reset</button>
        <button v-if="!editing" class="btn-sm btn-ghost" @click="startEdit">Edit steps</button>
        <button class="btn-danger btn-sm" @click="$emit('deleted')">Delete</button>
      </div>
    </div>

    <div v-if="scale !== 1 && !editing" class="scale-banner">Multiply all weights by {{ scale }}×</div>

    <div v-if="!editing && recipe.steps.length" class="steps">
      <div
        v-for="step in recipe.steps"
        :key="step.order"
        class="step"
        :class="{ done: checked.has(step.order) }"
        @click="toggle(step.order)"
      >
        <span class="step-num">
          <span v-if="checked.has(step.order)" class="check-icon">✓</span>
          <span v-else>{{ step.order }}</span>
        </span>
        <div class="step-body">
          <p>{{ step.description }}</p>
          <span v-if="step.duration_minutes" class="tag">{{ Math.round(step.duration_minutes * scale) }} min</span>
        </div>
      </div>
    </div>

    <div v-if="editing" class="step-editor">
      <div v-for="(step, i) in draftSteps" :key="i" class="draft-step">
        <span class="step-num">{{ step.order }}</span>
        <textarea v-model="draftSteps[i].description" rows="2" class="draft-desc" />
        <input v-model.number="draftSteps[i].duration_minutes" type="number" min="0" placeholder="min" class="draft-dur" />
        <button class="btn-sm btn-ghost" @click="removeStep(i)" title="Remove step">×</button>
      </div>
      <button class="btn-sm btn-ghost" style="margin-top:0.4rem" @click="addStep">+ Add step</button>
      <div class="btn-row" style="margin-top:0.75rem">
        <button class="btn-secondary btn-sm" @click="cancelEdit">Cancel</button>
        <button class="btn-primary btn-sm" :disabled="saving" @click="saveSteps">{{ saving ? 'Saving…' : 'Save steps' }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Recipe } from '@/types'
import { useRecipesStore } from '@/stores/recipes'

const props = defineProps<{ recipe: Recipe }>()
defineEmits<{ deleted: [] }>()

const recipesStore = useRecipesStore()

const scale = ref(1)
const checked = ref(new Set<number>())
const anyChecked = computed(() => checked.value.size > 0)
const editing = ref(false)
const saving = ref(false)

type DraftStep = { order: number; description: string; duration_minutes: number | null }
const draftSteps = ref<DraftStep[]>([])

function toggle(order: number) {
  const next = new Set(checked.value)
  if (next.has(order)) next.delete(order)
  else next.add(order)
  checked.value = next
}

function clearAll() {
  checked.value = new Set()
}

function startEdit() {
  draftSteps.value = props.recipe.steps.map((s) => ({
    order: s.order,
    description: s.description,
    duration_minutes: s.duration_minutes ?? null,
  }))
  editing.value = true
}

function cancelEdit() {
  editing.value = false
}

function addStep() {
  const nextOrder = draftSteps.value.length ? Math.max(...draftSteps.value.map((s) => s.order)) + 1 : 1
  draftSteps.value = [...draftSteps.value, { order: nextOrder, description: '', duration_minutes: null }]
}

function removeStep(i: number) {
  const next = draftSteps.value.filter((_, idx) => idx !== i).map((s, idx) => ({ ...s, order: idx + 1 }))
  draftSteps.value = next
}

async function saveSteps() {
  saving.value = true
  try {
    await recipesStore.replaceSteps(props.recipe.id, draftSteps.value)
    editing.value = false
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }
h3 { font-size: 1rem; font-weight: 600; }
.meta { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.15rem; }
.source { font-style: italic; }
.header-actions { display: flex; gap: 0.5rem; align-items: center; }
.scale-control { display: flex; align-items: center; gap: 0.3rem; font-size: 0.78rem; color: var(--text-muted); }
.scale-control input { width: 52px; padding: 0.15rem 0.3rem; font-size: 0.8rem; }
.scale-control label { margin: 0; }
.scale-banner { font-size: 0.8rem; background: var(--border); color: var(--text-muted); padding: 0.25rem 0.6rem; border-radius: 4px; margin-bottom: 0.5rem; }
.btn-ghost { background: none; border: 1px solid var(--border, #ccc); color: var(--text-muted); border-radius: 4px; padding: 0.2rem 0.5rem; cursor: pointer; font-size: 0.75rem; }
.steps { display: flex; flex-direction: column; gap: 0.5rem; }
.step { display: flex; gap: 0.75rem; cursor: pointer; user-select: none; }
.step.done .step-body p { text-decoration: line-through; color: var(--text-muted); }
.step.done .step-num { background: var(--text-muted, #999); }
.step-num { background: var(--accent); color: #fff; border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; transition: background 0.15s; }
.check-icon { font-size: 0.85rem; }
.step-body { flex: 1; font-size: 0.875rem; }
.step-body p { margin-bottom: 0.2rem; transition: color 0.15s; }
.step-editor { display: flex; flex-direction: column; gap: 0.5rem; }
.draft-step { display: flex; align-items: flex-start; gap: 0.5rem; }
.draft-desc { flex: 1; resize: vertical; font-size: 0.875rem; }
.draft-dur { width: 60px; font-size: 0.875rem; }
.btn-row { display: flex; gap: 0.5rem; justify-content: flex-end; }
</style>
