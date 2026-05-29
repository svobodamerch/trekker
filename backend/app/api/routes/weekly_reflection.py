"""Weekly AI Reflection endpoint."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api.deps import get_current_user, get_db
from app.models import User, Entry, Goal, AIAnalysis
from app.services.ai_service import AIService
from app.schemas.ai import WeeklyReflectionOut, WeeklyReflectionCreate

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/weekly-reflection", response_model=WeeklyReflectionOut)
async def create_weekly_reflection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate weekly reflection based on last 7 days entries.
    
    Requires at least 3 entries for meaningful reflection.
    Works with or without AI_API_KEY (graceful placeholder mode).
    """
    # Get entries from last 7 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    entries = db.query(Entry).filter(
        Entry.user_id == current_user.id,
        Entry.created_at >= start_date,
        Entry.created_at <= end_date,
    ).order_by(Entry.created_at.desc()).all()
    
    # Get active goals (month and dream_life prioritized)
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == "active",
    ).all()
    
    # Generate reflection
    ai_service = AIService()
    reflection_data = await ai_service.generate_weekly_reflection(entries, goals)
    
    # Store in ai_analyses
    analysis = AIAnalysis(
        user_id=current_user.id,
        analysis_type="weekly_reflection",
        period_start=start_date,
        period_end=end_date,
        entry_count=len(entries),
        raw_output=reflection_data,
        created_at=datetime.utcnow(),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return WeeklyReflectionOut(
        id=analysis.id,
        analysis_type=analysis.analysis_type,
        period_start=analysis.period_start,
        period_end=analysis.period_end,
        entry_count=analysis.entry_count,
        patterns=reflection_data["patterns"],
        energy_insights=reflection_data["energy_insights"],
        goal_connections=reflection_data["goal_connections"],
        next_week_question=reflection_data["next_week_question"],
        next_week_focus=reflection_data["next_week_focus"],
        is_placeholder=reflection_data.get("is_placeholder", True),
        created_at=analysis.created_at,
    )


@router.get("/weekly-reflection/latest", response_model=Optional[WeeklyReflectionOut])
def get_latest_weekly_reflection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the most recent weekly reflection for the user."""
    analysis = db.query(AIAnalysis).filter(
        AIAnalysis.user_id == current_user.id,
        AIAnalysis.analysis_type == "weekly_reflection",
    ).order_by(AIAnalysis.created_at.desc()).first()
    
    if not analysis:
        return None
    
    raw = analysis.raw_output or {}
    
    return WeeklyReflectionOut(
        id=analysis.id,
        analysis_type=analysis.analysis_type,
        period_start=analysis.period_start,
        period_end=analysis.period_end,
        entry_count=analysis.entry_count,
        patterns=raw.get("patterns", ""),
        energy_insights=raw.get("energy_insights", ""),
        goal_connections=raw.get("goal_connections", ""),
        next_week_question=raw.get("next_week_question", ""),
        next_week_focus=raw.get("next_week_focus", ""),
        is_placeholder=raw.get("is_placeholder", True),
        created_at=analysis.created_at,
    )
