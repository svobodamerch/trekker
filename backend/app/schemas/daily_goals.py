"""Schemas for daily 10 goals."""
from typing import List, Optional
from datetime import date
from pydantic import BaseModel


class DailyGoalsEntry(BaseModel):
    """Single day's 10 goals."""
    id: int
    goal_date: date
    goals: List[str]
    created_at: str


class DailyGoalsCreate(BaseModel):
    """Create new daily goals entry."""
    goals: List[str]


class DailyGoalsUpdate(BaseModel):
    """Update daily goals."""
    goals: List[str]


class DailyGoalsList(BaseModel):
    """List of daily goals with archive."""
    today: Optional[DailyGoalsEntry] = None
    archive: List[DailyGoalsEntry]
    streak_days: int = 0
