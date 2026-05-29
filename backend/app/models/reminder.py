from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class ReminderLog(SQLModel, table=True):
    """Track sent reminders to avoid duplicates."""
    __tablename__ = "reminder_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    reminder_date: str = Field(index=True)  # YYYY-MM-DD
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="sent")

    user: Optional["User"] = Relationship(back_populates="reminder_logs")
