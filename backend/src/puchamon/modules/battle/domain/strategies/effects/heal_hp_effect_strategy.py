"""Strategy for `heal_hp` move effects."""

from .pending import PendingMoveEffectStrategy


class HealHpEffectStrategy(PendingMoveEffectStrategy):
    kind = "heal_hp"
