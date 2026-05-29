from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    event_name: str = Field(index=True)
    event_properties: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="events")
