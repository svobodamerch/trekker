import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { HomePage } from './pages/HomePage'
import { NewPulsePage } from './pages/NewPulsePage'
import { HistoryPage } from './pages/HistoryPage'
import { WeeklyDynamicsPage } from './pages/WeeklyDynamicsPage'
import { GoalsPage } from './pages/GoalsPage'
import { GoalEditorPage } from './pages/GoalEditorPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/pulse" element={<NewPulsePage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/analytics" element={<WeeklyDynamicsPage />} />
        <Route path="/goals" element={<GoalsPage />} />
        <Route path="/goals/new" element={<GoalEditorPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
