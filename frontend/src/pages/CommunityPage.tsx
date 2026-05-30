import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCommunityFeed, toggleReaction, CommunityPost } from '../api/community'

export function CommunityPage() {
  const navigate = useNavigate()
  const [posts, setPosts] = useState<CommunityPost[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hasMore, setHasMore] = useState(false)
  const [cursor, setCursor] = useState<string | undefined>()
  const [showRules, setShowRules] = useState(() => {
    // Check if user has seen rules
    return !localStorage.getItem('community_rules_seen')
  })

  const loadFeed = async (reset = false) => {
    try {
      setLoading(true)
      const currentCursor = reset ? undefined : cursor
      const response = await getCommunityFeed(currentCursor)
      
      if (reset) {
        setPosts(response.posts)
      } else {
        setPosts(prev => [...prev, ...response.posts])
      }
      
      setHasMore(response.has_more)
      setCursor(response.next_cursor)
    } catch (err) {
      setError('Не удалось загрузить ленту')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadFeed(true)
  }, [])

  const handleReaction = async (postId: number) => {
    try {
      const result = await toggleReaction(postId)
      
      // Update local state
      setPosts(prev => prev.map(post => {
        if (post.id === postId) {
          return {
            ...post,
            has_user_reacted: !result.removed,
            reaction_count: result.removed 
              ? post.reaction_count - 1 
              : post.reaction_count + 1
          }
        }
        return post
      }))
    } catch (err) {
      console.error('Failed to toggle reaction', err)
    }
  }

  const acceptRules = () => {
    localStorage.setItem('community_rules_seen', 'true')
    setShowRules(false)
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="min-h-screen bg-soft-50">
      {/* Rules Modal */}
      {showRules && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-semibold text-soft-800 mb-4">
              Правила Круга поддержки
            </h2>
            <div className="space-y-3 text-soft-600 text-sm">
              <p>
                <strong className="text-soft-800">Что здесь:</strong><br/>
                Место, где можно вынести мысль или вопрос и получить мягкую поддержку.
              </p>
              <p>
                <strong className="text-soft-800">Принципы:</strong>
              </p>
              <ul className="list-disc list-inside space-y-1">
                <li>Публикация только вручную и по желанию</li>
                <li>По умолчанию анонимно</li>
                <li>Нет оценок, лайков, рейтингов</li>
                <li>Только мягкая поддержка и вопросы</li>
                <li>Нет давления и «долженствования»</li>
              </ul>
              <p>
                <strong className="text-soft-800">Не для:</strong><br/>
                Медицинской помощи, кризисных ситуаций, политики, агрессии.
              </p>
            </div>
            <button
              onClick={acceptRules}
              className="w-full mt-6 py-3 bg-soft-600 text-white rounded-xl font-medium hover:bg-soft-700"
            >
              Понятно, продолжить
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white border-b border-soft-200 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/')}
              className="p-2 hover:bg-soft-100 rounded-lg transition-colors"
            >
              ←
            </button>
            <h1 className="text-lg font-semibold text-soft-800">
              Круг поддержки
            </h1>
          </div>
          <button
            onClick={() => navigate('/community/new')}
            className="px-4 py-2 bg-soft-600 text-white rounded-lg text-sm font-medium hover:bg-soft-700"
          >
            + Поделиться
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 py-6">
        {error && (
          <div className="p-4 bg-red-50 text-red-600 rounded-xl mb-4">
            {error}
          </div>
        )}

        {/* Posts */}
        <div className="space-y-4">
          {posts.map(post => (
            <div
              key={post.id}
              onClick={() => navigate(`/community/post/${post.id}`)}
              className="bg-white rounded-2xl p-5 border border-soft-200 cursor-pointer hover:border-soft-300 transition-colors"
            >
              {/* Author & Date */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-soft-600">
                  {post.author.display_name}
                </span>
                <span className="text-xs text-soft-400">
                  {formatDate(post.created_at)}
                </span>
              </div>

              {/* Title */}
              {post.title && (
                <h3 className="font-semibold text-soft-800 mb-2">
                  {post.title}
                </h3>
              )}

              {/* Body */}
              <p className="text-soft-700 text-sm mb-3 line-clamp-4">
                {post.body}
              </p>

              {/* Discussion Prompt */}
              {post.discussion_prompt && (
                <div className="bg-soft-50 rounded-lg p-3 mb-4">
                  <p className="text-soft-600 text-sm italic">
                    💭 {post.discussion_prompt}
                  </p>
                </div>
              )}

              {/* Source Preview */}
              {post.source_preview && (
                <div className="border-l-2 border-soft-300 pl-3 mb-4">
                  <p className="text-soft-500 text-xs line-clamp-2">
                    {post.source_preview}
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-4 pt-3 border-t border-soft-100">
                {/* Reaction */}
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleReaction(post.id)
                  }}
                  className={`flex items-center gap-1.5 text-sm transition-colors ${
                    post.has_user_reacted
                      ? 'text-soft-600'
                      : 'text-soft-400 hover:text-soft-600'
                  }`}
                >
                  <span>🤗</span>
                  <span>{post.reaction_count || 'Поддержать'}</span>
                </button>

                {/* Comments */}
                <div className="flex items-center gap-1.5 text-sm text-soft-400">
                  <span>💬</span>
                  <span>{post.comment_count || 'Комментарии'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Load More */}
        {hasMore && (
          <button
            onClick={() => loadFeed()}
            disabled={loading}
            className="w-full mt-6 py-3 bg-white border border-soft-200 rounded-xl text-soft-600 hover:bg-soft-50 disabled:opacity-50"
          >
            {loading ? 'Загрузка...' : 'Загрузить ещё'}
          </button>
        )}

        {/* Empty State */}
        {!loading && posts.length === 0 && (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">🌱</div>
            <h3 className="font-medium text-soft-800 mb-2">
              Пока нет публикаций
            </h3>
            <p className="text-soft-500 text-sm mb-6">
              Будь первым, кто поделится мыслью или вопросом
            </p>
            <button
              onClick={() => navigate('/community/new')}
              className="px-6 py-3 bg-soft-600 text-white rounded-xl font-medium hover:bg-soft-700"
            >
              Поделиться
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
