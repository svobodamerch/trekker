import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { HomePage } from './pages/HomePage'
import { NewPulsePage } from './pages/NewPulsePage'
import { HistoryPage } from './pages/HistoryPage'
import { WeeklyDynamicsPage } from './pages/WeeklyDynamicsPage'
import { GoalsPage } from './pages/GoalsPage'
import { GoalEditorPage } from './pages/GoalEditorPage'
import { NewDiaryPage } from './pages/NewDiaryPage'
import { FeedbackPage } from './pages/FeedbackPage'
import { LifeBalancePage } from './pages/LifeBalancePage'
import { authenticateWithTelegram } from './telegram/init'
import { isAuthenticated, clearAuthToken } from './utils/auth'

function App() {
  const [authReady, setAuthReady] = useState(false)
  const [authFailed, setAuthFailed] = useState(false)

  useEffect(() => {
    const twa = window.Telegram?.WebApp
    if (twa) {
      twa.ready()
      twa.expand()
    }

    // Small delay to let Telegram inject initData after ready()
    const run = () => {
      const initData = window.Telegram?.WebApp?.initData
      if (initData) {
        // Always re-auth in Telegram to ensure correct user isolation
        clearAuthToken()
        authenticateWithTelegram().then((ok) => {
          if (!ok) setAuthFailed(true)
          setAuthReady(true)
        })
      } else if (isAuthenticated()) {
        setAuthReady(true)
      } else if (import.meta.env.DEV) {
        authenticateWithTelegram().finally(() => setAuthReady(true))
      } else {
        setAuthFailed(true)
        setAuthReady(true)
      }
    }

    // Give Telegram time to populate initData after ready()
    // Retry once if initData is still empty after first attempt
    setTimeout(() => {
      if (window.Telegram?.WebApp?.initData) {
        run()
      } else {
        setTimeout(run, 300)
      }
    }, 100)
  }, [])

  if (!authReady) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-soft-400 text-sm">Загрузка...</p>
      </div>
    )
  }

  if (authFailed) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="max-w-sm text-center space-y-4">
          <p className="text-soft-700 font-medium">Не удалось войти</p>
          <p className="text-soft-400 text-sm">
            Попробуй закрыть и снова открыть приложение через бота.
          </p>
          <button
            onClick={() => { clearAuthToken(); window.location.reload() }}
            className="px-6 py-2 bg-soft-700 text-white rounded-xl text-sm font-medium"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/pulse" element={<NewPulsePage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/analytics" element={<WeeklyDynamicsPage />} />
        <Route path="/goals" element={<GoalsPage />} />
        <Route path="/goals/new" element={<GoalEditorPage />} />
        <Route path="/diary" element={<NewDiaryPage />} />
        <Route path="/feedback" element={<FeedbackPage />} />
        <Route path="/life-balance" element={<LifeBalancePage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
