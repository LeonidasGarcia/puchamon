"""Strategy for `end_turn_bad_poison_damage` condition effects."""

from math import floor

from .....pokedex.domain.entities.conditions import BadPoisonEffect
from ...mechanics import faint_instance
from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput
from ...utils import format_pokemon_name
from .base import ConditionEffectStrategy


class BadPoisonConditionEffectStrategy(ConditionEffectStrategy):
    kind = "end_turn_bad_poison_damage"
    hook = "end_turn"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Apply progressive damage at the end of the turn from Bad Poison (Toxic)."""
        if not isinstance(execution.effect, BadPoisonEffect):
            return

        instance = context.get_instance(execution.holder_instance_id)
        if instance.fainted or instance.current_hp <= 0:
            return

        payload = execution.effect.payload

        # TODO: Implement progressive damage multiplier (N * base_ratio)
        # Currently BattleInstance doesn't store the number of turns the status has been active.
        # For now, we use the base_ratio (1/16).
        damage = max(1, floor(instance.max_hp * payload.base_ratio))
        applied_damage = min(instance.current_hp, damage)
        instance.current_hp -= applied_damage

        context.add_event(
            kind="condition_damage",
            message=f"{format_pokemon_name(instance.pokemon_id)} was hurt by toxic poison!",
            target_instance_id=instance.id,
            condition_id=execution.condition.id,
            value=applied_damage,
        )

        if instance.current_hp == 0:
            faint_instance(context, instance)
