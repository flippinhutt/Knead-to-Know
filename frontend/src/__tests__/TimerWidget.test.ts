import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TimerWidget from '../components/TimerWidget.vue'
import type { Timer } from '../types'

const baseTimer: Timer = {
  id: 1,
  name: 'Bulk Ferment',
  duration_minutes: 60,
  started_at: null,
  ends_at: null,
  is_active: false,
  recipe_step_id: null,
}

describe('TimerWidget', () => {
  it('renders timer name', () => {
    const w = mount(TimerWidget, { props: { timer: baseTimer } })
    expect(w.text()).toContain('Bulk Ferment')
  })

  it('shows full duration when inactive', () => {
    const w = mount(TimerWidget, { props: { timer: baseTimer } })
    expect(w.text()).toContain('1:00:00')
  })

  it('shows Start button when inactive', () => {
    const w = mount(TimerWidget, { props: { timer: baseTimer } })
    expect(w.find('button.btn-primary').text()).toBe('Start')
  })

  it('shows Stop button when active', () => {
    const ends = new Date(Date.now() + 60 * 60 * 1000).toISOString()
    const w = mount(TimerWidget, {
      props: { timer: { ...baseTimer, is_active: true, started_at: new Date().toISOString(), ends_at: ends } },
    })
    expect(w.find('button.btn-secondary').text()).toBe('Stop')
  })

  it('emits start on start click', async () => {
    const w = mount(TimerWidget, { props: { timer: baseTimer } })
    await w.find('button.btn-primary').trigger('click')
    expect(w.emitted('start')).toBeTruthy()
  })
})
