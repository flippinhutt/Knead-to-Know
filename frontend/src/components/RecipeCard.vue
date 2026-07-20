<template>
  <div class="card">
    <div class="card-header">
      <img v-if="recipe.image_url" :src="recipe.image_url" class="recipe-photo" alt="" />
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
        <button class="btn-sm btn-ghost" @click="photoInput?.click()">{{ recipe.image_url ? 'Change photo' : '+ Photo' }}</button>
        <input ref="photoInput" type="file" accept="image/*" style="display:none" @change="onPhotoChange" />
        <button v-if="!editing" class="btn-sm btn-ghost" @click="startEdit">Edit recipe</button>
        <button class="btn-danger btn-sm" @click="$emit('deleted')">Delete</button>
      </div>
    </div>

    <div v-if="scale !== 1 && !editing" class="scale-banner">Multiply all weights by {{ scale }}×</div>

    <div v-if="!editing && recipe.ingredients.length" class="ingredients">
      <strong class="section-label">Ingredients</strong>
      <ul>
        <li v-for="ing in recipe.ingredients" :key="ing.order">
          <span v-if="ing.amount" class="ing-amount">{{ scaleAmount(ing.amount) }}</span>
          {{ ing.name }}
        </li>
      </ul>
    </div>

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
          <strong v-if="step.title" class="step-title">{{ step.title }}</strong>
          <p>{{ step.description }}</p>
          <span v-if="step.duration_minutes" class="tag">{{ Math.round(step.duration_minutes * scale) }} min</span>
        </div>
        <button
          v-if="step.duration_minutes"
          class="btn-sm btn-ghost"
          :disabled="startingStep === step.order"
          @click.stop="startTimer(step)"
        >
          {{ startingStep === step.order ? 'Starting…' : 'Start timer' }}
        </button>
      </div>
    </div>

    <div v-if="editing" class="step-editor">
      <strong class="section-label">Ingredients</strong>
      <div v-for="(ingredient, i) in draftIngredients" :key="i" class="draft-ingredient">
        <input v-model="draftIngredients[i].amount" placeholder="Amount" class="draft-amount" />
        <input v-model="draftIngredients[i].name" placeholder="Ingredient" class="draft-ing-name" />
        <button class="btn-sm btn-ghost" @click="removeIngredient(i)" title="Remove ingredient">×</button>
      </div>
      <button class="btn-sm btn-ghost" style="margin-top:0.4rem" @click="addIngredient">+ Add ingredient</button>

      <strong class="section-label" style="margin-top:0.75rem;display:block">Steps</strong>
      <div v-for="(step, i) in draftSteps" :key="i" class="draft-step">
        <span class="step-num">{{ step.order }}</span>
        <div class="draft-body">
          <input v-model="draftSteps[i].title" placeholder="Title (optional)" class="draft-title" />
          <textarea v-model="draftSteps[i].description" rows="2" class="draft-desc" />
        </div>
        <input v-model.number="draftSteps[i].duration_minutes" type="number" min="0" placeholder="min" class="draft-dur" />
        <button class="btn-sm btn-ghost" @click="removeStep(i)" title="Remove step">×</button>
      </div>
      <button class="btn-sm btn-ghost" style="margin-top:0.4rem" @click="addStep">+ Add step</button>
      <div class="btn-row" style="margin-top:0.75rem">
        <button class="btn-secondary btn-sm" @click="cancelEdit">Cancel</button>
        <button class="btn-primary btn-sm" :disabled="saving" @click="saveRecipe">{{ saving ? 'Saving…' : 'Save recipe' }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Recipe, RecipeIngredient, RecipeStep } from '@/types'
import { useRecipesStore } from '@/stores/recipes'
import { useTimersStore } from '@/stores/timers'

const props = defineProps<{ recipe: Recipe }>()
defineEmits<{ deleted: [] }>()

const recipesStore = useRecipesStore()
const timersStore = useTimersStore()

const scale = ref(1)
const checked = ref(new Set<number>())
const anyChecked = computed(() => checked.value.size > 0)
const editing = ref(false)
const saving = ref(false)
const startingStep = ref<number | null>(null)
const photoInput = ref<HTMLInputElement | null>(null)

async function onPhotoChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const dataUrl = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
  await recipesStore.update(props.recipe.id, { image_url: dataUrl })
}

type DraftStep = { order: number; title?: string | null; description: string; duration_minutes: number | null }
const draftSteps = ref<DraftStep[]>([])

type DraftIngredient = { order: number; name: string; amount?: string | null }
const draftIngredients = ref<DraftIngredient[]>([])

function scaleAmount(amount: string): string {
  if (scale.value === 1) return amount
  const match = amount.match(/^(\d+(?:\.\d+)?)(.*)$/)
  if (!match) return amount
  const value = parseFloat(match[1]) * scale.value
  const rounded = Math.round(value * 100) / 100
  return `${rounded}${match[2]}`
}

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
  draftIngredients.value = props.recipe.ingredients.map((i) => ({
    order: i.order,
    name: i.name,
    amount: i.amount ?? null,
  }))
  editing.value = true
}

function cancelEdit() {
  editing.value = false
}

function addStep() {
  const nextOrder = draftSteps.value.length ? Math.max(...draftSteps.value.map((s) => s.order)) + 1 : 1
  draftSteps.value = [...draftSteps.value, { order: nextOrder, title: null, description: '', duration_minutes: null }]
}

function removeStep(i: number) {
  const next = draftSteps.value.filter((_, idx) => idx !== i).map((s, idx) => ({ ...s, order: idx + 1 }))
  draftSteps.value = next
}

function addIngredient() {
  const nextOrder = draftIngredients.value.length ? Math.max(...draftIngredients.value.map((i) => i.order)) + 1 : 1
  draftIngredients.value = [...draftIngredients.value, { order: nextOrder, name: '', amount: null }]
}

function removeIngredient(i: number) {
  const next = draftIngredients.value.filter((_, idx) => idx !== i).map((ing, idx) => ({ ...ing, order: idx + 1 }))
  draftIngredients.value = next
}

async function startTimer(step: RecipeStep) {
  if (!step.duration_minutes) return
  startingStep.value = step.order
  try {
    const timer = await timersStore.create({
      name: `${props.recipe.name} — step ${step.order}`,
      duration_minutes: Math.round(step.duration_minutes * scale.value),
      recipe_step_id: step.id,
    })
    await timersStore.start(timer.id)
  } finally {
    startingStep.value = null
  }
}

async function saveRecipe() {
  saving.value = true
  try {
    await recipesStore.replaceSteps(props.recipe.id, draftSteps.value)
    await recipesStore.replaceIngredients(props.recipe.id, draftIngredients.value)
    editing.value = false
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.card-header { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 0.75rem; margin-bottom: 0.75rem; }
.card-header > div:not(.header-actions) { flex: 1 1 200px; min-width: 0; }
.recipe-photo { width: 64px; height: 64px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }
h3 { font-size: 1rem; font-weight: 600; }
.meta { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.15rem; }
.source { font-style: italic; }
.header-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; justify-content: flex-end; max-width: 100%; flex-shrink: 0; }
.scale-control { display: flex; align-items: center; gap: 0.3rem; font-size: 0.78rem; color: var(--text-muted); }
.scale-control input { width: 52px; padding: 0.15rem 0.3rem; font-size: 0.8rem; }
.scale-control label { margin: 0; }
.scale-banner { font-size: 0.8rem; background: var(--border); color: var(--text-muted); padding: 0.25rem 0.6rem; border-radius: 4px; margin-bottom: 0.5rem; }
.section-label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.03em; color: var(--text-muted); }
.ingredients { margin-bottom: 0.75rem; }
.ingredients ul { list-style: none; margin-top: 0.3rem; display: flex; flex-direction: column; gap: 0.2rem; }
.ingredients li { font-size: 0.875rem; }
.ing-amount { font-weight: 600; margin-right: 0.4rem; }
.draft-ingredient { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.3rem; }
.draft-amount { width: 90px; font-size: 0.875rem; }
.draft-ing-name { flex: 1; font-size: 0.875rem; }
.btn-ghost { background: none; border: 1px solid var(--border, #ccc); color: var(--text-muted); border-radius: 4px; padding: 0.2rem 0.5rem; cursor: pointer; font-size: 0.75rem; }
.steps { display: flex; flex-direction: column; gap: 0.5rem; }
.step { display: flex; gap: 0.75rem; cursor: pointer; user-select: none; }
.step.done .step-body p { text-decoration: line-through; color: var(--text-muted); }
.step.done .step-num { background: var(--text-muted, #999); }
.step-num { background: var(--accent); color: #fff; border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; transition: background 0.15s; }
.check-icon { font-size: 0.85rem; }
.step-body { flex: 1; font-size: 0.875rem; }
.step-title { display: block; margin-bottom: 0.15rem; }
.step-body p { margin-bottom: 0.2rem; transition: color 0.15s; }
.step-editor { display: flex; flex-direction: column; gap: 0.5rem; }
.draft-step { display: flex; align-items: flex-start; gap: 0.5rem; }
.draft-body { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; }
.draft-title { font-size: 0.875rem; font-weight: 600; }
.draft-desc { flex: 1; resize: vertical; font-size: 0.875rem; }
.draft-dur { width: 60px; font-size: 0.875rem; }
.btn-row { display: flex; gap: 0.5rem; justify-content: flex-end; }
</style>
