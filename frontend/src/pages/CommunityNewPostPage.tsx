import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { createPost, shareFromSource, getSharePreview, SharePreview } from '../api/community'

const VISIBILITY_OPTIONS = [
  { value: 'anonymous', label: 'Анонимно', desc: 'Пользователь' },
  { value: 'named', label: 'С именем', desc: 'Твоё имя будет видно' }
]

export function CommunityNewPostPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  
  // Source params (if sharing from Pulse/Goal/LifeBalance)
  const sourceType = searchParams.get('source_type')
  const sourceId = searchParams.get('source_id')
  const isShareMode = sourceType && sourceId
  
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState<SharePreview | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Form state
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [discussionPrompt, setDiscussionPrompt] = useState('')
  const [visibility, setVisibility] = useState('anonymous')

  // Load preview if sharing from source
  useEffect(() => {
    if (isShareMode) {
      getSharePreview(sourceType, Number(sourceId))
        .then(data => {
          setPreview(data)
          if (data.can_share) {
            setTitle(data.title || '')
            setBody(data.body_preview)
          }
        })
        .catch(() => setError('Не удалось загрузить превью'))
    }
  }, [sourceType, sourceId])

  const handleSubmit = async () => {
    if (!body.trim()) return
    
    try {
      setLoading(true)
      
      if (isShareMode && preview?.can_share) {
        // Share from source
        await shareFromSource({
          source_type: sourceType,
          source_id: Number(sourceId),
          title: title || undefined,
          discussion_prompt: discussionPrompt || undefined,
          visibility: visibility as 'anonymous' | 'named'
        })
      } else {
        // Manual post
        await createPost({
          source_type: 'custom',
          title: title || undefined,
          body,
          discussion_prompt: discussionPrompt || undefined,
          visibility: visibility as 'anonymous' | 'named'
        })
      }
      
      navigate('/community')
    } catch (err) {
      setError('Не удалось опубликовать')
      setLoading(false)
    }
  }

  if (isShareMode && preview && !preview.can_share) {
    return (
      <div className="min-h-screen bg-soft-50 flex items-center justify-center p-4">
        <div className="text-center max-w-sm">
          <div className="text-4xl mb-4">🔒</div>
          <h2 className="font-semibold text-soft-800 mb-2">Нельзя поделиться</h2>
          <p className="text-soft-500 text-sm mb-4">{preview.error_message}</p>
          <button
            onClick={() => navigate('/community')}
            className="px-4 py-2 bg-soft-600 text-white rounded-lg"
          >
            Вернуться к ленте
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-soft-50">
      {/* Header */}
      <div className="bg-white border-b border-soft-200 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/community')}
              className="p-2 hover:bg-soft-100 rounded-lg"
            >
              ←
            </button>
            <h1 className="text-lg font-semibold text-soft-800">
              {isShareMode ? 'Поделиться в Круге' : 'Новая публикация'}
            </h1>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="max-w-2xl mx-auto px-4 py-6">
        {error && (
          <div className="p-4 bg-red-50 text-red-600 rounded-xl mb-4">
            {error}
          </div>
        )}

        <div className="bg-white rounded-2xl p-5 border border-soft-200 space-y-5">
          {/* Source Preview (if sharing) */}
          {isShareMode && preview && (
            <div className="bg-soft-50 rounded-xl p-4">
              <p className="text-xs text-soft-500 mb-2 uppercase tracking-wide">
                Источник: {preview.source_type}
              </p>
              <p className="text-soft-600 text-sm line-clamp-3">
                {preview.body_preview}
              </p>
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-soft-700 mb-2">
              Заголовок <span className="text-soft-400">(необязательно)</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Кратко о чём твоя мысль"
              className="w-full p-3 border border-soft-200 rounded-xl text-sm"
            />
          </div>

          {/* Body */}
          <div>
            <label className="block text-sm font-medium text-soft-700 mb-2">
              Текст <span className="text-red-500">*</span>
            </label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Опиши свою мысль, вопрос или ситуацию..."
              className="w-full p-3 border border-soft-200 rounded-xl text-sm h-40 resize-none"
            />
          </div>

          {/* Discussion Prompt */}
          <div>
            <label className="block text-sm font-medium text-soft-700 mb-2">
              Вопрос к сообществу <span className="text-soft-400">(необязательно)</span>
            </label>
            <input
              type="text"
              value={discussionPrompt}
              onChange={(e) => setDiscussionPrompt(e.target.value)}
              placeholder="Что бы ты хотел спросить или обсудить?"
              className="w-full p-3 border border-soft-200 rounded-xl text-sm"
            />
          </div>

          {/* Visibility */}
          <div>
            <label className="block text-sm font-medium text-soft-700 mb-3">
              Как тебя показать
            </label>
            <div className="space-y-2">
              {VISIBILITY_OPTIONS.map(opt => (
                <label
                  key={opt.value}
                  className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors ${
                    visibility === opt.value ? 'bg-soft-100' : 'hover:bg-soft-50'
                  }`}
                >
                  <input
                    type="radio"
                    value={opt.value}
                    checked={visibility === opt.value}
                    onChange={(e) => setVisibility(e.target.value)}
                  />
                  <div>
                    <div className="font-medium text-soft-800 text-sm">{opt.label}</div>
                    <div className="text-soft-500 text-xs">{opt.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Hint */}
          <p className="text-soft-400 text-xs">
            💡 Это публикуется в Круг поддержки. Модератор проверит перед публикацией.
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={() => navigate('/community')}
            className="flex-1 py-4 border border-soft-200 rounded-xl text-soft-600 font-medium"
          >
            Отмена
          </button>
          <button
            onClick={handleSubmit}
            disabled={!body.trim() || loading}
            className="flex-1 py-4 bg-soft-600 text-white rounded-xl font-medium disabled:opacity-50"
          >
            {loading ? 'Публикация...' : 'Опубликовать'}
          </button>
        </div>
      </div>
    </div>
  )
}
