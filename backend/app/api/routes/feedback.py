from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from app.api.deps import get_current_user, get_db
from app.models import User, FeedbackMessage

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
