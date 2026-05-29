from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EntryCreate(BaseModel):
    entry_type: str = Field(default="pulse", pattern="^(pulse|diary|deep)$")
    mood: Optional[int] = Field(default=None, ge=1, le=10)
    anxiety: Optional[int] = Field(default=None, ge=1, le=10)
    energy: Optional[int] = Field(default=None, ge=1, le=10)
    body_state: Optional[str] = None
    insight: Optional[str] = None
    gratitude: Optional[str] = None
    tomorrow_commitment: Optional[str] = None
    source: str = Field(default="mini_app", pattern="^(mini_app|bot|voice|import)$")


class EntryOut(BaseModel):
    id: int
    user_id: int
    entry_type: str
    mood: Optional[int]
    anxiety: Optional[int]
    energy: Optional[int]
    body_state: Optional[str]
    insight: Optional[str]
    gratitude: Optional[str]
    tomorrow_commitment: Optional[str]
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class EntryList(BaseModel):
    items: list[EntryOut]
    total: int
