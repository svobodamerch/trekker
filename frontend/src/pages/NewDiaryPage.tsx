import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { TextArea } from '../components/TextArea'
import { createEntry } from '../api/entries'

export function NewDiaryPage() {
  const navigate = useNavigate()
  const [saving, setSaving] = useState(false)
  const [text, setText] = useState('')

  const canSave = text.trim().length > 0

  const handleSave = async () => {
    if (!canSave) return
    setSaving(true)
    try {
      await createEntry({
        entry_type: 'diary',
        raw_text: text.trim(),
        source: 'mini_app',
      })
      navigate('/history')
    } catch (err) {
      alert('Не удалось сохранить. Проверь соединение и попробуй снова.')
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-semibold text-soft-800">Запись</h1>
          <button
            onClick={() => navigate('/history')}
            className="text-soft-500 text-sm hover:text-soft-700"
          >
            Отмена
          </button>
        </div>

        <div className="space-y-6">
          <TextArea
            label="Мысли, наблюдения, что угодно"
            value={text}
            onChange={setText}
            placeholder="Напиши всё, что хочется — без структуры, просто как есть..."
            rows={10}
          />

          <button
            onClick={handleSave}
            disabled={!canSave || saving}
            className="w-full py-4 bg-soft-600 text-white rounded-2xl font-medium hover:bg-soft-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {saving ? 'Сохраняем...' : 'Сохранить'}
          </button>
        </div>
      </div>
    </div>
  )
}
