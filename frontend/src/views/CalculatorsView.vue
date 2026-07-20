<template>
  <div>
    <h1>Calculators</h1>
    <p class="subtitle">Hydration targets and kitchen unit conversions.</p>

    <div class="tabs">
      <button :class="{ active: tab === 'hydration' }" @click="tab = 'hydration'">Hydration</button>
      <button :class="{ active: tab === 'converter' }" @click="tab = 'converter'">Unit Converter</button>
    </div>

    <div v-if="tab === 'hydration'" class="card calc-card">
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

    <div v-else class="card calc-card">
      <div class="inputs">
        <div>
          <label>Ingredient</label>
          <select v-model="ingredient">
            <option v-for="opt in ingredients" :key="opt.name" :value="opt.name">{{ opt.name }}</option>
          </select>
        </div>
        <div>
          <label>Grams</label>
          <input v-model.number="grams" type="number" min="0" @input="syncFromGrams" />
        </div>
        <div>
          <label>Cups</label>
          <input v-model.number="cups" type="number" min="0" step="0.01" @input="syncFromCups" />
        </div>
      </div>
      <p class="placeholder">1 cup {{ ingredient }} &asymp; {{ gramsPerCup }}g</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const tab = ref<'hydration' | 'converter'>('hydration')

// Hydration calculator
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

// Unit converter
const ingredients = [
  { name: 'All-purpose flour', gramsPerCup: 120 },
  { name: 'Bread flour', gramsPerCup: 127 },
  { name: 'Whole wheat flour', gramsPerCup: 113 },
  { name: 'Water', gramsPerCup: 236.6 },
  { name: 'Granulated sugar', gramsPerCup: 200 },
  { name: 'Brown sugar (packed)', gramsPerCup: 220 },
  { name: 'Butter', gramsPerCup: 227 },
  { name: 'Salt (fine)', gramsPerCup: 273 },
  { name: 'Rolled oats', gramsPerCup: 90 },
]

const ingredient = ref(ingredients[0].name)
const gramsPerCup = computed(() => ingredients.find(i => i.name === ingredient.value)?.gramsPerCup ?? 1)

const grams = ref<number>(120)
const cups = ref<number>(Math.round((120 / gramsPerCup.value) * 100) / 100)

function syncFromGrams() {
  cups.value = Math.round((grams.value / gramsPerCup.value) * 100) / 100
}

function syncFromCups() {
  grams.value = Math.round(cups.value * gramsPerCup.value)
}
</script>

<style scoped>
h1 { font-size: 1.4rem; margin-bottom: 0.25rem; }
.subtitle { color: var(--text-muted); font-size: 0.88rem; margin-bottom: 1rem; }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.tabs button { padding: 0.4rem 0.9rem; border: 1px solid var(--border); border-radius: 6px; background: var(--surface); cursor: pointer; font-size: 0.85rem; }
.tabs button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.calc-card { max-width: 480px; }
.inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1.25rem; }
label { display: block; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.2rem; }
select { width: 100%; padding: 0.4rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text); }
.results { display: flex; flex-direction: column; gap: 0.5rem; border-top: 1px solid var(--border); padding-top: 1rem; }
.result-row { display: flex; justify-content: space-between; font-size: 0.9rem; }
.result-row.highlight { background: var(--surface); padding: 0.35rem 0.5rem; border-radius: 6px; font-size: 1rem; }
.result-row strong { font-weight: 700; }
.placeholder { color: var(--text-muted); font-style: italic; }
</style>
