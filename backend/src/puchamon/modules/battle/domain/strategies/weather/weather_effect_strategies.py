"""Concrete weather effect strategies keyed by `WeatherEffect.kind`."""

from .base import WeatherEffectStrategy
from ..context import BattleStrategyContext, WeatherEffectExecutionInput
from ...exceptions import BattleValidationError


class PendingWeatherEffectStrategy(WeatherEffectStrategy):
    """Shared placeholder for weather effects that are not implemented yet."""

    kind: str
    hook: str

    def apply(self, context: BattleStrategyContext, execution: WeatherEffectExecutionInput) -> None:
        """Guard effect dispatch while the concrete logic is still pending."""
        if execution.effect.kind != self.kind:
            raise BattleValidationError(f"{self.__class__.__name__} cannot apply weather effect kind '{execution.effect.kind}'")

        raise NotImplementedError(f"Weather effect strategy '{self.kind}' is not implemented yet")


class TypePowerModifierWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "type_power_modifier"
    hook = "modify_damage"


class MoveAccuracyOverrideWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "move_accuracy_override"
    hook = "modify_accuracy"


class MoveChargeModifierWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "move_charge_modifier"
    hook = "modify_charge"


class MoveChargeOverrideWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "move_charge_override"
    hook = "modify_charge"


class EndTurnDamageWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "end_turn_damage"
    hook = "end_turn"


class SpecialDefenseModifierWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "special_defense_modifier"
    hook = "modify_special_defense"
