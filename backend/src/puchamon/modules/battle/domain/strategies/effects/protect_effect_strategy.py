"""Strategy for `protect` move effects."""

from .pending import PendingMoveEffectStrategy


class ProtectEffectStrategy(PendingMoveEffectStrategy):
    kind = "protect"
