<template>
  <div>
    <div class="header">
      <h1>Bake Log</h1>
      <button class="btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ Log Bake' }}
      </button>
    </div>

    <div v-if="showForm" class="card form-card">
      <div class="form-grid">
        <div>
          <label>Starter</label>
          <select v-model.number="form.starter_id">
            <option :value="undefined">— none —</option>
            <option v-for="s in startersStore.starters" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div>
          <label>Recipe</label>
          <select v-model.number="form.recipe_id">
            <option :value="undefined">— none —</option>
            <option v-for="r in recipesStore.recipes" :key="r.id" :value="r.id">{{ r.name }}</option>
          </select>
        </div>
        <div>
          <label>Hydration %</label>
          <input v-model.number="form.hydration_percent" type="number" min="50" max="120" />
        </div>
        <div>
          <label>Oven Temp ({{ unitsStore.tempLabel }})</label>
          <input v-model.number="form.oven_temp_display" type="number" />
        </div>
        <div>
          <label>Outcome</label>
          <select v-model="form.outcome">
            <option value="">— select —</option>
            <option value="great">Great</option>
            <option value="good">Good</option>
            <option value="ok">OK</option>
            <option value="poor">Poor</option>
          </select>
        </div>
        <div>
          <label>Date baked</label>
          <input v-model="form.baked_at" type="datetime-local" />
        </div>
      </div>
      <div style="margin-top:0.5rem">
        <label>Tags (comma-separated)</label>
        <input v-model="form.tags" placeholder="e.g. sourdough, pizza, whole wheat" />
      </div>
      <textarea v-model="form.notes" rows="3" placeholder="Notes on crumb, crust, flavor..." style="margin-top:0.5rem" />
      <button class="btn-primary btn-sm" style="margin-top:0.5rem" @click="submit">Save Bake</button>
    </div>

    <p v-if="!store.loading && !store.bakes.length && !showForm" class="muted">No bakes logged yet.</p>

    <div class="list">
      <BakeCard
        v-for="bake in store.bakes"
        :key="bake.id"
        :bake="bake"
        :starter-name="starterName(bake.starter_id)"
        :recipe-name="recipeName(bake.recipe_id)"
        @deleted="store.remove(bake.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useBakesStore } from '@/stores/bakes'
import { useStartersStore } from '@/stores/starters'
import { useRecipesStore } from '@/stores/recipes'
import { useUnitsStore } from '@/stores/units'
import BakeCard from '@/components/BakeCard.vue'

const store = useBakesStore()
const startersStore = useStartersStore()
const recipesStore = useRecipesStore()
const unitsStore = useUnitsStore()
const showForm = ref(false)
const form = reactive({
  starter_id: undefined as number | undefined,
  recipe_id: undefined as number | undefined,
  hydration_percent: undefined as number | undefined,
  oven_temp_display: undefined as number | undefined,
  outcome: '',
  baked_at: '',
  tags: '',
  notes: '',
})

onMounted(() => {
  store.fetchAll()
  startersStore.fetchAll()
  recipesStore.fetchAll()
})

function starterName(id: number | null) {
  return id ? startersStore.starters.find((s) => s.id === id)?.name ?? null : null
}

function recipeName(id: number | null) {
  return id ? recipesStore.recipes.find((r) => r.id === id)?.name ?? null : null
}

async function submit() {
  await store.create({
    starter_id: form.starter_id,
    recipe_id: form.recipe_id,
    hydration_percent: form.hydration_percent,
    oven_temp_f: unitsStore.toStoredTempF(form.oven_temp_display) ?? undefined,
    outcome: form.outcome || undefined,
    baked_at: form.baked_at || undefined,
    tags: form.tags || undefined,
    notes: form.notes || undefined,
  })
  form.starter_id = undefined
  form.recipe_id = undefined
  form.hydration_percent = undefined
  form.oven_temp_display = undefined
  form.outcome = ''
  form.baked_at = ''
  form.tags = ''
  form.notes = ''
  showForm.value = false
}
</script>

<style scoped>
.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
h1 { font-size: 1.4rem; }
.list { display: flex; flex-direction: column; gap: 0.75rem; }
.muted { color: var(--text-muted); }
.form-card { margin-bottom: 1rem; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.75rem; }
label { display: block; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.2rem; }
</style>
