<template>
  <div class="log">
    <div v-for="f in feedings" :key="f.id" class="row">
      <span class="date">{{ formatDate(f.fed_at) }}</span>
      <span v-if="f.starter_grams">{{ f.starter_grams }}g starter</span>
      <span v-if="f.flour_grams">{{ f.flour_grams }}g flour</span>
      <span v-if="f.water_grams">{{ f.water_grams }}g water</span>
      <span v-if="f.height_mm" class="height">{{ f.height_mm }}mm</span>
      <span v-if="f.notes" class="note">— {{ f.notes }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Feeding } from '@/types'
defineProps<{ feedings: Feeding[] }>()

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.log { margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.3rem; }
.row { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; font-size: 0.8rem; padding: 0.25rem 0; border-bottom: 1px solid var(--border); }
.date { color: var(--text-muted); min-width: 110px; }
.height { color: var(--accent); font-weight: 500; }
.note { color: var(--text-muted); font-style: italic; }
</style>
