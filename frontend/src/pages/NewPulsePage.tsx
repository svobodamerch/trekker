import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SliderInput } from '../components/SliderInput'
import { TextArea } from '../components/TextArea'
import { createEntry } from '../api/entries'
import { shareFromSource } from '../api/community'

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
  const [shareToCommunity, setShareToCommunity] = useState(false)
  const [sharePrompt, setSharePrompt] = useState('')

  const canSave = form.mood !== undefined && form.anxiety !== undefined && form.energy !== undefined

  const handleSave = async () => {
    if (!canSave) return
    setSaving(true)
    try {
      // Create the pulse entry
      const entry = await createEntry({
        mood: form.mood,
        anxiety: form.anxiety,
        energy: form.energy,
        body_state: form.body_state || undefined,
        insight: form.insight || undefined,
        gratitude: form.gratitude || undefined,
        tomorrow_commitment: form.tomorrow_commitment || undefined,
        source: 'mini_app',
      })
      
      // Optionally share to community
      if (shareToCommunity) {
        try {
          await shareFromSource({
            source_type: 'pulse',
            source_id: entry.id,
            discussion_prompt: sharePrompt || undefined,
            visibility: 'anonymous'
          })
        } catch (shareErr) {
          console.error('Failed to share to community', shareErr)
          // Don't block navigation on share error
        }
      }
      
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

          {/* Share to Community */}
          <div className="bg-soft-50 rounded-2xl p-4 space-y-3">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={shareToCommunity}
                onChange={(e) => setShareToCommunity(e.target.checked)}
                className="mt-1 w-5 h-5 accent-soft-600"
              />
              <div>
                <span className="font-medium text-soft-800 block">
                  Добавить в общую ленту в круг поддержки
                </span>
                <span className="text-soft-500 text-sm">
                  Люди смогут поддержать тебя и обсудить твой пульс
                </span>
              </div>
            </label>

            {shareToCommunity && (
              <div className="pt-2 border-t border-soft-200">
                <input
                  type="text"
                  value={sharePrompt}
                  onChange={(e) => setSharePrompt(e.target.value)}
                  placeholder="Вопрос к сообществу (необязательно)..."
                  className="w-full px-4 py-3 rounded-xl border border-soft-200 bg-white text-soft-900 placeholder:text-soft-400 focus:outline-none focus:ring-2 focus:ring-soft-400 text-sm"
                />
              </div>
            )}
          </div>

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
