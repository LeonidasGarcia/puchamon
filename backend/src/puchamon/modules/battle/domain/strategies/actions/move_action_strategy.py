"""Strategy for executing move actions."""

from ...exceptions import BattleValidationError
from ..context import ActionExecutionInput, BattleStrategyContext
from .base import ActionStrategy


class MoveActionStrategy(ActionStrategy):
    """Execute a turn action whose type is `move`."""

    action_type = "move"

    def execute(self, context: BattleStrategyContext, execution: ActionExecutionInput) -> None:
        """Resolve a move action against the current mutable battle state."""
        if execution.action.type != self.action_type:
            raise BattleValidationError(f"MoveActionStrategy cannot execute action type '{execution.action.type}'")

        raise NotImplementedError("Move action resolution is not implemented yet")
