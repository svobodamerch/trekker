import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str = ""
    mini_app_url: str = "http://localhost:5173"
    api_base_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
