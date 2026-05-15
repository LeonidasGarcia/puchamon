"""Strategy for `speed_modifier` condition effects."""

import math

from ...exceptions import BattleValidationError
from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput
from .base import ConditionEffectStrategy


class SpeedModifierConditionEffectStrategy(ConditionEffectStrategy):
    """Strategy that modifies the effective speed of a pokemon based on a condition."""

    kind = "speed_modifier"
    hook = "modify_speed"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Applies a speed modifier from a condition (like Paralysis)."""
        if execution.effect.kind != self.kind:
            raise BattleValidationError(f"{self.__class__.__name__} cannot apply condition effect kind '{execution.effect.kind}'")

        # The effective speed is passed via the transient dict in the context
        if "current_speed" not in context.transient:
            return

        current_speed = context.transient["current_speed"]

        # Expected payload format is MultiplierPayload (which has a 'multiplier' attribute)
        payload = execution.effect.payload
        multiplier = getattr(payload, "multiplier", 1.0)

        context.transient["current_speed"] = math.floor(current_speed * multiplier)
