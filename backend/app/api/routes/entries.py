from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User, Entry
from app.schemas.entry import EntryCreate, EntryOut, EntryList
from app.schemas.analytics import WeeklyAnalytics, DailyMetrics, WeeklyAverages
from app.schemas.home import HomeSummary

router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("", response_model=EntryOut)
def create_entry(
    entry_in: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = Entry(
        user_id=current_user.id,
        **entry_in.model_dump(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=EntryList)
def list_entries(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    entry_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Entry).filter(Entry.user_id == current_user.id)
    if entry_type:
        query = query.filter(Entry.entry_type == entry_type)

    total = query.count()
    entries = query.order_by(Entry.created_at.desc()).offset(offset).limit(limit).all()

    return EntryList(
        items=[EntryOut.model_validate(e) for e in entries],
        total=total,
    )


@router.get("/{entry_id}", response_model=EntryOut)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = db.query(Entry).filter(
        Entry.id == entry_id,
        Entry.user_id == current_user.id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.get("/analytics/weekly", response_model=WeeklyAnalytics)
def weekly_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    from datetime import datetime, timedelta

    # Last 7 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    results = db.query(
        func.date(Entry.created_at).label("date"),
        func.avg(Entry.mood).label("mood"),
        func.avg(Entry.anxiety).label("anxiety"),
        func.avg(Entry.energy).label("energy"),
    ).filter(
        Entry.user_id == current_user.id,
        Entry.created_at >= start_date,
    ).group_by(
        func.date(Entry.created_at),
    ).order_by("date").all()

    days = [
        DailyMetrics(
            date=str(r.date),
            mood=round(r.mood, 1) if r.mood else None,
            anxiety=round(r.anxiety, 1) if r.anxiety else None,
            energy=round(r.energy, 1) if r.energy else None,
        )
        for r in results
    ]

    # Calculate averages
    all_moods = [d.mood for d in days if d.mood is not None]
    all_anxiety = [d.anxiety for d in days if d.anxiety is not None]
    all_energy = [d.energy for d in days if d.energy is not None]

    averages = WeeklyAverages(
        mood=round(sum(all_moods) / len(all_moods), 1) if all_moods else None,
        anxiety=round(sum(all_anxiety) / len(all_anxiety), 1) if all_anxiety else None,
        energy=round(sum(all_energy) / len(all_energy), 1) if all_energy else None,
    )

    return WeeklyAnalytics(days=days, averages=averages)


@router.get("/home/summary", response_model=HomeSummary)
def home_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get home summary with return state for soft return mechanic."""
    # Get latest entry
    latest_entry = db.query(Entry).filter(
        Entry.user_id == current_user.id
    ).order_by(Entry.created_at.desc()).first()

    if not latest_entry:
        return HomeSummary(
            days_since_last_entry=None,
            return_state="new_user",
            has_entries=False,
            latest_entry_preview=None,
        )

    # Calculate days since last entry
    now = datetime.utcnow()
    last_entry_date = latest_entry.created_at
    days_diff = (now - last_entry_date).days

    # Determine return state
    if days_diff == 0:
        return_state = "active_today"
    elif days_diff == 1:
        return_state = "one_day_gap"
    elif days_diff >= 7:
        return_state = "long_pause"
    elif days_diff >= 3:
        return_state = "after_pause"
    else:
        # 2 days gap - treat as normal, not a pause
        return_state = "one_day_gap"

    return HomeSummary(
        days_since_last_entry=days_diff,
        return_state=return_state,
        has_entries=True,
        latest_entry_preview={
            "id": latest_entry.id,
            "created_at": latest_entry.created_at.isoformat(),
            "mood": latest_entry.mood,
            "anxiety": latest_entry.anxiety,
            "energy": latest_entry.energy,
            "insight": latest_entry.insight,
        } if latest_entry else None,
    )
