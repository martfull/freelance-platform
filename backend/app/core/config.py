from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Secure Freelance Marketplace"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = Field(
        default="postgresql://freelance:freelance@localhost:5432/freelance",
        alias="DATABASE_URL",
    )

    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    storage_path: str = Field(default="storage/chunks", alias="STORAGE_PATH")
    default_chunk_size: int = 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
