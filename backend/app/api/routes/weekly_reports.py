"""API routes for weekly reports (admin/trigger endpoints)."""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models import User, WeeklyReport, CommunityWeeklyReport
from app.services.weekly_report_service import WeeklyReportService
from app.config import settings

router = APIRouter(prefix="/weekly-reports", tags=["weekly-reports"])


def verify_admin_key(x_admin_key: Optional[str] = Header(None)):
    """Verify admin API key for bot-to-backend communication."""
    if not settings.admin_api_key:
        raise HTTPException(status_code=501, detail="Admin API not configured")
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return True


@router.post("/generate")
async def trigger_report_generation(
    background_tasks: BackgroundTasks,
    target_date: date = None,
    send_via_telegram: bool = True,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key),
):
    """Trigger generation of weekly reports (admin only, called by bot)."""

    service = WeeklyReportService(db)

    # Run in background to avoid timeout
    async def generate():
        await service.generate_all_reports(target_date, send_via_telegram=send_via_telegram)

    background_tasks.add_task(generate)

    return {
        "message": "Report generation started",
        "week": service.get_week_boundaries(target_date),
        "send_via_telegram": send_via_telegram,
    }


@router.get("/my", response_model=dict)
def get_my_latest_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's latest weekly report."""
    report = db.query(WeeklyReport).filter(
        WeeklyReport.user_id == current_user.id,
    ).order_by(WeeklyReport.week_start.desc()).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="No reports found")
    
    return {
        "id": report.id,
        "week_start": report.week_start.isoformat(),
        "week_end": report.week_end.isoformat(),
        "entries_count": report.entries_count,
        "days_with_entries": report.days_with_entries,
        "days_missed": report.days_missed,
        "avg_mood": report.avg_mood,
        "avg_anxiety": report.avg_anxiety,
        "avg_energy": report.avg_energy,
        "summary": report.summary,
        "highlights": report.highlights,
        "patterns": report.patterns,
        "encouragement": report.encouragement,
        "suggestions": report.suggestions,
        "sent_at": report.sent_at.isoformat() if report.sent_at else None,
        "created_at": report.created_at.isoformat(),
    }


@router.get("/my/history", response_model=List[dict])
def get_my_report_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all weekly reports for current user."""
    reports = db.query(WeeklyReport).filter(
        WeeklyReport.user_id == current_user.id,
    ).order_by(WeeklyReport.week_start.desc()).all()
    
    return [
        {
            "id": r.id,
            "week_start": r.week_start.isoformat(),
            "week_end": r.week_end.isoformat(),
            "entries_count": r.entries_count,
            "days_with_entries": r.days_with_entries,
            "summary": r.summary,
            "highlights": r.highlights,
        }
        for r in reports
    ]


@router.get("/community/latest", response_model=dict)
def get_latest_community_report(
    db: Session = Depends(get_db),
):
    """Get latest community weekly report."""
    report = db.query(CommunityWeeklyReport).order_by(
        CommunityWeeklyReport.week_start.desc()
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="No community reports found")
    
    return {
        "id": report.id,
        "week_start": report.week_start.isoformat(),
        "week_end": report.week_end.isoformat(),
        "total_users": report.total_users,
        "active_users": report.active_users,
        "total_entries": report.total_entries,
        "total_pulse_entries": report.total_pulse_entries,
        "total_diary_entries": report.total_diary_entries,
        "community_avg_mood": report.community_avg_mood,
        "community_avg_anxiety": report.community_avg_anxiety,
        "community_avg_energy": report.community_avg_energy,
        "community_summary": report.community_summary,
        "trends": report.trends,
        "encouragement": report.encouragement,
        "collective_challenge": report.collective_challenge,
        "created_at": report.created_at.isoformat(),
    }
