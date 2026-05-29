from typing import Optional
from pydantic import BaseModel


class SettingsOut(BaseModel):
    reminder_enabled: bool
    reminder_time: Optional[str] = None
    reminder_timezone: str = "UTC"
    soft_language_enabled: bool = True


class SettingsUpdate(BaseModel):
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[str] = None
    reminder_timezone: Optional[str] = None
    soft_language_enabled: Optional[bool] = None
