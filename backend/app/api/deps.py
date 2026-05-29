from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import get_db
from app.config import settings
from app.models import User

security = HTTPBearer(auto_error=False)


def get_current_user_mock(db: Session = Depends(get_db)) -> User:
    """Mock auth for MVP: returns test user or creates one."""
    user = db.query(User).filter(User.telegram_user_id == "mock_user").first()
    if not user:
        user = User(
            telegram_user_id="mock_user",
            username="mock",
            first_name="Mock",
            timezone="UTC",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """JWT auth - used when telegram_auth_mock is false."""
    if settings.telegram_auth_mock:
        return get_current_user_mock(db)

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        telegram_user_id: str = payload.get("sub")
        if telegram_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
