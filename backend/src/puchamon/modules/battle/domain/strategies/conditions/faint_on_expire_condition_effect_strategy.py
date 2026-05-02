"""Strategy for `faint_on_expire` condition effects."""

from .pending import PendingConditionEffectStrategy


class FaintOnExpireConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "faint_on_expire"
    hook = "on_expire"
