from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models import User, UserSettings
from app.schemas.settings import SettingsUpdate, SettingsOut

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsOut)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        settings = UserSettings(
            user_id=current_user.id,
            reminder_enabled=False,
            reminder_timezone="UTC",
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return SettingsOut(
        reminder_enabled=settings.reminder_enabled,
        reminder_time=settings.reminder_time,
        reminder_timezone=settings.reminder_timezone,
        soft_language_enabled=settings.soft_language_enabled,
    )


@router.patch("", response_model=SettingsOut)
def update_settings(
    update: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)

    return SettingsOut(
        reminder_enabled=settings.reminder_enabled,
        reminder_time=settings.reminder_time,
        reminder_timezone=settings.reminder_timezone,
        soft_language_enabled=settings.soft_language_enabled,
    )
