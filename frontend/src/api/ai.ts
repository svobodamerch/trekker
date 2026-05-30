import { api } from './client'

export interface AIAnalysisResult {
  key_patterns: string
  emotional_dynamics: string
  body_signals: string
  insight_themes: string
  goal_alignment: string
  recommendations: string
  is_placeholder?: boolean
  provider?: string
  entry_count?: number
  error?: string
}

export async function analyzeAllEntries(): Promise<AIAnalysisResult> {
  return api<AIAnalysisResult>('/ai/analyze-all', {
    method: 'POST',
  })
}
