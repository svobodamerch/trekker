import { api } from './client'

export interface UserProfile {
  id: number
  telegram_user_id: string
  username?: string
  first_name?: string
  last_name?: string
  gender?: string
  birth_date?: string  // YYYY-MM-DD
  age?: number  // Calculated from birth_date
  onboarding_completed: boolean
  timezone: string
}

export interface UserProfileUpdate {
  first_name?: string
  last_name?: string
  gender?: string
  birth_date?: string  // YYYY-MM-DD
}

export interface OnboardingData {
  first_name: string
  last_name: string
  gender: string  // male, female
  birth_date: string  // YYYY-MM-DD
}

export interface UsersStats {
  total_users: number
  active_users: number
  active_period_days: number
}

export async function getMyProfile(): Promise<UserProfile> {
  return api<UserProfile>('/users/me')
}

export async function updateMyProfile(data: UserProfileUpdate): Promise<UserProfile> {
  return api<UserProfile>('/users/me', {
    method: 'PATCH',
    body: JSON.stringify(data)
  })
}

export async function completeOnboarding(data: OnboardingData): Promise<UserProfile> {
  return api<UserProfile>('/users/onboarding', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export async function getUsersStats(): Promise<UsersStats> {
  return api<UsersStats>('/users/stats')
}
