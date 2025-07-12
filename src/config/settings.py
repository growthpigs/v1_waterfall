"""
Configuration settings for Brand BOS CIA System.
Manages environment variables and application configuration.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = Field(default="Brand BOS CIA System")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # Supabase
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon/public key")
    supabase_service_key: str = Field(..., description="Supabase service role key")
    
    # AI Services
    anthropic_api_key: str = Field(..., description="Claude API key")
    
    # DataForSEO
    dataforseo_login: str = Field(default="eca1d1f1229a0603")
    dataforseo_password: str = Field(default="team@badaboostadgrants.org")
    
    # Notifications
    slack_webhook_url: Optional[str] = Field(default=None)
    smtp_server: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_username: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    notification_email: str = Field(default="team@badaboostadgrants.org")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379")
    redis_db: int = Field(default=0)
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT encoding")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # Performance
    context_usage_threshold: float = Field(default=0.70)
    max_phase_duration_minutes: int = Field(default=3)
    human_loop_timeout_minutes: int = Field(default=30)
    max_retries: int = Field(default=3)
    retry_delay_seconds: int = Field(default=5)
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment is one of allowed values."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("context_usage_threshold")
    def validate_threshold(cls, v):
        """Validate context usage threshold is between 0 and 1."""
        if not 0 < v < 1:
            raise ValueError("Context usage threshold must be between 0 and 1")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    @property
    def supabase_headers(self) -> dict:
        """Get headers for Supabase API calls."""
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }
    
    @property
    def supabase_service_headers(self) -> dict:
        """Get headers for Supabase service role API calls."""
        return {
            "apikey": self.supabase_service_key,
            "Authorization": f"Bearer {self.supabase_service_key}"
        }


# Global settings instance
settings = Settings()