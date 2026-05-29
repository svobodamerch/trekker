from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Goal(SQLModel, table=True):
    __tablename__ = "goals"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    horizon: str = Field(index=True)
    custom_horizon_label: Optional[str] = None
    custom_horizon_years: Optional[int] = Field(default=None, gt=0)
    life_area: str = Field(default="other", index=True)
    title: str
    description: Optional[str] = None
    desired_state: Optional[str] = None
    status: str = Field(default="active", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_reviewed_at: Optional[datetime] = None

    user: Optional["User"] = Relationship(back_populates="goals")
    versions: list["GoalVersion"] = Relationship(back_populates="goal")
    entry_links: list["EntryGoalLink"] = Relationship(back_populates="goal")
    ai_analyses: list["AIAnalysis"] = Relationship(back_populates="goal")


class GoalVersion(SQLModel, table=True):
    __tablename__ = "goal_versions"

    id: Optional[int] = Field(default=None, primary_key=True)
    goal_id: int = Field(foreign_key="goals.id", index=True)
    title: str
    description: Optional[str] = None
    desired_state: Optional[str] = None
    status: str
    change_note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    goal: Optional[Goal] = Relationship(back_populates="versions")


class EntryGoalLink(SQLModel, table=True):
    __tablename__ = "entry_goal_links"

    id: Optional[int] = Field(default=None, primary_key=True)
    entry_id: int = Field(foreign_key="entries.id", index=True)
    goal_id: Optional[int] = Field(default=None, foreign_key="goals.id", index=True)
    horizon: Optional[str] = None
    step_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    entry: Optional["Entry"] = Relationship(back_populates="goal_links")
    goal: Optional[Goal] = Relationship(back_populates="entry_links")
