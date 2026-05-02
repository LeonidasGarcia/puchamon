"""Strategy for `self_switch` move effects."""

from .pending import PendingMoveEffectStrategy


class SelfSwitchEffectStrategy(PendingMoveEffectStrategy):
    kind = "self_switch"
