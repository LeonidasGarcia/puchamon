"""Shared placeholder for condition effect strategies pending implementation."""

from ...exceptions import BattleValidationError
from ..context import BattleStrategyContext, ConditionEffectExecutionInput
from .base import ConditionEffectStrategy


class PendingConditionEffectStrategy(ConditionEffectStrategy):
    """Shared placeholder for condition effects that are not implemented yet."""

    kind: str
    hook: str

    def apply(self, _context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Guard effect dispatch while the concrete logic is still pending."""
        if execution.effect.kind != self.kind:
            raise BattleValidationError(f"{self.__class__.__name__} cannot apply condition effect kind '{execution.effect.kind}'")

        raise NotImplementedError(f"Condition effect strategy '{self.kind}' is not implemented yet")
