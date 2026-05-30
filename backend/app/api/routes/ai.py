from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User, Entry, Goal, AIAnalysis
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/entries/{entry_id}/analyze")
async def analyze_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AI analysis for an entry."""
    entry = db.query(Entry).filter(
        Entry.id == entry_id,
        Entry.user_id == current_user.id,
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    ai_service = AIService()
    analysis_text = await ai_service.analyze_entry(entry)

    # Save analysis
    analysis = AIAnalysis(
        user_id=current_user.id,
        entry_id=entry.id,
        analysis_type="entry_day",
        model_name=ai_service.model if ai_service.api_key else "placeholder",
        analysis_text=analysis_text,
    )
    db.add(analysis)
    db.commit()

    return {"analysis": analysis_text, "analysis_id": analysis.id}


@router.post("/analyze-all")
async def analyze_all_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate comprehensive AI analysis of all user entries and goals."""
    from app.models import Entry, Goal
    
    # Get all user entries
    entries = db.query(Entry).filter(
        Entry.user_id == current_user.id,
    ).order_by(Entry.created_at.desc()).all()
    
    # Get active goals
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == "active",
    ).all()
    
    ai_service = AIService()
    result = await ai_service.analyze_all_entries(entries, goals)
    
    # Save analysis if not placeholder
    if not result.get("is_placeholder"):
        analysis = AIAnalysis(
            user_id=current_user.id,
            analysis_type="all_entries",
            model_name=ai_service.model if ai_service.api_key else "placeholder",
            raw_output={
                "key_patterns": result.get("key_patterns"),
                "emotional_dynamics": result.get("emotional_dynamics"),
                "body_signals": result.get("body_signals"),
                "insight_themes": result.get("insight_themes"),
                "goal_alignment": result.get("goal_alignment"),
                "recommendations": result.get("recommendations"),
            },
        )
        db.add(analysis)
        db.commit()
    
    return result


@router.post("/goals/analyze")
async def analyze_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AI reflection across all goals."""
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == "active",
    ).all()

    ai_service = AIService()
    analysis_text = await ai_service.analyze_goals(goals)

    # Save analysis
    analysis = AIAnalysis(
        user_id=current_user.id,
        analysis_type="goal_reflection",
        model_name=ai_service.model if ai_service.api_key else "placeholder",
        analysis_text=analysis_text,
    )
    db.add(analysis)
    db.commit()

    return {"analysis": analysis_text, "analysis_id": analysis.id}
