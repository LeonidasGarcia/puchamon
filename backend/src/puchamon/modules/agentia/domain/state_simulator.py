"""State simulation utilities for AI Minimax."""


from ...battle.domain.entities import Battle, BattleInstance
from .action_utils import Action
from .damage_calculator import calculate_damage


def simulate_action(
    battle: Battle,
    instances: dict[str, BattleInstance],
    action: Action,
    player_trainer_id: str,
    opponent_trainer_id: str,
    movements: dict | None = None,
) -> tuple[Battle, dict[str, BattleInstance]]:
    """Simulate an action and return the resulting state.

    Args:
        battle: The battle state to modify.
        instances: The battle instances to modify.
        action: The action to simulate (action_type, action_id).
        player_trainer_id: The AI player's trainer ID.
        opponent_trainer_id: The opponent's trainer ID.
        movements: Dict of Movement entities.

    Returns:
        Tuple of (modified_battle, modified_instances).
    """
    action_type, action_id = action

    if action_type == "MOVE":
        return _simulate_move(battle, instances, action_id, player_trainer_id, opponent_trainer_id, movements)
    elif action_type == "SWITCH":
        return _simulate_switch(battle, instances, action_id, player_trainer_id)
    return battle, instances


def _simulate_move(
    battle: Battle,
    instances: dict[str, BattleInstance],
    move_id: str,
    player_trainer_id: str,
    opponent_trainer_id: str,
    movements: dict | None = None,
) -> tuple[Battle, dict[str, BattleInstance]]:
    """Simulate a move action."""
    move = movements.get(move_id) if movements else None
    if move is None or move.power is None:
        return battle, instances

    player_side = battle.sides.get(player_trainer_id)
    opponent_side = battle.sides.get(opponent_trainer_id)

    if not player_side or not opponent_side:
        return battle, instances

    player_active_ids = [uid for uid in player_side.active_pokemon_instance_ids if uid is not None]
    opponent_active_ids = [uid for uid in opponent_side.active_pokemon_instance_ids if uid is not None]

    if not player_active_ids or not opponent_active_ids:
        return battle, instances

    player_instance = instances.get(player_active_ids[0])
    opponent_instance = instances.get(opponent_active_ids[0])

    if not player_instance or not opponent_instance:
        return battle, instances

    if player_instance.stats is None or opponent_instance.stats is None:
        return battle, instances

    damage = calculate_damage(move, player_instance, opponent_instance)
    opponent_instance.current_hp = max(0, opponent_instance.current_hp - damage)

    if opponent_instance.current_hp <= 0:
        opponent_instance.fainted = True
        opponent_side.active_pokemon_instance_ids[0] = None

    return battle, instances


def _simulate_switch(
    battle: Battle,
    instances: dict[str, BattleInstance],
    instance_id: str,
    player_trainer_id: str,
) -> tuple[Battle, dict[str, BattleInstance]]:
    """Simulate a switch action."""
    player_side = battle.sides.get(player_trainer_id)
    if not player_side:
        return battle, instances

    current_active_ids = [uid for uid in player_side.active_pokemon_instance_ids if uid is not None]
    new_instance = instances.get(instance_id)

    if not new_instance or new_instance.fainted:
        return battle, instances

    if current_active_ids:
        player_side.active_pokemon_instance_ids[0] = instance_id
    else:
        player_side.active_pokemon_instance_ids = [instance_id]

    return battle, instances
