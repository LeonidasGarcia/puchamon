"""Custom exceptions for battle-related logic."""

from ....core.domain import (
    BadGatewayError,
    ConflictError,
    ForbiddenError,
    GatewayTimeoutError,
    InternalServerError,
    NotFoundError,
    ServiceUnavailableError,
    UnauthorizedError,
    ValidationError,
)


class BattleNotFoundError(NotFoundError):
    """Exception for when a battle is not found."""

    def __init__(self, message: str = "Battle not found"):
        super().__init__(message)


class BattleValidationError(ValidationError):
    """Exception for when battle data is invalid."""

    def __init__(self, message: str = "Invalid battle data"):
        super().__init__(message)


class BattleConflictError(ConflictError):
    """Exception for when there is a conflict in battle state."""

    def __init__(self, message: str = "Battle state conflict"):
        super().__init__(message)


class BattleUnauthorizedError(UnauthorizedError):
    """Exception for when the user is not authorized to perform a battle action."""

    def __init__(self, message: str = "Unauthorized to perform this battle action"):
        super().__init__(message)


class BattleForbiddenError(ForbiddenError):
    """Exception for when the user does not have permission to perform a battle action."""

    def __init__(self, message: str = "Forbidden to perform this battle action"):
        super().__init__(message)


class BattleInternalServerError(InternalServerError):
    """Exception for when there is an internal server error during battle processing."""

    def __init__(self, message: str = "Internal server error during battle processing"):
        super().__init__(message)


class BattleServiceUnavailableError(ServiceUnavailableError):
    """Exception for when the battle service is unavailable."""

    def __init__(self, message: str = "Battle service is currently unavailable"):
        super().__init__(message)


class BattleGatewayTimeoutError(GatewayTimeoutError):
    """Exception for when the battle service times out."""

    def __init__(self, message: str = "Battle service timed out"):
        super().__init__(message)


class BattleBadGatewayError(BadGatewayError):
    """Exception for when there is a bad gateway error during battle processing."""

    def __init__(self, message: str = "Bad gateway error during battle processing"):
        super().__init__(message)
