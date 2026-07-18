import type { Timer } from '@/types'
import { apiFetch } from './index'

export const timersApi = {
  list: () => apiFetch<Timer[]>('/timers/'),
  create: (data: { name: string; duration_minutes: number; recipe_step_id?: number }) =>
    apiFetch<Timer>('/timers/', { method: 'POST', body: JSON.stringify(data) }),
  start: (id: number) => apiFetch<Timer>(`/timers/${id}/start`, { method: 'POST' }),
  stop: (id: number) => apiFetch<Timer>(`/timers/${id}/stop`, { method: 'POST' }),
  remove: (id: number) => apiFetch<void>(`/timers/${id}`, { method: 'DELETE' }),
}
