"""Shared placeholder for weather effect strategies pending implementation."""

from ...exceptions import BattleValidationError
from ...runtime import BattleStrategyContext, WeatherEffectExecutionInput
from .base import WeatherEffectStrategy


class PendingWeatherEffectStrategy(WeatherEffectStrategy):
    """Shared placeholder for weather effects that are not implemented yet."""

    kind: str
    hook: str

    def apply(self, _context: BattleStrategyContext, execution: WeatherEffectExecutionInput) -> None:
        """Guard effect dispatch while the concrete logic is still pending."""
        if execution.effect.kind != self.kind:
            raise BattleValidationError(f"{self.__class__.__name__} cannot apply weather effect kind '{execution.effect.kind}'")

        raise NotImplementedError(f"Weather effect strategy '{self.kind}' is not implemented yet")
