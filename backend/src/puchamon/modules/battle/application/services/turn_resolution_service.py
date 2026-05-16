"""Service for resolving battle turns."""

import random
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

    def resolve_turn(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        actions: list[TurnAction],
        movements: dict[str, "Movement"],
        conditions: dict[str, "Condition"],
        move_effects: dict[str, "MoveEffect"],
        type_chart: dict[str, "Type"],
    ) -> BattleStrategyContext:
        """Executes a full turn and returns the context with the resulting state and event log."""
        context = BattleStrategyContext(battle=battle, battle_instances=instances)
        context.transient["type_chart"] = type_chart

        logger.debug(f"Resolving turn {battle.turn} with {len(actions)} actions")
        # 1. Phase: Pre-Action (Switches)
        self._resolve_switches(context, actions)

        # 2. Phase: Determine Order
        ordered_actions = self._sort_actions(context, actions, movements, conditions)
        logger.debug(
            f"[SORT] Ordered actions: {[(a.user_instance_id, movements.get(a.move_id).name if movements.get(a.move_id) else a.move_id) for a in ordered_actions]}"
        )

        # 3. Phase: Execution (Moves)
        self._execute_actions(context, ordered_actions, movements, move_effects, conditions)
        logger.debug(f"Events after execution: {len(context.events)}")

        # 4. Phase: End of Turn (Residuals: Status conditions like Burn/Poison)
        self._resolve_residuals(context, conditions)

        # 5. Phase: Faint Resolution & Turn Cleanup
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
            movement = movements.get(action.move_id) if action.move_id else None
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
            if instance.status and instance.status in conditions:
                condition = conditions[instance.status]
                for effect in condition.effects:
                    try:
                        strategy = self._condition_effect_registry.get(effect.kind)
                        if strategy.hook == "modify_speed":
                            execution = ConditionEffectExecutionInput(
                                condition=condition,
                                effect=effect,
                                holder_instance_id=instance.id,
                                source_instance_id=None,
                                target_instance_id=None,
                                movement=None,
                            )
                            # Passing the speed inside the context transient data
                            context.transient["current_speed"] = effective_speed
                            strategy.apply(context, execution)
                            effective_speed = context.transient.pop("current_speed", effective_speed)
                    except Exception:
                        pass  # Ignore if not registered or pending

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
                # The strategy handles this internally, but it's good to keep the flow clear.
                pass

            movement = movements.get(action.move_id) if action.move_id else None
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

            # --- Mid-turn Replacement Check ---
            # We no longer auto-replace mid-turn.
            # In Gen 5+, replacements are chosen simultaneously after all turn actions are completed
            # unless it's a specific pivot move. Since we want manual replacements at the end of the turn,
            # we just leave the slot empty and let _resolve_faints_and_cleanup handle the phase change.
            pass

    def _resolve_residuals(self, context: BattleStrategyContext, conditions: dict[str, "Condition"]) -> None:
        """Applies end-of-turn effects like Burn, Poison."""
        # Major Status (Burn, Poison, Toxic)
        for instance in context.battle_instances.values():
            if instance.fainted or instance.current_hp <= 0 or not instance.status:
                continue

            status_condition = conditions.get(instance.status)
            if not status_condition:
                continue

            strategies = self._condition_effect_registry.for_hook("end_turn")
            for strategy in strategies:
                # Find matching effect in condition
                effect = next((e for e in status_condition.effects if e.kind == strategy.kind), None)
                if effect:
                    execution = ConditionEffectExecutionInput(condition=status_condition, effect=effect, holder_instance_id=instance.id)
                    strategy.apply(context, execution)

    def _cleanup_volatile_statuses(self, context: BattleStrategyContext) -> None:
        """Remove volatile statuses that expire at end of turn (e.g. protect)."""
        volatile_statuses_to_expire = {"protect"}
        for instance in context.battle_instances.values():
            if instance.fainted or instance.current_hp <= 0:
                continue
            expired = [vs for vs in instance.volatile_status if vs in volatile_statuses_to_expire]
            if expired:
                for status in expired:
                    instance.volatile_status.remove(status)
                context.add_event(
                    kind="volatile_status_expired",
                    message=f"{instance.pokemon_id}'s {', '.join(expired)} wore off!",
                    target_instance_id=instance.id,
                    volatile_status=expired,
                )

    def _resolve_faints_and_cleanup(self, context: BattleStrategyContext) -> None:
        """Increment the turn counter, update durations, and check for victory."""
        # 1. Check if replacements are needed first
        needs_replacement = False
        for side in context.battle.sides.values():
            if any(slot is None for slot in side.active_pokemon_instance_ids):
                needs_replacement = True
                break

        # 2. Cleanup volatile statuses that expire at end of turn
        self._cleanup_volatile_statuses(context)

        # 3. Only increment turn if no replacements are pending
        # Note: Turn increment moved to after move execution to keep turn number consistent in logs

        # 4. Check for Win Conditions
        # A trainer loses if all their pokemon are fainted (not just active ones).
        # However, for the scope of this resolution step, we check if anyone has NO pokemon left.
        # The logic for "replacements" will be handled by the phase transition.

        active_trainers = []
        for trainer_id, _side in context.battle.sides.items():
            # Check if this trainer has any pokemon that can still fight
            # This requires checking the party, but for now we look at the active instances
            # and assume if they all fainted and no replacements, they lose.
            # TODO: Integrate with a PartyService to check total fainted count.
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
                message=f"{winner_name} won the battle!",
                winner_trainer_id=winner_id,
            )
        elif len(active_trainers) == 0:
            context.battle.status = "finished"
            context.add_event(kind="battle_finished", message="The battle ended in a draw!")

        # 4. Phase Transition
        # If the battle isn't finished but someone needs to replace a pokemon
        if context.battle.status == "active":
            needs_replacement = False
            for side in context.battle.sides.values():
                if any(slot is None for slot in side.active_pokemon_instance_ids):
                    needs_replacement = True
                    break

            if needs_replacement:
                context.battle.phase = "awaiting_replacements"
            else:
                context.battle.phase = "awaiting_actions"
