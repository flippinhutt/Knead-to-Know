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
          <label>Hydration %</label>
          <input v-model.number="form.hydration_percent" type="number" min="50" max="120" />
        </div>
        <div>
          <label>Oven Temp (°F)</label>
          <input v-model.number="form.oven_temp_f" type="number" />
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
        @deleted="store.remove(bake.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useBakesStore } from '@/stores/bakes'
import BakeCard from '@/components/BakeCard.vue'

const store = useBakesStore()
const showForm = ref(false)
const form = reactive({
  hydration_percent: undefined as number | undefined,
  oven_temp_f: undefined as number | undefined,
  outcome: '',
  notes: '',
})

onMounted(() => store.fetchAll())

async function submit() {
  await store.create({
    hydration_percent: form.hydration_percent,
    oven_temp_f: form.oven_temp_f,
    outcome: form.outcome || undefined,
    notes: form.notes || undefined,
  })
  form.hydration_percent = undefined
  form.oven_temp_f = undefined
  form.outcome = ''
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
.form-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem; }
label { display: block; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.2rem; }
</style>
