"""Base interfaces for condition effect strategies."""

from abc import ABC, abstractmethod

from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput, StrategyHook


class ConditionEffectStrategy(ABC):
    """Strategy interface for applying a condition effect hook."""

    kind: str
    hook: StrategyHook

    @abstractmethod
    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Apply the condition effect against the mutable battle context."""
