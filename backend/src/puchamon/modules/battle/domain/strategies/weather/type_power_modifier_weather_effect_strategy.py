"""Strategy for `type_power_modifier` weather effects."""

from .pending import PendingWeatherEffectStrategy


class TypePowerModifierWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "type_power_modifier"
    hook = "modify_damage"
