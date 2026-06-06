"""Strategy for `damage` move effects."""

from loguru import logger

from .....pokedex.domain.entities import Movement
from .....pokedex.domain.entities.effects import DamagePayload
from ...exceptions import BattleValidationError
from ...mechanics import (
    DamageCalculationInput,
    calculate_damage,
    faint_instance,
    resolve_damage_hit_count,
    resolve_damage_roll_percent,
)
from ...runtime import (
    BattleStrategyContext,
    ConditionEffectExecutionInput,
    DamageApplicationInput,
    DamageResolutionInput,
    MoveEffectExecutionInput,
)
from ...utils import format_pokemon_name
from .pending import PendingMoveEffectStrategy


class DamageEffectStrategy(PendingMoveEffectStrategy):
    """Strategy that applies direct damage to targets."""

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
            self._emit_no_target_event(context, execution, execution.movement)
            return

        source_instance = context.get_instance(execution.source_instance_id)

        if execution.movement.power is None:
            self._apply_zero_damage(context, execution, execution.movement)
            return

        hit_count = resolve_damage_hit_count(payload)
        for target_id in execution.target_instance_ids:
            target = context.get_instance(target_id)
            if target.fainted or target.current_hp <= 0:
                continue

            self._apply_damage_to_target(
                DamageApplicationInput(
                    context=context,
                    execution=execution,
                    source=source_instance,
                    target=target,
                    payload=payload,
                    hit_count=hit_count,
                    movement=execution.movement,
                )
            )

    def _apply_damage_to_target(self, params: DamageApplicationInput) -> None:
        """Resolve and apply damage to a single target."""
        total_damage, roll_percent = self._resolve_total_damage(
            DamageResolutionInput(
                context=params.context,
                execution=params.execution,
                source=params.source,
                target=params.target,
                payload=params.payload,
                hit_count=params.hit_count,
                movement=params.movement,
            )
        )

        applied_damage = min(params.target.current_hp, total_damage)
        params.target.current_hp -= applied_damage

        logger.debug(
            f"[DAMAGE] {params.target.pokemon_id} recibió {applied_damage} daño "
            f"(HP: {params.target.current_hp + applied_damage} -> {params.target.current_hp}, roll: {roll_percent})"
        )

        params.context.add_event(
            kind="damage",
            message=f"¡{format_pokemon_name(params.target.pokemon_id)} recibió {applied_damage} puntos de daño por {params.movement.name}!",
            source_instance_id=params.execution.source_instance_id,
            target_instance_id=str(params.target.id),
            move_id=params.movement.id,
            value=applied_damage,
            damage_roll_percent=roll_percent,
            hits=params.hit_count,
        )

        if params.target.current_hp == 0:
            faint_instance(params.context, params.target)

    def _resolve_total_damage(self, params: DamageResolutionInput) -> tuple[int, int | None]:
        """Calculate the total damage for a target, including modifiers."""
        resolved_damage = params.execution.metadata.get("resolved_damage")
        if resolved_damage is not None:
            return max(1, int(resolved_damage) * params.hit_count), None

        if params.source.stats is None or params.target.stats is None:
            power = params.movement.power or 0
            return max(1, power * params.hit_count), None

        roll_percent = resolve_damage_roll_percent(params.execution.metadata.get("damage_roll_percent"))
        damage = calculate_damage(
            DamageCalculationInput(
                movement=params.movement,
                payload=params.payload,
                source=params.source,
                target=params.target,
                roll_percent=roll_percent,
                type_chart=params.context.transient.get("type_chart", {}),
            )
        )

        damage = self._evaluate_damage_modifiers(params, damage)

        return damage, roll_percent

    def _evaluate_damage_modifiers(self, params: DamageResolutionInput, base_damage: int) -> int:
        """Evaluate modify_damage hooks from conditions."""
        if not params.execution.condition_effect_strategy_registry or not params.execution.conditions:
            return base_damage

        strategies = params.execution.condition_effect_strategy_registry.for_hook("modify_damage")
        if not strategies:
            return base_damage

        current_damage = base_damage
        active_conditions = params.source.volatile_status + ([params.source.status] if params.source.status else [])

        for status_id in active_conditions:
            condition = params.execution.conditions.get(status_id)
            if not condition:
                continue

            for effect in condition.effects:
                for strategy in strategies:
                    if effect.kind == strategy.kind:
                        params.context.transient["current_damage"] = current_damage
                        strategy.apply(
                            params.context,
                            ConditionEffectExecutionInput(
                                condition=condition,
                                effect=effect,
                                holder_instance_id=params.execution.source_instance_id,
                                target_instance_id=str(params.target.id),
                                movement=params.movement,
                            ),
                        )
                        current_damage = params.context.transient.pop("current_damage", current_damage)

        return current_damage

    def _apply_zero_damage(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput, movement: Movement) -> None:
        """Emit 0 damage events for moves with null power."""
        for target_id in execution.target_instance_ids:
            target = context.get_instance(target_id)
            context.add_event(
                kind="damage",
                message=f"¡{format_pokemon_name(target.pokemon_id)} no recibió daño por {movement.name}!",
                source_instance_id=execution.source_instance_id,
                target_instance_id=target_id,
                move_id=movement.id,
                value=0,
            )

    def _emit_no_target_event(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput, movement: Movement) -> None:
        """Emit an event when there are no valid targets to damage."""
        context.add_event(
            kind="damage_no_target",
            message=f"¡{movement.name} no tenía objetivo al cual dañar!",
            source_instance_id=execution.source_instance_id,
            move_id=movement.id,
        )
