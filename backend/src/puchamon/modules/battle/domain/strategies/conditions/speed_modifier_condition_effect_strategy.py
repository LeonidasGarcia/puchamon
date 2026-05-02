"""Strategy for `speed_modifier` condition effects."""

from .pending import PendingConditionEffectStrategy


class SpeedModifierConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "speed_modifier"
    hook = "modify_speed"
