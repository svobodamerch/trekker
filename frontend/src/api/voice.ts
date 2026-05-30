export interface VoiceProcessResult {
  success: boolean
  recognized_type: 'entry' | 'goal'
  confidence: number
  transcript: string
  created: {
    type: 'entry' | 'goal'
    id: number
    entry_type?: string
    mood?: number
    energy?: number
    anxiety?: number
    title?: string
    horizon?: string
    // Text fields for entry
    body_state?: string
    insight?: string
    gratitude?: string
    tomorrow_commitment?: string
    today_moment?: string
  }
  data?: {
    body_state?: string
    insight?: string
    gratitude?: string
    tomorrow_commitment?: string
    today_moment?: string
  }
  parsed: boolean
}

export async function processVoiceRecording(audioBlob: Blob): Promise<VoiceProcessResult> {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'voice.ogg')

  return fetch(`${import.meta.env.VITE_API_URL || ''}/voice/process`, {
    method: 'POST',
    body: formData,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
    },
  }).then(async (res) => {
    if (!res.ok) {
      const err = await res.text()
      throw new Error(err || `HTTP ${res.status}`)
    }
    return res.json()
  })
}

export async function transcribeOnly(audioBlob: Blob): Promise<{ transcript: string; language: string }> {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'voice.ogg')

  return fetch(`${import.meta.env.VITE_API_URL || ''}/voice/transcribe-only`, {
    method: 'POST',
    body: formData,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
    },
  }).then(async (res) => {
    if (!res.ok) {
      const err = await res.text()
      throw new Error(err || `HTTP ${res.status}`)
    }
    return res.json()
  })
}
