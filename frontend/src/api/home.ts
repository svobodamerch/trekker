import { api } from './client'

export type ReturnState = 'new_user' | 'active_today' | 'one_day_gap' | 'after_pause' | 'long_pause'

export interface HomeSummary {
  days_since_last_entry: number | null
  return_state: ReturnState
  has_entries: boolean
  latest_entry_preview: {
    id: number
    created_at: string
    mood: number | null
    anxiety: number | null
    energy: number | null
    insight: string | null
  } | null
}

export async function getHomeSummary(): Promise<HomeSummary> {
  return api<HomeSummary>('/entries/home/summary')
}
