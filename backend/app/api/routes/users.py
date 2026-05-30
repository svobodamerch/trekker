from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models import User
from app.schemas.user import UserProfile, UserProfileUpdate, OnboardingComplete

router = APIRouter(prefix="/users", tags=["users"])


def calculate_age(birth_date_str: str) -> int:
    """Calculate age from birth date string (YYYY-MM-DD)."""
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth_date.year
        # Adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
    except (ValueError, TypeError):
        return None


@router.get("/me", response_model=UserProfile)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's full profile with calculated age."""
    # Calculate age from birth_date if available
    if current_user.birth_date:
        current_user.age = calculate_age(current_user.birth_date)
    return current_user


@router.patch("/me", response_model=UserProfile)
def update_my_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's profile."""
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/onboarding", response_model=UserProfile)
def complete_onboarding(
    data: OnboardingComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete onboarding with profile data."""
    current_user.first_name = data.first_name
    current_user.last_name = data.last_name
    current_user.gender = data.gender
    current_user.birth_date = data.birth_date
    current_user.onboarding_completed = True
    
    db.commit()
    db.refresh(current_user)
    
    # Calculate age for response
    current_user.age = calculate_age(current_user.birth_date)
    return current_user


@router.get("/stats")
def get_users_stats(db: Session = Depends(get_db)):
    """Get user statistics - total and active users."""
    # Total users
    total_users = db.query(func.count(User.id)).scalar() or 0
    
    # Active users (active in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = db.query(func.count(User.id)).filter(User.updated_at >= week_ago).scalar() or 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "active_period_days": 7
    }
