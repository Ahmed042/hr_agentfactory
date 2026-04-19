import secrets
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # API Keys
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7

    # Email SMTP
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""
    EMAIL_FROM: str = ""

    # Google Calendar
    GOOGLE_CREDENTIALS_FILE: str = ""

    # App
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "auto-generate-on-first-run"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET: str = ""

    model_config = {"env_file": ".env"}

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()

# Auto-generate SECRET_KEY if not set properly
if settings.SECRET_KEY in ("auto-generate-on-first-run", "change-this-in-production", "your-super-secret-key-change-this-in-production"):
    settings.SECRET_KEY = secrets.token_urlsafe(64)
