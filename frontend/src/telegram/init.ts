import { authTelegram } from '../api/auth'
import { setAuthToken, getAuthToken } from '../utils/auth'

// Global Telegram WebApp object type
declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string
        initDataUnsafe: {
          user?: {
            id: number
            username?: string
            first_name?: string
            last_name?: string
            language_code?: string
          }
        }
        ready: () => void
        expand: () => void
      }
    }
  }
}

export type AuthMode = 'telegram' | 'mock' | 'none'

export function getAuthMode(): AuthMode {
  if (window.Telegram?.WebApp?.initData) {
    return 'telegram'
  }
  if (import.meta.env.DEV) {
    return 'mock'
  }
  return 'none'
}

export function getTelegramInitData(): string | null {
  // Try to get from window.Telegram first (real Telegram)
  if (window.Telegram?.WebApp?.initData) {
    const initData = window.Telegram.WebApp.initData
    if (import.meta.env.DEV) {
      console.log('[Telegram] Using real initData:', initData.substring(0, 50) + '...')
    }
    return initData
  }
  
  // For local development, create mock init data
  if (import.meta.env.DEV) {
    console.log('[Telegram] Using mock initData (DEV mode)')
    const mockData = new URLSearchParams({
      user_id: '123456',
      username: 'test_user',
      first_name: 'Test',
      language_code: 'ru',
    })
    return mockData.toString()
  }
  
  return null
}

export async function authenticateWithTelegram(): Promise<boolean> {
  const initData = getTelegramInitData()
  if (!initData) {
    console.error('[Auth] No Telegram init data available')
    return false
  }

  try {
    const response = await authTelegram(initData)
    setAuthToken(response.token)
    
    if (import.meta.env.DEV) {
      console.log('[Auth] Success, token received')
    }
    return true
  } catch (err) {
    console.error('[Auth] Failed:', err)
    return false
  }
}

// Debug info for development
export function getAuthDebugInfo(): {
  mode: AuthMode
  hasInitData: boolean
  hasToken: boolean
  initDataPreview: string | null
} {
  const initData = getTelegramInitData()
  return {
    mode: getAuthMode(),
    hasInitData: !!initData,
    hasToken: !!getAuthToken(),
    initDataPreview: initData ? initData.substring(0, 30) + '...' : null,
  }
}

