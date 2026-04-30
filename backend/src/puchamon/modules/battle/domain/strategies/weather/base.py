"""Base interfaces for weather effect strategies."""

from abc import ABC, abstractmethod

from ..context import BattleStrategyContext, StrategyHook, WeatherEffectExecutionInput


class WeatherEffectStrategy(ABC):
    """Strategy interface for applying a weather effect hook."""

    kind: str
    hook: StrategyHook

    @abstractmethod
    def apply(self, context: BattleStrategyContext, execution: WeatherEffectExecutionInput) -> None:
        """Apply the weather effect against the mutable battle context."""
