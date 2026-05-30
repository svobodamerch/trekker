import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getPost, createComment, toggleReaction, createReport, updatePost, deletePost, CommunityPostDetail } from '../api/community'

const COMMENT_TYPES = [
  { value: 'support', label: '🤗 Поддержка', desc: 'Мягкая поддержка и принятие' },
  { value: 'question', label: '❓ Вопрос', desc: 'Уточнение или любопытство' },
  { value: 'similar_experience', label: '💭 Похожий опыт', desc: 'Я проходил через похожее' },
  { value: 'gentle_idea', label: '💡 Мягкая идея', desc: 'Не рекомендация, а возможность' }
]

export function CommunityPostPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [post, setPost] = useState<CommunityPostDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Comment form
  const [showCommentForm, setShowCommentForm] = useState(false)
  const [commentBody, setCommentBody] = useState('')
  const [commentType, setCommentType] = useState('support')
  const [submittingComment, setSubmittingComment] = useState(false)
  
  // Report modal
  const [showReport, setShowReport] = useState(false)
  const [reportReason, setReportReason] = useState('')
  const [reportDetails, setReportDetails] = useState('')
  
  // Edit modal
  const [showEdit, setShowEdit] = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [editBody, setEditBody] = useState('')
  const [editPrompt, setEditPrompt] = useState('')
  const [saving, setSaving] = useState(false)
  
  // Delete confirmation
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const loadPost = async () => {
    if (!id) return
    try {
      setLoading(true)
      const data = await getPost(Number(id))
      setPost(data)
    } catch (err) {
      setError('Не удалось загрузить публикацию')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPost()
  }, [id])

  const handleReaction = async () => {
    if (!post) return
    try {
      const result = await toggleReaction(post.id)
      setPost(prev => prev ? {
        ...prev,
        has_user_reacted: !result.removed,
        reaction_count: result.removed
          ? prev.reaction_count - 1
          : prev.reaction_count + 1
      } : null)
    } catch (err) {
      console.error('Failed to toggle reaction', err)
    }
  }

  const handleSubmitComment = async () => {
    if (!post || !commentBody.trim()) return
    try {
      setSubmittingComment(true)
      const newComment = await createComment(post.id, {
        body: commentBody,
        comment_type: commentType as any
      })
      setPost(prev => prev ? {
        ...prev,
        comments: [...prev.comments, newComment],
        comment_count: prev.comment_count + 1
      } : null)
      setCommentBody('')
      setShowCommentForm(false)
    } catch (err) {
      console.error('Failed to add comment', err)
    } finally {
      setSubmittingComment(false)
    }
  }

  const handleReport = async () => {
    if (!post || !reportReason) return
    try {
      await createReport({
        post_id: post.id,
        reason: reportReason,
        details: reportDetails
      })
      setShowReport(false)
      alert('Репорт отправлен. Спасибо.')
    } catch (err) {
      console.error('Failed to report', err)
    }
  }

  const openEditModal = () => {
    if (!post) return
    setEditTitle(post.title || '')
    setEditBody(post.body)
    setEditPrompt(post.discussion_prompt || '')
    setShowEdit(true)
  }

  const handleSaveEdit = async () => {
    if (!post || !editBody.trim()) return
    
    try {
      setSaving(true)
      const updated = await updatePost(post.id, {
        title: editTitle || undefined,
        body: editBody,
        discussion_prompt: editPrompt || undefined
      })
      // Preserve comments from existing post
      setPost({ ...updated, comments: post.comments })
      setShowEdit(false)
    } catch (err) {
      console.error('Failed to update post', err)
      alert('Не удалось сохранить изменения')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!post) return
    
    try {
      await deletePost(post.id)
      navigate('/community')
    } catch (err) {
      console.error('Failed to delete post', err)
      alert('Не удалось удалить публикацию')
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-soft-50 flex items-center justify-center">
        <p className="text-soft-400">Загрузка...</p>
      </div>
    )
  }

  if (error || !post) {
    return (
      <div className="min-h-screen bg-soft-50 flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-soft-600 mb-4">{error || 'Публикация не найдена'}</p>
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
      {/* Report Modal */}
      {showReport && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <h3 className="font-semibold text-soft-800 mb-4">Пожаловаться</h3>
            <select
              value={reportReason}
              onChange={(e) => setReportReason(e.target.value)}
              className="w-full p-3 border border-soft-200 rounded-xl mb-4 text-sm"
            >
              <option value="">Выбери причину</option>
              <option value="spam">Спам или реклама</option>
              <option value="aggression">Агрессия или токсичность</option>
              <option value="offtopic">Оффтопик</option>
              <option value="other">Другое</option>
            </select>
            <textarea
              value={reportDetails}
              onChange={(e) => setReportDetails(e.target.value)}
              placeholder="Детали (необязательно)"
              className="w-full p-3 border border-soft-200 rounded-xl mb-4 text-sm h-24 resize-none"
            />
            <div className="flex gap-3">
              <button
                onClick={() => setShowReport(false)}
                className="flex-1 py-3 border border-soft-200 rounded-xl text-soft-600"
              >
                Отмена
              </button>
              <button
                onClick={handleReport}
                disabled={!reportReason}
                className="flex-1 py-3 bg-soft-600 text-white rounded-xl disabled:opacity-50"
              >
                Отправить
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white border-b border-soft-200 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/community')}
              className="px-3 py-2 bg-white border border-soft-300 text-soft-700 font-medium rounded-xl hover:bg-soft-50 hover:border-soft-400 shadow-sm"
            >
              ← Назад
            </button>
            <h1 className="text-lg font-semibold text-soft-800">Публикация</h1>
          </div>
          <button
            onClick={() => setShowReport(true)}
            className="text-soft-400 hover:text-soft-600 text-sm"
          >
            Пожаловаться
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 py-6">
        <div className="bg-white rounded-2xl p-5 border border-soft-200 mb-4">
          {/* Author */}
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-soft-600">
              {post.author.display_name}
            </span>
            <span className="text-xs text-soft-400">
              {formatDate(post.created_at)}
            </span>
          </div>

          {/* Title & Body */}
          {post.title && (
            <h2 className="font-semibold text-soft-800 mb-3">{post.title}</h2>
          )}
          <p className="text-soft-700 whitespace-pre-wrap mb-4">{post.body}</p>

          {/* Discussion Prompt */}
          {post.discussion_prompt && (
            <div className="bg-soft-50 rounded-lg p-4 mb-4">
              <p className="text-soft-600 italic">
                💭 {post.discussion_prompt}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-4 pt-4 border-t border-soft-100">
            <button
              onClick={handleReaction}
              className={`flex items-center gap-1.5 text-sm transition-colors ${
                post.has_user_reacted ? 'text-soft-600' : 'text-soft-400 hover:text-soft-600'
              }`}
            >
              <span>🤗</span>
              <span>{post.reaction_count || 'Поддержать'}</span>
            </button>
            <button
              onClick={() => setShowCommentForm(!showCommentForm)}
              className="flex items-center gap-1.5 text-sm text-soft-400 hover:text-soft-600"
            >
              <span>💬</span>
              <span>{post.comment_count || 'Комментировать'}</span>
            </button>

            {/* Edit/Delete for own posts */}
            {post.is_own_post && (
              <>
                <button
                  onClick={openEditModal}
                  className="text-sm text-soft-400 hover:text-soft-600 ml-auto"
                  title="Редактировать"
                >
                  ✏️
                </button>
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="text-sm text-red-400 hover:text-red-600"
                  title="Удалить"
                >
                  🗑️
                </button>
              </>
            )}
          </div>
        </div>

        {/* Comment Form */}
        {showCommentForm && (
          <div className="bg-white rounded-2xl p-5 border border-soft-200 mb-4">
            <h3 className="font-medium text-soft-800 mb-3">Твой ответ</h3>
            <div className="space-y-2 mb-4">
              {COMMENT_TYPES.map(type => (
                <label
                  key={type.value}
                  className={`flex items-start gap-3 p-3 rounded-xl cursor-pointer transition-colors ${
                    commentType === type.value ? 'bg-soft-100' : 'hover:bg-soft-50'
                  }`}
                >
                  <input
                    type="radio"
                    value={type.value}
                    checked={commentType === type.value}
                    onChange={(e) => setCommentType(e.target.value)}
                    className="mt-1"
                  />
                  <div>
                    <div className="font-medium text-soft-800 text-sm">{type.label}</div>
                    <div className="text-soft-500 text-xs">{type.desc}</div>
                  </div>
                </label>
              ))}
            </div>
            <textarea
              value={commentBody}
              onChange={(e) => setCommentBody(e.target.value)}
              placeholder="Напиши свой ответ..."
              className="w-full p-3 border border-soft-200 rounded-xl text-sm h-32 resize-none mb-3"
            />
            <div className="flex gap-3">
              <button
                onClick={() => setShowCommentForm(false)}
                className="flex-1 py-3 border border-soft-200 rounded-xl text-soft-600"
              >
                Отмена
              </button>
              <button
                onClick={handleSubmitComment}
                disabled={!commentBody.trim() || submittingComment}
                className="flex-1 py-3 bg-soft-600 text-white rounded-xl disabled:opacity-50"
              >
                {submittingComment ? 'Отправка...' : 'Отправить'}
              </button>
            </div>
          </div>
        )}

        {/* Comments */}
        {post.comments.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-medium text-soft-600 text-sm uppercase tracking-wide">
              Комментарии ({post.comments.length})
            </h3>
            {post.comments.map(comment => (
              <div key={comment.id} className="bg-white rounded-2xl p-4 border border-soft-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-soft-600">
                    {comment.author.display_name}
                  </span>
                  <span className="text-xs text-soft-400 bg-soft-100 px-2 py-1 rounded">
                    {COMMENT_TYPES.find(t => t.value === comment.comment_type)?.label || comment.comment_type}
                  </span>
                </div>
                <p className="text-soft-700 text-sm">{comment.body}</p>
              </div>
            ))}
          </div>
        )}

        {/* Edit Modal */}
        {showEdit && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
              <h2 className="text-xl font-semibold text-soft-800 mb-4">
                Редактировать публикацию
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-soft-700 mb-2">
                    Заголовок <span className="text-soft-400">(необязательно)</span>
                  </label>
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    placeholder="Заголовок..."
                    className="w-full p-3 border border-soft-200 rounded-xl text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-soft-700 mb-2">
                    Текст <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={editBody}
                    onChange={(e) => setEditBody(e.target.value)}
                    placeholder="Текст публикации..."
                    className="w-full p-3 border border-soft-200 rounded-xl text-sm h-40 resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-soft-700 mb-2">
                    Вопрос к сообществу <span className="text-soft-400">(необязательно)</span>
                  </label>
                  <input
                    type="text"
                    value={editPrompt}
                    onChange={(e) => setEditPrompt(e.target.value)}
                    placeholder="Что бы вы хотели спросить?"
                    className="w-full p-3 border border-soft-200 rounded-xl text-sm"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowEdit(false)}
                  className="flex-1 py-3 border border-soft-200 rounded-xl text-soft-600 font-medium"
                >
                  Отмена
                </button>
                <button
                  onClick={handleSaveEdit}
                  disabled={!editBody.trim() || saving}
                  className="flex-1 py-3 bg-soft-600 text-white rounded-xl font-medium disabled:opacity-50"
                >
                  {saving ? 'Сохранение...' : 'Сохранить'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-md w-full p-6">
              <h2 className="text-xl font-semibold text-soft-800 mb-4">
                Удалить публикацию?
              </h2>
              <p className="text-soft-600 mb-6">
                Это действие нельзя отменить. Публикация будет удалена навсегда.
              </p>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="flex-1 py-3 border border-soft-200 rounded-xl text-soft-600 font-medium"
                >
                  Отмена
                </button>
                <button
                  onClick={handleDelete}
                  className="flex-1 py-3 bg-red-500 text-white rounded-xl font-medium"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
