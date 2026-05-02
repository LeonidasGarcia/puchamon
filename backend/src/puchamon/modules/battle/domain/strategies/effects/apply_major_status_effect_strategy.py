"""Strategy for `apply_major_status` move effects."""

from .pending import PendingMoveEffectStrategy


class ApplyMajorStatusEffectStrategy(PendingMoveEffectStrategy):
    kind = "apply_major_status"
