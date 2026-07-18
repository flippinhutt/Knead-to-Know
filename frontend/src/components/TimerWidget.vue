<template>
  <div class="card timer" :class="{ active: timer.is_active, done: isDone }">
    <div class="timer-header">
      <h3>{{ timer.name }}</h3>
      <button class="btn-danger btn-sm" @click="$emit('deleted')">×</button>
    </div>

    <div class="countdown">{{ displayTime }}</div>
    <div class="duration-label">{{ timer.duration_minutes }} min total</div>

    <div class="btn-row">
      <button v-if="!timer.is_active" class="btn-primary btn-sm" @click="$emit('start')">Start</button>
      <button v-else class="btn-secondary btn-sm" @click="$emit('stop')">Stop</button>
    </div>

    <div v-if="isDone" class="done-badge">Done!</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import type { Timer } from '@/types'

const props = defineProps<{ timer: Timer }>()
defineEmits<{ start: []; stop: []; deleted: [] }>()

const now = ref(Date.now())
let interval: ReturnType<typeof setInterval> | null = null

onMounted(() => { interval = setInterval(() => { now.value = Date.now() }, 1000) })
onUnmounted(() => { if (interval) clearInterval(interval) })

const remaining = computed(() => {
  if (!props.timer.is_active || !props.timer.ends_at) return props.timer.duration_minutes * 60
  return Math.max(0, Math.floor((new Date(props.timer.ends_at).getTime() - now.value) / 1000))
})

const isDone = computed(() => props.timer.is_active && remaining.value === 0)

const displayTime = computed(() => {
  const s = remaining.value
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
})
</script>

<style scoped>
.timer { text-align: center; position: relative; transition: border-color 0.3s; }
.timer.active { border-color: var(--accent); }
.timer.done { border-color: var(--success); }
.timer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
h3 { font-size: 0.95rem; font-weight: 600; }
.countdown { font-size: 2.5rem; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--accent); line-height: 1; margin-bottom: 0.25rem; }
.duration-label { font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.75rem; }
.btn-row { display: flex; justify-content: center; }
.done-badge { position: absolute; top: 0.5rem; right: 2.5rem; background: var(--success); color: #fff; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
</style>
