"""Main entry point for the Puchamon application."""

from fastapi import FastAPI
from loguru import logger
from uvicorn import run

from .shared import settings, setup

setup()

try:
    from .factory import create

    app: FastAPI = create()
except Exception as e:
    logger.exception("Error al crear la aplicación FastAPI: {}", e)
    raise


def main():
    """Principal function to run the application."""
    run(app="puchamon.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG, log_config=None)
