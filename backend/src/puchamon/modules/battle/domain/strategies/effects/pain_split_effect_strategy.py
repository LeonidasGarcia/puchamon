"""Strategy for `pain_split` move effects."""

from .pending import PendingMoveEffectStrategy


class PainSplitEffectStrategy(PendingMoveEffectStrategy):
    kind = "pain_split"
