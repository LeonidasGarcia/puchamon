"""Strategy for `apply_volatile_status` move effects."""

from .pending import PendingMoveEffectStrategy


class ApplyVolatileStatusEffectStrategy(PendingMoveEffectStrategy):
    kind = "apply_volatile_status"
