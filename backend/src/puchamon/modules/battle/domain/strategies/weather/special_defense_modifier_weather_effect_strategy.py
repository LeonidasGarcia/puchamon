"""Strategy for `special_defense_modifier` weather effects."""

from .pending import PendingWeatherEffectStrategy


class SpecialDefenseModifierWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "special_defense_modifier"
    hook = "modify_special_defense"
