"""Daily 10 Goals model for Brian Tracy technique."""
from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class DailyTenGoals(SQLModel, table=True):
    """User's daily 10 goals (Brian Tracy technique)."""
    __tablename__ = "daily_ten_goals"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    goal_date: date = Field(default_factory=date.today, index=True)
    
    # 10 goals as text lines
    goals: str = Field(default="")  # JSON array or newline-separated
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional["User"] = Relationship(back_populates="daily_goals")
