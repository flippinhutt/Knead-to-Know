<template>
  <div class="card">
    <div class="card-header">
      <div>
        <h3>{{ recipe.name }}</h3>
        <p v-if="recipe.description" class="meta">{{ recipe.description }}</p>
        <p v-if="recipe.source" class="meta source">Source: {{ recipe.source }}</p>
      </div>
      <div class="header-actions">
        <button v-if="anyChecked" class="btn-sm btn-ghost" @click="clearAll">Reset</button>
        <button class="btn-danger btn-sm" @click="$emit('deleted')">Delete</button>
      </div>
    </div>

    <div v-if="recipe.steps.length" class="steps">
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
          <p>{{ step.description }}</p>
          <span v-if="step.duration_minutes" class="tag">{{ step.duration_minutes }} min</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Recipe } from '@/types'

defineProps<{ recipe: Recipe }>()
defineEmits<{ deleted: [] }>()

const checked = ref(new Set<number>())
const anyChecked = computed(() => checked.value.size > 0)

function toggle(order: number) {
  const next = new Set(checked.value)
  if (next.has(order)) next.delete(order)
  else next.add(order)
  checked.value = next
}

function clearAll() {
  checked.value = new Set()
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }
h3 { font-size: 1rem; font-weight: 600; }
.meta { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.15rem; }
.source { font-style: italic; }
.header-actions { display: flex; gap: 0.5rem; align-items: center; }
.btn-ghost { background: none; border: 1px solid var(--border, #ccc); color: var(--text-muted); border-radius: 4px; padding: 0.2rem 0.5rem; cursor: pointer; font-size: 0.75rem; }
.steps { display: flex; flex-direction: column; gap: 0.5rem; }
.step { display: flex; gap: 0.75rem; cursor: pointer; user-select: none; }
.step.done .step-body p { text-decoration: line-through; color: var(--text-muted); }
.step.done .step-num { background: var(--text-muted, #999); }
.step-num { background: var(--accent); color: #fff; border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; transition: background 0.15s; }
.check-icon { font-size: 0.85rem; }
.step-body { flex: 1; font-size: 0.875rem; }
.step-body p { margin-bottom: 0.2rem; transition: color 0.15s; }
</style>
