import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Inkloom AI"
    TAGLINE: str = "Intelligent Brand Governance Platform"
    API_V1_PREFIX: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "change-me-in-production-inkloom-secret-key-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database (Render PostgreSQL or local SQLite for development)
    DATABASE_URL: str = "sqlite:///./inkloom_dev.db"
    
    # OpenRouter & NVIDIA Nemotron
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    NEMOTRON_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    
    # Frontend CORS
    FRONTEND_URL: str = "http://localhost:5173"
    ADDITIONAL_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://inkloom.vercel.app"
    ]
    
    # Max file upload size in bytes (15 MB)
    MAX_UPLOAD_SIZE: int = 15 * 1024 * 1024
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> List[str]:
        origins = list(set([self.FRONTEND_URL] + self.ADDITIONAL_CORS_ORIGINS))
        return [o.rstrip("/") for o in origins if o]

    @property
    def is_postgres(self) -> bool:
        return "postgresql" in self.DATABASE_URL.lower()

settings = Settings()
