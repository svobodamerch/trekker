import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./app.db"
    jwt_secret: str = "change-me"
    bot_token: str = ""
    mini_app_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"
    telegram_auth_mock: bool = True
    ai_api_key: str = ""
    ai_model: str = ""
    cors_origins: str = ""
    admin_secret: str = ""
    groq_api_key: str = ""  # For Whisper voice transcription

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
