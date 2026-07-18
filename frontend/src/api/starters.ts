import type { Feeding, Starter } from '@/types'
import { apiFetch } from './index'

export const startersApi = {
  list: () => apiFetch<Starter[]>('/starters/'),
  get: (id: number) => apiFetch<Starter>(`/starters/${id}`),
  create: (data: { name: string; description?: string; hydration_percent?: number }) =>
    apiFetch<Starter>('/starters/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: Partial<{ name: string; description: string; hydration_percent: number; feed_interval_hours: number }>) =>
    apiFetch<Starter>(`/starters/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  remove: (id: number) => apiFetch<void>(`/starters/${id}`, { method: 'DELETE' }),
  addFeeding: (
    starterId: number,
    data: { flour_grams?: number; water_grams?: number; starter_grams?: number; height_mm?: number; notes?: string },
  ) =>
    apiFetch<Feeding>(`/starters/${starterId}/feedings`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  listFeedings: (starterId: number) => apiFetch<Feeding[]>(`/starters/${starterId}/feedings`),
}
