"""Strategy for `modify_stat` move effects."""

from .pending import PendingMoveEffectStrategy


class ModifyStatEffectStrategy(PendingMoveEffectStrategy):
    kind = "modify_stat"
