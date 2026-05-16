"""Strategy for `end_turn_damage` condition effects."""

from math import floor

from .....pokedex.domain.entities.conditions import EndTurnDamageEffect
from ...mechanics import faint_instance
from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput
from ...utils import format_pokemon_name
from .base import ConditionEffectStrategy


class EndTurnDamageConditionEffectStrategy(ConditionEffectStrategy):
    kind = "end_turn_damage"
    hook = "end_turn"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Apply damage at the end of the turn from a condition (e.g. Poison, Burn)."""
        if not isinstance(execution.effect, EndTurnDamageEffect):
            return

        instance = context.get_instance(execution.holder_instance_id)
        if instance.fainted or instance.current_hp <= 0:
            return

        payload = execution.effect.payload
        damage = max(1, floor(instance.max_hp * payload.ratio))
        applied_damage = min(instance.current_hp, damage)
        instance.current_hp -= applied_damage

        context.add_event(
            kind="condition_damage",
            message=f"{format_pokemon_name(instance.pokemon_id)} was hurt by its {execution.condition.name}!",
            target_instance_id=str(instance.id),
            condition_id=execution.condition.id,
            value=applied_damage,
        )

        if instance.current_hp == 0:
            faint_instance(context, instance)
