from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class FeedbackMessage(SQLModel, table=True):
    __tablename__ = "feedback_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    telegram_user_id: Optional[str] = None
    category: str = Field(default="other")
    message: str
    source: str = Field(default="mini_app")
    status: str = Field(default="new")
    created_at: datetime = Field(default_factory=datetime.utcnow)
