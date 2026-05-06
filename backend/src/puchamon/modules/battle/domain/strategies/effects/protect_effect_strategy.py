"""Strategy for `protect` move effects."""

from .....pokedex.domain.entities.effects import ProtectPayload
from ...exceptions import BattleValidationError
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from .base import MoveEffectStrategy


class ProtectEffectStrategy(MoveEffectStrategy):
    kind = "protect"

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Apply a protection status to the user."""
        if execution.effect.kind != self.kind:
            return

        payload = execution.effect.payload
        if not isinstance(payload, ProtectPayload):
            raise BattleValidationError("Protect effect strategies require a ProtectPayload instance")

        source = context.get_instance(execution.source_instance_id)
        if source.fainted or source.current_hp <= 0:
            return

        # Check if already protected
        if "protect" in source.volatile_status:
            context.add_event(
                kind="move_failed",
                message=f"{source.pokemon_id} is already protected!",
                source_instance_id=execution.source_instance_id,
            )
            return

        source.volatile_status.append("protect")
        context.add_event(
            kind="status_applied",
            message=f"{source.pokemon_id} protected itself!",
            target_instance_id=execution.source_instance_id,
            status_id="protect",
        )
