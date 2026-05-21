"""Strategy for `cannot_move` condition effects."""

from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput
from ...utils import format_pokemon_name
from .base import ConditionEffectStrategy


class CannotMoveConditionEffectStrategy(ConditionEffectStrategy):
    kind = "cannot_move"
    hook = "before_action"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Block the holder action for the current resolution step."""
        if execution.effect.kind != self.kind:
            return

        instance = context.get_instance(execution.holder_instance_id)
        if instance.fainted or instance.current_hp <= 0:
            return

        context.mark_action_blocked(execution.holder_instance_id, self.kind)

        message = f"{format_pokemon_name(instance.pokemon_id)} cannot move because of {execution.condition.name}"
        if execution.condition.id == "flinch":
            message = f"{format_pokemon_name(instance.pokemon_id)} flinched and couldn't move!"

        context.add_event(
            kind="action_skipped",
            message=message,
            source_instance_id=execution.holder_instance_id,
            condition_id=execution.condition.id,
        )
