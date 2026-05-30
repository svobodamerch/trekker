"""Community Support Circle models."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class CommunityPost(SQLModel, table=True):
    """Public posts in the support circle."""
    __tablename__ = "community_posts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Source tracking (optional - can be manual post)
    source_type: str = Field(default="custom")  # pulse, goal, dream_life, life_balance, custom
    source_id: Optional[int] = Field(default=None)
    
    # Content
    title: Optional[str] = Field(default=None)
    body: str = Field()
    discussion_prompt: Optional[str] = Field(default=None)
    
    # Visibility
    visibility: str = Field(default="anonymous")  # anonymous, named
    status: str = Field(default="published")  # published, hidden, deleted, flagged
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="community_posts")
    comments: List["CommunityComment"] = Relationship(back_populates="post")
    reactions: List["CommunityReaction"] = Relationship(back_populates="post")


class CommunityComment(SQLModel, table=True):
    """Comments on community posts."""
    __tablename__ = "community_comments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="community_posts.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    body: str = Field()
    comment_type: str = Field(default="support")  # support, question, similar_experience, gentle_idea
    status: str = Field(default="published")  # published, hidden, deleted, flagged
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    post: Optional[CommunityPost] = Relationship(back_populates="comments")
    user: Optional["User"] = Relationship(back_populates="community_comments")


class CommunityReaction(SQLModel, table=True):
    """Reactions on community posts (only 'support' in MVP)."""
    __tablename__ = "community_reactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="community_posts.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    reaction_type: str = Field(default="support")  # support, similar, thanks, saved (MVP: support only)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    post: Optional[CommunityPost] = Relationship(back_populates="reactions")
    user: Optional["User"] = Relationship(back_populates="community_reactions")
    
    class Config:
        # Unique constraint: one reaction per user per post
        # This should be enforced at DB level with a unique index
        pass


class CommunityReport(SQLModel, table=True):
    """Reports on posts or comments."""
    __tablename__ = "community_reports"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    reporter_user_id: int = Field(foreign_key="users.id")
    post_id: Optional[int] = Field(default=None, foreign_key="community_posts.id")
    comment_id: Optional[int] = Field(default=None, foreign_key="community_comments.id")
    
    reason: str = Field()
    details: Optional[str] = Field(default=None)
    status: str = Field(default="new")  # new, reviewed, resolved, ignored
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Update User model relationships
# Add to models/user.py imports and relationships:
# community_posts: List["CommunityPost"] = Relationship(back_populates="user")
# community_comments: List["CommunityComment"] = Relationship(back_populates="user")
# community_reactions: List["CommunityReaction"] = Relationship(back_populates="user")
