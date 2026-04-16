"""Configuration settings for the application."""

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the application."""

    PROJECT_NAME: str = "PUCHAMON"
    LOG_LEVEL: str = "DEBUG"
    GLOBAL_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    DEBUG: bool = Field(default=False)

    DATABASE_URI: str | None = Field(default=..., env="DATABASE_URI")
    DATABASE_NAME: str | None = Field(default=..., env="DATABASE_NAME")

    DATABASE_POOL_SIZE: int = Field(default=5)
    DATABASE_MAX_OVERFLOW: int = Field(default=5)
    DATABASE_POOL_TIMEOUT: int = Field(default=15)
    DATABASE_POOL_RECYCLE: int = Field(default=1800)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Error de validación en la configuración: {e}") from e
