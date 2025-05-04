from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import EmailStr, validator
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

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, any]) -> any:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    class Config:
        case_sensitive = True
        # Находим корневую директорию проекта
        root_dir = Path(__file__).parent.parent.parent
        # Путь к глобальному .env файлу
        env_file = str(root_dir / ".env")
        # Проверяем существование файла
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"Configuration file not found: {env_file}")


settings = Settings() 