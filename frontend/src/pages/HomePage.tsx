import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getUsersStats, UsersStats } from '../api/users'
import { SoftCard } from '../components/SoftCard'
import { listEntries, type Entry } from '../api/entries'
import { getHomeSummary, type HomeSummary, type ReturnState } from '../api/home'
import { getAuthDebugInfo, type AuthMode } from '../telegram/init'
import { BetaDisclaimer } from '../components/BetaDisclaimer'
import { getStoredUser } from '../utils/auth'

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
  const [stats, setStats] = useState<UsersStats | null>(null)

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
    
    // Load user stats
    getUsersStats().then(setStats).catch(console.error)
  }, [])

  const returnState = homeSummary?.return_state || 'new_user'
  const copy = RETURN_STATE_COPY[returnState]
  const showQuickPulse = returnState === 'after_pause' || returnState === 'long_pause'

  const storedUser = getStoredUser()
  const userLabel = storedUser?.first_name || (storedUser?.username ? `@${storedUser.username}` : null)

  return (
    <div className="min-h-screen p-4">
      <BetaDisclaimer />
      <div className="max-w-md mx-auto space-y-4">
        {userLabel && (
          <div className="flex justify-end">
            <span className="text-xs text-soft-400 bg-soft-50 px-2 py-1 rounded-lg">
              {userLabel}
            </span>
          </div>
        )}
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
            История Пульса
          </button>
          <button
            onClick={() => navigate('/analytics')}
            className="py-3 bg-white border border-soft-200 rounded-xl text-soft-700 font-medium hover:border-soft-400"
          >
            Моя динамика
          </button>
          <button
            onClick={() => navigate('/goals')}
            className="py-3 bg-white border border-soft-200 rounded-xl text-soft-700 font-medium hover:border-soft-400 col-span-2"
          >
            Цели и жизнь мечты
          </button>
          <button
            onClick={() => navigate('/community')}
            className="py-3 bg-white border border-soft-200 rounded-xl text-soft-700 font-medium hover:border-soft-400 col-span-2"
          >
            🤗 Круг поддержки
          </button>
        </div>

        <div className="bg-soft-50 rounded-xl p-4 text-sm text-soft-500 space-y-1">
          <p className="font-medium text-soft-600 mb-2">Как пользоваться</p>
          <p>1. Записывай Пульс дня — настроение, энергию и тревогу.</p>
          <p>2. Смотри динамику, когда накопится несколько записей.</p>
          <p>3. Связывай день с целями и ориентирами.</p>
        </div>

        <button
          onClick={() => navigate('/feedback')}
          className="w-full py-3 bg-white border border-soft-200 rounded-xl text-soft-600 text-sm font-medium hover:border-soft-400 transition-colors"
        >
          💬 Оставить обратную связь
        </button>

        {/* User Statistics */}
        {stats && (
          <div className="pt-4 border-t border-soft-200">
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
        <div className="pt-4 border-t border-soft-200">
          <p className="text-xs text-soft-400 uppercase tracking-wide mb-3">История версий и обновлений</p>
          <div className="space-y-3 text-sm">
            <div className="bg-soft-50 rounded-xl p-3">
              <p className="font-medium text-soft-700 mb-1">v1.1 — Сейчас</p>
              <ul className="text-soft-600 space-y-1 ml-4 list-disc">
                <li>Круг поддержки — общая лента с постами и комментариями</li>
                <li>Возможность поделиться пульсом в ленту</li>
                <li>Редактирование и удаление своих постов</li>
                <li>Профиль пользователя с именем, полом и датой рождения</li>
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
  )
}
