import { api } from './client'
import type { Goal } from './goals'

export interface GoalReviewData {
  is_alive?: boolean
  became_clearer?: string
  wants_to_change?: string
  next_week_step?: string
  title?: string
  description?: string
  desired_state?: string
  status?: 'active' | 'paused' | 'completed' | 'archived'
}

export interface GoalsNeedingReview {
  goals: Goal[]
  count: number
  message: string
}

export async function reviewGoal(goalId: number, data: GoalReviewData): Promise<Goal> {
  return api<Goal>(`/goals/${goalId}/review`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getGoalsNeedingReview(): Promise<GoalsNeedingReview> {
  return api<GoalsNeedingReview>('/goals/needs-review')
}
