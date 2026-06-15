"""Configuration settings for the application."""

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the application."""

    PROJECT_NAME: str = "PUCHAMON"
    LOG_LEVEL: str = "DEBUG"
    DEBUG: bool = False

    DATABASE_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "puchamon"

    MINIMAX_DEPTH: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Error de validación en la configuración: {e}") from e
