<template>
  <div class="card">
    <div class="card-header">
      <div>
        <div class="bake-meta">
          <span class="date">{{ formatDate(bake.baked_at) }}</span>
          <span v-if="bake.outcome" :class="['outcome', bake.outcome]">{{ bake.outcome }}</span>
        </div>
        <div class="bake-links">
          <span v-if="starterName" class="link-tag">{{ starterName }}</span>
          <span v-if="recipeName" class="link-tag">{{ recipeName }}</span>
        </div>
        <div class="bake-details">
          <span v-if="bake.hydration_percent">{{ bake.hydration_percent }}% hydration</span>
          <span v-if="bake.oven_temp_f">{{ bake.oven_temp_f }}°F</span>
        </div>
        <p v-if="bake.notes" class="notes">{{ bake.notes }}</p>
      </div>
      <button class="btn-danger btn-sm" @click="$emit('deleted')">Delete</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Bake } from '@/types'
defineProps<{ bake: Bake; starterName?: string | null; recipeName?: string | null }>()
defineEmits<{ deleted: [] }>()

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: flex-start; }
.bake-meta { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; }
.date { font-weight: 600; font-size: 0.9rem; }
.outcome { font-size: 0.7rem; font-weight: 700; padding: 0.1rem 0.4rem; border-radius: 4px; text-transform: capitalize; }
.outcome.great { background: #c6f6d5; color: #276749; }
.outcome.good { background: #bee3f8; color: #2b6cb0; }
.outcome.ok { background: #fefcbf; color: #744210; }
.outcome.poor { background: #fed7d7; color: #c53030; }
.bake-links { display: flex; gap: 0.4rem; margin-bottom: 0.25rem; flex-wrap: wrap; }
.link-tag { font-size: 0.72rem; background: var(--border); color: var(--text-muted); padding: 0.1rem 0.4rem; border-radius: 4px; }
.bake-details { display: flex; gap: 0.75rem; font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.25rem; }
.notes { font-size: 0.82rem; color: var(--text-muted); font-style: italic; margin-top: 0.25rem; }
</style>
