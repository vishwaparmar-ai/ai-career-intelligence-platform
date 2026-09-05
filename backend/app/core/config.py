"""
Centralized app configuration. Never hardcode secrets or connection strings
elsewhere in the codebase — read them through Settings.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = (
        "postgresql+asyncpg://user:password@localhost:5432/career_intelligence"
    )

    # Redis / background jobs
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60

    # LLM provider
    llm_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"

    # Observability
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
