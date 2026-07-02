"""Application configuration loaded from environment variables.

All secrets and environment-specific values MUST come from environment
variables / the .env file. Nothing is hardcoded here.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings, populated from the process environment."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- LLM provider abstraction ---
    # Which provider implementation to instantiate. Switching this single
    # value (and the matching API key) changes the LLM backend with zero
    # code changes.
    llm_provider: str = Field(default="gemini")

    gemini_api_key: str | None = Field(default=None)
    gemini_model: str = Field(default="gemini-2.5-flash")

    openai_api_key: str | None = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")

    groq_api_key: str | None = Field(default=None)
    groq_model: str = Field(default="llama-3.3-70b-versatile")

    # --- Database ---
    database_url: str

    # --- CORS ---
    cors_origins: str = Field(default="*")

    # --- Logging ---
    log_level: str = Field(default="INFO")

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
