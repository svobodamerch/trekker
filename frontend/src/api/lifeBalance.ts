import { api } from './client'

export interface ScoreOut {
  area_key: string
  area_label: string
  score: number
  comment: string | null
}

export interface SnapshotOut {
  id: number
  created_at: string
  note: string | null
  scores: ScoreOut[]
}

export interface ScoreIn {
  area_key: string
  score: number
  comment?: string
}

export interface SnapshotCreate {
  scores: ScoreIn[]
  note?: string
}

export interface ComparisonChange {
  area_key: string
  area_label: string
  previous: number
  current: number
  delta: number
}

export interface ComparisonResult {
  has_comparison: boolean
  latest_date?: string
  previous_date?: string
  changes?: ComparisonChange[]
}

export const LIFE_AREAS: { key: string; label: string }[] = [
  { key: 'health_body', label: 'Здоровье и тело' },
  { key: 'energy_state', label: 'Энергия и состояние' },
  { key: 'relationships_family', label: 'Отношения и семья' },
  { key: 'friends_environment', label: 'Друзья и окружение' },
  { key: 'money', label: 'Деньги' },
  { key: 'work_business', label: 'Работа / бизнес / реализация' },
  { key: 'home_space', label: 'Дом и среда' },
  { key: 'freedom_meaning_growth', label: 'Свобода, смысл и рост' },
]

export function createSnapshot(data: SnapshotCreate): Promise<SnapshotOut> {
  return api<SnapshotOut>('/life-balance/snapshots', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function getLatestSnapshot(): Promise<SnapshotOut | null> {
  return api<SnapshotOut | null>('/life-balance/latest')
}

export function getComparison(): Promise<ComparisonResult> {
  return api<ComparisonResult>('/life-balance/comparison')
}

export function getHistory(): Promise<SnapshotOut[]> {
  return api<SnapshotOut[]>('/life-balance/history')
}
