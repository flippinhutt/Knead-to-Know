export interface Feeding {
  id: number
  starter_id: number
  fed_at: string
  flour_grams: number | null
  water_grams: number | null
  starter_grams: number | null
  height_mm: number | null
  ambient_temp_f: number | null
  flour_type: string | null
  flour_brand: string | null
  notes: string | null
}

export interface Starter {
  id: number
  name: string
  description: string | null
  hydration_percent: number | null
  feed_interval_hours: number | null
  archived: boolean
  created_at: string
  feedings: Feeding[]
}

export interface Bake {
  id: number
  starter_id: number | null
  recipe_id: number | null
  baked_at: string
  hydration_percent: number | null
  oven_temp_f: number | null
  outcome: string | null
  notes: string | null
  tags: string | null
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface RecipeStep {
  id?: number
  recipe_id?: number
  order: number
  description: string
  duration_minutes: number | null
}

export interface Recipe {
  id: number
  name: string
  description: string | null
  source: string | null
  created_at: string
  steps: RecipeStep[]
}

export interface RecipeImportPreview {
  name: string
  description: string | null
  steps: RecipeStep[]
}

export interface Timer {
  id: number
  name: string
  duration_minutes: number
  started_at: string | null
  ends_at: string | null
  is_active: boolean
  recipe_step_id: number | null
}

export interface OllamaModel {
  name: string
  size: number | null
  modified_at: string | null
}

export interface OllamaConfig {
  ollama_base_url: string
  ollama_model: string
}
