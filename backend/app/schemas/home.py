from typing import Optional, Dict, Any
from pydantic import BaseModel


class HomeSummary(BaseModel):
    """Home page summary with return state for soft return mechanic."""

    days_since_last_entry: Optional[int]
    return_state: str  # new_user, active_today, one_day_gap, after_pause, long_pause
    has_entries: bool
    latest_entry_preview: Optional[Dict[str, Any]]
