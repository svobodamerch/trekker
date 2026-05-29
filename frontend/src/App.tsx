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

    // Give Telegram ~100ms to populate initData after ready()
    setTimeout(run, 100)
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
        <div className="max-w-sm text-center space-y-3">
          <p className="text-soft-700 font-medium">Откройте приложение из Telegram</p>
          <p className="text-soft-400 text-sm">
            Это приложение работает только внутри Telegram Mini App.
            Открой его через бота, чтобы данные сохранились в твоём личном кабинете.
          </p>
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
      </Routes>
    </BrowserRouter>
  )
}

export default App
