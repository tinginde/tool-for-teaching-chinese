"""
Configuration settings for the FastAPI application.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "華語教材智能生成器"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # Anthropic Claude API
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_MAX_TOKENS: int = 4096

    # Generation Settings
    DEFAULT_ARTICLE_LENGTH: int = 400
    MIN_ARTICLE_LENGTH: int = 300
    MAX_ARTICLE_LENGTH: int = 600
    DEFAULT_QUESTION_COUNT: int = 5

    # Validation Settings
    VOCABULARY_ACCURACY_TARGET: float = 1.0  # 100%
    GRAMMAR_ACCURACY_TARGET: float = 0.9     # 90%

    # Database (for future use)
    DATABASE_URL: str = "sqlite+aiosqlite:///./chinese_teaching_tool.db"

    # Redis (for future use)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Rate Limiting (for future use)
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience function
def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from settings."""
    settings = get_settings()
    return settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
