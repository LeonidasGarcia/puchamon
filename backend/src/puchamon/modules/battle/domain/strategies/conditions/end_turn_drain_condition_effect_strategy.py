"""Strategy for `end_turn_drain` condition effects."""

from .pending import PendingConditionEffectStrategy


class EndTurnDrainConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "end_turn_drain"
    hook = "end_turn"
