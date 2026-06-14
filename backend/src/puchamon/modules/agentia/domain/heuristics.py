"""Heuristic functions for AI decision making."""

from collections.abc import Mapping
from math import floor
from typing import TYPE_CHECKING

from ...battle.domain.entities import Battle, BattleInstance
from ...pokedex.domain.entities import MoveEffect, Movement
from .action_utils import get_opponent_trainer_id
from .damage_calculator import calculate_simulated_damage
from .genetic_weights import LEVEL_3_GA_OPTIMIZED_WEIGHTS, LEVEL_3_MANUAL_WEIGHTS

if TYPE_CHECKING:
    from ...pokedex.domain.entities import Type

WEIGHT_VIVOS = 150.0
WEIGHT_HP = 100.0
WEIGHT_MOMENTUM = 80.0
WEIGHT_STAGES = 5.0
PENALTY_INCAPACITATED = -40.0
PENALTY_MAJOR_STATUS = -20.0
PENALTY_VOLATILE = -10.0

_INCAPACITATED_STATUSES = {"sleep", "asleep", "slp", "freeze", "frozen", "frz"}
_MAJOR_STATUSES = {"burn", "burned", "brn", "poison", "poisoned", "bad_poison", "badly_poisoned", "tox", "paralysis", "paralyzed", "par"}
_PARALYSIS_STATUSES = {"paralysis", "paralyzed", "par"}
_PENALIZED_VOLATILE_STATUSES = {"confusion", "confused", "leech_seed", "leechseed"}
_STAGE_UTILITY_BY_STAT = {"atk": 1.0, "spa": 1.1, "spe": 0.9, "def": 0.8, "def_": 0.8, "spd": 0.8, "acc": 0.5, "eva": 0.5}

GENETIC_WEIGHT_KEYS = ("hp", "alive", "damage", "type", "speed", "status", "effects")


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
        active_id = None
        for instance_id in side.active_pokemon_instance_ids:
            if instance_id is not None:
                active_id = instance_id
                break
        if active_id:
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


def _normalize_status(status: str | None) -> str | None:
    if status is None:
        return None
    return status.strip().lower().replace("-", "_").replace(" ", "_")


def _team_instances(instances: dict[str, BattleInstance], trainer_id: str) -> list[BattleInstance]:
    return [instance for instance in instances.values() if instance.trainer_id == trainer_id]


def _alive_team_count(instances: dict[str, BattleInstance], trainer_id: str) -> int:
    return sum(1 for instance in _team_instances(instances, trainer_id) if not instance.fainted and instance.current_hp > 0)


def _team_hp_percent(instances: dict[str, BattleInstance], trainer_id: str) -> float:
    max_hp = sum(max(0, instance.max_hp) for instance in _team_instances(instances, trainer_id))
    if max_hp <= 0:
        return 0.0

    current_hp = sum(max(0, min(instance.current_hp, instance.max_hp)) for instance in _team_instances(instances, trainer_id))
    return current_hp / max_hp


def _active_instances(battle: Battle, instances: dict[str, BattleInstance], trainer_id: str) -> list[BattleInstance]:
    side = battle.sides.get(trainer_id)
    if side is None:
        return []

    active_instances: list[BattleInstance] = []
    for instance_id in side.active_pokemon_instance_ids:
        if instance_id is None:
            continue
        instance = instances.get(instance_id)
        if instance is not None and not instance.fainted and instance.current_hp > 0:
            active_instances.append(instance)
    return active_instances


def _first_active_instance(battle: Battle, instances: dict[str, BattleInstance], trainer_id: str) -> BattleInstance | None:
    active_instances = _active_instances(battle, instances, trainer_id)
    return active_instances[0] if active_instances else None


def _status_penalty(instance: BattleInstance) -> float:
    penalty = 0.0
    normalized_status = _normalize_status(instance.status)
    if normalized_status in _INCAPACITATED_STATUSES:
        penalty += PENALTY_INCAPACITATED
    elif normalized_status in _MAJOR_STATUSES:
        penalty += PENALTY_MAJOR_STATUS

    for volatile_status in instance.volatile_status:
        if _normalize_status(volatile_status) in _PENALIZED_VOLATILE_STATUSES:
            penalty += PENALTY_VOLATILE
    return penalty


def _active_status_penalty(battle: Battle, instances: dict[str, BattleInstance], trainer_id: str) -> float:
    return sum(_status_penalty(instance) for instance in _active_instances(battle, instances, trainer_id))


def _stage_values(instance: BattleInstance) -> float:
    if isinstance(instance.stages, Mapping):
        stage_data = instance.stages
    elif hasattr(instance.stages, "model_dump"):
        stage_data = instance.stages.model_dump()
    else:
        stage_data = vars(instance.stages)
    return float(sum(value for value in stage_data.values() if isinstance(value, (int, float))))


def _stage_value(instance: BattleInstance, stage_attribute: str) -> int:
    if isinstance(instance.stages, Mapping):
        aliased_attribute = "def" if stage_attribute == "def_" else stage_attribute
        return int(instance.stages.get(stage_attribute, instance.stages.get(aliased_attribute, 0)) or 0)
    return getattr(instance.stages, stage_attribute, 0)


def _active_stage_total(battle: Battle, instances: dict[str, BattleInstance], trainer_id: str) -> float:
    return sum(_stage_values(instance) for instance in _active_instances(battle, instances, trainer_id))


def _apply_stage(base_stat: int, stage: int) -> int:
    bounded_stage = max(-6, min(6, stage))
    if bounded_stage >= 0:
        multiplier = (2 + bounded_stage) / 2
    else:
        multiplier = 2 / (2 - bounded_stage)
    return max(1, floor(base_stat * multiplier))


def _effective_speed(instance: BattleInstance) -> int:
    if instance.stats is None:
        return 0

    speed = _apply_stage(instance.stats.spe, _stage_value(instance, "spe"))
    if _normalize_status(instance.status) in _PARALYSIS_STATUSES:
        return max(1, floor(speed * 0.5))
    return speed


def _move_accuracy(move: Movement) -> float:
    if move.accuracy is None or move.accuracy == 0:
        return 100.0
    return float(max(0, min(100, move.accuracy)))


def _offensive_pressure_for_pair(
    attacker: BattleInstance,
    target: BattleInstance,
    movements: Mapping[str, Movement] | None,
    type_chart: Mapping[str, "Type"] | None,
) -> float:
    if movements is None or target.max_hp <= 0:
        return 0.0

    speed_modifier = 1.2 if _effective_speed(attacker) > _effective_speed(target) else 1.0
    best_pressure = 0.0
    for move_state in attacker.move_state:
        if move_state.current_pp <= 0:
            continue
        move = movements.get(move_state.move_id)
        if move is None or move.power is None or move.power <= 0:
            continue

        simulated_damage = calculate_simulated_damage(move, attacker, target, type_chart=type_chart)
        expected_damage = simulated_damage * (_move_accuracy(move) / 100)
        pressure = (expected_damage / target.max_hp) * speed_modifier
        best_pressure = max(best_pressure, pressure)
    return best_pressure


def _team_offensive_pressure(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    trainer_id: str,
    opponent_trainer_id: str,
    movements: Mapping[str, Movement] | None,
    type_chart: Mapping[str, "Type"] | None,
) -> float:
    attackers = _active_instances(battle, instances, trainer_id)
    targets = _active_instances(battle, instances, opponent_trainer_id)
    if not attackers or not targets:
        return 0.0

    total_pressure = 0.0
    for attacker in attackers:
        total_pressure += max(_offensive_pressure_for_pair(attacker, target, movements, type_chart) for target in targets)
    return total_pressure


def _clamp_unit(value: float) -> float:
    return max(-1.0, min(1.0, value))


def _normalize_weight_mapping(weights: Mapping[str, float] | None) -> dict[str, float]:
    raw_weights = LEVEL_3_GA_OPTIMIZED_WEIGHTS if weights is None else weights
    normalized_weights = {key: max(0.0, float(raw_weights.get(key, 0.0))) for key in GENETIC_WEIGHT_KEYS}
    total = sum(normalized_weights.values())
    if total <= 0:
        return dict(LEVEL_3_GA_OPTIMIZED_WEIGHTS)
    return {key: value / total for key, value in normalized_weights.items()}


def _type_effectiveness(movement_type: str, target_types: list[str], type_chart: Mapping[str, "Type"] | None) -> float:
    if not type_chart:
        return 1.0

    normalized_movement_type = movement_type.strip().lower().replace("-", "_").replace(" ", "_")
    type_data = type_chart.get(normalized_movement_type) or type_chart.get(movement_type)
    if type_data is None:
        return 1.0

    super_effective = {type_name.strip().lower().replace("-", "_").replace(" ", "_") for type_name in type_data.super_effective}
    not_very_effective = {type_name.strip().lower().replace("-", "_").replace(" ", "_") for type_name in type_data.not_very_effective}
    no_effect = {type_name.strip().lower().replace("-", "_").replace(" ", "_") for type_name in type_data.no_effect}

    effectiveness = 1.0
    for target_type in target_types:
        normalized_target_type = target_type.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized_target_type in super_effective:
            effectiveness *= 2.0
        elif normalized_target_type in not_very_effective:
            effectiveness *= 0.5
        elif normalized_target_type in no_effect:
            effectiveness *= 0.0
    return effectiveness


def _best_type_matchup_for_pair(
    attacker: BattleInstance,
    target: BattleInstance,
    movements: Mapping[str, Movement] | None,
    type_chart: Mapping[str, "Type"] | None,
) -> float:
    if movements is None:
        return 0.0

    best_effectiveness = 1.0
    for move_state in attacker.move_state:
        if move_state.current_pp <= 0:
            continue
        move = movements.get(move_state.move_id)
        if move is None or move.power is None or move.power <= 0:
            continue
        best_effectiveness = max(best_effectiveness, _type_effectiveness(move.type, target.types, type_chart))
    return _clamp_unit((best_effectiveness - 1.0) / 3.0)


def _team_type_matchup_score(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    trainer_id: str,
    opponent_trainer_id: str,
    movements: Mapping[str, Movement] | None,
    type_chart: Mapping[str, "Type"] | None,
) -> float:
    attackers = _active_instances(battle, instances, trainer_id)
    targets = _active_instances(battle, instances, opponent_trainer_id)
    if not attackers or not targets:
        return 0.0

    matchup_scores = []
    for attacker in attackers:
        matchup_scores.append(max(_best_type_matchup_for_pair(attacker, target, movements, type_chart) for target in targets))
    return sum(matchup_scores) / len(matchup_scores)


def _team_speed_score(battle: Battle, instances: dict[str, BattleInstance], trainer_id: str) -> float:
    active_instances = _active_instances(battle, instances, trainer_id)
    if not active_instances:
        return 0.0
    return sum(_effective_speed(instance) for instance in active_instances) / len(active_instances)


def _effect_scope_multiplier(effect: MoveEffect) -> float:
    if effect.target in {"self", "ally_side"}:
        return 1.0
    if effect.target in {"target", "foe_side"}:
        return -1.0
    return 0.0


def _modify_stat_effect_utility(effect: MoveEffect) -> float:
    payload = effect.payload
    changes = getattr(payload, "changes", None)
    if not changes:
        return 0.0

    scope_multiplier = _effect_scope_multiplier(effect)
    if scope_multiplier == 0.0:
        return 0.0

    utility = 0.0
    for change in changes:
        stat = "def_" if change.stat == "def" else change.stat
        stat_weight = _STAGE_UTILITY_BY_STAT.get(stat, 0.5)
        utility += change.stages * stat_weight * 0.06 * scope_multiplier
    return utility


def _move_effect_utility(effect: MoveEffect) -> float:
    chance_multiplier = max(0.0, min(1.0, effect.chance / 100))
    if effect.kind == "damage":
        return 0.0
    if effect.kind == "modify_stat":
        return _modify_stat_effect_utility(effect) * chance_multiplier
    if effect.kind in {"apply_major_status", "apply_volatile_status"}:
        return -0.12 * _effect_scope_multiplier(effect) * chance_multiplier
    if effect.kind == "heal_hp":
        return 0.15 * _effect_scope_multiplier(effect) * chance_multiplier
    if effect.kind == "protect":
        return 0.10 * _effect_scope_multiplier(effect) * chance_multiplier
    return 0.0


def _team_move_effect_utility(
    battle: Battle,
    instances: dict[str, BattleInstance],
    trainer_id: str,
    movements: Mapping[str, Movement] | None,
    move_effects: Mapping[str, MoveEffect] | None,
) -> float:
    if movements is None:
        return 0.0

    active_instances = _active_instances(battle, instances, trainer_id)
    if not active_instances:
        return 0.0

    total_utility = 0.0
    for instance in active_instances:
        instance_utility: float | None = None
        for move_state in instance.move_state:
            if move_state.current_pp <= 0:
                continue
            move = movements.get(move_state.move_id)
            if move is None:
                continue
            if move_effects:
                effect_utility = sum(_move_effect_utility(move_effects[effect_id]) for effect_id in move.effect_ids if effect_id in move_effects)
                effect_utility = max(-0.30, min(0.30, effect_utility))
            else:
                effect_utility = min(0.30, len(move.effect_ids) * 0.05)
            status_move_bonus = 0.20 if move.power is None or move.power <= 0 else 0.0
            move_utility = effect_utility + status_move_bonus
            instance_utility = move_utility if instance_utility is None else max(instance_utility, move_utility)
        total_utility += max(-1.0, min(1.0, instance_utility or 0.0))
    return total_utility / len(active_instances)


def _weighted_level_3_factors(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
    opponent_trainer_id: str,
    movements: Mapping[str, Movement] | None,
    move_effects: Mapping[str, MoveEffect] | None,
    type_chart: Mapping[str, "Type"] | None,
) -> dict[str, float]:
    player_team_size = max(1, len(_team_instances(instances, player_trainer_id)))
    opponent_team_size = max(1, len(_team_instances(instances, opponent_trainer_id)))
    max_team_size = max(player_team_size, opponent_team_size)

    player_speed = _team_speed_score(battle, instances, player_trainer_id)
    opponent_speed = _team_speed_score(battle, instances, opponent_trainer_id)
    max_speed = max(1.0, player_speed, opponent_speed)

    player_status_penalty = _active_status_penalty(battle, instances, player_trainer_id)
    opponent_status_penalty = _active_status_penalty(battle, instances, opponent_trainer_id)
    opponent_active = _first_active_instance(battle, instances, opponent_trainer_id)
    opponent_active_hp = get_hp_percent(opponent_active) if opponent_active is not None else 0.0

    return {
        "hp": _clamp_unit(_team_hp_percent(instances, player_trainer_id) - opponent_active_hp),
        "alive": _clamp_unit((_alive_team_count(instances, player_trainer_id) - _alive_team_count(instances, opponent_trainer_id)) / max_team_size),
        "damage": _clamp_unit(
            _team_offensive_pressure(battle, instances, player_trainer_id, opponent_trainer_id, movements, type_chart)
            - _team_offensive_pressure(battle, instances, opponent_trainer_id, player_trainer_id, movements, type_chart)
        ),
        "type": _clamp_unit(
            _team_type_matchup_score(battle, instances, player_trainer_id, opponent_trainer_id, movements, type_chart)
            - _team_type_matchup_score(battle, instances, opponent_trainer_id, player_trainer_id, movements, type_chart)
        ),
        "speed": _clamp_unit((player_speed - opponent_speed) / max_speed),
        "status": _clamp_unit(
            (player_status_penalty - opponent_status_penalty) / abs(PENALTY_INCAPACITATED + PENALTY_MAJOR_STATUS + PENALTY_VOLATILE)
        ),
        "effects": _clamp_unit(
            _team_move_effect_utility(battle, instances, player_trainer_id, movements, move_effects)
            - _team_move_effect_utility(battle, instances, opponent_trainer_id, movements, move_effects)
        ),
    }


def evaluate_level_2(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,  # noqa: ARG001
    type_chart: Mapping[str, "Type"] | None = None,  # noqa: ARG001
    move_effects: Mapping[str, MoveEffect] | None = None,  # noqa: ARG001
) -> float:
    """Evaluate battle state using only HP percentage (Level 2 heuristic).

    Score = team HP percentage for the AI side minus the active opponent HP percentage.

    Args:
        battle: The current battle state.
        instances: Dict of battle instances keyed by ID.
        player_trainer_id: The trainer ID of the player being evaluated.
        movements: Unused in this level; kept to share the Minimax heuristic signature.
        type_chart: Unused in this level; kept to share the Minimax heuristic signature.

    Returns:
        Heuristic score where positive values favor the player.
    """
    opponent_trainer_id = get_opponent_trainer_id(battle, player_trainer_id)
    opponent_active = _first_active_instance(battle, instances, opponent_trainer_id) if opponent_trainer_id else None
    opponent_active_hp = get_hp_percent(opponent_active) if opponent_active is not None else 0.0

    return _team_hp_percent(instances, player_trainer_id) - opponent_active_hp


def evaluate_level_3_manual(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
    move_effects: Mapping[str, MoveEffect] | None = None,
) -> float:
    """Evaluate battle state with the manually tuned advanced heuristic."""
    return evaluate_level_3_weighted(
        battle,
        instances,
        player_trainer_id,
        movements=movements,
        move_effects=move_effects,
        type_chart=type_chart,
        weights=LEVEL_3_MANUAL_WEIGHTS,
    )


def evaluate_level_3_ga(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
    move_effects: Mapping[str, MoveEffect] | None = None,
) -> float:
    """Evaluate battle state with the GA-optimized advanced heuristic."""
    return evaluate_level_3_weighted(
        battle,
        instances,
        player_trainer_id,
        movements=movements,
        move_effects=move_effects,
        type_chart=type_chart,
        weights=LEVEL_3_GA_OPTIMIZED_WEIGHTS,
    )


def evaluate_level_3(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
    move_effects: Mapping[str, MoveEffect] | None = None,
) -> float:
    """Evaluate battle state with the GA-optimized advanced heuristic."""
    return evaluate_level_3_ga(battle, instances, player_trainer_id, movements=movements, move_effects=move_effects, type_chart=type_chart)


def evaluate_level_3_weighted(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
    movements: Mapping[str, Movement] | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
    weights: Mapping[str, float] | None = None,
    move_effects: Mapping[str, MoveEffect] | None = None,
) -> float:
    """Evaluate a configurable GA-friendly Level 3 heuristic.

    The genetic algorithm uses normalized real-coded chromosomes over seven factors: HP, alive count, expected damage,
    type matchup, speed, status and move-effect utility. This function keeps those factors in a comparable [-1, 1]
    range before applying the normalized weights.
    """
    opponent_trainer_id = get_opponent_trainer_id(battle, player_trainer_id)
    if opponent_trainer_id is None:
        return 0.0

    normalized_weights = _normalize_weight_mapping(weights)
    factors = _weighted_level_3_factors(battle, instances, player_trainer_id, opponent_trainer_id, movements, move_effects, type_chart)
    return sum(normalized_weights[key] * factors[key] for key in GENETIC_WEIGHT_KEYS)
