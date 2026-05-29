from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column, JSON


class AIAnalysis(SQLModel, table=True):
    __tablename__ = "ai_analyses"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    entry_id: Optional[int] = Field(default=None, foreign_key="entries.id", index=True)
    goal_id: Optional[int] = Field(default=None, foreign_key="goals.id", index=True)
    analysis_type: str
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    analysis_text: Optional[str] = None  # Made optional for weekly reflections
    
    # Weekly reflection fields
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    entry_count: Optional[int] = None
    raw_output: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="ai_analyses")
    entry: Optional["Entry"] = Relationship(back_populates="ai_analyses")
    goal: Optional["Goal"] = Relationship(back_populates="ai_analyses")
