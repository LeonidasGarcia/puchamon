"""Strategy for `block_protectable_moves` condition effects."""

from loguru import logger
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

        logger.debug(
            f"[BLOCK_PROTECT] Evaluating {execution.movement.id if execution.movement else 'unknown'} protectable={execution.movement.protectable if execution.movement else False}"
        )

        if execution.movement and execution.movement.protectable:
            target_instance = context.get_instance(execution.holder_instance_id)
            logger.debug(f"[BLOCK_PROTECT] Target {target_instance.pokemon_id} has volatile_status: {target_instance.volatile_status}")
            if "protect" not in target_instance.volatile_status:
                logger.debug(f"[BLOCK_PROTECT] 'protect' NOT in volatile_status - allowing move")
                return

            logger.debug(f"[BLOCK_PROTECT] 'protect' FOUND - blocking move!")
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
