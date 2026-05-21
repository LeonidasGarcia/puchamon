"""Strategy for `full_paralysis_chance` condition effects."""

import random

from .....pokedex.domain.entities.conditions import FullParalysisChanceEffect
from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput
from ...utils import format_pokemon_name
from .base import ConditionEffectStrategy


class FullParalysisChanceConditionEffectStrategy(ConditionEffectStrategy):
    kind = "full_paralysis_chance"
    hook = "before_action"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Apply full paralysis chance that may block a move."""
        if not isinstance(execution.effect, FullParalysisChanceEffect):
            return

        instance = context.get_instance(execution.holder_instance_id)
        if instance.fainted or instance.current_hp <= 0:
            return

        chance = execution.effect.payload.chance / 100.0

        if random.random() < chance:
            context.mark_action_blocked(execution.holder_instance_id, self.kind)
            context.add_event(
                kind="action_skipped",
                message=f"{format_pokemon_name(instance.pokemon_id)} is paralyzed! It can't move!",
                target_instance_id=str(instance.id),
                condition_id=execution.condition.id,
            )
