from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, field_validator, model_validator, ValidationInfo
import secrets
import os
from pathlib import Path

# Загружаем APP_ENV из os.environ СНАЧАЛА, чтобы определить, какой .env файл использовать.
# Это нужно сделать до того, как pydantic-settings попытается автоматически загрузить .env файлы.
# python-dotenv можно использовать здесь, если APP_ENV задан в каком-то "мета" .env файле,
# или мы ожидаем, что APP_ENV будет системной переменной.
# Для простоты, предположим, что APP_ENV может быть системной переменной.
# Либо, мы можем загрузить "базовый" .env, который содержит только APP_ENV.

# Determine .env files to load based on APP_ENV
APP_ENV_VALUE = os.getenv("APP_ENV", "development") # Default to "development"
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

env_files_to_load = []
default_env_path = _PROJECT_ROOT / ".env"
if default_env_path.exists():
    env_files_to_load.append(default_env_path)

if APP_ENV_VALUE == "test":
    test_env_path = _PROJECT_ROOT / ".env.test"
    if test_env_path.exists():
        env_files_to_load.append(test_env_path) # .env.test loads after .env and overrides its values
elif APP_ENV_VALUE == "production":
    prod_env_path = _PROJECT_ROOT / ".env.prod"
    if prod_env_path.exists():
        env_files_to_load.append(prod_env_path)
# Add other environments here if needed (e.g., "staging")

class Settings(BaseSettings):
    APP_ENV: str = "development" # Default value if not set in .env

    PROJECT_NAME: str = "Meeting Transcription System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT Settings
    SECRET_KEY: str = "default_unsafe_secret" # Default unsafe value, ensure it's overridden in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database connection components
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "meeting_system"
    POSTGRES_PORT: str = "5432" # Added POSTGRES_PORT for explicit DSN construction
    # For test/production, these values will be sourced from .env.test or .env.prod

    DATABASE_URL: Optional[str] = None # Assembled by validator if not provided directly

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"
    LOG_ROTATION_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
    LOG_ROTATION_BACKUP_COUNT: int = 5
    LOG_FORMAT: str = "json" # "text" or "json"

    # Model API settings
    MODEL_API_URL: str = "http://model-api:8000"
    MODEL_API_TIMEOUT: int = 300

    # Storage settings
    STORAGE_DIR: str = "storage"

    # File upload settings
    ALLOWED_AUDIO_MIME_TYPES: List[str] = [
        "audio/mpeg", # .mp3
        "audio/wav",  # .wav
        "audio/ogg",  # .ogg
        "audio/aac",  # .aac
        "audio/flac", # .flac
        "audio/x-m4a" # .m4a
    ]
    MAX_AUDIO_FILE_SIZE_MB: int = 500  # Max size in Megabytes

    ALLOWED_UPLOAD_PREFIXES: List[str] = ["audio/", "video/"] # For general upload validation by prefix

    @field_validator('SECRET_KEY')
    def check_secret_key_production(cls, v, info):
        if info.data.get('APP_ENV') == 'production' and v == "default_unsafe_secret":
            raise ValueError("CRITICAL: Default SECRET_KEY is used in production environment!")
        return v

    # Assembles DATABASE_URL from components if not explicitly provided in .env files.
    @model_validator(mode="before")
    @classmethod
    def assemble_db_connection(cls, data: Dict[str, Any], info: ValidationInfo) -> Dict[str, Any]:
        # 'data' is the dictionary of all raw values passed to the model.
        
        # Check if DATABASE_URL is already provided in 'data' and is a non-empty string.
        database_url_from_data = data.get("DATABASE_URL")
        if isinstance(database_url_from_data, str) and database_url_from_data.strip():
            # If DATABASE_URL is explicitly provided and valid, return 'data' as is.
            return data

        # If DATABASE_URL is not set, is None, or is an empty string, try to assemble it.
        # Components are sourced from 'data'.
        user = data.get("POSTGRES_USER")
        password = data.get("POSTGRES_PASSWORD")
        server = data.get("POSTGRES_SERVER")
        db_name = data.get("POSTGRES_DB")
        port = data.get("POSTGRES_PORT", "5432") # Default to '5432' if POSTGRES_PORT is not specified.

        if not all([user, password, server, db_name]): # Port has a default
            # This condition implies that DATABASE_URL was not provided (or was invalid)
            # AND essential components for assembly are missing.
            raise ValueError(
                "DATABASE_URL is not set or is invalid, and essential components "
                "(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_SERVER, POSTGRES_DB) "
                "for assembling it are missing."
            )
        
        # Assemble the DSN.
        assembled_url = f"postgresql://{user}:{password}@{server}:{port}/{db_name}?client_encoding=utf8"
        
        # Update the 'data' dictionary with the assembled DATABASE_URL.
        data["DATABASE_URL"] = assembled_url
        return data # Return the modified dictionary.

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=env_files_to_load if env_files_to_load else None, # Dynamically determined list of .env files
        env_file_encoding='utf-8',
        extra='ignore' # Ignore extra variables in .env files
    )

# Settings instance is created using the .env files determined by APP_ENV.
settings = Settings()
# Теперь при создании settings, он будет использовать os.environ, который
# в тестах будет предварительно настроен conftest.py (через .env.test и override=True),
# а в прод/дев окружении - main.py (через .env основного проекта). 