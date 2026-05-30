import { api } from './client'

export interface CommunityPost {
  id: number
  author: {
    id: number
    display_name: string
    avatar?: string
  }
  title?: string
  body: string
  discussion_prompt?: string
  source_type: string
  source_preview?: string
  comment_count: number
  reaction_count: number
  has_user_reacted: boolean
  created_at: string
}

export interface CommunityPostDetail extends CommunityPost {
  comments: CommunityComment[]
}

export interface CommunityComment {
  id: number
  author: {
    id: number
    display_name: string
  }
  body: string
  comment_type: 'support' | 'question' | 'similar_experience' | 'gentle_idea'
  status: string
  created_at: string
}

export interface CommunityFeedResponse {
  posts: CommunityPost[]
  has_more: boolean
  next_cursor?: string
}

export interface SharePreview {
  source_type: string
  source_id: number
  title?: string
  body_preview: string
  can_share: boolean
  error_message?: string
}

export interface CreatePostData {
  source_type: string
  source_id?: number
  title?: string
  body: string
  discussion_prompt?: string
  visibility: 'anonymous' | 'named'
}

export interface CreateCommentData {
  body: string
  comment_type: 'support' | 'question' | 'similar_experience' | 'gentle_idea'
}

export interface ReportData {
  post_id?: number
  comment_id?: number
  reason: string
  details?: string
}

// Feed
export async function getCommunityFeed(cursor?: string, limit = 20): Promise<CommunityFeedResponse> {
  const params = new URLSearchParams()
  if (cursor) params.append('cursor', cursor)
  params.append('limit', String(limit))
  
  return api<CommunityFeedResponse>(`/community/feed?${params}`)
}

// Posts
export async function getPost(postId: number): Promise<CommunityPostDetail> {
  return api<CommunityPostDetail>(`/community/posts/${postId}`)
}

export async function createPost(data: CreatePostData): Promise<CommunityPost> {
  return api<CommunityPost>('/community/posts', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export async function updatePost(postId: number, data: Partial<CreatePostData>): Promise<CommunityPost> {
  return api<CommunityPost>(`/community/posts/${postId}`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  })
}

export async function deletePost(postId: number): Promise<{ success: boolean; message: string }> {
  return api<{ success: boolean; message: string }>(`/community/posts/${postId}`, {
    method: 'DELETE'
  })
}

// Comments
export async function createComment(postId: number, data: CreateCommentData): Promise<CommunityComment> {
  return api<CommunityComment>(`/community/posts/${postId}/comments`, {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export async function deleteComment(commentId: number): Promise<{ success: boolean; message: string }> {
  return api<{ success: boolean; message: string }>(`/community/comments/${commentId}`, {
    method: 'DELETE'
  })
}

// Reactions
export async function toggleReaction(postId: number, reactionType = 'support'): Promise<{
  id: number
  user_id: number
  reaction_type: string
  created_at: string
  removed: boolean
}> {
  return api(`/community/posts/${postId}/reactions`, {
    method: 'POST',
    body: JSON.stringify({ reaction_type: reactionType })
  })
}

// Reports
export async function createReport(data: ReportData): Promise<{
  id: number
  status: string
  message: string
}> {
  return api('/community/reports', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

// Share from source
export async function getSharePreview(sourceType: string, sourceId: number): Promise<SharePreview> {
  return api<SharePreview>(`/community/share-preview?source_type=${sourceType}&source_id=${sourceId}`)
}

export async function shareFromSource(data: {
  source_type: string
  source_id: number
  title?: string
  discussion_prompt?: string
  visibility: 'anonymous' | 'named'
}): Promise<CommunityPost> {
  return api<CommunityPost>('/community/share', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

// User stats
export async function getUserStats(): Promise<{
  posts_count: number
  comments_count: number
  reactions_given: number
  reactions_received: number
}> {
  return api('/community/user/stats')
}
