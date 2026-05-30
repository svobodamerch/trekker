import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { ScaleInput } from '../components/ScaleInput'
import { TextArea } from '../components/TextArea'
import { createEntry } from '../api/entries'
import { processVoiceRecording } from '../api/voice'

export function NewPulsePage() {
  const navigate = useNavigate()
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({
    mood: undefined as number | undefined,
    anxiety: undefined as number | undefined,
    energy: undefined as number | undefined,
    body_state: '',
    insight: '',
    gratitude: '',
    tomorrow_commitment: '',
  })

  const canSave = form.mood !== undefined && form.anxiety !== undefined && form.energy !== undefined

  // Voice recording state
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessingVoice, setIsProcessingVoice] = useState(false)
  const [voicePreview, setVoicePreview] = useState<string | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/ogg' })
        await handleVoiceProcessing(audioBlob)
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (err) {
      alert('Не удалось получить доступ к микрофону. Проверь разрешения.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleVoiceProcessing = async (audioBlob: Blob) => {
    setIsProcessingVoice(true)
    try {
      const result = await processVoiceRecording(audioBlob)

      if (result.success && result.recognized_type === 'entry') {
        // Fill form with voice data
        setForm(prev => ({
          ...prev,
          mood: result.created.mood ?? prev.mood,
          energy: result.created.energy ?? prev.energy,
          anxiety: result.created.anxiety ?? prev.anxiety,
        }))
        setVoicePreview(result.transcript)
      } else if (result.success && result.recognized_type === 'goal') {
        // Redirect to goals if voice was classified as goal
        alert(`Распознана цель: "${result.created.title}". Перенаправляю в раздел целей.`)
        navigate('/goals')
        return
      } else {
        setVoicePreview(result.transcript || 'Голос не распознан')
      }
    } catch (err) {
      alert('Не удалось обработать голос. Попробуй ещё раз.')
    } finally {
      setIsProcessingVoice(false)
    }
  }

  const handleSave = async () => {
    if (!canSave) return
    setSaving(true)
    try {
      await createEntry({
        mood: form.mood,
        anxiety: form.anxiety,
        energy: form.energy,
        body_state: form.body_state || undefined,
        insight: form.insight || undefined,
        gratitude: form.gratitude || undefined,
        tomorrow_commitment: form.tomorrow_commitment || undefined,
        raw_text: voicePreview || undefined,  // Include voice transcript if present
        source: voicePreview ? 'voice' : 'mini_app',
      })
      navigate('/')
    } catch (err) {
      alert('Что-то пошло не так. Давай попробуем ещё раз?')
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-md mx-auto">
        <h1 className="text-xl font-semibold text-soft-800 mb-6">
          Новый Пульс
        </h1>

        {/* Voice recording */}
        <div className="mb-6">
          {!isRecording && !isProcessingVoice && !voicePreview && (
            <button
              onClick={startRecording}
              className="w-full py-3 bg-white border-2 border-dashed border-soft-300 rounded-xl text-soft-600 flex items-center justify-center gap-2 hover:border-soft-500 hover:text-soft-700 transition-colors"
            >
              <span className="text-xl">🎤</span>
              <span className="text-sm font-medium">Голосовой отчет — скажи вслух</span>
            </button>
          )}

          {isRecording && (
            <div className="flex items-center justify-center gap-3 py-4 bg-red-50 rounded-xl">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <span className="text-red-600 text-sm font-medium">Идет запись... Нажми, чтобы остановить</span>
              <button
                onClick={stopRecording}
                className="px-3 py-1 bg-red-500 text-white text-xs rounded-full"
              >
                Стоп
              </button>
            </div>
          )}

          {isProcessingVoice && (
            <div className="flex items-center justify-center py-4 bg-soft-50 rounded-xl">
              <span className="text-soft-500 text-sm">Распознаю голос...</span>
            </div>
          )}

          {voicePreview && (
            <div className="p-3 bg-soft-50 rounded-xl">
              <p className="text-xs text-soft-400 mb-1">Распознано:</p>
              <p className="text-sm text-soft-700 italic">"{voicePreview}"</p>
              <button
                onClick={() => setVoicePreview(null)}
                className="mt-2 text-xs text-soft-400 hover:text-soft-600"
              >
                Очистить
              </button>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <ScaleInput
            label="Настроение"
            value={form.mood}
            onChange={(v) => setForm({ ...form, mood: v })}
          />

          <ScaleInput
            label="Тревога"
            value={form.anxiety}
            onChange={(v) => setForm({ ...form, anxiety: v })}
          />

          <ScaleInput
            label="Энергия"
            value={form.energy}
            onChange={(v) => setForm({ ...form, energy: v })}
          />

          <TextArea
            label="Что сейчас в теле?"
            value={form.body_state}
            onChange={(v) => setForm({ ...form, body_state: v })}
            placeholder="Например: легкая усталость, напряжение в плечах..."
            rows={2}
          />

          <TextArea
            label="Главный инсайт"
            value={form.insight}
            onChange={(v) => setForm({ ...form, insight: v })}
            placeholder="О чем узнал сегодня?"
            rows={2}
          />

          <TextArea
            label="За что благодарен?"
            value={form.gratitude}
            onChange={(v) => setForm({ ...form, gratitude: v })}
            placeholder="Одна маленькая вещь..."
            rows={2}
          />

          <TextArea
            label="Одно обязательство на завтра"
            value={form.tomorrow_commitment}
            onChange={(v) => setForm({ ...form, tomorrow_commitment: v })}
            placeholder="Что одно точно сделаешь?"
            rows={2}
          />

          <div className="pt-4 space-y-3">
            <button
              onClick={handleSave}
              disabled={!canSave || saving}
              className="w-full py-4 bg-soft-600 text-white rounded-2xl font-medium hover:bg-soft-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {saving ? 'Сохраняем...' : 'Сохранить'}
            </button>

            <button
              onClick={() => navigate('/')}
              className="w-full py-3 text-soft-500 text-sm hover:text-soft-700"
            >
              Отмена
            </button>
          </div>

          {!canSave && (
            <p className="text-center text-soft-400 text-xs">
              Выбери значения для настроения, тревоги и энергии
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
