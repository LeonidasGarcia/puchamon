"""Strategy for `full_paralysis_chance` condition effects."""

from .pending import PendingConditionEffectStrategy


class FullParalysisChanceConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "full_paralysis_chance"
    hook = "before_action"
