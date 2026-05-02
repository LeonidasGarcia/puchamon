"""Strategy for `skip_action` condition effects."""

from .pending import PendingConditionEffectStrategy


class SkipActionConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "skip_action"
    hook = "before_action"
