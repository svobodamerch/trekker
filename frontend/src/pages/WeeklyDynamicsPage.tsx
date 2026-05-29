import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SoftCard } from '../components/SoftCard'
import type { Entry } from '../api/entries'
import { createWeeklyReflection, getLatestWeeklyReflection, type WeeklyReflection } from '../api/weeklyReflection'
import { listEntries } from '../api/entries'

interface DayData {
  date: string
  mood: number | null
  anxiety: number | null
  energy: number | null
}

export function WeeklyDynamicsPage() {
  const navigate = useNavigate()
  const [days, setDays] = useState<DayData[]>([])
  const [loading, setLoading] = useState(true)
  const [reflection, setReflection] = useState<WeeklyReflection | null>(null)
  const [reflectionLoading, setReflectionLoading] = useState(false)
  const [entryCount, setEntryCount] = useState(0)

  useEffect(() => {
    // Fetch entries and group by day
    listEntries(50)
      .then((data) => {
        const entries: Entry[] = data.items
        const last7Days = getLast7Days()

        const dayData = last7Days.map((dateStr) => {
          const dayEntries = entries.filter((e) => {
            const entryDate = new Date(e.created_at).toISOString().split('T')[0]
            return entryDate === dateStr
          })

          if (dayEntries.length === 0) {
            return { date: dateStr, mood: null, anxiety: null, energy: null }
          }

          const avg = (vals: (number | null)[]) => {
            const valid = vals.filter((v) => v !== null) as number[]
            return valid.length > 0
              ? Math.round((valid.reduce((a, b) => a + b, 0) / valid.length) * 10) / 10
              : null
          }

          return {
            date: dateStr,
            mood: avg(dayEntries.map((e) => e.mood)),
            anxiety: avg(dayEntries.map((e) => e.anxiety)),
            energy: avg(dayEntries.map((e) => e.energy)),
          }
        })

        setDays(dayData)
        setEntryCount(entries.length)
        setLoading(false)
      })
      .catch(() => {
        setLoading(false)
      })

    // Load latest reflection
    getLatestWeeklyReflection()
      .then((data) => {
        setReflection(data)
      })
      .catch(() => {})
  }, [])

  const handleCreateReflection = async () => {
    setReflectionLoading(true)
    try {
      const newReflection = await createWeeklyReflection()
      setReflection(newReflection)
    } catch (err) {
      console.error('Failed to create reflection:', err)
    } finally {
      setReflectionLoading(false)
    }
  }

  const getLast7Days = () => {
    const days: string[] = []
    for (let i = 6; i >= 0; i--) {
      const d = new Date()
      d.setDate(d.getDate() - i)
      days.push(d.toISOString().split('T')[0])
    }
    return days
  }

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString('ru-RU', { weekday: 'short', day: 'numeric' })
  }

  const hasData = days.some((d) => d.mood !== null || d.energy !== null)

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-semibold text-soft-800">Недельная динамика</h1>
          <button
            onClick={() => navigate('/')}
            className="text-soft-500 text-sm hover:text-soft-700"
          >
            Назад
          </button>
        </div>

        {loading ? (
          <p className="text-center text-soft-400 py-8">Загрузка...</p>
        ) : !hasData ? (
          <SoftCard className="p-6 text-center">
            <p className="text-soft-500 mb-2">Пока рано для выводов</p>
            <p className="text-soft-400 text-sm">
              Динамика появится после 2-3 записей. Не спеши.
            </p>
          </SoftCard>
        ) : (
          <div className="space-y-3">
            {days.map((day) => (
              <SoftCard key={day.date} className="p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-soft-700">
                    {formatDate(day.date)}
                  </span>
                  <div className="flex gap-3 text-sm">
                    {day.mood !== null && (
                      <span className="text-green-600">Н: {day.mood}</span>
                    )}
                    {day.anxiety !== null && (
                      <span className="text-orange-600">Т: {day.anxiety}</span>
                    )}
                    {day.energy !== null && (
                      <span className="text-blue-600">Э: {day.energy}</span>
                    )}
                    {day.mood === null && day.anxiety === null && day.energy === null && (
                      <span className="text-soft-300">—</span>
                    )}
                  </div>
                </div>
              </SoftCard>
            ))}
          </div>
        )}

        {/* Weekly Reflection Card */}
        <SoftCard className="p-4 mt-6 bg-soft-50 border-soft-200">
          <h2 className="text-sm font-semibold text-soft-700 mb-2">
            Недельное отражение
          </h2>
          
          <p className="text-xs text-soft-500 mb-3">
            AI-отражение — это не диагноз и не профессиональный совет. Оно просто помогает заметить возможные повторения в твоих записях: темы, состояние, энергию и связь с целями.
          </p>
          
          {reflection ? (
            <div className="space-y-3">
              <p className="text-xs text-soft-400">
                {new Date(reflection.created_at).toLocaleDateString('ru-RU')} • {reflection.entry_count} записей
                {reflection.is_placeholder && ' • placeholder mode'}
              </p>
              
              <div className="space-y-2">
                <div>
                  <p className="text-xs font-medium text-soft-500">Что повторялось:</p>
                  <p className="text-sm text-soft-700">{reflection.patterns}</p>
                </div>
                
                <div>
                  <p className="text-xs font-medium text-soft-500">Энергия:</p>
                  <p className="text-sm text-soft-700">{reflection.energy_insights}</p>
                </div>
                
                <div>
                  <p className="text-xs font-medium text-soft-500">Связь с целями:</p>
                  <p className="text-sm text-soft-700">{reflection.goal_connections}</p>
                </div>
                
                <div className="pt-2 border-t border-soft-200">
                  <p className="text-xs font-medium text-soft-500">Вопрос на следующую неделю:</p>
                  <p className="text-sm text-soft-600 italic">{reflection.next_week_question}</p>
                </div>
                
                <div>
                  <p className="text-xs font-medium text-soft-500">Фокус на 7 дней:</p>
                  <p className="text-sm text-soft-600">{reflection.next_week_focus}</p>
                </div>
              </div>
              
              <button
                onClick={handleCreateReflection}
                disabled={reflectionLoading || entryCount < 3}
                className="w-full py-2 bg-soft-600 text-white rounded-lg text-sm font-medium hover:bg-soft-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {reflectionLoading ? 'Создаю...' : 'Обновить отражение'}
              </button>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-soft-500 text-sm mb-3">
                {entryCount < 3 
                  ? `Для отражения нужно минимум 3 записи за неделю. Сейчас: ${entryCount}.`
                  : 'Сделай недельное отражение, чтобы увидеть мягкие гипотезы о своём состоянии.'}
              </p>
              <button
                onClick={handleCreateReflection}
                disabled={reflectionLoading || entryCount < 3}
                className="px-4 py-2 bg-soft-600 text-white rounded-lg text-sm font-medium hover:bg-soft-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {reflectionLoading ? 'Создаю...' : 'Сделать недельное отражение'}
              </button>
            </div>
          )}
        </SoftCard>

        <p className="text-center text-soft-400 text-xs mt-6">
          Н — настроение, Т — тревога, Э — энергия
        </p>
      </div>
    </div>
  )
}
