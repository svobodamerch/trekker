from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Entry(SQLModel, table=True):
    __tablename__ = "entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    entry_type: str = Field(default="pulse")
    mood: Optional[int] = Field(default=None, ge=1, le=10)
    anxiety: Optional[int] = Field(default=None, ge=1, le=10)
    energy: Optional[int] = Field(default=None, ge=1, le=10)
    body_state: Optional[str] = None
    insight: Optional[str] = None
    gratitude: Optional[str] = None
    tomorrow_commitment: Optional[str] = None
    raw_text: Optional[str] = None
    source: str = Field(default="mini_app")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="entries")
    goal_links: list["EntryGoalLink"] = Relationship(back_populates="entry")
    ai_analyses: list["AIAnalysis"] = Relationship(back_populates="entry")
