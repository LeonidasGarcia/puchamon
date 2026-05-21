"""Strategy for `skip_action` condition effects."""

from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput
from ...utils import format_pokemon_name
from .base import ConditionEffectStrategy


class SkipActionConditionEffectStrategy(ConditionEffectStrategy):
    kind = "skip_action"
    hook = "before_action"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Apply a skip action condition (e.g. Sleep, Freeze) that blocks a move."""
        if execution.effect.kind != self.kind:
            return

        instance = context.get_instance(execution.holder_instance_id)
        if instance.fainted or instance.current_hp <= 0:
            return

        # Block the action
        context.mark_action_blocked(execution.holder_instance_id, self.kind)

        # Depending on the condition, emit a different message
        message = f"{format_pokemon_name(instance.pokemon_id)} is unable to move!"
        if execution.condition.id == "sleep":
            message = f"{format_pokemon_name(instance.pokemon_id)} is fast asleep."
        elif execution.condition.id == "freeze":
            message = f"{format_pokemon_name(instance.pokemon_id)} is frozen solid!"

        context.add_event(
            kind="action_skipped",
            message=message,
            target_instance_id=str(instance.id),
            condition_id=execution.condition.id,
        )
