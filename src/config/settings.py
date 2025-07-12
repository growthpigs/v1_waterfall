"""
Application Settings
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    supabase_url: str = Field("", env="SUPABASE_URL")
    supabase_key: str = Field("", env="SUPABASE_KEY")
    
    # API
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()


# Global settings instance
settings = get_settings()