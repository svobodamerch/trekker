import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SliderInput } from '../components/SliderInput'
import { TextArea } from '../components/TextArea'
import { createEntry } from '../api/entries'

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
        source: 'mini_app',
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
