from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class WeeklyReflectionCreate(BaseModel):
    """Request to create weekly reflection (no body needed, uses last 7 days)."""
    pass


class WeeklyReflectionOut(BaseModel):
    """Weekly AI reflection output."""
    
    id: int
    analysis_type: str
    period_start: datetime
    period_end: datetime
    entry_count: int
    
    # AI-generated content
    patterns: str
    energy_insights: str
    goal_connections: str
    next_week_question: str
    next_week_focus: str
    
    is_placeholder: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
