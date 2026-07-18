import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export type WeightUnit = 'g' | 'oz' | 'cup'

const CONVERSIONS: Record<WeightUnit, { label: string; factor: number; precision: number }> = {
  g:   { label: 'g',   factor: 1,         precision: 0 },
  oz:  { label: 'oz',  factor: 0.035274,   precision: 1 },
  cup: { label: 'cup', factor: 1 / 240,    precision: 2 },
}

export const useUnitsStore = defineStore('units', () => {
  const unit = ref<WeightUnit>((localStorage.getItem('weightUnit') as WeightUnit) ?? 'g')
  const label = computed(() => CONVERSIONS[unit.value].label)

  function setUnit(u: WeightUnit) {
    unit.value = u
    localStorage.setItem('weightUnit', u)
  }

  function toDisplay(grams: number | null | undefined): number | null {
    if (grams == null) return null
    const c = CONVERSIONS[unit.value]
    return +((grams * c.factor).toFixed(c.precision))
  }

  function toGrams(value: number | null | undefined): number | null {
    if (value == null) return null
    return Math.round(value / CONVERSIONS[unit.value].factor)
  }

  return { unit, label, setUnit, toDisplay, toGrams }
})
