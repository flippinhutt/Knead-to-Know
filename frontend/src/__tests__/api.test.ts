import { describe, it, expect, vi, beforeEach } from 'vitest'
import { apiFetch } from '../api/index'

describe('apiFetch', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  it('returns parsed JSON on success', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: 1, name: 'Bubbles' }),
    } as Response)

    const result = await apiFetch<{ id: number; name: string }>('/starters/')
    expect(result).toEqual({ id: 1, name: 'Bubbles' })
    expect(fetch).toHaveBeenCalledWith('/api/starters/', expect.objectContaining({ headers: expect.any(Object) }))
  })

  it('returns undefined on 204', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      status: 204,
    } as Response)

    const result = await apiFetch<void>('/starters/1', { method: 'DELETE' })
    expect(result).toBeUndefined()
  })

  it('throws on HTTP error', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Starter not found' }),
    } as Response)

    await expect(apiFetch('/starters/999')).rejects.toThrow('Starter not found')
  })
})
