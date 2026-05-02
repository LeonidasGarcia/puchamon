"""Strategy for `end_turn_damage` condition effects."""

from .pending import PendingConditionEffectStrategy


class EndTurnDamageConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "end_turn_damage"
    hook = "end_turn"
