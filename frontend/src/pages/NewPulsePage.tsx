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
  const [recordingStep, setRecordingStep] = useState(0)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  // Voice guidance questions
  const voiceQuestions = [
    { emoji: '🎭', question: 'Какое сейчас настроение?', hint: 'Скажи число от 1 до 10' },
    { emoji: '⚡', question: 'Какая энергия в теле?', hint: 'Оцени от 1 до 10' },
    { emoji: '🌊', question: 'Есть ли тревога?', hint: 'Или скажи "нет"' },
    { emoji: '🎯', question: 'Что в теле сейчас?', hint: 'Напряжение, расслабленность...' },
    { emoji: '💡', question: 'Главный инсайт дня?', hint: 'Или скажи "нет"' },
    { emoji: '🙏', question: 'За что благодарен?', hint: 'Можно пропустить' },
    { emoji: '📍', question: 'Момент осознанности?', hint: 'Когда был здесь и сейчас?' },
    { emoji: '🌅', question: 'Обязательство на завтра?', hint: 'Одно, что точно сделаешь?' },
  ]

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
      setRecordingStep(0)
    } catch (err) {
      alert('Не удалось получить доступ к микрофону. Проверь разрешения.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setRecordingStep(0)
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
            <div className="py-6 px-4 bg-gradient-to-br from-soft-100 to-soft-200 rounded-2xl">
              {/* Progress dots */}
              <div className="flex justify-center gap-1 mb-4">
                {voiceQuestions.map((_, idx) => (
                  <div
                    key={idx}
                    className={`w-2 h-2 rounded-full transition-colors ${
                      idx === recordingStep ? 'bg-soft-600' :
                      idx < recordingStep ? 'bg-soft-400' : 'bg-soft-200'
                    }`}
                  />
                ))}
              </div>

              {/* Current question */}
              <div className="text-center mb-4">
                <div className="text-4xl mb-2">{voiceQuestions[recordingStep]?.emoji}</div>
                <h3 className="text-lg font-medium text-soft-800 mb-1">
                  {voiceQuestions[recordingStep]?.question}
                </h3>
                <p className="text-sm text-soft-500">
                  {voiceQuestions[recordingStep]?.hint}
                </p>
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-center gap-3">
                {recordingStep > 0 && (
                  <button
                    onClick={() => setRecordingStep(prev => prev - 1)}
                    className="px-4 py-2 text-soft-500 text-sm hover:text-soft-700"
                  >
                    ← Назад
                  </button>
                )}

                <button
                  onClick={stopRecording}
                  className="px-6 py-3 bg-red-500 text-white rounded-full font-medium hover:bg-red-600 transition-colors flex items-center gap-2"
                >
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                  Завершить
                </button>

                {recordingStep < voiceQuestions.length - 1 && (
                  <button
                    onClick={() => setRecordingStep(prev => prev + 1)}
                    className="px-4 py-2 text-soft-500 text-sm hover:text-soft-700"
                  >
                    Пропустить →
                  </button>
                )}
              </div>

              <p className="text-center text-xs text-soft-400 mt-3">
                Вопрос {recordingStep + 1} из {voiceQuestions.length}
              </p>
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
