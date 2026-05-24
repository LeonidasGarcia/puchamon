"""Utility functions for action selection in AI."""

from ...battle.domain.entities import Battle, BattleInstance

Action = tuple[str, str]


def get_opponent_trainer_id(battle: Battle, player_trainer_id: str) -> str | None:
    """Get the opponent's trainer ID.

    Args:
        battle: The battle state.
        player_trainer_id: The player's trainer ID.

    Returns:
        The opponent's trainer ID or None if not found.
    """
    for trainer_id in battle.sides.keys():
        if trainer_id != player_trainer_id:
            return trainer_id
    return None


def get_available_actions(
    battle: Battle,
    instances: dict[str, BattleInstance],
    trainer_id: str,
) -> list[Action]:
    """Get all available actions (moves and switches) for the player.

    Args:
        battle: The battle state to evaluate.
        instances: The battle instances to evaluate.
        trainer_id: The trainer ID of the player.

    Returns:
        List of Action tuples (action_type, action_id).
    """
    actions: list[Action] = []

    side = battle.sides.get(trainer_id)
    if not side:
        return actions

    active_ids = [uid for uid in side.active_pokemon_instance_ids if uid is not None]
    active_instance_id = active_ids[0] if active_ids else None

    if active_instance_id:
        active_instance = instances.get(active_instance_id)
        if active_instance and not active_instance.fainted:
            for ms in active_instance.move_state:
                if ms.current_pp > 0:
                    actions.append(("MOVE", ms.move_id))

    for instance in instances.values():
        if instance.trainer_id != trainer_id:
            continue
        if instance.fainted:
            continue
        if active_instance_id and instance.id == active_instance_id:
            continue
        if instance.slot is not None:
            continue
        actions.append(("SWITCH", str(instance.id)))

    return actions
