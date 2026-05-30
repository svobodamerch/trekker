"""Community Support Circle schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# === Community Post Schemas ===

class CommunityPostBase(BaseModel):
    """Base schema for community posts."""
    title: Optional[str] = None
    body: str
    discussion_prompt: Optional[str] = None
    visibility: str = "anonymous"  # anonymous, named


class CommunityPostCreate(CommunityPostBase):
    """Create new post (manual or from source)."""
    source_type: str = "custom"  # pulse, goal, dream_life, life_balance, custom
    source_id: Optional[int] = None


class CommunityPostUpdate(BaseModel):
    """Update existing post."""
    title: Optional[str] = None
    body: Optional[str] = None
    discussion_prompt: Optional[str] = None
    visibility: Optional[str] = None
    status: Optional[str] = None


class CommunityPostAuthor(BaseModel):
    """Public author info (anonymous or named)."""
    id: int
    display_name: str  # "Пользователь" or actual name
    avatar: Optional[str] = None


class CommunityPostInFeed(BaseModel):
    """Post as it appears in the feed."""
    id: int
    author: CommunityPostAuthor
    title: Optional[str] = None
    body: str
    discussion_prompt: Optional[str] = None
    source_type: str
    source_preview: Optional[str] = None  # Short excerpt from source
    
    # Engagement
    comment_count: int = 0
    reaction_count: int = 0
    has_user_reacted: bool = False
    
    # Ownership (for edit/delete permissions)
    is_own_post: bool = False
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommunityPostDetail(CommunityPostInFeed):
    """Full post with comments."""
    comments: List["CommunityCommentResponse"] = []


# === Community Comment Schemas ===

class CommunityCommentBase(BaseModel):
    """Base schema for comments."""
    body: str
    comment_type: str = "support"  # support, question, similar_experience, gentle_idea


class CommunityCommentCreate(CommunityCommentBase):
    """Create new comment."""
    pass


class CommunityCommentUpdate(BaseModel):
    """Update existing comment."""
    body: Optional[str] = None
    comment_type: Optional[str] = None


class CommunityCommentAuthor(BaseModel):
    """Comment author (always anonymous in MVP)."""
    id: int
    display_name: str = "Пользователь"


class CommunityCommentResponse(BaseModel):
    """Comment in response."""
    id: int
    author: CommunityCommentAuthor
    body: str
    comment_type: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# === Reaction Schemas ===

class CommunityReactionCreate(BaseModel):
    """Add reaction to post."""
    reaction_type: str = "support"  # MVP: support only


class CommunityReactionResponse(BaseModel):
    """Reaction info."""
    id: int
    user_id: int
    reaction_type: str
    created_at: datetime
    removed: bool = False  # True if reaction was toggled off


# === Report Schemas ===

class CommunityReportCreate(BaseModel):
    """Report post or comment."""
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    reason: str
    details: Optional[str] = None


class CommunityReportResponse(BaseModel):
    """Report response."""
    id: int
    status: str = "new"
    message: str = "Спасибо. Я получил репорт и разберусь."


# === Feed/List Schemas ===

class CommunityFeedResponse(BaseModel):
    """Feed of posts."""
    posts: List[CommunityPostInFeed]
    has_more: bool
    next_cursor: Optional[str] = None


class CommunityUserStats(BaseModel):
    """User's activity in community."""
    posts_count: int
    comments_count: int
    reactions_given: int
    reactions_received: int


# === Share from Source Schemas ===

class ShareSourcePreview(BaseModel):
    """Preview before sharing from source."""
    source_type: str
    source_id: int
    title: Optional[str]
    body_preview: str
    can_share: bool
    error_message: Optional[str] = None


class ShareSourceRequest(BaseModel):
    """Request to share from source."""
    source_type: str  # pulse, goal, dream_life, life_balance
    source_id: int
    title: Optional[str] = None
    discussion_prompt: Optional[str] = None
    visibility: str = "anonymous"


# Update forward references
CommunityPostDetail.model_rebuild()
