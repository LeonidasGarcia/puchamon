"""Error handlers personalizated to the application."""
import contextlib

from fastapi import Request, WebSocket, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.datastructures import State

from ...core.domain import AppError


async def _handle_websocket_error(request: Request, exc: Exception, close_code: int = 1011) -> bool:
    """Handle WebSocket errors by closing the connection properly."""
    if request.scope.get("type") == "websocket":
        logger.error(f"Error en WebSocket (Code {close_code}): {exc}", exc_info=exc)
        with contextlib.suppress(Exception):
            # Casting to WebSocket for correct type checking on .close()
            websocket: WebSocket[State] = WebSocket(request.scope, receive=request.receive, send=request._send)
            await websocket.close(code=close_code, reason="Error interno en el motor de batalla.")
        return True
    return False


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse | None:
    """Error handler for custom application exceptions."""
    if await _handle_websocket_error(request, exc):
        return None

    request_id = getattr(request.state, "request_id", "unknown")

    log_msg = f"[{request_id}] {exc.__class__.__name__}: {exc.message}"
    if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.error(log_msg)
    else:
        logger.warning(log_msg)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "type": exc.__class__.__name__,
            "message": exc.message,
            "request_id": request_id,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse | None:
    """Error handler for HTTP exceptions."""
    if await _handle_websocket_error(request, exc, close_code=1000):
        return None

    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"[{request_id}] HTTP/Validation Error: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "type": "FrameworkError",
            "message": exc.detail,
            "request_id": request_id,
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse | None:
    """Global error handler for unhandled exceptions.

    Handles both HTTP and WebSocket connections properly.
    For WebSocket, closes the connection with code 1011 (Unexpected Error).
    """
    if await _handle_websocket_error(request, exc):
        return None

    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(f"[{request_id}] Unhandled Server Error")

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "type": "InternalServerError",
            "message": "Ocurrió un error inesperado en los servidores de Puchamon.",
            "request_id": request_id,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse | None:
    """Error handler for validation exceptions."""
    if await _handle_websocket_error(request, exc):
        return None

    request_id = getattr(request.state, "request_id", "unknown")
    errors = exc.errors()
    error_messages = []

    for err in errors:
        field = " -> ".join([str(x) for x in err.get("loc", [])])
        error_messages.append(f"{field}: {err.get('msg')}")

    detalles_log = " | ".join(error_messages)
    logger.warning(f"[{request_id}] Validation Error: {detalles_log}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "type": "ValidationError",
            "message": "Los datos enviados en la petición no son válidos.",
            "details": error_messages,
            "request_id": request_id,
        },
    )
