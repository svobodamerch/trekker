from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.api.deps import get_current_user, get_db
from app.models import User
from app.models.life_balance import LifeBalanceSnapshot, LifeBalanceScore, LIFE_BALANCE_AREAS

router = APIRouter(prefix="/life-balance", tags=["life-balance"])


class ScoreIn(BaseModel):
    area_key: str
    score: int = Field(ge=1, le=10)
    comment: Optional[str] = Field(default=None, max_length=500)


class SnapshotCreate(BaseModel):
    scores: List[ScoreIn]
    note: Optional[str] = Field(default=None, max_length=1000)


class ScoreOut(BaseModel):
    area_key: str
    area_label: str
    score: int
    comment: Optional[str]


class SnapshotOut(BaseModel):
    id: int
    created_at: datetime
    note: Optional[str]
    scores: List[ScoreOut]


AREA_LABELS = dict(LIFE_BALANCE_AREAS)


def _snapshot_out(snapshot: LifeBalanceSnapshot) -> SnapshotOut:
    scores = [
        ScoreOut(
            area_key=s.area_key,
            area_label=AREA_LABELS.get(s.area_key, s.area_key),
            score=s.score,
            comment=s.comment,
        )
        for s in sorted(snapshot.scores, key=lambda x: list(AREA_LABELS.keys()).index(x.area_key) if x.area_key in AREA_LABELS else 99)
    ]
    return SnapshotOut(
        id=snapshot.id,
        created_at=snapshot.created_at,
        note=snapshot.note,
        scores=scores,
    )


@router.post("/snapshots", response_model=SnapshotOut, status_code=201)
def create_snapshot(
    data: SnapshotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    valid_keys = {k for k, _ in LIFE_BALANCE_AREAS}
    for s in data.scores:
        if s.area_key not in valid_keys:
            raise HTTPException(status_code=422, detail=f"Unknown area_key: {s.area_key}")

    snapshot = LifeBalanceSnapshot(
        user_id=current_user.id,
        note=data.note,
    )
    db.add(snapshot)
    db.flush()

    for s in data.scores:
        db.add(LifeBalanceScore(
            snapshot_id=snapshot.id,
            area_key=s.area_key,
            score=s.score,
            comment=s.comment,
        ))

    db.commit()
    db.refresh(snapshot)
    return _snapshot_out(snapshot)


@router.get("/latest", response_model=Optional[SnapshotOut])
def get_latest(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snap = (
        db.query(LifeBalanceSnapshot)
        .filter(LifeBalanceSnapshot.user_id == current_user.id)
        .order_by(LifeBalanceSnapshot.created_at.desc())
        .first()
    )
    if not snap:
        return None
    return _snapshot_out(snap)


@router.get("/history", response_model=List[SnapshotOut])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snaps = (
        db.query(LifeBalanceSnapshot)
        .filter(LifeBalanceSnapshot.user_id == current_user.id)
        .order_by(LifeBalanceSnapshot.created_at.desc())
        .limit(10)
        .all()
    )
    return [_snapshot_out(s) for s in snaps]


@router.get("/comparison")
def get_comparison(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snaps = (
        db.query(LifeBalanceSnapshot)
        .filter(LifeBalanceSnapshot.user_id == current_user.id)
        .order_by(LifeBalanceSnapshot.created_at.desc())
        .limit(2)
        .all()
    )
    if len(snaps) < 2:
        return {"has_comparison": False}

    latest, previous = snaps[0], snaps[1]
    latest_map = {s.area_key: s.score for s in latest.scores}
    previous_map = {s.area_key: s.score for s in previous.scores}

    changes = []
    for key, label in LIFE_BALANCE_AREAS:
        cur = latest_map.get(key)
        prev = previous_map.get(key)
        if cur is not None and prev is not None:
            changes.append({
                "area_key": key,
                "area_label": label,
                "previous": prev,
                "current": cur,
                "delta": cur - prev,
            })

    return {
        "has_comparison": True,
        "latest_date": latest.created_at.isoformat(),
        "previous_date": previous.created_at.isoformat(),
        "changes": changes,
    }
