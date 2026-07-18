<template>
  <div>
    <div class="header">
      <h1>Starters</h1>
      <div class="header-actions">
        <button class="btn-sm btn-ghost" @click="toggleArchived">
          {{ showArchived ? 'Hide archived' : 'Show archived' }}
        </button>
        <button class="btn-primary" @click="showCreate = true">+ New Starter</button>
      </div>
    </div>

    <div v-if="store.error" class="error" style="margin-bottom:1rem">{{ store.error }}</div>

    <div v-if="showCreate" class="card" style="margin-bottom:1rem">
      <h3 style="margin-bottom:0.75rem">New Starter</h3>
      <div class="form-row">
        <div><label>Name</label><input v-model="form.name" placeholder="Bubbles" /></div>
        <div><label>Hydration %</label><input v-model.number="form.hydration_percent" type="number" placeholder="100" /></div>
      </div>
      <div style="margin-top:0.5rem"><label>Description</label><input v-model="form.description" placeholder="Optional notes" /></div>
      <div class="btn-row">
        <button class="btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn-primary" :disabled="!form.name" @click="submit">Create</button>
      </div>
    </div>

    <p v-if="!store.loading && !store.starters.length" class="muted">
      {{ showArchived ? 'No archived starters.' : 'No starters yet.' }}
    </p>

    <div class="grid">
      <StarterCard
        v-for="starter in store.starters"
        :key="starter.id"
        :starter="starter"
        @deleted="store.remove(starter.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useStartersStore } from '@/stores/starters'
import StarterCard from '@/components/StarterCard.vue'

const store = useStartersStore()
const showCreate = ref(false)
const showArchived = ref(false)
const form = reactive({ name: '', hydration_percent: undefined as number | undefined, description: '' })

onMounted(() => store.fetchAll())

async function toggleArchived() {
  showArchived.value = !showArchived.value
  await store.fetchAll(showArchived.value)
}

async function submit() {
  await store.create({ name: form.name, hydration_percent: form.hydration_percent, description: form.description || undefined })
  showCreate.value = false
  form.name = ''
  form.hydration_percent = undefined
  form.description = ''
}
</script>

<style scoped>
.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
h1 { font-size: 1.4rem; }
.header-actions { display: flex; gap: 0.5rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.btn-row { display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 0.75rem; }
.muted { color: var(--text-muted); }
.btn-ghost { background: none; border: 1px solid var(--border, #ccc); color: var(--text-muted); border-radius: 4px; padding: 0.2rem 0.6rem; cursor: pointer; font-size: 0.8rem; }
</style>
