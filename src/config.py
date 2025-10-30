"""Configuration management for WhatsApp Connect service."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Whapi Configuration
    whapi_api_token: str
    whapi_api_url: str = "https://gate.whapi.cloud"
    whapi_channel_id: str
    whatsapp_number: str

    # Backend API Configuration
    backend_api_url: str = "http://localhost:8000"

    # Database Configuration
    database_url: str

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"

    # Session Configuration
    session_timeout_hours: int = 24
    reminder_delay_hours: int = 2
    max_resume_hours: int = 48

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8765
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
