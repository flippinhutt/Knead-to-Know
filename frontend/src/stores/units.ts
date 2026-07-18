import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export type WeightUnit = 'g' | 'oz' | 'cup'
export type TempUnit = 'f' | 'c'

const CONVERSIONS: Record<WeightUnit, { label: string; factor: number; precision: number }> = {
  g:   { label: 'g',   factor: 1,         precision: 0 },
  oz:  { label: 'oz',  factor: 0.035274,   precision: 1 },
  cup: { label: 'cup', factor: 1 / 240,    precision: 2 },
}

export const useUnitsStore = defineStore('units', () => {
  const unit = ref<WeightUnit>((localStorage.getItem('weightUnit') as WeightUnit) ?? 'g')
  const tempUnit = ref<TempUnit>((localStorage.getItem('tempUnit') as TempUnit) ?? 'f')

  const label = computed(() => CONVERSIONS[unit.value].label)
  const tempLabel = computed(() => tempUnit.value === 'c' ? '°C' : '°F')

  function setUnit(u: WeightUnit) {
    unit.value = u
    localStorage.setItem('weightUnit', u)
  }

  function setTempUnit(u: TempUnit) {
    tempUnit.value = u
    localStorage.setItem('tempUnit', u)
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

  function toDisplayTemp(fahrenheit: number | null | undefined): number | null {
    if (fahrenheit == null) return null
    if (tempUnit.value === 'c') return +((fahrenheit - 32) * 5 / 9).toFixed(1)
    return fahrenheit
  }

  function toStoredTempF(value: number | null | undefined): number | null {
    if (value == null) return null
    if (tempUnit.value === 'c') return Math.round(value * 9 / 5 + 32)
    return Math.round(value)
  }

  return { unit, tempUnit, label, tempLabel, setUnit, setTempUnit, toDisplay, toGrams, toDisplayTemp, toStoredTempF }
})
