"""Strategy for `apply_major_status` move effects."""

from .....pokedex.domain.entities.effects import StatusPayload
from ...mechanics import is_immune_to_status
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from .base import MoveEffectStrategy


class ApplyMajorStatusEffectStrategy(MoveEffectStrategy):
    kind = "apply_major_status"

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Apply a major status condition (Burn, Poison, Paralysis, etc.) to targets."""
        if execution.effect.kind != self.kind:
            return

        payload = execution.effect.payload
        if not isinstance(payload, StatusPayload):
            return

        for target_id in execution.target_instance_ids:
            target = context.get_instance(target_id)
            if target.fainted or target.current_hp <= 0:
                continue

            # Pokemon can only have one major status condition at a time
            if target.status:
                continue

            # Check for type immunities
            if is_immune_to_status(target, payload.condition_id):
                context.add_event(
                    kind="status_failed_immune",
                    message=f"It doesn't affect {target.pokemon_id}...",
                    target_instance_id=target_id,
                )
                continue

            target.status = payload.condition_id

            context.add_event(
                kind="status_applied",
                message=f"{target.pokemon_id} was {payload.condition_id}ed!",
                target_instance_id=target_id,
                status_id=payload.condition_id,
            )
