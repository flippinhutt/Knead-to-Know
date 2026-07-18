<template>
  <div class="card" :class="{ archived: starter.archived }">
    <div class="card-header">
      <div>
        <h3>{{ starter.name }}</h3>
        <p v-if="starter.hydration_percent" class="meta">{{ starter.hydration_percent }}% hydration</p>
        <p v-if="starter.description" class="meta">{{ starter.description }}</p>
      </div>
      <div class="header-actions">
        <span v-if="isOverdue" class="badge-overdue">Feed me!</span>
        <button class="btn-sm btn-ghost" @click="toggleArchive">
          {{ starter.archived ? 'Restore' : 'Archive' }}
        </button>
        <button class="btn-danger btn-sm" @click="$emit('deleted')">Delete</button>
      </div>
    </div>

    <div class="last-fed">
      <span v-if="lastFeeding">Last fed {{ timeAgo(lastFeeding.fed_at) }}</span>
      <span v-else class="muted">Never fed</span>
      <span v-if="starter.feed_interval_hours" class="interval-tag">every {{ starter.feed_interval_hours }}h</span>
    </div>

    <details v-if="!starter.archived">
      <summary>Add feeding</summary>
      <div class="feeding-form">
        <div class="form-row">
          <div><label>Starter ({{ units.label }})</label><input v-model.number="feed.starter_display" type="number" /></div>
          <div><label>Flour ({{ units.label }})</label><input v-model.number="feed.flour_display" type="number" /></div>
          <div><label>Water ({{ units.label }})</label><input v-model.number="feed.water_display" type="number" /></div>
          <div><label>Height (mm)</label><input v-model.number="feed.height_mm" type="number" /></div>
          <div><label>Temp ({{ units.tempLabel }})</label><input v-model.number="feed.temp_display" type="number" /></div>
        </div>
        <div class="form-row" style="margin-top:0.4rem">
          <div>
            <label>Flour type</label>
            <input v-model="feed.flour_type" list="flour-types" placeholder="e.g. AP, Bread, Whole Wheat" />
            <datalist id="flour-types">
              <option value="All-Purpose" />
              <option value="Bread" />
              <option value="Whole Wheat" />
              <option value="Rye" />
              <option value="Spelt" />
              <option value="Einkorn" />
              <option value="Semolina" />
              <option value="00" />
            </datalist>
          </div>
          <div><label>Flour brand</label><input v-model="feed.flour_brand" placeholder="e.g. King Arthur" /></div>
        </div>
        <input v-model="feed.notes" placeholder="Notes (optional)" style="margin-top:0.4rem" />
        <button class="btn-primary btn-sm" style="margin-top:0.5rem" @click="submitFeeding">Log Feeding</button>
      </div>
    </details>

    <details v-if="!starter.archived">
      <summary>Reminder interval</summary>
      <div class="interval-form">
        <label>Feed every</label>
        <input v-model.number="intervalHours" type="number" min="1" max="168" style="width:60px" />
        <span>hours</span>
        <button class="btn-primary btn-sm" @click="saveInterval">Save</button>
        <button v-if="starter.feed_interval_hours" class="btn-sm btn-ghost" @click="clearInterval">Clear</button>
      </div>
    </details>

    <details v-if="starter.feedings.length">
      <summary>History ({{ starter.feedings.length }})</summary>
      <FeedingLog :feedings="starter.feedings" />
    </details>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { Starter } from '@/types'
import { useStartersStore } from '@/stores/starters'
import { useUnitsStore } from '@/stores/units'
import FeedingLog from './FeedingLog.vue'

const props = defineProps<{ starter: Starter }>()
defineEmits<{ deleted: [] }>()

const store = useStartersStore()
const units = useUnitsStore()

const feed = reactive({
  starter_display: undefined as number | undefined,
  flour_display: undefined as number | undefined,
  water_display: undefined as number | undefined,
  height_mm: undefined as number | undefined,
  temp_display: undefined as number | undefined,
  flour_type: '',
  flour_brand: '',
  notes: '',
})
const intervalHours = ref<number | undefined>(props.starter.feed_interval_hours ?? undefined)
const lastFeeding = computed(() => props.starter.feedings[0] ?? null)

const isOverdue = computed(() => {
  if (!props.starter.feed_interval_hours || !lastFeeding.value) return false
  const due = new Date(lastFeeding.value.fed_at).getTime() + props.starter.feed_interval_hours * 3.6e6
  return Date.now() > due
})

async function submitFeeding() {
  await store.addFeeding(props.starter.id, {
    starter_grams: units.toGrams(feed.starter_display) ?? undefined,
    flour_grams: units.toGrams(feed.flour_display) ?? undefined,
    water_grams: units.toGrams(feed.water_display) ?? undefined,
    height_mm: feed.height_mm,
    ambient_temp_f: units.toStoredTempF(feed.temp_display) ?? undefined,
    flour_type: feed.flour_type || undefined,
    flour_brand: feed.flour_brand || undefined,
    notes: feed.notes || undefined,
  })
  feed.starter_display = undefined
  feed.flour_display = undefined
  feed.water_display = undefined
  feed.height_mm = undefined
  feed.temp_display = undefined
  feed.flour_type = ''
  feed.flour_brand = ''
  feed.notes = ''
}

async function saveInterval() {
  await store.update(props.starter.id, { feed_interval_hours: intervalHours.value })
}

async function clearInterval() {
  intervalHours.value = undefined
  await store.update(props.starter.id, { feed_interval_hours: undefined })
}

async function toggleArchive() {
  await store.update(props.starter.id, { archived: !props.starter.archived })
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
.card { transition: opacity 0.2s; }
.card.archived { opacity: 0.55; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
h3 { font-size: 1rem; font-weight: 600; }
.meta { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.1rem; }
.header-actions { display: flex; align-items: center; gap: 0.5rem; }
.badge-overdue { background: #e53e3e; color: #fff; font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.4rem; border-radius: 4px; }
.last-fed { font-size: 0.85rem; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }
.interval-tag { font-size: 0.75rem; color: var(--text-muted); background: var(--border); padding: 0.1rem 0.35rem; border-radius: 4px; }
.muted { color: var(--text-muted); }
details { margin-top: 0.5rem; }
summary { cursor: pointer; font-size: 0.85rem; color: var(--accent); user-select: none; }
.feeding-form { margin-top: 0.5rem; }
.form-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); gap: 0.5rem; }
.interval-form { margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; }
.btn-ghost { background: none; border: 1px solid var(--border, #ccc); color: var(--text-muted); border-radius: 4px; padding: 0.2rem 0.5rem; cursor: pointer; font-size: 0.75rem; }
</style>
