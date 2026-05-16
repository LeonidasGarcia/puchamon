"""Strategy for `damage` move effects."""

from loguru import logger

from .....pokedex.domain.entities.effects import DamagePayload
from ...exceptions import BattleValidationError
from ...mechanics import calculate_damage, faint_instance, resolve_damage_hit_count, resolve_damage_roll_percent
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from ...utils import format_pokemon_name
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

        # TODO: Implement proper special damage calculation for moves like Gyro Ball
        # that have power=null but still deal damage based on speed or other stats.
        # For now, skip damage calculation when power is None.
        if execution.movement.power is None:
            for target_instance_id in execution.target_instance_ids:
                target_instance = context.get_instance(target_instance_id)
                context.add_event(
                    kind="damage",
                    message=f"{format_pokemon_name(target_instance.pokemon_id)} took 0 damage from {execution.movement.name}",
                    source_instance_id=execution.source_instance_id,
                    target_instance_id=target_instance_id,
                    move_id=execution.movement.id,
                    value=0,
                )
            return

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
                    type_chart=context.transient.get("type_chart", {}),
                )
            else:
                total_damage = max(1, execution.movement.power * hit_count)

            applied_damage = min(target_instance.current_hp, total_damage)
            target_instance.current_hp -= applied_damage

            logger.debug(
                f"[DAMAGE] {target_instance.pokemon_id} recibió {applied_damage} daño (HP: {target_instance.current_hp + applied_damage} -> {target_instance.current_hp}, roll: {damage_roll_percent})"
            )

            context.add_event(
                kind="damage",
                message=f"{format_pokemon_name(target_instance.pokemon_id)} took {applied_damage} damage from {execution.movement.name}",
                source_instance_id=execution.source_instance_id,
                target_instance_id=target_instance_id,
                move_id=execution.movement.id,
                value=applied_damage,
                damage_roll_percent=damage_roll_percent,
                hits=hit_count,
            )

            if target_instance.current_hp == 0:
                faint_instance(context, target_instance)
