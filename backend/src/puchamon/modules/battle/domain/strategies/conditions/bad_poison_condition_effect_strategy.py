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
        if instance.fainted or instance.current_hp <= 0 or not instance.status:
            return

        payload = execution.effect.payload

        # Number of turns the status has been active
        turns_active = instance.turn_counters.get(instance.status, 1)

        damage = max(1, floor(instance.max_hp * (payload.base_ratio * turns_active)))
        applied_damage = min(instance.current_hp, damage)
        instance.current_hp -= applied_damage

        context.add_event(
            kind="condition_damage",
            message=f"{format_pokemon_name(instance.pokemon_id)} was hurt by toxic poison!",
            target_instance_id=str(instance.id),
            condition_id=execution.condition.id,
            value=applied_damage,
        )

        if instance.current_hp == 0:
            faint_instance(context, instance)
        else:
            instance.turn_counters[instance.status] = turns_active + 1
