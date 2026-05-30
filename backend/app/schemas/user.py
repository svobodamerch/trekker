from typing import Optional
from pydantic import BaseModel


class UserProfile(BaseModel):
    """User profile data."""
    id: int
    telegram_user_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    onboarding_completed: bool = False
    timezone: str = "UTC"
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Update user profile."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None  # male, female, other
    age: Optional[int] = None


class OnboardingComplete(BaseModel):
    """Complete onboarding with profile data."""
    first_name: str
    last_name: str
    gender: str  # male, female, other
    age: int
