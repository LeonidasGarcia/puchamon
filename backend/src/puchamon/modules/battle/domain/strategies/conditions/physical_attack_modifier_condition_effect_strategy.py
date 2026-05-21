"""Strategy for `physical_attack_modifier` condition effects."""

import math

from .....pokedex.domain.entities.conditions import PhysicalAttackModifierEffect
from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput
from .base import ConditionEffectStrategy


class PhysicalAttackModifierConditionEffectStrategy(ConditionEffectStrategy):
    kind = "physical_attack_modifier"
    hook = "modify_damage"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Apply damage modification if the move is physical."""
        if not isinstance(execution.effect, PhysicalAttackModifierEffect):
            return

        if not execution.movement or execution.movement.category != "physical":
            return

        if "current_damage" not in context.transient:
            return

        multiplier = execution.effect.payload.multiplier
        current_damage = context.transient["current_damage"]

        context.transient["current_damage"] = max(1, math.floor(current_damage * multiplier))
