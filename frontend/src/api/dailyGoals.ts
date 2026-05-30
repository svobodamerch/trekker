import { api } from './client'

export interface DailyGoalsEntry {
  id: number
  goal_date: string
  goals: string[]
  created_at: string
}

export interface DailyGoalsHistory {
  today: DailyGoalsEntry | null
  archive: DailyGoalsEntry[]
  streak_days: number
}

export async function getTodayGoals(): Promise<DailyGoalsEntry> {
  return api<DailyGoalsEntry>('/daily-goals/today')
}

export async function saveTodayGoals(goals: string[]): Promise<DailyGoalsEntry> {
  return api<DailyGoalsEntry>('/daily-goals/today', {
    method: 'POST',
    body: JSON.stringify({ goals }),
  })
}

export async function getGoalsHistory(): Promise<DailyGoalsHistory> {
  return api<DailyGoalsHistory>('/daily-goals/history')
}

export async function deleteGoalsEntry(entryId: number): Promise<void> {
  await api(`/daily-goals/${entryId}`, {
    method: 'DELETE',
  })
}
