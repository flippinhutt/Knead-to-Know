import type { Bake } from '@/types'
import { apiFetch } from './index'

export const bakesApi = {
  list: () => apiFetch<Bake[]>('/bakes/'),
  create: (data: Partial<Bake>) =>
    apiFetch<Bake>('/bakes/', { method: 'POST', body: JSON.stringify(data) }),
  remove: (id: number) => apiFetch<void>(`/bakes/${id}`, { method: 'DELETE' }),
}
