"""Strategy for `end_turn_bad_poison_damage` condition effects."""

from .pending import PendingConditionEffectStrategy


class BadPoisonConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "end_turn_bad_poison_damage"
    hook = "end_turn"
