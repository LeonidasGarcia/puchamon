"""Strategy for `end_turn_damage` weather effects."""

from .pending import PendingWeatherEffectStrategy


class EndTurnDamageWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "end_turn_damage"
    hook = "end_turn"
