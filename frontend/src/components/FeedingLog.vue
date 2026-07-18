<template>
  <div class="log">
    <svg v-if="chartPoints" class="chart" viewBox="0 0 200 60" preserveAspectRatio="none">
      <polyline :points="chartPoints" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-linejoin="round" />
    </svg>
    <div v-for="f in feedings" :key="f.id" class="row">
      <span class="date">{{ formatDate(f.fed_at) }}</span>
      <span v-if="f.starter_grams">{{ units.toDisplay(f.starter_grams) }}{{ units.label }} starter</span>
      <span v-if="f.flour_grams">{{ units.toDisplay(f.flour_grams) }}{{ units.label }} flour</span>
      <span v-if="f.water_grams">{{ units.toDisplay(f.water_grams) }}{{ units.label }} water</span>
      <span v-if="f.height_mm" class="height">{{ f.height_mm }}mm</span>
      <span v-if="f.ambient_temp_f" class="temp">{{ units.toDisplayTemp(f.ambient_temp_f) }}{{ units.tempLabel }}</span>
      <span v-if="f.flour_type || f.flour_brand" class="flour">{{ [f.flour_brand, f.flour_type].filter(Boolean).join(' ') }}</span>
      <span v-if="f.notes" class="note">— {{ f.notes }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Feeding } from '@/types'
import { useUnitsStore } from '@/stores/units'

const props = defineProps<{ feedings: Feeding[] }>()
const units = useUnitsStore()

const chartPoints = computed(() => {
  const pts = [...props.feedings].filter((f) => f.height_mm != null).reverse().slice(-12)
  if (pts.length < 2) return null
  const heights = pts.map((f) => f.height_mm!)
  const max = Math.max(...heights), min = Math.min(...heights)
  const range = max - min || 1
  return pts.map((f, i) => {
    const x = 5 + (i / (pts.length - 1)) * 190
    const y = 55 - ((f.height_mm! - min) / range) * 50
    return `${x},${y}`
  }).join(' ')
})

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.log { margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.3rem; }
.chart { width: 100%; height: 60px; margin-bottom: 0.5rem; border-bottom: 1px solid var(--border); }
.row { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; font-size: 0.8rem; padding: 0.25rem 0; border-bottom: 1px solid var(--border); }
.date { color: var(--text-muted); min-width: 110px; }
.height { color: var(--accent); font-weight: 500; }
.temp { color: #d97706; font-weight: 500; }
.flour { color: #7c3aed; font-size: 0.78rem; }
.note { color: var(--text-muted); font-style: italic; }
</style>
