"""Database infrastructure for Puchamon."""

from beanie import init_beanie
from loguru import logger
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from ...core.domain import InternalServerError
from .config import settings


class DatabaseInitializationError(InternalServerError):
    """Raised when the database cannot be initialized."""

    def __init__(self, message: str = "Error al inicializar la base de datos"):
        super().__init__(message)


async def init_db():
    """Initialize the database connection."""
    try:
        client: AsyncMongoClient = AsyncMongoClient(host=settings.DATABASE_URI)
        if not settings.DATABASE_NAME:
            raise DatabaseInitializationError("DATABASE_NAME is not configured")
        await client.admin.command(command="ping")
        database: AsyncDatabase = client[settings.DATABASE_NAME]
        await init_beanie(database=database, document_models=[])
        logger.debug("Database connection established successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        raise DatabaseInitializationError(f"Failed to connect to the database: {e}") from e
