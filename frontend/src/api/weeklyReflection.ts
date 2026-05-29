import { api } from './client'

export interface WeeklyReflection {
  id: number
  analysis_type: string
  period_start: string
  period_end: string
  entry_count: number
  patterns: string
  energy_insights: string
  goal_connections: string
  next_week_question: string
  next_week_focus: string
  is_placeholder: boolean
  created_at: string
}

export async function createWeeklyReflection(): Promise<WeeklyReflection> {
  return api<WeeklyReflection>('/ai/weekly-reflection', {
    method: 'POST',
  })
}

export async function getLatestWeeklyReflection(): Promise<WeeklyReflection | null> {
  return api<WeeklyReflection | null>('/ai/weekly-reflection/latest')
}
