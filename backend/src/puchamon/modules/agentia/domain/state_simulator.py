"""State simulation utilities for AI Minimax."""

import copy
from collections.abc import Mapping

from ...battle.domain.entities import Battle, BattleInstance
from ...pokedex.domain.entities import Movement
from .action_utils import Action
from .damage_calculator import calculate_simulated_damage


def simulate_state_transition(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    action: Action,
    acting_trainer_id: str,
    opposing_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
) -> tuple[Battle, dict[str, BattleInstance]]:
    """Clone the state and apply one deterministic sequential action.

    This is the only transition function used by Minimax. It assumes every move hits and delegates all stochastic
    uncertainty to the leaf heuristic through deterministic expected-damage helpers.
    """
    battle_copy = copy.deepcopy(battle)
    instances_copy = copy.deepcopy(instances)
    return _apply_action_to_state(battle_copy, instances_copy, action, acting_trainer_id, opposing_trainer_id, movements)


def simulate_action(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    action: Action,
    player_trainer_id: str,
    opponent_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
) -> tuple[Battle, dict[str, BattleInstance]]:
    """Simulate an action and return the resulting cloned state.

    Args:
        battle: The battle state to modify.
        instances: The battle instances to modify.
        action: The action to simulate (action_type, action_id).
        player_trainer_id: The acting trainer ID.
        opponent_trainer_id: The opposing trainer ID.
        movements: Dict of Movement entities.

    Returns:
        Tuple of (modified_battle, modified_instances).
    """
    return simulate_state_transition(battle, instances, action, player_trainer_id, opponent_trainer_id, movements)


def _apply_action_to_state(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    action: Action,
    acting_trainer_id: str,
    opposing_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
) -> tuple[Battle, dict[str, BattleInstance]]:
    action_type, action_id = action

    if action_type == "MOVE":
        return _simulate_move(battle, instances, action_id, acting_trainer_id, opposing_trainer_id, movements)
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

    damage = calculate_simulated_damage(move, actor_instance, target_instance)
    target_instance.current_hp = max(0, target_instance.current_hp - damage)

    if target_instance.current_hp <= 0:
        target_instance.fainted = True
        _remove_active_instance(opposing_side.active_pokemon_instance_ids, str(target_instance.id))

    return battle, instances


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
