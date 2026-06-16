"""Service for resolving battle turns."""

import contextlib
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

from ...domain.entities import Battle, BattleInstance, TurnAction
from ...domain.entities.battle import BattleResult
from ...domain.mechanics.stats import calculate_effective_stat
from ...domain.registries import (
    ActionStrategyRegistry,
    ConditionEffectStrategyRegistry,
    MoveEffectStrategyRegistry,
)
from ...domain.runtime.context import (
    ActionExecutionInput,
    BattleStrategyContext,
    ConditionEffectExecutionInput,
)

if TYPE_CHECKING:
    from ....pokedex.domain.entities import Condition, MoveEffect, Movement, Type


@dataclass(frozen=True)
class _ResolveTurnParams:
    """Bundled parameters for resolve_turn to reduce argument count (PLR0913)."""

    battle: Battle
    instances: dict[str, BattleInstance]
    actions: list[TurnAction]
    movements: dict[str, "Movement"]
    conditions: dict[str, "Condition"]
    move_effects: dict[str, "MoveEffect"]
    type_chart: dict[str, "Type"]


class TurnResolutionService:
    """Core domain service for battle turn execution.

    Responsible for the strict step-by-step execution of a single battle turn,
    following Pokémon Gen 5 rules. This service handles the orchestration of
    switches, move execution, and end-of-turn residuals.
    """

    def __init__(
        self,
        action_registry: ActionStrategyRegistry,
        move_effect_registry: MoveEffectStrategyRegistry,
        condition_effect_registry: ConditionEffectStrategyRegistry,
    ):
        self._action_registry = action_registry
        self._move_effect_registry = move_effect_registry
        self._condition_effect_registry = condition_effect_registry

    def resolve_turn(self, params: _ResolveTurnParams) -> BattleStrategyContext:
        """Executes a full turn and returns the context with the resulting state and event log."""
        battle = params.battle
        instances = params.instances
        context = BattleStrategyContext(battle=battle, battle_instances=instances)
        context.transient["type_chart"] = params.type_chart

        logger.debug(f"Resolving turn {battle.turn} with {len(params.actions)} actions")
        self._resolve_switches(context, params.actions)

        ordered_actions = self._sort_actions(context, params.actions, params.movements, params.conditions)

        move_names: list[tuple[str, str]] = []
        for a in ordered_actions:
            if move_id := a.move_id:
                m = params.movements.get(move_id)
                name = m.name if m else move_id
            else:
                name = "unknown"
            move_names.append((a.user_instance_id, name))

        logger.debug(f"[SORT] Ordered actions: {move_names}")

        self._execute_actions(context, ordered_actions, params.movements, params.move_effects, params.conditions)
        logger.debug(f"Events after execution: {len(context.events)}")

        self._resolve_residuals(context, params.conditions)

        self._resolve_faints_and_cleanup(context)

        return context

    def _resolve_switches(self, context: BattleStrategyContext, actions: list[TurnAction]) -> None:
        """Executes 'switch' actions."""
        switch_actions = [a for a in actions if a.type == "switch"]

        for action in switch_actions:
            strategy = self._action_registry.get("switch")
            execution = ActionExecutionInput(action=action, replacement_instance_id=action.replacement_instance_id)
            strategy.execute(context, execution)

    def _sort_actions(
        self,
        context: BattleStrategyContext,
        actions: list[TurnAction],
        movements: dict[str, "Movement"],
        conditions: dict[str, "Condition"],
    ) -> list[TurnAction]:
        """Sort the remaining 'move' actions based on priority and speed.

        1. Move Priority.
        2. Effective Speed (Base + IV/EV + Nature + Stages + Condition modifiers).
        3. Speed Tie (Random 50/50).
        """
        # We only sort 'move' actions, since switches were already resolved in Phase 1
        move_actions = [a for a in actions if a.type == "move"]

        def get_action_priority_and_speed(action: TurnAction) -> tuple[int, int, float]:
            move_id = action.move_id
            movement = movements.get(move_id) if move_id else None
            priority = movement.priority if movement else 0

            instance = context.get_instance(action.user_instance_id)
            if not instance.stats:
                logger.debug(
                    f"[SORT] {instance.pokemon_id} used {movement.name if movement else action.move_id}: priority={priority}, speed=0 (no stats)"
                )
                return (priority, 0, random.random())

            base_speed = instance.stats.spe
            effective_speed = calculate_effective_stat(base_speed, instance.stages.spe)

            # Invoke ConditionEffectStrategyRegistry with hook="modify_speed"
            # to dynamically alter the `effective_speed` based on conditions like paralysis.
            active_conditions = instance.volatile_status + ([instance.status] if instance.status else [])
            for status_id in active_conditions:
                if status_id not in conditions:
                    continue
                condition = conditions[status_id]
                for effect in condition.effects:
                    with contextlib.suppress(Exception):
                        strategy = self._condition_effect_registry.get(effect.kind)
                        if strategy.hook == "modify_speed":
                            execution = ConditionEffectExecutionInput(
                                condition=condition,
                                effect=effect,
                                holder_instance_id=str(instance.id),
                                source_instance_id=None,
                                target_instance_id=None,
                                movement=None,
                            )
                            # Passing the speed inside the context transient data
                            context.transient["current_speed"] = effective_speed
                            strategy.apply(context, execution)
                            effective_speed = context.transient.pop("current_speed", effective_speed)
            logger.debug(
                f"[SORT] {instance.pokemon_id} used {movement.name if movement else action.move_id}: priority={priority}, speed={effective_speed}"
            )
            return (priority, effective_speed, random.random())

        return sorted(move_actions, key=get_action_priority_and_speed, reverse=True)

    def _execute_actions(
        self,
        context: BattleStrategyContext,
        actions: list[TurnAction],
        movements: dict[str, "Movement"],
        move_effects: dict[str, "MoveEffect"],
        conditions: dict[str, "Condition"],
    ) -> None:
        """Iterate over ordered actions and execute them.

        Checks if user is still alive, evaluates status conditions
        (Sleep, Paralysis, Confusion), checks Accuracy, and applies
        Move Effects (Damage, Stat changes).
        """
        for action in actions:
            if action.type != "move":
                logger.debug(f"Skipping action type {action.type}")
                continue

            instance = context.get_instance(action.user_instance_id)
            if instance.fainted or instance.current_hp <= 0:
                logger.debug(f"Skipping fainted instance {instance.pokemon_id}")
                continue

            # Check if skipped by condition (e.g. Paralyzed)
            if context.get_action_block_reason(action.user_instance_id):
                continue

            move_id = action.move_id
            movement = movements.get(move_id) if move_id else None
            if not movement:
                logger.debug(f"Movement not found for {action.move_id}")
                continue

            resolved_effects = [move_effects[eid] for eid in movement.effect_ids if eid in move_effects]
            logger.debug(f"[MOVE] {instance.pokemon_id} usado {movement.name} (power={movement.power}, accuracy={movement.accuracy})")
            logger.debug(f"[MOVE] {movement.name} tiene {len(resolved_effects)} efectos: {[e.kind for e in resolved_effects]}")

            strategy = self._action_registry.get("move")
            execution = ActionExecutionInput(
                action=action,
                movement=movement,
                move_effects=resolved_effects,
                move_effect_strategy_registry=self._move_effect_registry,
                condition_effect_strategy_registry=self._condition_effect_registry,
                conditions=conditions,
            )

            # This triggers all validations (PP, target accuracy, damage calculation, etc.)
            strategy.execute(context, execution)

    def _resolve_residuals(self, context: BattleStrategyContext, conditions: dict[str, "Condition"]) -> None:
        """Applies end-of-turn effects like Burn, Poison."""
        for instance in context.battle_instances.values():
            if instance.fainted or instance.current_hp <= 0:
                continue

            active_conditions = instance.volatile_status + ([instance.status] if instance.status else [])
            for status_id in active_conditions:
                status_condition = conditions.get(status_id)
                if not status_condition:
                    continue

                strategies = self._condition_effect_registry.for_hook("end_turn")
                for strategy in strategies:
                    if effect := next(
                        (e for e in status_condition.effects if e.kind == strategy.kind),
                        None,
                    ):
                        execution = ConditionEffectExecutionInput(condition=status_condition, effect=effect, holder_instance_id=str(instance.id))
                        strategy.apply(context, execution)

    def _cleanup_volatile_statuses(self, context: BattleStrategyContext) -> None:
        """Remove volatile statuses that expire at end of turn (e.g. protect, flinch)."""
        volatile_statuses_to_expire = {"protect", "flinch"}
        for instance in context.battle_instances.values():
            if instance.fainted or instance.current_hp <= 0:
                continue
            if expired := [vs for vs in instance.volatile_status if vs in volatile_statuses_to_expire]:
                for status in expired:
                    instance.volatile_status.remove(status)
                context.add_event(
                    kind="volatile_status_expired",
                    message=f"¡El efecto de {', '.join(expired)} de {instance.pokemon_id} se ha desvanecido!",
                    target_instance_id=str(instance.id),
                    volatile_status=expired,
                )

    def _resolve_faints_and_cleanup(self, context: BattleStrategyContext) -> None:
        """Update residual effects, victory state, and the next battle phase."""
        self._cleanup_volatile_statuses(context)

        active_trainers = []
        for trainer_id in context.battle.sides:
            has_alive_pokemon = any(not inst.fainted for inst in context.battle_instances.values() if inst.trainer_id == trainer_id)
            if has_alive_pokemon:
                active_trainers.append(trainer_id)

        if len(active_trainers) == 1:
            winner_id = active_trainers[0]
            context.battle.status = "finished"
            context.battle.result = BattleResult(winner_trainer_id=winner_id, reason="knockout")
            winner_name = next(
                (player.name for player in context.battle.players if player.trainer_id == winner_id),
                winner_id,
            )
            context.add_event(
                kind="battle_finished",
                message=f"¡{winner_name} ha ganado la batalla!",
                winner_trainer_id=winner_id,
            )
        elif not active_trainers:
            context.battle.status = "finished"
            context.add_event(kind="battle_finished", message="¡La batalla ha terminado en empate!")

        if context.battle.status == "active":
            needs_replacement = next(
                (True for side in context.battle.sides.values() if any(slot is None for slot in side.active_pokemon_instance_ids)),
                False,
            )
            if needs_replacement:
                context.battle.phase = "awaiting_replacements"
            else:
                context.battle.phase = "awaiting_actions"
