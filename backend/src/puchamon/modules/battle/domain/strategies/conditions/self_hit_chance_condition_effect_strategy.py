"""Strategy for `self_hit_chance` condition effects."""

from .pending import PendingConditionEffectStrategy


class SelfHitChanceConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "self_hit_chance"
    hook = "before_action"
