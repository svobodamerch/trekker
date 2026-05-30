from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_user_id: str = Field(index=True, unique=True)
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    timezone: str = Field(default="UTC")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    settings: Optional["UserSettings"] = Relationship(back_populates="user")
    entries: list["Entry"] = Relationship(back_populates="user")
    goals: list["Goal"] = Relationship(back_populates="user")
    voice_notes: list["VoiceNote"] = Relationship(back_populates="user")
    ai_analyses: list["AIAnalysis"] = Relationship(back_populates="user")
    events: list["Event"] = Relationship(back_populates="user")
    reminder_logs: list["ReminderLog"] = Relationship(back_populates="user")
    # Community Support Circle
    community_posts: list["CommunityPost"] = Relationship(back_populates="user")
    community_comments: list["CommunityComment"] = Relationship(back_populates="user")
    community_reactions: list["CommunityReaction"] = Relationship(back_populates="user")


class UserSettings(SQLModel, table=True):
    __tablename__ = "user_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    reminder_enabled: bool = Field(default=False)
    reminder_time: Optional[str] = None
    reminder_timezone: str = Field(default="UTC")
    soft_language_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="settings")
