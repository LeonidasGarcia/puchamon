"""Strategy for `cannot_move` condition effects."""

from ..context import BattleStrategyContext, ConditionEffectExecutionInput
from .pending import PendingConditionEffectStrategy


class CannotMoveConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "cannot_move"
    hook = "before_action"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Block the holder action for the current resolution step."""
        if execution.effect.kind != self.kind:
            return super().apply(context, execution)

        holder_instance = context.get_instance(execution.holder_instance_id)
        context.mark_action_blocked(execution.holder_instance_id, self.kind)
        context.add_event(
            kind="cannot_move",
            message=f"{holder_instance.pokemon_id} cannot move because of {execution.condition.name}",
            source_instance_id=execution.holder_instance_id,
            status_id=execution.condition.id,
        )
