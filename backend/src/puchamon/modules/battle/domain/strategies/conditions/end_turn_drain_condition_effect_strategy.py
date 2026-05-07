"""Strategy for `end_turn_drain` condition effects."""

from math import floor
from typing import TYPE_CHECKING

from .....pokedex.domain.entities.conditions import EndTurnDrainEffect
from ...battlefield import get_active_slot_for_instance, get_side_for_trainer
from ...mechanics import faint_instance
from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput
from ...utils import format_pokemon_name
from .base import ConditionEffectStrategy

if TYPE_CHECKING:
    from ...entities import BattleInstance


class EndTurnDrainConditionEffectStrategy(ConditionEffectStrategy):
    kind = "end_turn_drain"
    hook = "end_turn"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Apply HP drain at the end of the turn (e.g. Leech Seed)."""
        if not isinstance(execution.effect, EndTurnDrainEffect):
            return

        instance = context.get_instance(execution.holder_instance_id)
        if instance.fainted or instance.current_hp <= 0:
            return

        payload = execution.effect.payload
        drain_amount = max(1, floor(instance.max_hp * payload.ratio))
        applied_drain = min(instance.current_hp, drain_amount)
        instance.current_hp -= applied_drain

        context.add_event(
            kind="condition_drain",
            message=f"{format_pokemon_name(instance.pokemon_id)}'s health is sapped by {execution.condition.name}!",
            target_instance_id=instance.id,
            condition_id=execution.condition.id,
            value=applied_drain,
        )

        # Find the beneficiary (the opponent in the same slot)
        # TODO: In the future, we should store the 'source_instance_id' in the volatile status
        # to handle cases where the original user switched out (it should heal the replacement).
        beneficiary = self._find_opposite_instance(context, instance)
        if beneficiary and not beneficiary.fainted and beneficiary.current_hp > 0:
            heal_amount = applied_drain
            actual_heal = min(beneficiary.max_hp - beneficiary.current_hp, heal_amount)
            beneficiary.current_hp += actual_heal

            context.add_event(
                kind="condition_heal",
                message=f"{format_pokemon_name(beneficiary.pokemon_id)} regained health from {execution.condition.name}!",
                target_instance_id=beneficiary.id,
                condition_id=execution.condition.id,
                value=actual_heal,
            )

        if instance.current_hp == 0:
            faint_instance(context, instance)

    def _find_opposite_instance(self, context: BattleStrategyContext, instance) -> "BattleInstance | None":
        """Find the pokemon on the opposite side in the same active slot."""
        side = get_side_for_trainer(context.battle, instance.trainer_id)
        slot_index = get_active_slot_for_instance(side, instance.id)

        if slot_index is None:
            return None

        # Find the other side(s)
        for other_side_id, other_side in context.battle.sides.items():
            if other_side_id == instance.trainer_id: # Side ID is currently trainer_id in this project
                continue

            if slot_index < len(other_side.active_pokemon_instance_ids):
                target_id = other_side.active_pokemon_instance_ids[slot_index]
                if target_id:
                    return context.get_instance(target_id)

        return None
