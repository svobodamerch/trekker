import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SoftCard } from '../components/SoftCard'
import {
  LIFE_AREAS,
  createSnapshot,
  getLatestSnapshot,
  getComparison,
  type SnapshotOut,
  type ComparisonResult,
} from '../api/lifeBalance'

type Screen = 'loading' | 'onboarding' | 'form' | 'result' | 'view'

export function LifeBalancePage() {
  const navigate = useNavigate()
  const [screen, setScreen] = useState<Screen>('loading')
  const [scores, setScores] = useState<Record<string, number>>(() =>
    Object.fromEntries(LIFE_AREAS.map((a) => [a.key, 5]))
  )
  const [latest, setLatest] = useState<SnapshotOut | null>(null)
  const [comparison, setComparison] = useState<ComparisonResult | null>(null)
  const [saving, setSaving] = useState(false)
  const [daysSince, setDaysSince] = useState<number | null>(null)

  useEffect(() => {
    getLatestSnapshot()
      .then((snap) => {
        if (!snap) {
          setScreen('onboarding')
          return
        }
        setLatest(snap)
        const days = Math.floor(
          (Date.now() - new Date(snap.created_at).getTime()) / 86400000
        )
        setDaysSince(days)
        getComparison().then(setComparison).catch(() => {})
        setScreen('view')
      })
      .catch(() => setScreen('onboarding'))
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      const snap = await createSnapshot({
        scores: LIFE_AREAS.map((a) => ({ area_key: a.key, score: scores[a.key] })),
      })
      setLatest(snap)
      getComparison().then(setComparison).catch(() => {})
      setScreen('result')
    } catch {
      // ignore
    } finally {
      setSaving(false)
    }
  }

  const lowestArea = latest?.scores.reduce((min, s) =>
    s.score < min.score ? s : min,
    latest.scores[0]
  )

  if (screen === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-soft-400 text-sm">Загрузка...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-semibold text-soft-800">Колесо баланса</h1>
          <button
            onClick={() => navigate('/goals')}
            className="px-4 py-2 bg-white border border-soft-300 text-soft-700 text-sm font-medium rounded-xl hover:bg-soft-50 hover:border-soft-400 shadow-sm"
          >
            ← Назад
          </button>
        </div>

        {/* ONBOARDING */}
        {screen === 'onboarding' && (
          <div className="space-y-4">
            <SoftCard className="p-6">
              <p className="text-soft-700 text-sm leading-relaxed mb-3">
                Перед целями можно сделать короткий срез текущей жизни.
              </p>
              <p className="text-soft-500 text-sm leading-relaxed mb-3">
                Оцени каждую сферу от 1 до 10 — не «как должно быть», а как ощущается сейчас.
              </p>
              <p className="text-soft-400 text-sm italic">
                Это не тест и не оценка. Это точка отсчёта.
              </p>
            </SoftCard>
            <button
              onClick={() => setScreen('form')}
              className="w-full py-3 bg-soft-700 text-white rounded-xl text-sm font-medium hover:bg-soft-800"
            >
              Сделать срез
            </button>
          </div>
        )}

        {/* FORM */}
        {screen === 'form' && (
          <div className="space-y-3">
            {LIFE_AREAS.map((area) => (
              <SoftCard key={area.key} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-soft-700">{area.label}</span>
                  <span className="text-lg font-bold text-soft-800 w-6 text-right">
                    {scores[area.key]}
                  </span>
                </div>
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={scores[area.key]}
                  onChange={(e) =>
                    setScores((prev) => ({ ...prev, [area.key]: Number(e.target.value) }))
                  }
                  className="w-full accent-soft-600"
                />
                <div className="flex justify-between text-xs text-soft-300 mt-1">
                  <span>1</span>
                  <span>10</span>
                </div>
              </SoftCard>
            ))}
            <button
              onClick={handleSave}
              disabled={saving}
              className="w-full py-3 bg-soft-700 text-white rounded-xl text-sm font-medium hover:bg-soft-800 disabled:opacity-50 mt-2"
            >
              {saving ? 'Сохраняю...' : 'Сохранить срез'}
            </button>
          </div>
        )}

        {/* RESULT after first save */}
        {screen === 'result' && latest && (
          <div className="space-y-4">
            <SoftCard className="p-6 text-center">
              <p className="text-soft-700 font-medium mb-2">Готово. Это твоя текущая точка.</p>
              <p className="text-soft-500 text-sm">
                Теперь можно выбрать одну сферу, которую хочется мягко поддержать в ближайший месяц.
              </p>
            </SoftCard>

            {lowestArea && (
              <SoftCard className="p-4 bg-soft-50 border-soft-200">
                <p className="text-xs text-soft-500 mb-1">Сфера с наименьшей оценкой</p>
                <p className="text-sm font-medium text-soft-700 mb-1">{lowestArea.area_label}</p>
                <p className="text-xs text-soft-400">Оценка: {lowestArea.score}/10</p>
                <p className="text-xs text-soft-500 mt-2 italic">
                  Что могло бы поднять эту сферу хотя бы на 1 балл за месяц?
                </p>
              </SoftCard>
            )}

            <div className="space-y-2">
              <button
                onClick={() => navigate('/goals')}
                className="w-full py-3 bg-soft-700 text-white rounded-xl text-sm font-medium hover:bg-soft-800"
              >
                Перейти к целям
              </button>
              <button
                onClick={() => setScreen('view')}
                className="w-full py-3 bg-white border border-soft-200 rounded-xl text-soft-600 text-sm hover:border-soft-400"
              >
                Посмотреть срез
              </button>
            </div>
          </div>
        )}

        {/* VIEW existing snapshot */}
        {screen === 'view' && latest && (
          <div className="space-y-3">
            {/* Comparison */}
            {comparison?.has_comparison && comparison.changes && (
              <SoftCard className="p-4 bg-soft-50 border-soft-200">
                <p className="text-xs font-medium text-soft-600 mb-3">Что изменилось с прошлого среза</p>
                <div className="space-y-1">
                  {comparison.changes
                    .filter((c) => c.delta !== 0)
                    .map((c) => (
                      <div key={c.area_key} className="flex items-center justify-between text-sm">
                        <span className="text-soft-600">{c.area_label}</span>
                        <span className={c.delta > 0 ? 'text-green-600' : 'text-orange-500'}>
                          {c.previous} → {c.current}
                        </span>
                      </div>
                    ))}
                  {comparison.changes.every((c) => c.delta === 0) && (
                    <p className="text-xs text-soft-400">Оценки не изменились</p>
                  )}
                </div>
              </SoftCard>
            )}

            {/* Scores */}
            {latest.scores.map((s) => (
              <SoftCard key={s.area_key} className="p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-soft-700">{s.area_label}</span>
                  <div className="flex items-center gap-2">
                    <div className="flex gap-0.5">
                      {Array.from({ length: 10 }).map((_, i) => (
                        <div
                          key={i}
                          className={`w-2 h-4 rounded-sm ${
                            i < s.score ? 'bg-soft-500' : 'bg-soft-100'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-sm font-bold text-soft-800 w-5 text-right">{s.score}</span>
                  </div>
                </div>
              </SoftCard>
            ))}

            <p className="text-xs text-soft-400 text-center pt-1">
              Срез от {new Date(latest.created_at).toLocaleDateString('ru-RU')}
            </p>

            {/* Prompt to update if 14+ days */}
            {daysSince !== null && daysSince >= 14 && (
              <SoftCard className="p-4 bg-soft-50 border-soft-200 text-center">
                <p className="text-sm text-soft-600 mb-3">
                  Можно сделать новый срез и посмотреть, что изменилось.
                </p>
                <button
                  onClick={() => setScreen('form')}
                  className="px-4 py-2 bg-soft-700 text-white rounded-xl text-sm font-medium hover:bg-soft-800"
                >
                  Обновить срез
                </button>
              </SoftCard>
            )}

            {daysSince !== null && daysSince < 14 && (
              <button
                onClick={() => setScreen('form')}
                className="w-full py-3 bg-white border border-soft-200 rounded-xl text-soft-500 text-sm hover:border-soft-400"
              >
                Сделать новый срез
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
