"""Base interfaces for battle action strategies."""

from abc import ABC, abstractmethod

from ..context import ActionExecutionInput, BattleStrategyContext


class ActionStrategy(ABC):
    """Strategy interface for resolving a battle turn action."""

    action_type: str

    @abstractmethod
    def execute(self, context: BattleStrategyContext, execution: ActionExecutionInput) -> None:
        """Execute a specific turn action against the mutable battle context."""
