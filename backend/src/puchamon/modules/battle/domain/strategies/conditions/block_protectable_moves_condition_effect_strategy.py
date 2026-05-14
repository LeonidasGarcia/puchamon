"""Strategy for `block_protectable_moves` condition effects."""

from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput
from ...utils import format_pokemon_name
from .base import ConditionEffectStrategy


class BlockProtectableMovesConditionEffectStrategy(ConditionEffectStrategy):
    """Strategy that blocks incoming protectable moves."""

    kind = "block_protectable_moves"
    hook = "validate_move"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Evaluate if the incoming move should be blocked."""
        if execution.effect.kind != self.kind:
            return

        if execution.movement and execution.movement.protectable:
            target_instance = context.get_instance(execution.holder_instance_id)
            if "protect" not in target_instance.volatile_status:
                return

            blocked_targets = context.transient.setdefault("blocked_targets", set())

            if execution.holder_instance_id not in blocked_targets:
                blocked_targets.add(execution.holder_instance_id)
                context.add_event(
                    kind="move_blocked",
                    message=f"{format_pokemon_name(target_instance.pokemon_id)} protected itself!",
                    source_instance_id=execution.source_instance_id,
                    target_instance_id=execution.holder_instance_id,
                    move_id=execution.movement.id,
                )
