import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

const CATEGORIES = [
  { value: 'bug', label: 'Ошибка' },
  { value: 'unclear', label: 'Непонятно' },
  { value: 'idea', label: 'Идея' },
  { value: 'other', label: 'Другое' },
] as const

type Category = typeof CATEGORIES[number]['value']

export function FeedbackPage() {
  const navigate = useNavigate()
  const [category, setCategory] = useState<Category>('other')
  const [message, setMessage] = useState('')
  const [saving, setSaving] = useState(false)
  const [done, setDone] = useState(false)

  const canSave = message.trim().length > 0

  const handleSave = async () => {
    if (!canSave) return
    setSaving(true)
    try {
      await api('/feedback', {
        method: 'POST',
        body: JSON.stringify({ category, message: message.trim(), source: 'mini_app' }),
      })
      setDone(true)
    } catch {
      alert('Не удалось отправить. Попробуй ещё раз.')
      setSaving(false)
    }
  }

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="max-w-sm text-center space-y-4">
          <p className="text-soft-700 font-medium text-lg">Спасибо</p>
          <p className="text-soft-500 text-sm">
            Обратная связь сохранена. Если это что-то срочное, можешь написать напрямую.
          </p>
          <button
            onClick={() => navigate('/')}
            className="w-full py-3 bg-soft-600 text-white rounded-xl font-medium"
          >
            На главную
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-semibold text-soft-800">Обратная связь</h1>
          <button
            onClick={() => navigate(-1)}
            className="text-soft-500 text-sm hover:text-soft-700"
          >
            Отмена
          </button>
        </div>

        <div className="space-y-5">
          <div>
            <p className="text-sm text-soft-600 mb-2">Тема</p>
            <div className="flex gap-2 flex-wrap">
              {CATEGORIES.map((c) => (
                <button
                  key={c.value}
                  onClick={() => setCategory(c.value)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium border transition-colors ${
                    category === c.value
                      ? 'bg-soft-600 text-white border-soft-600'
                      : 'bg-white text-soft-600 border-soft-200 hover:border-soft-400'
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="text-sm text-soft-600 mb-2">Сообщение</p>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Напиши что сломалось, что непонятно или что хочется изменить..."
              rows={6}
              className="w-full px-4 py-3 bg-white border border-soft-200 rounded-2xl text-soft-800 placeholder-soft-300 focus:outline-none focus:border-soft-400 resize-none"
            />
          </div>

          <button
            onClick={handleSave}
            disabled={!canSave || saving}
            className="w-full py-4 bg-soft-600 text-white rounded-2xl font-medium hover:bg-soft-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {saving ? 'Отправляем...' : 'Отправить'}
          </button>
        </div>
      </div>
    </div>
  )
}
