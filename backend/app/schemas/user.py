from typing import Optional
from pydantic import BaseModel, computed_field
from datetime import datetime, date


class UserProfile(BaseModel):
    """User profile data."""
    id: int
    telegram_user_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None  # male, female
    birth_date: Optional[str] = None  # YYYY-MM-DD
    onboarding_completed: bool = False
    timezone: str = "UTC"
    
    @computed_field
    @property
    def age(self) -> Optional[int]:
        """Calculate age from birth_date."""
        if not self.birth_date:
            return None
        try:
            birth = datetime.strptime(self.birth_date, "%Y-%m-%d").date()
            today = date.today()
            age = today.year - birth.year
            if (today.month, today.day) < (birth.month, birth.day):
                age -= 1
            return age
        except (ValueError, TypeError):
            return None
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Update user profile."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None  # male, female
    birth_date: Optional[str] = None  # YYYY-MM-DD


class OnboardingComplete(BaseModel):
    """Complete onboarding with profile data."""
    first_name: str
    last_name: str
    gender: str  # male, female
    birth_date: str  # YYYY-MM-DD
