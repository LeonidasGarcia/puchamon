"""Factory for creating Puchamon instances."""

from contextlib import asynccontextmanager
from importlib.metadata import version as get_version

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.domain import AppError
from .modules.battle.api.websocket import router as websocket_router
from .shared.api import (
    LoguruMiddleware,
    app_error_handler,
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from .shared.infrastructure import settings
from .shared.infrastructure.database import init_db

__version__: str = get_version(distribution_name="puchamon")


def create() -> FastAPI:
    """Creates and configures the FastAPI application."""

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        """Lifespan context manager for startup and shutdown events."""
        await init_db()
        yield

    app = FastAPI(title=settings.PROJECT_NAME, version=__version__, lifespan=lifespan)

    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(middleware_class=LoguruMiddleware)

    app.add_exception_handler(exc_class_or_status_code=AppError, handler=app_error_handler)  # ty:ignore[invalid-argument-type]
    app.add_exception_handler(exc_class_or_status_code=StarletteHTTPException, handler=http_exception_handler)  # ty:ignore[invalid-argument-type]
    app.add_exception_handler(exc_class_or_status_code=RequestValidationError, handler=validation_exception_handler)  # ty:ignore[invalid-argument-type]
    app.add_exception_handler(exc_class_or_status_code=Exception, handler=global_exception_handler)  # ty:ignore[invalid-argument-type]

    @app.get(path="/")
    def home():
        """Endpoint raíz para verificar que la aplicación está funcionando."""
        return {"message": "¡Bienvenido a Puchamon!", "version": __version__}

    app.include_router(websocket_router)

    return app
