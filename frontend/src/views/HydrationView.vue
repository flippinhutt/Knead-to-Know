<template>
  <div>
    <h1>Hydration Calculator</h1>
    <p class="subtitle">Target a hydration % from your flour weight.</p>

    <div class="card calc-card">
      <div class="inputs">
        <div>
          <label>Flour (g)</label>
          <input v-model.number="flour" type="number" min="1" />
        </div>
        <div>
          <label>Target Hydration %</label>
          <input v-model.number="hydration" type="number" min="50" max="120" />
        </div>
        <div>
          <label>Starter hydration %</label>
          <input v-model.number="starterHydration" type="number" min="50" max="200" />
        </div>
        <div>
          <label>Starter amount (g)</label>
          <input v-model.number="starterAmount" type="number" min="0" />
        </div>
      </div>

      <div v-if="flour && hydration" class="results">
        <div class="result-row">
          <span>Total water needed</span>
          <strong>{{ totalWater }}g</strong>
        </div>
        <div class="result-row">
          <span>Water from starter</span>
          <strong>{{ waterFromStarter }}g</strong>
        </div>
        <div class="result-row highlight">
          <span>Added water</span>
          <strong>{{ addedWater }}g</strong>
        </div>
        <div class="result-row">
          <span>Actual hydration</span>
          <strong>{{ actualHydration }}%</strong>
        </div>
        <div class="result-row">
          <span>Baker's % (starter)</span>
          <strong>{{ starterPercent }}%</strong>
        </div>
      </div>
      <p v-else class="placeholder">Enter flour weight and hydration target to calculate.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const flour = ref<number>(500)
const hydration = ref<number>(75)
const starterHydration = ref<number>(100)
const starterAmount = ref<number>(100)

const totalWater = computed(() => Math.round(flour.value * (hydration.value / 100)))
const waterFromStarter = computed(() => Math.round(starterAmount.value * (starterHydration.value / 100) / (1 + starterHydration.value / 100)))
const addedWater = computed(() => Math.max(0, totalWater.value - waterFromStarter.value))
const flourFromStarter = computed(() => starterAmount.value - waterFromStarter.value)
const actualHydration = computed(() => {
  const totalFlour = flour.value + flourFromStarter.value
  const totalW = waterFromStarter.value + addedWater.value
  return totalFlour > 0 ? Math.round((totalW / totalFlour) * 100) : 0
})
const starterPercent = computed(() => flour.value > 0 ? Math.round((starterAmount.value / flour.value) * 100) : 0)
</script>

<style scoped>
h1 { font-size: 1.4rem; margin-bottom: 0.25rem; }
.subtitle { color: var(--text-muted); font-size: 0.88rem; margin-bottom: 1rem; }
.calc-card { max-width: 480px; }
.inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1.25rem; }
label { display: block; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.2rem; }
.results { display: flex; flex-direction: column; gap: 0.5rem; border-top: 1px solid var(--border); padding-top: 1rem; }
.result-row { display: flex; justify-content: space-between; font-size: 0.9rem; }
.result-row.highlight { background: var(--surface); padding: 0.35rem 0.5rem; border-radius: 6px; font-size: 1rem; }
.result-row strong { font-weight: 700; }
.placeholder { color: var(--text-muted); font-style: italic; }
</style>
