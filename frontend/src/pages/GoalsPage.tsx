import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SoftCard } from '../components/SoftCard'
import { listGoals, type GoalsByHorizon, type Goal } from '../api/goals'
import { getGoalsNeedingReview, reviewGoal, type GoalsNeedingReview } from '../api/goalReview'
import { saveTodayGoals, getGoalsHistory, type DailyGoalsHistory } from '../api/dailyGoals'

const HORIZON_LABELS: Record<string, string> = {
  month: '1 месяц',
  year: '1 год',
  three_years: '3 года',
  five_years: '5 лет',
  dream_life: 'Жизнь мечты',
}

const AREA_LABELS: Record<string, string> = {
  health: 'Здоровье',
  relationships: 'Отношения',
  money: 'Деньги',
  business: 'Бизнес',
  work: 'Работа',
  home: 'Дом',
  freedom: 'Свобода',
  spirituality: 'Духовность',
  body: 'Тело',
  learning: 'Обучение',
  contribution: 'Вклад',
  other: 'Другое',
}

export function GoalsPage() {
  const navigate = useNavigate()
  const [goals, setGoals] = useState<GoalsByHorizon | null>(null)
  const [loading, setLoading] = useState(true)
  const [needsReview, setNeedsReview] = useState<GoalsNeedingReview | null>(null)
  const [reviewingGoal, setReviewingGoal] = useState<Goal | null>(null)
  const [reviewForm, setReviewForm] = useState({
    is_alive: true,
    became_clearer: '',
    wants_to_change: '',
    next_week_step: '',
  })
  const [savingReview, setSavingReview] = useState(false)
  
  // Daily 10 Goals (Brian Tracy)
  const [dailyGoals, setDailyGoals] = useState<DailyGoalsHistory | null>(null)
  const [dailyGoalsInput, setDailyGoalsInput] = useState<string[]>(Array(10).fill(''))
  const [savingDaily, setSavingDaily] = useState(false)
  const [showAboutPractice, setShowAboutPractice] = useState(false)
  const [showDailyArchive, setShowDailyArchive] = useState(false)

  useEffect(() => {
    Promise.all([
      listGoals().then((data) => setGoals(data)),
      getGoalsNeedingReview().then((data) => setNeedsReview(data)),
      getGoalsHistory().then((data) => {
        setDailyGoals(data)
        if (data.today && data.today.goals && data.today.goals.length > 0) {
          const goals = [...data.today.goals]
          while (goals.length < 10) goals.push('')
          setDailyGoalsInput(goals.slice(0, 10))
        }
      }),
    ])
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const hasAnyGoals = goals && Object.values(goals).some((g) => g.length > 0)

  const handleStartReview = (goal: Goal) => {
    setReviewingGoal(goal)
    setReviewForm({
      is_alive: true,
      became_clearer: '',
      wants_to_change: '',
      next_week_step: '',
    })
  }

  const handleSaveReview = async () => {
    if (!reviewingGoal) return
    
    setSavingReview(true)
    try {
      await reviewGoal(reviewingGoal.id, reviewForm)
      // Refresh data
      const [goalsData, needsReviewData] = await Promise.all([
        listGoals(),
        getGoalsNeedingReview(),
      ])
      setGoals(goalsData)
      setNeedsReview(needsReviewData)
      setReviewingGoal(null)
    } catch (err) {
      console.error('Failed to save review:', err)
    } finally {
      setSavingReview(false)
    }
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-semibold text-soft-800">Цели</h1>
          <button
            onClick={() => navigate('/')}
            className="text-soft-500 text-sm hover:text-soft-700"
          >
            Назад
          </button>
        </div>

        {/* Life Balance block */}
        <SoftCard
          className="p-4 mb-6 cursor-pointer hover:border-soft-300 transition-colors"
          onClick={() => navigate('/life-balance')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-soft-700">Колесо баланса жизни</p>
              <p className="text-xs text-soft-400 mt-0.5">Текущий срез по 8 сферам жизни</p>
            </div>
            <span className="text-soft-400 text-lg">→</span>
          </div>
        </SoftCard>

        {/* Review Prompt */}
        {!loading && needsReview && needsReview.count > 0 && !reviewingGoal && (
          <SoftCard className="p-4 mb-6 bg-soft-50 border-soft-200">
            <p className="text-soft-600 text-sm mb-3">{needsReview.message}</p>
            <div className="flex gap-2 flex-wrap">
              {needsReview.goals.slice(0, 2).map((goal) => (
                <button
                  key={goal.id}
                  onClick={() => handleStartReview(goal)}
                  className="px-3 py-1.5 bg-soft-600 text-white rounded-lg text-sm hover:bg-soft-700"
                >
                  {goal.title.length > 20 ? goal.title.slice(0, 20) + '...' : goal.title}
                </button>
              ))}
              {needsReview.count > 2 && (
                <span className="text-soft-400 text-sm self-center">
                  и ещё {needsReview.count - 2}
                </span>
              )}
            </div>
          </SoftCard>
        )}

        {/* Review Modal */}
        {reviewingGoal && (
          <SoftCard className="p-4 mb-6 bg-white">
            <h2 className="text-lg font-semibold text-soft-800 mb-1">
              Пересмотр цели
            </h2>
            <p className="text-soft-500 text-sm mb-4">
              Цели можно менять — это не провал, а уточнение направления.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-soft-700">
                  Эта цель всё ещё живая?
                </label>
                <div className="flex gap-4 mt-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      checked={reviewForm.is_alive === true}
                      onChange={() => setReviewForm({ ...reviewForm, is_alive: true })}
                      className="text-soft-600"
                    />
                    <span className="text-sm text-soft-700">Да</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      checked={reviewForm.is_alive === false}
                      onChange={() => setReviewForm({ ...reviewForm, is_alive: false })}
                      className="text-soft-600"
                    />
                    <span className="text-sm text-soft-700">Не уверен</span>
                  </label>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-soft-700">
                  Что стало яснее?
                </label>
                <textarea
                  value={reviewForm.became_clearer}
                  onChange={(e) => setReviewForm({ ...reviewForm, became_clearer: e.target.value })}
                  placeholder="Можно пропустить, если нечего добавить"
                  className="w-full mt-1 p-2 border border-soft-200 rounded-lg text-sm focus:border-soft-400 focus:outline-none"
                  rows={2}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-soft-700">
                  Что хочется изменить?
                </label>
                <textarea
                  value={reviewForm.wants_to_change}
                  onChange={(e) => setReviewForm({ ...reviewForm, wants_to_change: e.target.value })}
                  placeholder="Или оставить как есть"
                  className="w-full mt-1 p-2 border border-soft-200 rounded-lg text-sm focus:border-soft-400 focus:outline-none"
                  rows={2}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-soft-700">
                  Какой маленький шаг на эту неделю?
                </label>
                <input
                  type="text"
                  value={reviewForm.next_week_step}
                  onChange={(e) => setReviewForm({ ...reviewForm, next_week_step: e.target.value })}
                  placeholder="Один маленький шаг"
                  className="w-full mt-1 p-2 border border-soft-200 rounded-lg text-sm focus:border-soft-400 focus:outline-none"
                />
              </div>
              
              <div className="flex gap-3 pt-2">
                <button
                  onClick={handleSaveReview}
                  disabled={savingReview}
                  className="flex-1 py-2 bg-soft-600 text-white rounded-lg text-sm font-medium hover:bg-soft-700 disabled:opacity-50"
                >
                  {savingReview ? 'Сохраняю...' : 'Сохранить'}
                </button>
                <button
                  onClick={() => setReviewingGoal(null)}
                  disabled={savingReview}
                  className="px-4 py-2 border border-soft-200 text-soft-600 rounded-lg text-sm hover:border-soft-400"
                >
                  Пропустить
                </button>
              </div>
            </div>
          </SoftCard>
        )}

        {loading ? (
          <p className="text-center text-soft-400 py-8">Загрузка...</p>
        ) : !hasAnyGoals ? (
          <div className="text-center py-8">
            <p className="text-soft-500 mb-2">Цели появятся, когда ты будешь готов</p>
            <p className="text-soft-400 text-sm mb-6">
              Необязательно всё планировать сразу. Можно начать с одного маленького направления.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(HORIZON_LABELS).map(([key, label]) => {
              const horizonGoals = goals?.[key as keyof GoalsByHorizon] || []
              if (horizonGoals.length === 0) return null

              return (
                <div key={key}>
                  <h2 className="text-sm font-medium text-soft-400 uppercase mb-3">
                    {label}
                  </h2>
                  <div className="space-y-2">
                    {horizonGoals.map((goal) => (
                      <SoftCard
                        key={goal.id}
                        className="p-4 cursor-pointer hover:border-soft-300"
                        onClick={() => navigate(`/goals/${goal.id}`)}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <span className="text-xs text-soft-400">
                              {AREA_LABELS[goal.life_area] || goal.life_area}
                            </span>
                            <h3 className="font-medium text-soft-800 mt-1">
                              {goal.title}
                            </h3>
                            {goal.desired_state && (
                              <p className="text-soft-600 text-sm mt-1">
                                {goal.desired_state}
                              </p>
                            )}
                          </div>
                          {key === 'dream_life' && goal.custom_horizon_label && (
                            <span className="text-xs text-soft-400 whitespace-nowrap">
                              {goal.custom_horizon_label}
                            </span>
                          )}
                        </div>
                      </SoftCard>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Daily 10 Goals (Brian Tracy Technique) */}
        <SoftCard className="p-4 bg-soft-50 border-soft-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl">📝</span>
              <h3 className="font-semibold text-soft-800">10 целей ежедневно</h3>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowAboutPractice(true)}
                className="text-xs bg-soft-100 text-soft-600 px-2 py-1 rounded-lg hover:bg-soft-200"
              >
                О практике
              </button>
              {dailyGoals?.archive && dailyGoals.archive.length > 0 && (
                <button
                  onClick={() => setShowDailyArchive(true)}
                  className="text-xs bg-white text-soft-600 px-2 py-1 rounded-lg border border-soft-200 hover:bg-soft-50"
                >
                  Архив ({dailyGoals.archive.length})
                </button>
              )}
            </div>
          </div>
          
          {dailyGoals && dailyGoals.streak_days > 0 && (
            <p className="text-xs text-soft-500 mb-3">
              🔥 Серия: {dailyGoals.streak_days} {dailyGoals.streak_days === 1 ? 'день' : dailyGoals.streak_days < 5 ? 'дня' : 'дней'} подряд
            </p>
          )}
          
          <p className="text-xs text-soft-500 mb-3">
            Запиши 10 целей по памяти. Цели могут повторяться с прошлым днём — просто важно каждый раз фиксировать 10 штук. Формулируй в настоящем времени: «Я...»
          </p>
          
          <div className="space-y-2">
            {dailyGoalsInput.map((goal, index) => (
              <div key={index} className="flex gap-2">
                <span className="text-xs text-soft-400 w-5 pt-2">{index + 1}.</span>
                <input
                  type="text"
                  value={goal}
                  onChange={(e) => {
                    const newGoals = [...dailyGoalsInput]
                    newGoals[index] = e.target.value
                    setDailyGoalsInput(newGoals)
                  }}
                  placeholder={`Цель ${index + 1}...`}
                  className="flex-1 px-3 py-2 text-sm bg-white border border-soft-200 rounded-lg focus:border-soft-400 focus:outline-none"
                />
              </div>
            ))}
          </div>
          
          <button
            onClick={async () => {
              setSavingDaily(true)
              try {
                const result = await saveTodayGoals(dailyGoalsInput.filter(g => g.trim()))
                setDailyGoals(prev => prev ? { ...prev, today: result } : null)
              } catch (e) {
                console.error('Failed to save daily goals:', e)
              } finally {
                setSavingDaily(false)
              }
            }}
            disabled={savingDaily}
            className="w-full mt-4 py-3 bg-soft-600 text-white rounded-xl font-medium hover:bg-soft-700 disabled:opacity-50"
          >
            {savingDaily ? 'Сохраняю...' : '💾 Сохранить 10 целей'}
          </button>
        </SoftCard>

        <div className="fixed bottom-6 left-4 right-4 max-w-md mx-auto">
          <button
            onClick={() => navigate('/goals/new')}
            className="w-full py-4 bg-soft-600 text-white rounded-2xl font-medium hover:bg-soft-700"
          >
            Добавить цель
          </button>
        </div>

        {/* About Practice Modal */}
        {showAboutPractice && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center p-4">
            <div className="bg-white rounded-2xl max-w-md w-full max-h-[80vh] overflow-y-auto">
              <div className="p-4 border-b border-soft-200 flex items-center justify-between">
                <h3 className="font-semibold text-soft-800">Техника 10 целей Брайана Трейси</h3>
                <button
                  onClick={() => setShowAboutPractice(false)}
                  className="text-soft-400 hover:text-soft-600"
                >
                  ✕
                </button>
              </div>
              <div className="p-4 space-y-4 text-sm text-soft-600">
                <p className="font-medium text-soft-800">
                  Готовы ли Вы переучить свой мозг думать целями на протяжении 30 дней?
                </p>
                <p>
                  Хочу поделиться с Вам очень простой, но очень эффективной техникой, которая скорее не про мечтания, а про то, что можно научить себя ставить цели, обдумывать цели, повышать свою эффективность, да и просто, понимать, чего ты хочешь на самом деле.
                </p>
                <div>
                  <p className="font-medium text-soft-800 mb-2">Немного о технике Трейси 10 целей:</p>
                  <p>
                    Метод «10 целей» направлен на то, чтобы наши стремления становились частью подсознательной системы фильтрации.
                  </p>
                </div>
                <div>
                  <p className="font-medium text-soft-800 mb-2">Ключевое правило:</p>
                  <p>
                    Каждый день ты записываешь 10 целей, которые хочешь реализовать. Ключевой – пишешь каждый день заново, не подглядывая в записи предыдущего дня, то есть – по памяти. В идеале записи нужно делать утром.
                  </p>
                </div>
                <div>
                  <p className="font-medium text-soft-800 mb-2">Правило 3-х «П»:</p>
                  <ul className="space-y-1 ml-4">
                    <li>• <strong>Positive (Позитивно):</strong> без частицы «не» — «Я вешу 70 кг» вместо «Я не толстый»</li>
                    <li>• <strong>Present (Настоящее):</strong> так, будто цель уже достигнута — «Я зарабатываю...», «Я пишу...»</li>
                    <li>• <strong>Personal (Личное):</strong> начинай со слова «Я» — прямая команда подсознанию</li>
                  </ul>
                </div>
                <div>
                  <p className="font-medium text-soft-800 mb-2">Пошаговая инструкция:</p>
                  <ol className="space-y-1 ml-4 list-decimal">
                    <li>Выбери время, лучше всего утро</li>
                    <li>Пиши 10 целей каждое утро</li>
                    <li>Главный секрет: не подглядывать вчерашние записи</li>
                    <li>Повторяй 30 дней</li>
                  </ol>
                </div>
                <div>
                  <p className="font-medium text-soft-800 mb-2">Что дает этот метод?</p>
                  <ul className="space-y-1 ml-4">
                    <li>• <strong>Уточнение:</strong> цели становятся более конкретными</li>
                    <li>• <strong>Фокус:</strong> мозг начинает автоматически искать возможности</li>
                    <li>• <strong>Приоритетность:</strong> быстро понимаешь главную цель</li>
                  </ul>
                </div>
                <p className="text-xs text-soft-400 italic pt-2 border-t border-soft-100">
                  Через 10–14 дней ты начинаешь видеть, как меняется фокус. Через месяц многие отмечают, что цели становятся яснее и понятнее.
                </p>
              </div>
              <div className="p-4 border-t border-soft-200">
                <button
                  onClick={() => setShowAboutPractice(false)}
                  className="w-full py-3 bg-soft-600 text-white rounded-xl font-medium"
                >
                  Понятно, начну писать цели
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Archive Modal */}
        {showDailyArchive && dailyGoals?.archive && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center p-4">
            <div className="bg-white rounded-2xl max-w-md w-full max-h-[80vh] overflow-y-auto">
              <div className="p-4 border-b border-soft-200 flex items-center justify-between">
                <h3 className="font-semibold text-soft-800">Архив 10 целей</h3>
                <button
                  onClick={() => setShowDailyArchive(false)}
                  className="text-soft-400 hover:text-soft-600"
                >
                  ✕
                </button>
              </div>
              <div className="p-4 space-y-4">
                {dailyGoals.archive.map((entry) => (
                  <div key={entry.id} className="bg-soft-50 rounded-xl p-3">
                    <p className="text-xs text-soft-400 mb-2">
                      {new Date(entry.goal_date).toLocaleDateString('ru-RU')}
                    </p>
                    <ol className="space-y-1 text-sm text-soft-700">
                      {entry.goals.filter(g => g).map((goal, i) => (
                        <li key={i} className="flex gap-2">
                          <span className="text-soft-400">{i + 1}.</span>
                          <span>{goal}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                ))}
              </div>
              <div className="p-4 border-t border-soft-200">
                <button
                  onClick={() => setShowDailyArchive(false)}
                  className="w-full py-3 bg-soft-600 text-white rounded-xl font-medium"
                >
                  Закрыть
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
