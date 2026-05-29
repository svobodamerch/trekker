import { api } from './client'

export interface AuthResponse {
  token: string
  user: {
    id: number
    telegram_user_id: string
    username: string | null
    first_name: string | null
  }
}

export async function authTelegram(initData: string): Promise<AuthResponse> {
  return api<AuthResponse>('/auth/telegram', {
    method: 'POST',
    body: JSON.stringify({ init_data: initData }),
  })
}

export async function getCurrentUser() {
  return api<{ id: number; telegram_user_id: string; username: string | null; first_name: string | null }>('/auth/me')
}
