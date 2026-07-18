<template>
  <div class="card">
    <div class="card-header">
      <div>
        <h3>{{ starter.name }}</h3>
        <p v-if="starter.hydration_percent" class="meta">{{ starter.hydration_percent }}% hydration</p>
        <p v-if="starter.description" class="meta">{{ starter.description }}</p>
      </div>
      <button class="btn-danger btn-sm" @click="$emit('deleted')">Delete</button>
    </div>

    <div class="last-fed">
      <span v-if="lastFeeding">Last fed {{ timeAgo(lastFeeding.fed_at) }}</span>
      <span v-else class="muted">Never fed</span>
    </div>

    <details>
      <summary>Add feeding</summary>
      <div class="feeding-form">
        <div class="form-row">
          <div><label>Starter (g)</label><input v-model.number="feed.starter_grams" type="number" /></div>
          <div><label>Flour (g)</label><input v-model.number="feed.flour_grams" type="number" /></div>
          <div><label>Water (g)</label><input v-model.number="feed.water_grams" type="number" /></div>
        </div>
        <input v-model="feed.notes" placeholder="Notes (optional)" style="margin-top:0.4rem" />
        <button class="btn-primary btn-sm" style="margin-top:0.5rem" @click="submitFeeding">Log Feeding</button>
      </div>
    </details>

    <details v-if="starter.feedings.length">
      <summary>History ({{ starter.feedings.length }})</summary>
      <FeedingLog :feedings="starter.feedings" />
    </details>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import type { Starter } from '@/types'
import { useStartersStore } from '@/stores/starters'
import FeedingLog from './FeedingLog.vue'

const props = defineProps<{ starter: Starter }>()
defineEmits<{ deleted: [] }>()

const store = useStartersStore()
const feed = reactive({ starter_grams: undefined as number | undefined, flour_grams: undefined as number | undefined, water_grams: undefined as number | undefined, notes: '' })
const lastFeeding = computed(() => props.starter.feedings[0] ?? null)

async function submitFeeding() {
  await store.addFeeding(props.starter.id, {
    starter_grams: feed.starter_grams,
    flour_grams: feed.flour_grams,
    water_grams: feed.water_grams,
    notes: feed.notes || undefined,
  })
  feed.starter_grams = undefined
  feed.flour_grams = undefined
  feed.water_grams = undefined
  feed.notes = ''
}

function timeAgo(isoDate: string) {
  const diff = Date.now() - new Date(isoDate).getTime()
  const h = Math.floor(diff / 3.6e6)
  if (h < 1) return 'just now'
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
h3 { font-size: 1rem; font-weight: 600; }
.meta { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.1rem; }
.last-fed { font-size: 0.85rem; margin-bottom: 0.75rem; }
.muted { color: var(--text-muted); }
details { margin-top: 0.5rem; }
summary { cursor: pointer; font-size: 0.85rem; color: var(--accent); user-select: none; }
.feeding-form { margin-top: 0.5rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; }
</style>
