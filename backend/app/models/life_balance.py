from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


LIFE_BALANCE_AREAS = [
    ("health_body", "Здоровье и тело"),
    ("energy_state", "Энергия и состояние"),
    ("relationships_family", "Отношения и семья"),
    ("friends_environment", "Друзья и окружение"),
    ("money", "Деньги"),
    ("work_business", "Работа / бизнес / реализация"),
    ("home_space", "Дом и среда"),
    ("freedom_meaning_growth", "Свобода, смысл и рост"),
]


class LifeBalanceSnapshot(SQLModel, table=True):
    __tablename__ = "life_balance_snapshots"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    scores: List["LifeBalanceScore"] = Relationship(back_populates="snapshot")


class LifeBalanceScore(SQLModel, table=True):
    __tablename__ = "life_balance_scores"

    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_id: int = Field(foreign_key="life_balance_snapshots.id", index=True)
    area_key: str
    score: int
    comment: Optional[str] = None

    snapshot: Optional[LifeBalanceSnapshot] = Relationship(back_populates="scores")
