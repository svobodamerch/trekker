from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.api.deps import get_current_user, get_db
from app.models import User, FeedbackMessage
from app.config import settings

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackCreate(BaseModel):
    category: str = Field(default="other", pattern="^(bug|unclear|idea|other)$")
    message: str = Field(min_length=1, max_length=2000)
    source: str = Field(default="mini_app", pattern="^(bot|mini_app)$")


@router.post("", status_code=201)
def create_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fb = FeedbackMessage(
        user_id=current_user.id,
        telegram_user_id=current_user.telegram_user_id,
        category=data.category,
        message=data.message,
        source=data.source,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"status": "saved", "id": fb.id}


@router.get("/admin")
def list_feedback(
    x_admin_secret: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    if not settings.admin_secret or x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Forbidden")
    items = db.query(FeedbackMessage).order_by(FeedbackMessage.created_at.desc()).all()
    return [
        {
            "id": fb.id,
            "telegram_user_id": fb.telegram_user_id,
            "category": fb.category,
            "message": fb.message,
            "source": fb.source,
            "status": fb.status,
            "created_at": fb.created_at.isoformat() if fb.created_at else None,
        }
        for fb in items
    ]
