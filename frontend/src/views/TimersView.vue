<template>
  <div>
    <div class="header">
      <h1>Timers</h1>
      <button class="btn-primary" @click="showCreate = true">+ New Timer</button>
    </div>

    <div v-if="showCreate" class="card" style="margin-bottom:1rem">
      <h3 style="margin-bottom:0.75rem">New Timer</h3>
      <div class="form-row">
        <div><label>Name</label><input v-model="form.name" placeholder="Bulk Ferment" /></div>
        <div><label>Duration (minutes)</label><input v-model.number="form.duration_minutes" type="number" min="1" /></div>
      </div>
      <div class="btn-row">
        <button class="btn-secondary" @click="showCreate = false">Cancel</button>
        <button class="btn-primary" :disabled="!form.name || !form.duration_minutes" @click="submit">Create</button>
      </div>
    </div>

    <p v-if="!store.loading && !store.timers.length" class="muted">No timers yet.</p>

    <div class="grid">
      <TimerWidget
        v-for="timer in store.timers"
        :key="timer.id"
        :timer="timer"
        @start="store.start(timer.id)"
        @stop="store.stop(timer.id)"
        @deleted="store.remove(timer.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useTimersStore } from '@/stores/timers'
import TimerWidget from '@/components/TimerWidget.vue'

const store = useTimersStore()
const showCreate = ref(false)
const form = reactive({ name: '', duration_minutes: 0 })

onMounted(() => store.fetchAll())

async function submit() {
  await store.create({ name: form.name, duration_minutes: form.duration_minutes })
  showCreate.value = false
  form.name = ''
  form.duration_minutes = 0
}
</script>

<style scoped>
.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
h1 { font-size: 1.4rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.btn-row { display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 0.75rem; }
.muted { color: var(--text-muted); }
</style>
