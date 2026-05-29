import { api } from './client'

export interface EntryCreate {
  entry_type?: string
  mood?: number
  anxiety?: number
  energy?: number
  body_state?: string
  insight?: string
  gratitude?: string
  tomorrow_commitment?: string
  source?: string
}

export interface Entry {
  id: number
  user_id: number
  entry_type: string
  mood: number | null
  anxiety: number | null
  energy: number | null
  body_state: string | null
  insight: string | null
  gratitude: string | null
  tomorrow_commitment: string | null
  source: string
  created_at: string
}

export interface EntryList {
  items: Entry[]
  total: number
}

export async function createEntry(data: EntryCreate): Promise<Entry> {
  return api<Entry>('/entries', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function listEntries(limit = 20, offset = 0): Promise<EntryList> {
  return api<EntryList>(`/entries?limit=${limit}&offset=${offset}`)
}

export async function getEntry(id: number): Promise<Entry> {
  return api<Entry>(`/entries/${id}`)
}
