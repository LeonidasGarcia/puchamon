"""Strategy for executing move actions."""

import random

from loguru import logger

from .....pokedex.domain.entities import Movement
from ...battlefield import get_side_for_trainer, resolve_effect_target_instance_ids
from ...entities import BattleInstance, MoveState
from ...exceptions import BattleValidationError
from ...mechanics import calculate_accuracy, resolve_damage_roll_percent
from ...runtime import ActionExecutionInput, BattleStrategyContext, ConditionEffectExecutionInput
from ...utils import format_pokemon_name
from .base import ActionStrategy


def _apply_move_effects(
    context: BattleStrategyContext,
    execution: ActionExecutionInput,
    source_instance: BattleInstance,
    damage_roll_percent: int | None = None,
) -> None:
    movement = execution.movement
    if movement is None:
        raise BattleValidationError("execution.movement cannot be None when applying move effects")

    move_effect_strategy_registry = execution.move_effect_strategy_registry
    if not move_effect_strategy_registry:
        raise BattleValidationError("Cannot apply move effects without a registered strategy dispatcher")

    effect_metadata = {"damage_roll_percent": damage_roll_percent}

    for index, effect in enumerate(execution.move_effects):
        target_instance_ids = resolve_effect_target_instance_ids(
            battle=context.battle,
            source_instance=source_instance,
            action_target=execution.action.target,
            effect=effect,
        )

        blocked_targets: set[str] = context.transient.get("blocked_targets", set())
        target_instance_ids = [tid for tid in target_instance_ids if tid not in blocked_targets]

        if not target_instance_ids:
            if not blocked_targets and index == 0:
                context.add_event(
                    kind="move_failed_no_target",
                    message=f"¡{movement.name} falló porque no había un objetivo válido!",
                    source_instance_id=execution.action.user_instance_id,
                    move_id=execution.action.move_id,
                )
            continue

        # Chance Check: Roll for secondary effects (e.g. flinch, burn chance)
        full_chance = 100
        if effect.chance < full_chance and random.randint(1, full_chance) > effect.chance:
            logger.debug(f"[EFFECT] {effect.kind} falló chance ({effect.chance}%)")
            continue

        effect_strategy = move_effect_strategy_registry.get(effect.kind)
        logger.debug(f"[EFFECT] Aplicando {effect.kind} a {len(target_instance_ids)} targets: {target_instance_ids}")
        effect_strategy.apply(
            context,
            execution.build_move_effect_execution(effect=effect, target_instance_ids=target_instance_ids, metadata=effect_metadata),
        )


class MoveActionStrategy(ActionStrategy):
    """Execute a turn action whose type is `move`."""

    action_type = "move"

    def _validate_preconditions(
        self, context: BattleStrategyContext, execution: ActionExecutionInput
    ) -> tuple[BattleInstance | None, Movement | None, "MoveState | None"]:
        if execution.action.type != self.action_type:
            raise BattleValidationError(f"MoveActionStrategy cannot execute action type '{execution.action.type}'")

        if execution.movement is None:
            raise BattleValidationError("Move actions require a resolved movement entity")

        if execution.move_effect_strategy_registry is None:
            raise BattleValidationError("Move actions require a move effect strategy registry for dispatch")

        if execution.action.move_id is None:
            raise BattleValidationError("Move actions require a move_id")

        source_instance = context.get_instance(execution.action.user_instance_id)
        if source_instance.fainted or source_instance.current_hp <= 0:
            return None, None, None

        if execution.action.player != source_instance.trainer_id:
            raise BattleValidationError("Move actions must be declared by the trainer that owns the source instance")

        source_side = get_side_for_trainer(context.battle, source_instance.trainer_id)
        if execution.action.user_instance_id not in source_side.active_pokemon_instance_ids:
            raise BattleValidationError("Only active pokemon can execute move actions")

        skip_reason = context.get_action_block_reason(execution.action.user_instance_id)
        if skip_reason is not None:
            context.add_event(
                kind="action_skipped",
                message=f"¡{format_pokemon_name(source_instance.pokemon_id)} no pudo actuar debido a {skip_reason}!",
                source_instance_id=execution.action.user_instance_id,
                move_id=execution.action.move_id,
                reason=skip_reason,
            )
            context.clear_action_block(execution.action.user_instance_id)
            return None, None, None

        move_state = next((move_state for move_state in source_instance.move_state if move_state.move_id == execution.action.move_id), None)
        if move_state is None:
            raise BattleValidationError(
                f"Move '{execution.action.move_id}' is not available for battle instance '{execution.action.user_instance_id}'"
            )

        if move_state.current_pp <= 0:
            raise BattleValidationError(f"Move '{execution.action.move_id}' has no PP remaining")

        return source_instance, execution.movement, move_state

    def _evaluate_source_conditions(
        self,
        context: BattleStrategyContext,
        execution: ActionExecutionInput,
        source_instance: BattleInstance,
    ) -> None:
        active_conditions = source_instance.volatile_status + ([source_instance.status] if source_instance.status else [])
        if not active_conditions:
            return
        if not execution.conditions or not execution.condition_effect_strategy_registry:
            return

        strategies = execution.condition_effect_strategy_registry.for_hook("before_action")
        for status_id in active_conditions:
            condition = execution.conditions.get(status_id)
            if not condition:
                continue

            for effect in condition.effects:
                for strategy in strategies:
                    if effect.kind == strategy.kind:
                        hook_input = ConditionEffectExecutionInput(
                            condition=condition,
                            effect=effect,
                            holder_instance_id=execution.action.user_instance_id,
                        )
                        strategy.apply(context, hook_input)

    def _evaluate_target_conditions(
        self,
        context: BattleStrategyContext,
        execution: ActionExecutionInput,
        movement: Movement,
        target_instance_ids: list[str],
    ) -> None:
        logger.debug(f"[VALIDATE] conditions={execution.conditions is not None}, registry={execution.condition_effect_strategy_registry is not None}")
        if execution.conditions and execution.condition_effect_strategy_registry:
            strategies = execution.condition_effect_strategy_registry.for_hook("validate_move")
            logger.debug(f"[VALIDATE] Checking {len(target_instance_ids)} targets for {movement.name}")
            for target_id in target_instance_ids:
                target = context.get_instance(target_id)
                active_conditions = target.volatile_status + ([target.status] if target.status else [])
                logger.debug(f"[VALIDATE] Target {target.pokemon_id} active_conditions: {active_conditions}")
                for status_id in active_conditions:
                    condition = execution.conditions.get(status_id)
                    logger.debug(f"[VALIDATE] Condition '{status_id}' found: {condition is not None}")
                    if condition:
                        for effect in condition.effects:
                            for strategy in strategies:
                                if strategy.kind == effect.kind:
                                    logger.debug(f"[VALIDATE] Applying strategy {strategy.kind} for condition '{status_id}'")
                                    hook_input = ConditionEffectExecutionInput(
                                        condition=condition,
                                        effect=effect,
                                        holder_instance_id=target_id,
                                        source_instance_id=execution.action.user_instance_id,
                                        movement=movement,
                                    )
                                    strategy.apply(context, hook_input)

    def execute(self, context: BattleStrategyContext, execution: ActionExecutionInput) -> None:
        """Resolve a move action against the current mutable battle state."""
        source_instance, movement, move_state = self._validate_preconditions(context, execution)
        if source_instance is None or movement is None or move_state is None:
            return

        self._evaluate_source_conditions(context, execution, source_instance)

        # Re-check for blocks after evaluating source conditions (e.g. Paralysis roll, Flinch)
        skip_reason = context.get_action_block_reason(execution.action.user_instance_id)
        if skip_reason is not None:
            context.clear_action_block(execution.action.user_instance_id)
            return

        move_state.current_pp -= 1
        if move_state.move_id not in source_instance.revealed_moves:
            source_instance.revealed_moves.append(move_state.move_id)

        context.add_event(
            kind="move_used",
            message=f"¡{format_pokemon_name(source_instance.pokemon_id)} usó {movement.name}!",
            source_instance_id=execution.action.user_instance_id,
            move_id=move_state.move_id,
        )

        # Validation Phase: Evaluate validate_move hooks for all targets
        context.transient["blocked_targets"] = set()

        if not execution.move_effects:
            return

        if movement.target in {"target", "all_foes", "all_adjacent"}:
            # For simplicity, we check against the first resolved target's accuracy later,
            # but we need to resolve all targets for validation blocks (like Protect).
            target_instance_ids = resolve_effect_target_instance_ids(
                battle=context.battle,
                source_instance=source_instance,
                action_target=execution.action.target,
                effect=execution.move_effects[0],
            )

            self._evaluate_target_conditions(context, execution, movement, target_instance_ids)

            # Filter out targets that successfully blocked the move
            valid_target_ids = [tid for tid in target_instance_ids if tid not in context.transient["blocked_targets"]]

            # If targets were found but ALL of them blocked the move, the action ends here
            if target_instance_ids and not valid_target_ids:
                return

            if valid_target_ids:
                target = context.get_instance(valid_target_ids[0])
                if not calculate_accuracy(movement, target):
                    context.add_event(
                        kind="move_missed",
                        message=f"¡El ataque de {format_pokemon_name(source_instance.pokemon_id)} falló!",
                        source_instance_id=execution.action.user_instance_id,
                        move_id=execution.action.move_id,
                    )
                    return

        _apply_move_effects(
            context,
            execution,
            source_instance,
            damage_roll_percent=resolve_damage_roll_percent(),
        )
