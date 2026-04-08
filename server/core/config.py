from typing import List, Optional
import os

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
        case_sensitive=False,
    )

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOGIN_RATE_LIMIT_ENABLED: bool = True
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 900

    # AI Service - Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3-flash-preview"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_EXPIRATION: int = 3600

    # Application
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # File Upload
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_FILE_TYPES: str = "pdf,docx,doc"

    # CORS
    ALLOWED_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173,http://localhost:5500,"
        "http://127.0.0.1:5500,http://127.0.0.1:5173,http://127.0.0.1:3000"
    )

    # Paths
    UPLOAD_DIR: str = "uploads"
    LOG_DIR: str = "logs"

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://127.0.0.1:8000/api/Auth/google/callback"
    GOOGLE_OAUTH_SUCCESS_REDIRECT_URL: str = "http://127.0.0.1:5500/client/page/Homepage.html"

    @field_validator("DATABASE_URL", "REDIS_URL", "ALLOWED_ORIGINS", mode="before")
    @classmethod
    def strip_string_settings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_value(cls, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return False

        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
            return False
        return value

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string to list."""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Parse ALLOWED_FILE_TYPES string to list."""
        return [file_type.strip() for file_type in self.ALLOWED_FILE_TYPES.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT.lower() == "production"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(f"{self.UPLOAD_DIR}/cvs", exist_ok=True)
        os.makedirs(self.LOG_DIR, exist_ok=True)


settings = Settings()


def display_settings():
    """Display current settings."""
    print("=" * 60)
    print("CAREERMATE - APPLICATION SETTINGS")
    print("=" * 60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Database: {settings.DATABASE_URL.split('@')[-1]}")
    print(f"Redis: {settings.REDIS_URL}")
    print(f"AI Model: {settings.GEMINI_MODEL}")
    print(f"Gemini API Key: {'Set' if settings.GEMINI_API_KEY else 'Not set'}")
    print(f"Allowed Origins: {settings.allowed_origins_list}")
    print(f"Google Redirect URI: {settings.GOOGLE_REDIRECT_URI}")
    print(f"Google Success Redirect: {settings.GOOGLE_OAUTH_SUCCESS_REDIRECT_URL}")
    print(
        "Login Rate Limit: "
        f"{settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS} attempts / "
        f"{settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS}s "
        f"(enabled={settings.LOGIN_RATE_LIMIT_ENABLED})"
    )
    print("=" * 60)
