"""API routes for daily 10 goals (Brian Tracy technique)."""
import json
from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models import User, DailyTenGoals
from app.schemas.daily_goals import DailyGoalsEntry, DailyGoalsCreate, DailyGoalsUpdate, DailyGoalsList

router = APIRouter(prefix="/daily-goals", tags=["daily-goals"])


def _parse_goals(goals_str: str) -> List[str]:
    """Parse stored goals string to list."""
    if not goals_str:
        return []
    try:
        return json.loads(goals_str)
    except:
        return goals_str.split('\n') if goals_str else []


def _store_goals(goals: List[str]) -> str:
    """Store goals list as JSON string."""
    return json.dumps([g.strip() for g in goals if g.strip()], ensure_ascii=False)


@router.get("/today", response_model=DailyGoalsEntry)
def get_today_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's 10 goals or create empty entry."""
    today = date.today()
    entry = db.query(DailyTenGoals).filter(
        DailyTenGoals.user_id == current_user.id,
        DailyTenGoals.goal_date == today,
    ).first()
    
    if not entry:
        return DailyGoalsEntry(
            id=0,
            goal_date=today,
            goals=[],
            created_at="",
        )
    
    return DailyGoalsEntry(
        id=entry.id,
        goal_date=entry.goal_date,
        goals=_parse_goals(entry.goals),
        created_at=entry.created_at.isoformat(),
    )


@router.post("/today", response_model=DailyGoalsEntry)
def save_today_goals(
    data: DailyGoalsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save today's 10 goals."""
    today = date.today()
    
    # Check if entry exists
    entry = db.query(DailyTenGoals).filter(
        DailyTenGoals.user_id == current_user.id,
        DailyTenGoals.goal_date == today,
    ).first()
    
    if entry:
        # Update existing
        entry.goals = _store_goals(data.goals)
        db.commit()
        db.refresh(entry)
    else:
        # Create new
        entry = DailyTenGoals(
            user_id=current_user.id,
            goal_date=today,
            goals=_store_goals(data.goals),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
    
    return DailyGoalsEntry(
        id=entry.id,
        goal_date=entry.goal_date,
        goals=_parse_goals(entry.goals),
        created_at=entry.created_at.isoformat(),
    )


@router.get("/history", response_model=DailyGoalsList)
def get_goals_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get history of all daily goals and streak."""
    today = date.today()
    
    # Get all entries
    entries = db.query(DailyTenGoals).filter(
        DailyTenGoals.user_id == current_user.id,
    ).order_by(DailyTenGoals.goal_date.desc()).all()
    
    today_entry = None
    archive = []
    
    for entry in entries:
        entry_data = DailyGoalsEntry(
            id=entry.id,
            goal_date=entry.goal_date,
            goals=_parse_goals(entry.goals),
            created_at=entry.created_at.isoformat(),
        )
        if entry.goal_date == today:
            today_entry = entry_data
        else:
            archive.append(entry_data)
    
    # Calculate streak (consecutive days with entries)
    streak = 0
    check_date = today - timedelta(days=1)
    while True:
        has_entry = db.query(DailyTenGoals).filter(
            DailyTenGoals.user_id == current_user.id,
            DailyTenGoals.goal_date == check_date,
        ).first() is not None
        if has_entry:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    return DailyGoalsList(
        today=today_entry,
        archive=archive,
        streak_days=streak,
    )


@router.delete("/{entry_id}")
def delete_goals_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a daily goals entry."""
    entry = db.query(DailyTenGoals).filter(
        DailyTenGoals.id == entry_id,
        DailyTenGoals.user_id == current_user.id,
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    db.delete(entry)
    db.commit()
    return {"success": True}
