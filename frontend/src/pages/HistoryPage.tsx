import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SoftCard } from '../components/SoftCard'
import { listEntries, type Entry } from '../api/entries'

export function HistoryPage() {
  const navigate = useNavigate()
  const [entries, setEntries] = useState<Entry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listEntries(50).then((data) => {
      setEntries(data.items)
      setLoading(false)
    }).catch(() => {
      setLoading(false)
    })
  }, [])

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-semibold text-soft-800">История</h1>
          <button
            onClick={() => navigate('/')}
            className="text-soft-500 text-sm hover:text-soft-700"
          >
            Назад
          </button>
        </div>

        {loading ? (
          <p className="text-center text-soft-400 py-8">Загрузка...</p>
        ) : entries.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-soft-500 mb-2">Здесь будет твоя история</p>
            <p className="text-soft-400 text-sm mb-6">Начни с одной короткой записи — этого достаточно</p>
            <button
              onClick={() => navigate('/pulse')}
              className="px-6 py-3 bg-soft-600 text-white rounded-xl font-medium"
            >
              Записать Пульс
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {entries.map((entry) => (
              <SoftCard key={entry.id} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-soft-400">
                    {new Date(entry.created_at).toLocaleDateString('ru-RU', {
                      day: 'numeric',
                      month: 'long',
                    })}
                  </span>
                  <span className="text-xs text-soft-400 uppercase">
                    {entry.entry_type}
                  </span>
                </div>

                <div className="flex gap-4 text-sm mb-2">
                  {entry.mood && (
                    <span className="text-soft-600">Н: {entry.mood}</span>
                  )}
                  {entry.anxiety && (
                    <span className="text-soft-600">Т: {entry.anxiety}</span>
                  )}
                  {entry.energy && (
                    <span className="text-soft-600">Э: {entry.energy}</span>
                  )}
                </div>

                {entry.insight && (
                  <p className="text-soft-700 text-sm">{entry.insight}</p>
                )}
              </SoftCard>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
