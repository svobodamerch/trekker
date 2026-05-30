import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { getUsersStats, UsersStats } from '../api/users'

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
  const [stats, setStats] = useState<UsersStats | null>(null)

  useEffect(() => {
    getUsersStats().then(setStats).catch(console.error)
  }, [])

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
            Обратная связь сохранена. Если это что-то срочное, напиши напрямую:
          </p>
          <a
            href="https://t.me/alyalin"
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-3 bg-[#0088cc] text-white rounded-xl font-medium"
          >
            Написать @alyalin в Telegram
          </a>
          <button
            onClick={() => navigate('/')}
            className="w-full py-3 text-soft-500 hover:text-soft-700"
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

          {/* User Statistics */}
          {stats && (
            <div className="pt-6 border-t border-soft-200">
              <p className="text-xs text-soft-400 uppercase tracking-wide mb-2">Сообщество</p>
              <div className="flex gap-4">
                <div>
                  <span className="text-lg font-semibold text-soft-700">{stats.total_users}</span>
                  <span className="text-soft-500 text-sm ml-1">пользователей</span>
                </div>
                <div>
                  <span className="text-lg font-semibold text-soft-700">{stats.active_users}</span>
                  <span className="text-soft-500 text-sm ml-1">активных за 7 дней</span>
                </div>
              </div>
            </div>
          )}

          {/* Version History */}
          <div className="pt-6 border-t border-soft-200">
            <p className="text-xs text-soft-400 uppercase tracking-wide mb-3">История версий и обновлений</p>
            <div className="space-y-3 text-sm">
              <div className="bg-soft-50 rounded-xl p-3">
                <p className="font-medium text-soft-700 mb-1">v1.1 — Сейчас</p>
                <ul className="text-soft-600 space-y-1 ml-4 list-disc">
                  <li>Круг поддержки — общая лента с постами и комментариями</li>
                  <li>Возможность поделиться пульсом в ленту</li>
                  <li>Редактирование и удаление своих постов</li>
                  <li>Профиль пользователя с именем, полом и возрастом</li>
                </ul>
              </div>
              <div className="bg-soft-50 rounded-xl p-3">
                <p className="font-medium text-soft-700 mb-1">v1.0 — Май 2025</p>
                <ul className="text-soft-600 space-y-1 ml-4 list-disc">
                  <li>Пульс дня — настроение, тревога, энергия</li>
                  <li>Цели и мечты</li>
                  <li>Жизненный баланс</li>
                  <li>Голосовые заметки</li>
                </ul>
              </div>
              <div className="rounded-xl p-3 border border-dashed border-soft-300">
                <p className="font-medium text-soft-700 mb-1">В планах</p>
                <ul className="text-soft-500 space-y-1 ml-4 list-disc">
                  <li>Аналитика и инсайты по пройденным трекерам</li>
                  <li>Уведомления и напоминания</li>
                  <li>Рефлексии по неделям и месяцам</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
