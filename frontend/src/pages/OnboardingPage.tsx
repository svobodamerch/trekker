import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { completeOnboarding } from '../api/users'

export function OnboardingPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    gender: '' as 'male' | 'female' | 'other' | '',
    age: '' as string | number,
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canSubmit = form.firstName.trim() && form.lastName.trim() && form.gender && form.age

  const handleSubmit = async () => {
    if (!canSubmit) return
    
    setSaving(true)
    setError(null)
    
    try {
      await completeOnboarding({
        first_name: form.firstName.trim(),
        last_name: form.lastName.trim(),
        gender: form.gender,
        age: Number(form.age)
      })
      navigate('/')
    } catch (err) {
      setError('Не удалось сохранить профиль. Попробуй ещё раз.')
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-soft-50 p-4">
      <div className="max-w-md mx-auto pt-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-soft-800 mb-2">
            Добро пожаловать!
          </h1>
          <p className="text-soft-600">
            Расскажи немного о себе, чтобы мы могли лучше поддерживать тебя
          </p>
        </div>

        <div className="bg-white rounded-2xl p-6 space-y-6">
          {error && (
            <div className="p-3 bg-red-50 text-red-600 rounded-xl text-sm">
              {error}
            </div>
          )}

          {/* First Name */}
          <div>
            <label className="block text-sm font-medium text-soft-700 mb-2">
              Имя <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={form.firstName}
              onChange={(e) => setForm({ ...form, firstName: e.target.value })}
              placeholder="Твоё имя"
              className="w-full px-4 py-3 rounded-xl border border-soft-200 bg-white text-soft-900 placeholder:text-soft-400 focus:outline-none focus:ring-2 focus:ring-soft-400"
            />
          </div>

          {/* Last Name */}
          <div>
            <label className="block text-sm font-medium text-soft-700 mb-2">
              Фамилия <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={form.lastName}
              onChange={(e) => setForm({ ...form, lastName: e.target.value })}
              placeholder="Твоя фамилия"
              className="w-full px-4 py-3 rounded-xl border border-soft-200 bg-white text-soft-900 placeholder:text-soft-400 focus:outline-none focus:ring-2 focus:ring-soft-400"
            />
          </div>

          {/* Gender */}
          <div>
            <label className="block text-sm font-medium text-soft-700 mb-2">
              Пол <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'male', label: 'Мужской' },
                { value: 'female', label: 'Женский' },
                { value: 'other', label: 'Другой' }
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setForm({ ...form, gender: option.value as any })}
                  className={`py-3 px-2 rounded-xl text-sm font-medium transition-colors ${
                    form.gender === option.value
                      ? 'bg-soft-600 text-white'
                      : 'bg-soft-50 text-soft-700 hover:bg-soft-100'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* Age */}
          <div>
            <label className="block text-sm font-medium text-soft-700 mb-2">
              Возраст <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="13"
              max="100"
              value={form.age}
              onChange={(e) => setForm({ ...form, age: e.target.value })}
              placeholder="Сколько тебе лет?"
              className="w-full px-4 py-3 rounded-xl border border-soft-200 bg-white text-soft-900 placeholder:text-soft-400 focus:outline-none focus:ring-2 focus:ring-soft-400"
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={!canSubmit || saving}
            className="w-full py-4 bg-soft-600 text-white rounded-2xl font-medium hover:bg-soft-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {saving ? 'Сохраняем...' : 'Продолжить'}
          </button>
        </div>
      </div>
    </div>
  )
}
