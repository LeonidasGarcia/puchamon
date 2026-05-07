"""Strategy for `apply_volatile_status` move effects."""

from .....pokedex.domain.entities.effects import StatusPayload
from ...mechanics import is_immune_to_volatile
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from ...utils import format_pokemon_name
from .base import MoveEffectStrategy


class ApplyVolatileStatusEffectStrategy(MoveEffectStrategy):
    kind = "apply_volatile_status"

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Apply a volatile status condition (Leech Seed, Confusion, etc.) to targets."""
        if execution.effect.kind != self.kind:
            return

        payload = execution.effect.payload
        if not isinstance(payload, StatusPayload):
            return

        for target_id in execution.target_instance_ids:
            target = context.get_instance(target_id)
            if target.fainted or target.current_hp <= 0:
                continue

            # Volatile statuses can accumulate
            if payload.condition_id in target.volatile_status:
                continue

            # Check for specific immunities
            if is_immune_to_volatile(target, payload.condition_id):
                context.add_event(
                    kind="volatile_status_failed_immune",
                    message=f"It doesn't affect {format_pokemon_name(target.pokemon_id)}...",
                    target_instance_id=target_id,
                )
                continue

            target.volatile_status.append(payload.condition_id)

            context.add_event(
                kind="volatile_status_applied",
                message=f"{format_pokemon_name(target.pokemon_id)} was affected by {payload.condition_id}!",
                target_instance_id=target_id,
                status_id=payload.condition_id,
            )
