"""Strategy for executing move actions."""

import random
from typing import TYPE_CHECKING

from .....pokedex.domain.entities import Movement
from ...battlefield import get_side_for_trainer, resolve_effect_target_instance_ids
from ...mechanics import calculate_accuracy
from ...entities import BattleInstance
from ...exceptions import BattleValidationError
from ...runtime import ActionExecutionInput, BattleStrategyContext
from .base import ActionStrategy

if TYPE_CHECKING:
    from ...registries import MoveEffectStrategyRegistry


def _apply_move_effects(
    context: BattleStrategyContext,
    execution: ActionExecutionInput,
    move_effect_strategy_registry: "MoveEffectStrategyRegistry",
    movement: Movement,
    source_instance: BattleInstance,
) -> None:
    """Apply the resolved move effects in execution order."""
    ordered_effects = sorted(execution.move_effects, key=lambda effect: effect.order)
    for effect in ordered_effects:
        target_instance_ids = resolve_effect_target_instance_ids(
            battle=context.battle,
            source_instance=source_instance,
            action_target=execution.action.target,
            effect=effect,
        )

        if effect.target == "target" and not target_instance_ids:
            context.add_event(
                kind="move_failed_no_target",
                message=f"{movement.name} failed because there was no valid target",
                source_instance_id=execution.action.user_instance_id,
                move_id=execution.action.move_id,
            )
            continue

        # Chance Check: Roll for secondary effects (e.g. flinch, burn chance)
        if effect.chance < 100:
            if random.randint(1, 100) > effect.chance:
                continue

        effect_strategy = move_effect_strategy_registry.get(effect.kind)
        effect_strategy.apply(
            context,
            execution.build_move_effect_execution(effect=effect, target_instance_ids=target_instance_ids),
        )


class MoveActionStrategy(ActionStrategy):
    """Execute a turn action whose type is `move`."""

    action_type = "move"

    def execute(self, context: BattleStrategyContext, execution: ActionExecutionInput) -> None:
        """Resolve a move action against the current mutable battle state."""
        if execution.action.type != self.action_type:
            raise BattleValidationError(f"MoveActionStrategy cannot execute action type '{execution.action.type}'")

        if execution.movement is None:
            raise BattleValidationError("Move actions require a resolved movement entity")

        movement = execution.movement

        if execution.move_effect_strategy_registry is None:
            raise BattleValidationError("Move actions require a move effect strategy registry for dispatch")

        move_effect_strategy_registry = execution.move_effect_strategy_registry

        if execution.action.move_id is None:
            raise BattleValidationError("Move actions require a move_id")

        source_instance = context.get_instance(execution.action.user_instance_id)
        if execution.action.player != source_instance.trainer_id:
            raise BattleValidationError("Move actions must be declared by the trainer that owns the source instance")

        source_side = get_side_for_trainer(context.battle, source_instance.trainer_id)
        if execution.action.user_instance_id not in source_side.active_pokemon_instance_ids:
            raise BattleValidationError("Only active pokemon can execute move actions")

        if source_instance.fainted or source_instance.current_hp <= 0:
            raise BattleValidationError("A fainted pokemon cannot execute a move action")

        skip_reason = context.get_action_block_reason(execution.action.user_instance_id)
        if skip_reason is not None:
            context.add_event(
                kind="action_skipped",
                message=f"{source_instance.pokemon_id} could not act because of {skip_reason}",
                source_instance_id=execution.action.user_instance_id,
                move_id=execution.action.move_id,
                reason=skip_reason,
            )
            context.clear_action_block(execution.action.user_instance_id)
            return

        move_state = next((move_state for move_state in source_instance.move_state if move_state.move_id == execution.action.move_id), None)
        if move_state is None:
            raise BattleValidationError(
                f"Move '{execution.action.move_id}' is not available for battle instance '{execution.action.user_instance_id}'"
            )

        if move_state.current_pp <= 0:
            raise BattleValidationError(f"Move '{execution.action.move_id}' has no PP remaining")

        move_state.current_pp -= 1
        if execution.action.move_id not in source_instance.revealed_moves:
            source_instance.revealed_moves.append(execution.action.move_id)

        context.add_event(
            kind="move_used",
            message=f"{source_instance.pokemon_id} used {movement.name}",
            source_instance_id=execution.action.user_instance_id,
            move_id=execution.action.move_id,
        )

        # Accuracy Check (only for moves that target specific pokemons)
        if movement.target in {"target", "all_foes", "all_adjacent"}:
            # For simplicity, we check against the first resolved target
            # TODO: Handle multi-target accuracy checks for each target separately
            target_instance_ids = resolve_effect_target_instance_ids(
                battle=context.battle,
                source_instance=source_instance,
                action_target=execution.action.target,
                effect=execution.move_effects[0] if execution.move_effects else None,
            )
            
            if target_instance_ids:
                target = context.get_instance(target_instance_ids[0])
                if not calculate_accuracy(context, movement, source_instance, target):
                    context.add_event(
                        kind="move_missed",
                        message=f"{source_instance.pokemon_id}'s attack missed!",
                        source_instance_id=execution.action.user_instance_id,
                        move_id=execution.action.move_id,
                    )
                    return

        _apply_move_effects(context, execution, move_effect_strategy_registry, movement, source_instance)
