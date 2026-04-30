"""Strategy for executing switch actions."""

from .base import ActionStrategy
from ..context import ActionExecutionInput, BattleStrategyContext
from ...exceptions import BattleValidationError


class SwitchActionStrategy(ActionStrategy):
    """Execute a turn action whose type is `switch`."""

    action_type = "switch"

    def execute(self, context: BattleStrategyContext, execution: ActionExecutionInput) -> None:
        """Resolve a switch action against the current mutable battle state."""
        if execution.action.type != self.action_type:
            raise BattleValidationError(f"SwitchActionStrategy cannot execute action type '{execution.action.type}'")

        raise NotImplementedError("Switch action resolution is not implemented yet")
