import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SoftCard } from '../components/SoftCard'
import { listEntries, type Entry } from '../api/entries'
import { getHomeSummary, type HomeSummary, type ReturnState } from '../api/home'
import { getAuthDebugInfo, type AuthMode } from '../telegram/init'
import { BetaDisclaimer } from '../components/BetaDisclaimer'

function DebugAuth() {
  const [info, setInfo] = useState<{
    mode: AuthMode
    hasInitData: boolean
    hasToken: boolean
    initDataPreview: string | null
  } | null>(null)

  useEffect(() => {
    if (import.meta.env.DEV) {
      setInfo(getAuthDebugInfo())
    }
  }, [])

  if (!import.meta.env.DEV || !info) return null

  return (
    <SoftCard className="p-3 bg-yellow-50 border-yellow-200">
      <p className="text-xs font-medium text-yellow-700 mb-1">Debug (DEV only)</p>
      <div className="text-xs text-yellow-600 space-y-0.5">
        <p>Режим: <span className="font-medium">{info.mode}</span></p>
        <p>initData: {info.hasInitData ? '✓' : '✗'}</p>
        <p>Токен: {info.hasToken ? '✓' : '✗'}</p>
        {info.initDataPreview && (
          <p className="truncate">{info.initDataPreview}</p>
        )}
      </div>
    </SoftCard>
  )
}

const RETURN_STATE_COPY: Record<ReturnState, { title: string; subtitle: string; cta: string }> = {
  new_user: {
    title: 'Рад тебя видеть',
    subtitle: 'Можно начать с короткого Пульса. Это займет около минуты.',
    cta: 'Начать с Пульса',
  },
  active_today: {
    title: 'Сегодняшний Пульс уже сохранен',
    subtitle: 'Можно просто посмотреть динамику или цели.',
    cta: 'Ещё один Пульс',
  },
  one_day_gap: {
    title: 'Рад тебя видеть',
    subtitle: 'Можно продолжить сегодня с короткого Пульса.',
    cta: 'Записать Пульс',
  },
  after_pause: {
    title: 'Рад тебя видеть',
    subtitle: 'Пропуски нормальны. Можно начать с короткого Пульса на 30 секунд.',
    cta: 'Начать за 30 секунд',
  },
  long_pause: {
    title: 'Добро пожаловать',
    subtitle: 'Давай не восстанавливать всё прошлое. Просто отметим, как ты сейчас.',
    cta: 'Отметить как сейчас',
  },
}

export function HomePage() {
  const navigate = useNavigate()
  const [latestEntry, setLatestEntry] = useState<Entry | null>(null)
  const [homeSummary, setHomeSummary] = useState<HomeSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      listEntries(1).then((data) => {
        setLatestEntry(data.items[0] || null)
      }).catch(() => {}),
      getHomeSummary().then((data) => {
        setHomeSummary(data)
      }).catch(() => {}),
    ]).finally(() => {
      setLoading(false)
    })
  }, [])

  const returnState = homeSummary?.return_state || 'new_user'
  const copy = RETURN_STATE_COPY[returnState]
  const showQuickPulse = returnState === 'after_pause' || returnState === 'long_pause'

  return (
    <div className="min-h-screen p-4">
      <BetaDisclaimer />
      <div className="max-w-md mx-auto space-y-4">
        <DebugAuth />

        <div className="text-center py-6">
          <h1 className="text-xl font-semibold text-soft-800">
            {copy.title}
          </h1>
          <p className="text-soft-500 text-sm mt-2 px-4">
            {copy.subtitle}
          </p>
        </div>

        {showQuickPulse && (
          <SoftCard className="p-4 bg-soft-50 border-soft-200">
            <p className="text-soft-600 text-sm mb-3">
              Быстрый Пульс — только основное:
            </p>
            <button
              onClick={() => navigate('/pulse?quick=true')}
              className="w-full py-3 bg-soft-600 text-white rounded-xl font-medium hover:bg-soft-700 transition-colors"
            >
              {copy.cta}
            </button>
          </SoftCard>
        )}

        {!showQuickPulse && (
          <button
            onClick={() => navigate('/pulse')}
            className="w-full py-4 bg-soft-600 text-white rounded-2xl font-medium hover:bg-soft-700 transition-colors"
          >
            {copy.cta}
          </button>
        )}

        {!loading && latestEntry && (
          <SoftCard className="p-4">
            <p className="text-xs text-soft-400 mb-2">
              Последняя запись: {new Date(latestEntry.created_at).toLocaleDateString('ru-RU')}
              {homeSummary && homeSummary.days_since_last_entry !== null && homeSummary.days_since_last_entry > 0 && (
                <span className="text-soft-300 ml-2">
                  ({homeSummary.days_since_last_entry} {homeSummary.days_since_last_entry === 1 ? 'день' : homeSummary.days_since_last_entry < 5 ? 'дня' : 'дней'} назад)
                </span>
              )}
            </p>
            <div className="flex gap-4 text-sm">
              {latestEntry.mood && (
                <span className="text-soft-600">Настроение: {latestEntry.mood}/10</span>
              )}
              {latestEntry.energy && (
                <span className="text-soft-600">Энергия: {latestEntry.energy}/10</span>
              )}
            </div>
            {latestEntry.insight && (
              <p className="text-soft-700 mt-2 text-sm">{latestEntry.insight}</p>
            )}
          </SoftCard>
        )}

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => navigate('/history')}
            className="py-3 bg-white border border-soft-200 rounded-xl text-soft-700 font-medium hover:border-soft-400"
          >
            История
          </button>
          <button
            onClick={() => navigate('/analytics')}
            className="py-3 bg-white border border-soft-200 rounded-xl text-soft-700 font-medium hover:border-soft-400"
          >
            Динамика
          </button>
          <button
            onClick={() => navigate('/goals')}
            className="py-3 bg-white border border-soft-200 rounded-xl text-soft-700 font-medium hover:border-soft-400 col-span-2"
          >
            Цели и ориентиры
          </button>
        </div>
      </div>
    </div>
  )
}
