"""Shared placeholder for move effect strategies pending implementation."""

from ...exceptions import BattleValidationError
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from .base import MoveEffectStrategy


class PendingMoveEffectStrategy(MoveEffectStrategy):
    """Shared placeholder for move effect kinds that are not implemented yet."""

    kind: str

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:  # noqa: ARG002
        """Guard effect dispatch while the concrete logic is still pending."""
        if execution.effect.kind != self.kind:
            raise BattleValidationError(f"{self.__class__.__name__} cannot apply move effect kind '{execution.effect.kind}'")

        raise NotImplementedError(f"Move effect strategy '{self.kind}' is not implemented yet")
