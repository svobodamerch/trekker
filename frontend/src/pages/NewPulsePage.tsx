import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { SliderInput } from '../components/SliderInput'
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
  const streamRef = useRef<MediaStream | null>(null)

  // Voice guidance questions - text fields only (no numbers)
  const voiceQuestions = [
    { emoji: '🎯', question: 'Что в теле сейчас?', hint: 'Напряжение, расслабленность, ощущения...' },
    { emoji: '💡', question: 'Главный инсайт дня?', hint: 'Что осознал сегодня?' },
    { emoji: '🙏', question: 'За что благодарен?', hint: 'Маленькие или большие вещи...' },
    { emoji: '📍', question: 'Момент осознанности?', hint: 'Когда был "здесь и сейчас"?' },
    { emoji: '🌅', question: 'Обязательство на завтра?', hint: 'Одно конкретное действие...' },
  ]

  // Audio visualization refs
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animationRef = useRef<number | null>(null)
  const [audioData, setAudioData] = useState<number[]>(new Array(12).fill(10))

  // Real-time audio visualization
  const startAudioVisualization = (stream: MediaStream) => {
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const analyser = audioContext.createAnalyser()
      const source = audioContext.createMediaStreamSource(stream)
      
      source.connect(analyser)
      analyser.fftSize = 64
      analyser.smoothingTimeConstant = 0.8
      
      audioContextRef.current = audioContext
      analyserRef.current = analyser
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount)
      
      const animate = () => {
        if (!analyserRef.current) return
        
        analyserRef.current.getByteFrequencyData(dataArray)
        
        // Take 12 samples from the frequency data
        const samples = []
        const step = Math.floor(dataArray.length / 12)
        for (let i = 0; i < 12; i++) {
          const value = dataArray[i * step] || 0
          // Scale to 10-100 range for visual
          samples.push(Math.max(10, Math.min(100, value)))
        }
        
        setAudioData(samples)
        animationRef.current = requestAnimationFrame(animate)
      }
      
      animate()
    } catch (e) {
      console.log('Audio visualization not supported, using fallback')
      // Fallback: random animation
      const fallbackAnimate = () => {
        setAudioData(new Array(12).fill(0).map(() => 20 + Math.random() * 60))
        animationRef.current = requestAnimationFrame(fallbackAnimate)
      }
      fallbackAnimate()
    }
  }
  
  const stopAudioVisualization = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
      animationRef.current = null
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    analyserRef.current = null
    setAudioData(new Array(12).fill(10))
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        stopAudioVisualization()
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/ogg' })
        await handleVoiceProcessing(audioBlob)
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
        streamRef.current = null
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingStep(0)
      
      // Start real-time visualization
      startAudioVisualization(stream)
    } catch (err) {
      alert('Не удалось получить доступ к микрофону. Проверь разрешения.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setRecordingStep(0)
      stopAudioVisualization()
    }
  }

  const handleVoiceProcessing = async (audioBlob: Blob) => {
    setIsProcessingVoice(true)
    try {
      const result = await processVoiceRecording(audioBlob)

      if (result.success && result.recognized_type === 'entry') {
        // Fill text fields only - numbers come from sliders, not voice
        setForm(prev => ({
          ...prev,
          // Text fields from voice only
          body_state: result.data?.body_state || result.created.body_state || prev.body_state,
          insight: result.data?.insight || result.created.insight || prev.insight,
          gratitude: result.data?.gratitude || result.created.gratitude || prev.gratitude,
          tomorrow_commitment: result.data?.tomorrow_commitment || result.created.tomorrow_commitment || prev.tomorrow_commitment,
          // Note: mood/energy/anxiety come from sliders, NOT from voice
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
      console.error('Voice processing error:', err)
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
          Пульс дня
        </h1>

        <div className="space-y-8">
          <SliderInput
            label="Настроение"
            value={form.mood}
            onChange={(v: number) => setForm({ ...form, mood: v })}
            leftLabel="Тяжело"
            rightLabel="Отлично"
          />

          <SliderInput
            label="Тревога"
            value={form.anxiety}
            onChange={(v: number) => setForm({ ...form, anxiety: v })}
            leftLabel="Спокойно"
            rightLabel="Тревожно"
          />

          <SliderInput
            label="Энергия"
            value={form.energy}
            onChange={(v: number) => setForm({ ...form, energy: v })}
            leftLabel="Нет сил"
            rightLabel="Полный ресурс"
          />

          {/* Voice recording - after sliders */}
          <div className="py-4 border-t border-soft-200">
            {!isRecording && !isProcessingVoice && !voicePreview && (
              <button
                onClick={startRecording}
                className="w-full py-4 bg-soft-100 border-2 border-dashed border-soft-300 rounded-xl text-soft-600 flex items-center justify-center gap-2 hover:border-soft-500 hover:text-soft-700 hover:bg-soft-150 transition-colors"
              >
                <span className="text-2xl">🎤</span>
                <span className="text-sm font-medium">Голосовой отчет — расскажи текстом</span>
              </button>
            )}

            {isRecording && (
              <div className="py-6 px-4 bg-gradient-to-br from-soft-100 to-soft-200 rounded-2xl">
                {/* Real audio wave visualization */}
                <div className="flex justify-center items-end gap-1 h-16 mb-6">
                  {audioData.map((value, i) => (
                    <div
                      key={i}
                      className="w-2 bg-soft-500 rounded-full transition-all duration-75"
                      style={{
                        height: `${Math.max(8, value)}%`,
                        opacity: value > 30 ? 1 : 0.5,
                      }}
                    />
                  ))}
                </div>

                {/* Progress dots */}
                <div className="flex justify-center gap-1.5 mb-4">
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
                <div className="text-center mb-6">
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
