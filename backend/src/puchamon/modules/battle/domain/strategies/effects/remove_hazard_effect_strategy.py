"""Strategy for `remove_hazard` move effects."""

from .pending import PendingMoveEffectStrategy


class RemoveHazardEffectStrategy(PendingMoveEffectStrategy):
    kind = "remove_hazard"
