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


def get_hp_percent(instance: BattleInstance) -> float:
    """Get the HP percentage of a battle instance.

    Args:
        instance: The battle instance to evaluate.

    Returns:
        HP percentage as a float between 0.0 and 1.0.
    """
    if instance.fainted or instance.max_hp <= 0:
        return 0.0
    return max(0.0, min(1.0, instance.current_hp / instance.max_hp))


def evaluate_level_2(
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
) -> float:
    """Evaluate battle state using only HP percentage (Level 2 heuristic).

    Returns a score normalized to [-1.0, 1.0] representing how favorable
    the position is for the player. Positive values favor the player,
    negative values favor the opponent.

    Score = player_hp_percent - opponent_hp_percent (clamped to [-1, 1])

    Args:
        battle: The current battle state.
        instances: Dict of battle instances keyed by ID.
        player_trainer_id: The trainer ID of the player being evaluated.

    Returns:
        Heuristic score between -1.0 and 1.0.
    """
    player_hp = 0.0
    opponent_hp = 0.0

    for trainer_id, side in battle.sides.items():
        if not side.active_pokemon_instance_ids:
            continue
        active_id = side.active_pokemon_instance_ids[0]
        if active_id is None:
            continue
        instance = instances.get(active_id)
        if instance is None or instance.fainted:
            continue

        hp_percent = get_hp_percent(instance)

        if trainer_id == player_trainer_id:
            player_hp = hp_percent
        else:
            opponent_hp = hp_percent

    hp_diff = player_hp - opponent_hp
    return max(-1.0, min(1.0, hp_diff))


def evaluate_level_3(
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
) -> float:
    """Evaluate battle state using multiple factors (Level 3 heuristic).

    Returns a score normalized to [-1.0, 1.0] representing how favorable
    the position is for the player. Positive values favor the player,
    negative values favor the opponent.

    Factors (all normalized to [-1, 1]):
    - HP advantage: Difference in HP percentage between active Pokemon
    - Type matchup: Advantage based on type effectiveness (future)
    - Status advantage: Benefit from status conditions
    - Field presence: Number of alive Pokemon differences

    Args:
        battle: The current battle state.
        instances: Dict of battle instances keyed by ID.
        player_trainer_id: The trainer ID of the player being evaluated.

    Returns:
        Heuristic score between -1.0 and 1.0.
    """
    player_hp = 0.0
    opponent_hp = 0.0
    player_alive_count = 0
    opponent_alive_count = 0
    player_has_status_advantage = False
    opponent_has_status_advantage = False

    for trainer_id, _side in battle.sides.items():
        is_player = trainer_id == player_trainer_id

        for instance in instances.values():
            if instance.trainer_id != trainer_id:
                continue
            if instance.fainted:
                continue

            hp_percent = get_hp_percent(instance)

            if is_player:
                player_hp = hp_percent
                player_alive_count += 1
                if instance.status is not None:
                    player_has_status_advantage = True
            else:
                opponent_hp = hp_percent
                opponent_alive_count += 1
                if instance.status is not None:
                    opponent_has_status_advantage = True

    hp_factor = max(-1.0, min(1.0, player_hp - opponent_hp))

    alive_diff = player_alive_count - opponent_alive_count
    field_factor = max(-1.0, min(1.0, alive_diff / 3.0))

    status_factor = 0.0
    if player_has_status_advantage and not opponent_has_status_advantage:
        status_factor = 0.3
    elif opponent_has_status_advantage and not player_has_status_advantage:
        status_factor = -0.3

    total_score = (0.5 * hp_factor) + (0.3 * field_factor) + (0.2 * status_factor)

    return max(-1.0, min(1.0, total_score))
