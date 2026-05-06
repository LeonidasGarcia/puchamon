"""Strategy for `damage` move effects."""

from .....pokedex.domain.entities.effects import DamagePayload
from ...battlefield import get_active_slot_for_instance, get_side_for_trainer, set_active_instance_for_slot
from ...exceptions import BattleValidationError
from ...mechanics import calculate_damage, resolve_damage_hit_count, resolve_damage_roll_percent
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from .pending import PendingMoveEffectStrategy


class DamageEffectStrategy(PendingMoveEffectStrategy):
    kind = "damage"

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Apply direct damage to every resolved target instance."""
        if execution.effect.kind != self.kind:
            return super().apply(context, execution)

        payload = execution.effect.payload
        if not isinstance(payload, DamagePayload):
            raise BattleValidationError("Damage effect strategies require a DamagePayload instance")

        if execution.movement is None:
            raise BattleValidationError("Damage effects require a resolved movement entity")

        if not execution.target_instance_ids:
            context.add_event(
                kind="damage_no_target",
                message=f"{execution.movement.name} had no active target to damage",
                source_instance_id=execution.source_instance_id,
                move_id=execution.movement.id,
            )
            return

        hit_count = resolve_damage_hit_count(payload)
        resolved_damage = execution.metadata.get("resolved_damage")
        configured_damage_roll_percent = execution.metadata.get("damage_roll_percent")
        source_instance = context.get_instance(execution.source_instance_id)

        for target_instance_id in execution.target_instance_ids:
            target_instance = context.get_instance(target_instance_id)
            if target_instance.fainted or target_instance.current_hp <= 0:
                continue

            damage_roll_percent: int | None = None
            if resolved_damage is not None:
                total_damage = max(1, int(resolved_damage) * hit_count)
            elif source_instance.stats is not None and target_instance.stats is not None:
                damage_roll_percent = resolve_damage_roll_percent(configured_damage_roll_percent)
                total_damage = calculate_damage(
                    movement=execution.movement,
                    payload=payload,
                    source_instance=source_instance,
                    target_instance=target_instance,
                    damage_roll_percent=damage_roll_percent,
                )
            else:
                total_damage = max(1, execution.movement.power * hit_count)

            applied_damage = min(target_instance.current_hp, total_damage)
            target_instance.current_hp -= applied_damage

            context.add_event(
                kind="damage",
                message=f"{target_instance.pokemon_id} took {applied_damage} damage from {execution.movement.name}",
                source_instance_id=execution.source_instance_id,
                target_instance_id=target_instance_id,
                move_id=execution.movement.id,
                value=applied_damage,
                damage_roll_percent=damage_roll_percent,
                hits=hit_count,
            )

            if target_instance.current_hp == 0:
                target_instance.fainted = True
                target_side = get_side_for_trainer(context.battle, target_instance.trainer_id)
                target_active_slot = get_active_slot_for_instance(target_side, target_instance_id)
                set_active_instance_for_slot(target_side, target_active_slot, None)
                context.mark_fainted(target_instance_id)
                context.add_event(
                    kind="pokemon_fainted",
                    message=f"{target_instance.pokemon_id} fainted",
                    target_instance_id=target_instance_id,
                    active_slot=target_active_slot,
                )
