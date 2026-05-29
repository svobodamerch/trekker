import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createGoal } from '../api/goals'
import { TextArea } from '../components/TextArea'

const HORIZONS = [
  { value: 'month', label: '1 месяц' },
  { value: 'year', label: '1 год' },
  { value: 'three_years', label: '3 года' },
  { value: 'five_years', label: '5 лет' },
  { value: 'dream_life', label: 'Жизнь мечты' },
]

const LIFE_AREAS = [
  { value: 'health', label: 'Состояние и здоровье' },
  { value: 'relationships', label: 'Отношения и семья' },
  { value: 'money', label: 'Деньги' },
  { value: 'business', label: 'Бизнес' },
  { value: 'work', label: 'Работа и реализация' },
  { value: 'home', label: 'Дом и среда' },
  { value: 'freedom', label: 'Свобода и путешествия' },
  { value: 'spirituality', label: 'Духовность и рост' },
  { value: 'body', label: 'Тело и энергия' },
  { value: 'learning', label: 'Обучение и навыки' },
  { value: 'contribution', label: 'Вклад и смысл' },
  { value: 'other', label: 'Другое' },
]

export function GoalEditorPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEditing = !!id
  const [saving, setSaving] = useState(false)

  const [form, setForm] = useState({
    horizon: 'month',
    custom_horizon_label: '',
    custom_horizon_years: '',
    life_area: 'other',
    title: '',
    description: '',
    desired_state: '',
  })

  const isDreamLife = form.horizon === 'dream_life'

  const handleSave = async () => {
    if (!form.title.trim()) return

    setSaving(true)
    try {
      await createGoal({
        horizon: form.horizon,
        custom_horizon_label: isDreamLife ? form.custom_horizon_label : undefined,
        custom_horizon_years: isDreamLife && form.custom_horizon_years
          ? parseInt(form.custom_horizon_years)
          : undefined,
        life_area: form.life_area,
        title: form.title,
        description: form.description || undefined,
        desired_state: form.desired_state || undefined,
      })
      navigate('/goals')
    } catch (err) {
      alert('Не удалось сохранить. Проверь соединение и попробуй снова.')
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-semibold text-soft-800">
            {isEditing ? 'Редактировать цель' : 'Новая цель'}
          </h1>
          <button
            onClick={() => navigate('/goals')}
            className="text-soft-500 text-sm hover:text-soft-700"
          >
            Назад
          </button>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-soft-700 mb-2">
              Горизонт
            </label>
            <select
              value={form.horizon}
              onChange={(e) => setForm({ ...form, horizon: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-soft-200 bg-white"
            >
              {HORIZONS.map((h) => (
                <option key={h.value} value={h.value}>
                  {h.label}
                </option>
              ))}
            </select>
          </div>

          {isDreamLife && (
            <>
              <TextArea
                label="Какой срок для жизни мечты?"
                value={form.custom_horizon_label}
                onChange={(v) => setForm({ ...form, custom_horizon_label: v })}
                placeholder="Например: через 10 лет, или до 45 лет"
                rows={1}
              />
              <div>
                <label className="block text-sm font-medium text-soft-700 mb-2">
                  Сколько лет
                </label>
                <input
                  type="number"
                  value={form.custom_horizon_years}
                  onChange={(e) => setForm({ ...form, custom_horizon_years: e.target.value })}
                  placeholder="10"
                  className="w-full px-4 py-3 rounded-xl border border-soft-200 bg-white"
                />
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-soft-700 mb-2">
              Сфера жизни
            </label>
            <select
              value={form.life_area}
              onChange={(e) => setForm({ ...form, life_area: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border border-soft-200 bg-white"
            >
              {LIFE_AREAS.map((a) => (
                <option key={a.value} value={a.value}>
                  {a.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-soft-700 mb-2">
              Название цели
            </label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Коротко, что хочу достичь"
              className="w-full px-4 py-3 rounded-xl border border-soft-200 bg-white"
            />
          </div>

          <TextArea
            label="Описание"
            value={form.description}
            onChange={(v) => setForm({ ...form, description: v })}
            placeholder="Подробнее о цели..."
            rows={3}
          />

          <TextArea
            label="Желаемое состояние"
            value={form.desired_state}
            onChange={(v) => setForm({ ...form, desired_state: v })}
            placeholder="Как я буду себя чувствовать, когда достигну?"
            rows={2}
          />

          <div className="pt-4 space-y-3">
            <button
              onClick={handleSave}
              disabled={!form.title.trim() || saving}
              className="w-full py-4 bg-soft-600 text-white rounded-2xl font-medium hover:bg-soft-700 disabled:opacity-50"
            >
              {saving ? 'Сохраняем...' : 'Сохранить'}
            </button>

            <button
              onClick={() => navigate('/goals')}
              className="w-full py-3 text-soft-500 text-sm hover:text-soft-700"
            >
              Отмена
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
