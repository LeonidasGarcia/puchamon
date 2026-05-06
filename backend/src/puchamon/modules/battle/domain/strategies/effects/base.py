"""Base interfaces for move effect strategies."""

from abc import ABC, abstractmethod

from ...runtime import BattleStrategyContext, MoveEffectExecutionInput


class MoveEffectStrategy(ABC):
    """Strategy interface for applying a move effect kind."""

    kind: str

    @abstractmethod
    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Apply the effect against the mutable battle context."""
