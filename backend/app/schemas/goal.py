from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    horizon: str = Field(pattern="^(month|year|three_years|five_years|dream_life)$")
    custom_horizon_label: Optional[str] = None
    custom_horizon_years: Optional[int] = Field(default=None, gt=0)
    life_area: str = Field(
        default="other",
        pattern="^(health|relationships|money|business|work|home|freedom|spirituality|body|learning|contribution|other)$"
    )
    title: str
    description: Optional[str] = None
    desired_state: Optional[str] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    desired_state: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(active|paused|completed|archived)$")
    change_note: Optional[str] = None


class GoalOut(BaseModel):
    id: int
    user_id: int
    horizon: str
    custom_horizon_label: Optional[str]
    custom_horizon_years: Optional[int]
    life_area: str
    title: str
    description: Optional[str]
    desired_state: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    last_reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True


class GoalsByHorizon(BaseModel):
    month: list[GoalOut]
    year: list[GoalOut]
    three_years: list[GoalOut]
    five_years: list[GoalOut]
    dream_life: list[GoalOut]


class EntryGoalLinkCreate(BaseModel):
    goal_id: Optional[int] = None
    horizon: Optional[str] = Field(default=None, pattern="^(month|year|three_years|five_years|dream_life)$")
    step_text: Optional[str] = None


class GoalReviewCreate(BaseModel):
    """Goal review submission with reflective questions."""
    is_alive: Optional[bool] = None  # Is the goal still relevant/feels alive
    became_clearer: Optional[str] = None  # What became clearer
    wants_to_change: Optional[str] = None  # What user wants to change
    next_week_step: Optional[str] = None  # Small step for coming week
    # Optional goal updates during review
    title: Optional[str] = None
    description: Optional[str] = None
    desired_state: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(active|paused|completed|archived)$")


class GoalNeedsReview(BaseModel):
    """Goals that need monthly review (no review or >30 days)."""
    goals: list[GoalOut]
    count: int
    message: str
