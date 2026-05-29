from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.services.telegram_auth import validate_telegram_init_data, create_jwt_token
from app.models import User, UserSettings
from app.schemas.auth import TelegramAuthRequest, TelegramAuthResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=TelegramAuthResponse)
def auth_telegram(
    auth_data: TelegramAuthRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user via Telegram Mini App init_data.
    Creates user and settings if not exists.
    """
    # Validate init data
    user_info = validate_telegram_init_data(auth_data.init_data)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram init data",
        )

    telegram_user_id = user_info['telegram_user_id']

    # Find or create user
    user = db.query(User).filter(
        User.telegram_user_id == telegram_user_id
    ).first()

    if not user:
        user = User(
            telegram_user_id=telegram_user_id,
            username=user_info.get('username'),
            first_name=user_info.get('first_name'),
            last_name=user_info.get('last_name'),
            language_code=user_info.get('language_code'),
            timezone='UTC',
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create default settings
        settings = UserSettings(
            user_id=user.id,
            reminder_enabled=False,
            reminder_timezone='UTC',
            soft_language_enabled=True,
        )
        db.add(settings)
        db.commit()

    # Create JWT token
    token = create_jwt_token(telegram_user_id)

    return TelegramAuthResponse(
        token=token,
        user={
            'id': user.id,
            'telegram_user_id': user.telegram_user_id,
            'username': user.username,
            'first_name': user.first_name,
        },
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return {
        'id': current_user.id,
        'telegram_user_id': current_user.telegram_user_id,
        'username': current_user.username,
        'first_name': current_user.first_name,
        'timezone': current_user.timezone,
    }
