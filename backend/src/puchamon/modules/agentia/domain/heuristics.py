"""Heuristic functions for AI decision making."""

from ...battle.domain.entities import Battle, BattleInstance


def get_opponent_hp_values(
    battle: Battle,
    instances: dict[str, BattleInstance],
    exclude_trainer_id: str | None = None,
) -> tuple[int, int] | None:
    """Get the opponent's current and max HP.

    Args:
        battle: The current battle state.
        instances: Dict of battle instances keyed by ID.
        exclude_trainer_id: Optional trainer ID to exclude (usually the current player).

    Returns:
        Tuple of (current_hp, max_hp) or None if no opponent found.
    """
    for trainer_id, side in battle.sides.items():
        if exclude_trainer_id and trainer_id == exclude_trainer_id:
            continue
        if active_id := side.active_pokemon_instance_ids[0]:
            opponent = instances.get(active_id)
            if opponent and not opponent.fainted:
                return (opponent.current_hp, opponent.max_hp)
    return None


def calculate_hp_score(
    move_power: int,
    opponent_current_hp: int,
    opponent_max_hp: int,
) -> float:
    """Calculate heuristic score for a move based on opponent HP.

    h(move) = 1 - HP_percent_post

    Args:
        move_power: Power of the move being evaluated.
        opponent_current_hp: Current HP of the opponent.
        opponent_max_hp: Max HP of the opponent.

    Returns:
        Heuristic score (higher = better move).
    """
    hp_post = opponent_current_hp - move_power
    hp_percent_post = max(0, hp_post) / opponent_max_hp
    return 1.0 - hp_percent_post
