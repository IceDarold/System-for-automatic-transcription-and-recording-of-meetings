from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, field_validator
import secrets
import os
from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str = "Meeting Transcription System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT Settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "meeting_system"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Model API settings
    MODEL_API_URL: str = "http://model-api:8000"  # Default for Docker
    MODEL_API_TIMEOUT: int = 300  # 5 minutes timeout for long-running tasks

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}?client_encoding=utf8"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding='utf-8'
    )


settings = Settings() 