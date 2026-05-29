import { api } from './client'

export interface Goal {
  id: number
  user_id: number
  horizon: 'month' | 'year' | 'three_years' | 'five_years' | 'dream_life'
  custom_horizon_label: string | null
  custom_horizon_years: number | null
  life_area: string
  title: string
  description: string | null
  desired_state: string | null
  status: string
  created_at: string
  updated_at: string
  last_reviewed_at: string | null
}

export interface GoalCreate {
  horizon: string
  custom_horizon_label?: string
  custom_horizon_years?: number
  life_area?: string
  title: string
  description?: string
  desired_state?: string
}

export interface GoalsByHorizon {
  month: Goal[]
  year: Goal[]
  three_years: Goal[]
  five_years: Goal[]
  dream_life: Goal[]
}

export async function createGoal(data: GoalCreate): Promise<Goal> {
  return api<Goal>('/goals', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function listGoals(): Promise<GoalsByHorizon> {
  return api<GoalsByHorizon>('/goals')
}

export async function getGoal(id: number): Promise<Goal> {
  return api<Goal>(`/goals/${id}`)
}

export async function updateGoal(
  id: number,
  data: Partial<GoalCreate> & { change_note?: string }
): Promise<Goal> {
  return api<Goal>(`/goals/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function linkEntryToGoal(
  entryId: number,
  goalId?: number,
  horizon?: string,
  stepText?: string
): Promise<{ status: string; link_id: number }> {
  return api(`/goals/entry-link/${entryId}`, {
    method: 'POST',
    body: JSON.stringify({
      goal_id: goalId,
      horizon,
      step_text: stepText,
    }),
  })
}
