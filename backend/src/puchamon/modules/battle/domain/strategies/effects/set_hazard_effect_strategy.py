"""Strategy for `set_hazard` move effects."""

from .pending import PendingMoveEffectStrategy


class SetHazardEffectStrategy(PendingMoveEffectStrategy):
    kind = "set_hazard"
