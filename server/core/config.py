
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Service - Gemini
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
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
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Paths
    UPLOAD_DIR: str = "uploads"
    LOG_DIR: str = "logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(f"{self.UPLOAD_DIR}/cvs", exist_ok=True)
        os.makedirs(self.LOG_DIR, exist_ok=True)


settings = Settings()


def display_settings():
    """Display current settings"""
    print("=" * 60)
    print("🚀 CAREERMATE - APPLICATION SETTINGS")
    print("=" * 60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Database: {settings.DATABASE_URL.split('@')[-1]}")
    print(f"Redis: {settings.REDIS_URL}")
    print(f"AI Model: {settings.GEMINI_MODEL}")
    print(f"Allowed Origins: {settings.allowed_origins_list}")
    print("=" * 60)