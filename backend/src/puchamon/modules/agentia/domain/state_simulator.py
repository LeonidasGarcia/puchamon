"""State simulation utilities for AI Minimax."""

import copy
from collections.abc import Mapping
from typing import TYPE_CHECKING

from ...battle.domain.entities import Battle, BattleInstance
from ...battle.domain.rules import MAX_STAT_STAGE, MIN_STAT_STAGE
from ...pokedex.domain.entities import MoveEffect, Movement
from .action_utils import Action
from .damage_calculator import calculate_simulated_damage, resolve_move_damage_payload

if TYPE_CHECKING:
    from ...pokedex.domain.entities import Type

GUARANTEED_EFFECT_CHANCE = 100


def simulate_state_transition(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    action: Action,
    acting_trainer_id: str,
    opposing_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
    move_effects: Mapping[str, MoveEffect] | None = None,
) -> tuple[Battle, dict[str, BattleInstance]]:
    """Clone the state and apply one deterministic sequential action.

    This is the only transition function used by Minimax. It assumes every move hits and delegates all stochastic
    uncertainty to the leaf heuristic through deterministic expected-damage helpers.
    """
    battle_copy = copy.deepcopy(battle)
    instances_copy = copy.deepcopy(instances)
    return _apply_action_to_state(battle_copy, instances_copy, action, acting_trainer_id, opposing_trainer_id, movements, type_chart, move_effects)


def simulate_action(
    battle: Battle,
    instances: dict[str, BattleInstance],
    action: Action,
    player_trainer_id: str,
    opponent_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
    move_effects: Mapping[str, MoveEffect] | None = None,
) -> tuple[Battle, dict[str, BattleInstance]]:
    """Simulate an action and return the resulting cloned state."""
    return simulate_state_transition(battle, instances, action, player_trainer_id, opponent_trainer_id, movements, type_chart, move_effects)


def _apply_action_to_state(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    action: Action,
    acting_trainer_id: str,
    opposing_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
    move_effects: Mapping[str, MoveEffect] | None = None,
) -> tuple[Battle, dict[str, BattleInstance]]:
    action_type, action_id = action

    if action_type == "MOVE":
        return _simulate_move(battle, instances, action_id, acting_trainer_id, opposing_trainer_id, movements, type_chart, move_effects)
    if action_type == "SWITCH":
        return _simulate_switch(battle, instances, action_id, acting_trainer_id)
    return battle, instances


def _simulate_move(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    move_id: str,
    acting_trainer_id: str,
    opposing_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
    move_effects: Mapping[str, MoveEffect] | None = None,
) -> tuple[Battle, dict[str, BattleInstance]]:
    """Simulate a deterministic move action by the acting trainer."""
    move = movements.get(move_id) if movements else None
    if move is None:
        return battle, instances

    acting_side = battle.sides.get(acting_trainer_id)
    opposing_side = battle.sides.get(opposing_trainer_id)

    if not acting_side or not opposing_side:
        return battle, instances

    actor_instance = _first_usable_active_instance(acting_side.active_pokemon_instance_ids, instances)
    target_instance = _first_usable_active_instance(opposing_side.active_pokemon_instance_ids, instances)

    if actor_instance is None or target_instance is None:
        return battle, instances

    move_state = next((candidate for candidate in actor_instance.move_state if candidate.move_id == move_id), None)
    if move_state is not None:
        move_state.current_pp = max(0, move_state.current_pp - 1)

    payload = resolve_move_damage_payload(move, move_effects)
    damage = calculate_simulated_damage(move, actor_instance, target_instance, payload=payload, type_chart=type_chart)
    target_instance.current_hp = max(0, target_instance.current_hp - damage)
    _simulate_move_stat_effects(move, actor_instance, target_instance, move_effects)

    if target_instance.current_hp <= 0:
        target_instance.fainted = True
        _remove_active_instance(opposing_side.active_pokemon_instance_ids, str(target_instance.id))

    return battle, instances


def _simulate_move_stat_effects(
    move: Movement,
    actor_instance: BattleInstance,
    target_instance: BattleInstance,
    move_effects: Mapping[str, MoveEffect] | None,
) -> None:
    if not move_effects:
        return

    for effect_id in move.effect_ids:
        effect = move_effects.get(effect_id)
        if effect is None or effect.kind != "modify_stat" or effect.chance < GUARANTEED_EFFECT_CHANCE:
            continue
        for affected_instance in _resolve_effect_targets(effect, actor_instance, target_instance):
            _apply_modify_stat_effect(affected_instance, effect)


def _resolve_effect_targets(effect: MoveEffect, actor_instance: BattleInstance, target_instance: BattleInstance) -> list[BattleInstance]:
    if effect.target == "self":
        return [actor_instance]
    if effect.target == "target" and not target_instance.fainted and target_instance.current_hp > 0:
        return [target_instance]
    return []


def _apply_modify_stat_effect(instance: BattleInstance, effect: MoveEffect) -> None:
    changes = getattr(effect.payload, "changes", None)
    if not changes or instance.fainted or instance.current_hp <= 0:
        return

    for change in changes:
        stat_key = "def_" if change.stat == "def" else change.stat
        if not hasattr(instance.stages, stat_key):
            continue
        current_stage = getattr(instance.stages, stat_key)
        new_stage = max(MIN_STAT_STAGE, min(MAX_STAT_STAGE, current_stage + change.stages))
        setattr(instance.stages, stat_key, new_stage)


def _simulate_switch(
    battle: Battle,
    instances: dict[str, BattleInstance],
    instance_id: str,
    acting_trainer_id: str,
) -> tuple[Battle, dict[str, BattleInstance]]:
    """Simulate a switch action."""
    acting_side = battle.sides.get(acting_trainer_id)
    if not acting_side:
        return battle, instances

    new_instance = instances.get(instance_id)

    if not new_instance or new_instance.trainer_id != acting_trainer_id or new_instance.fainted or new_instance.current_hp <= 0:
        return battle, instances

    if instance_id in acting_side.active_pokemon_instance_ids:
        return battle, instances

    target_slot = _resolve_switch_slot(acting_side.active_pokemon_instance_ids)
    if target_slot is None:
        acting_side.active_pokemon_instance_ids.append(instance_id)
    else:
        acting_side.active_pokemon_instance_ids[target_slot] = instance_id
    new_instance.is_revealed = True

    return battle, instances


def _first_usable_active_instance(active_instance_ids: list[str | None], instances: dict[str, BattleInstance]) -> BattleInstance | None:
    for instance_id in active_instance_ids:
        if instance_id is None:
            continue
        instance = instances.get(instance_id)
        if instance is not None and not instance.fainted and instance.current_hp > 0:
            return instance
    return None


def _remove_active_instance(active_instance_ids: list[str | None], instance_id: str) -> None:
    for index, active_instance_id in enumerate(active_instance_ids):
        if active_instance_id == instance_id:
            active_instance_ids[index] = None
            return


def _resolve_switch_slot(active_instance_ids: list[str | None]) -> int | None:
    for index, active_instance_id in enumerate(active_instance_ids):
        if active_instance_id is None:
            return index

    for index, active_instance_id in enumerate(active_instance_ids):
        if active_instance_id is not None:
            return index
    return None
