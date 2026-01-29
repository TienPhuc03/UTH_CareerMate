from pydantic_settings import BaseSettings
from typing import List, Optional
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
    GEMINI_API_KEY: Optional[str] = None  # ✅ Optional now
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
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:5500,http://127.0.0.1:5500,http://127.0.0.1:5173,http://127.0.0.1:3000"
    
    # Paths
    UPLOAD_DIR: str = "uploads"
    LOG_DIR: str = "logs"

    # Google OAuth (MỚI THÊM VÀO ĐÚNG VỊ TRÍ)
    # Pydantic sẽ tự động lấy từ file .env nếu tên biến trùng khớp
    GOOGLE_CLIENT_ID: str 
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://127.0.0.1:8000/api/Auth/google/callback"
    
    class Config:
        env_file = ".env"      # Chỉ định file chứa biến môi trường
        extra = "ignore"
        case_sensitive = False # Không phân biệt chữ hoa chữ thường (google_client_id vẫn nhận)
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Parse ALLOWED_FILE_TYPES string to list"""
        return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(f"{self.UPLOAD_DIR}/cvs", exist_ok=True)
        os.makedirs(self.LOG_DIR, exist_ok=True)


# Create settings instance
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
    print(f"Gemini API Key: {'✅ Set' if settings.GEMINI_API_KEY else '❌ Not set'}")
    print(f"Allowed Origins: {settings.allowed_origins_list}")
    print("=" * 60)