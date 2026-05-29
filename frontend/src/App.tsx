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
    const twa = window.Telegram?.WebApp
    const debugInfo = {
      hasTelegram: !!window.Telegram,
      hasWebApp: !!twa,
      initData: twa?.initData ? twa.initData.substring(0, 80) + '...' : '(empty)',
      initDataUnsafe: JSON.stringify(twa?.initDataUnsafe || {}),
      version: (twa as any)?.version,
    }
    return (
      <div className="min-h-screen p-4 text-xs text-soft-600 space-y-2">
        <p className="font-bold text-red-600">Auth failed — debug:</p>
        {Object.entries(debugInfo).map(([k, v]) => (
          <p key={k}><b>{k}:</b> {String(v)}</p>
        ))}
        <button
          onClick={() => { clearAuthToken(); window.location.reload() }}
          className="mt-4 px-4 py-2 bg-soft-600 text-white rounded-xl text-sm"
        >
          Повторить
        </button>
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
