from typing import Optional
from pydantic import BaseModel


class TelegramAuthRequest(BaseModel):
    init_data: str


class TelegramAuthResponse(BaseModel):
    token: str
    user: dict


class UserOut(BaseModel):
    id: int
    telegram_user_id: str
    username: Optional[str]
    first_name: Optional[str]
    timezone: str = 'UTC'
