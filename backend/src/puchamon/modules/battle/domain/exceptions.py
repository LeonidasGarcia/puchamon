"""Custom exceptions for battle-related logic."""

from ....core.domain import ConflictError, ValidationError


class BattleValidationError(ValidationError):
    """Exception for when battle data is invalid."""

    def __init__(self, message: str = "Invalid battle data"):
        super().__init__(message)


class BattleConflictError(ConflictError):
    """Exception for when there is a conflict in battle state."""

    def __init__(self, message: str = "Battle state conflict"):
        super().__init__(message)
