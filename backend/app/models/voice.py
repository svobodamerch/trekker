from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class VoiceNote(SQLModel, table=True):
    __tablename__ = "voice_notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    telegram_file_id: str
    telegram_file_unique_id: Optional[str] = None
    transcription_text: Optional[str] = None
    status: str = Field(default="uploaded")
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="voice_notes")
