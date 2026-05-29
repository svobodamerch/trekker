from typing import Optional
from pydantic import BaseModel


class DailyMetrics(BaseModel):
    date: str
    mood: Optional[float]
    anxiety: Optional[float]
    energy: Optional[float]


class WeeklyAverages(BaseModel):
    mood: Optional[float]
    anxiety: Optional[float]
    energy: Optional[float]


class WeeklyAnalytics(BaseModel):
    days: list[DailyMetrics]
    averages: WeeklyAverages
