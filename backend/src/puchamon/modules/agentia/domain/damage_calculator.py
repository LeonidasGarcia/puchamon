"""Damage calculation utilities for both AI search and real resolution contexts."""

from collections.abc import Mapping
from dataclasses import dataclass
from math import floor
from secrets import randbelow
from typing import TYPE_CHECKING, Literal

from ...battle.domain.entities import BattleInstance
from ...pokedex.domain.entities import Movement
from ...pokedex.domain.entities.effects import DamagePayload, RandomRange

if TYPE_CHECKING:
    from ...pokedex.domain.entities import Type

DamageContext = Literal["real", "simulation"]

MIN_REAL_DAMAGE_ROLL_PERCENT = 85
MAX_REAL_DAMAGE_ROLL_PERCENT = 100
SIMULATION_DAMAGE_ROLL_PERCENT = 92.5
SIMULATION_MULTI_HIT_COUNT = 3

_ATTACK_STAT_BY_CATEGORY: dict[str, str] = {
    "physical": "atk",
    "special": "spa",
}
_DEFENSE_STAT_BY_CATEGORY: dict[str, str] = {
    "physical": "def_",
    "special": "spd",
}
_STAGE_ATTRIBUTE_BY_STAT: dict[str, str] = {
    "atk": "atk",
    "def_": "def_",
    "spa": "spa",
    "spd": "spd",
    "spe": "spe",
}


@dataclass(frozen=True, slots=True)
class _DamageInput:
    move: Movement
    source: BattleInstance
    target: BattleInstance
    roll_percent: float
    hit_count: int
    type_chart: Mapping[str, "Type"] | None = None


def _roll_int(start: int, end: int) -> int:
    """Return an inclusive unpredictable integer for real battle resolution."""
    return start + randbelow((end - start) + 1)


def _normalize_token(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _get_stat(instance: BattleInstance, stat_key: str) -> int | None:
    if instance.stats is None:
        return None

    value = getattr(instance.stats, stat_key, None)
    if not isinstance(value, int) or value <= 0:
        return None
    return value


def _get_stage(instance: BattleInstance, stat_key: str) -> int:
    stage_attribute = _STAGE_ATTRIBUTE_BY_STAT.get(stat_key)
    if stage_attribute is None:
        return 0
    if isinstance(instance.stages, Mapping):
        aliased_attribute = "def" if stage_attribute == "def_" else stage_attribute
        return int(instance.stages.get(stage_attribute, instance.stages.get(aliased_attribute, 0)) or 0)
    return getattr(instance.stages, stage_attribute, 0)


def _apply_stage(base_stat: int, stage: int) -> int:
    bounded_stage = max(-6, min(6, stage))
    if bounded_stage >= 0:
        multiplier = (2 + bounded_stage) / 2
    else:
        multiplier = 2 / (2 - bounded_stage)
    return max(1, floor(base_stat * multiplier))


def _resolve_attack_stat_key(move: Movement) -> str:
    return _ATTACK_STAT_BY_CATEGORY.get(move.category.lower(), "atk")


def _resolve_defense_stat_key(move: Movement) -> str:
    return _DEFENSE_STAT_BY_CATEGORY.get(move.category.lower(), "def_")


def _calculate_type_effectiveness(movement_type: str, target_types: list[str], type_chart: Mapping[str, "Type"] | None) -> float:
    if not type_chart:
        return 1.0

    type_data = type_chart.get(_normalize_token(movement_type)) or type_chart.get(movement_type)
    if type_data is None:
        return 1.0

    super_effective = {_normalize_token(type_name) for type_name in type_data.super_effective}
    not_very_effective = {_normalize_token(type_name) for type_name in type_data.not_very_effective}
    no_effect = {_normalize_token(type_name) for type_name in type_data.no_effect}

    effectiveness = 1.0
    for target_type in target_types:
        normalized_target_type = _normalize_token(target_type)
        if normalized_target_type in super_effective:
            effectiveness *= 2.0
        elif normalized_target_type in not_very_effective:
            effectiveness *= 0.5
        elif normalized_target_type in no_effect:
            effectiveness *= 0.0
    return effectiveness


def _calculate_modified_damage(input_data: _DamageInput) -> int:
    move = input_data.move
    if move.power is None or move.power <= 0:
        return 0

    attack_stat_key = _resolve_attack_stat_key(move)
    defense_stat_key = _resolve_defense_stat_key(move)
    attack = _get_stat(input_data.source, attack_stat_key)
    defense = _get_stat(input_data.target, defense_stat_key)
    if attack is None or defense is None:
        return 0

    effective_attack = _apply_stage(attack, _get_stage(input_data.source, attack_stat_key))
    effective_defense = _apply_stage(defense, _get_stage(input_data.target, defense_stat_key))

    level_factor = floor((2 * input_data.source.level) / 5) + 2
    base_damage = floor((((level_factor * move.power * effective_attack) / effective_defense) / 50) + 2)

    source_types = {_normalize_token(source_type) for source_type in input_data.source.types}
    stab = 1.5 if _normalize_token(move.type) in source_types else 1.0
    effectiveness = _calculate_type_effectiveness(move.type, input_data.target.types, input_data.type_chart)

    per_hit_damage = max(1, floor((base_damage * stab * effectiveness * input_data.roll_percent) / 100))
    return per_hit_damage * max(1, input_data.hit_count)


def _resolve_simulated_hit_count(payload: DamagePayload | None) -> int:
    if payload is None:
        return 1
    if isinstance(payload.hits, RandomRange):
        return SIMULATION_MULTI_HIT_COUNT
    return max(1, payload.hits)


def _resolve_real_hit_count(payload: DamagePayload | None) -> int:
    if payload is None:
        return 1
    if isinstance(payload.hits, RandomRange):
        return _roll_int(max(1, payload.hits.min), max(1, payload.hits.max))
    return max(1, payload.hits)


def _real_accuracy_check(move: Movement) -> bool:
    if move.accuracy is None or move.accuracy == 0:
        return True

    bounded_accuracy = max(0, min(100, move.accuracy))
    return _roll_int(1, 100) <= bounded_accuracy


def calculate_simulated_damage(
    move: Movement,
    source: BattleInstance,
    target: BattleInstance,
    payload: DamagePayload | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
) -> int:
    """Calculate deterministic damage for Minimax navigation.

    Simulation never rolls accuracy and never samples damage variance. Multi-hit payloads use a fixed three-hit count,
    while regular damaging moves keep their declared hit count.
    """
    return _calculate_modified_damage(
        _DamageInput(
            move=move,
            source=source,
            target=target,
            roll_percent=SIMULATION_DAMAGE_ROLL_PERCENT,
            hit_count=_resolve_simulated_hit_count(payload),
            type_chart=type_chart,
        )
    )


def calculate_real_damage(
    move: Movement,
    source: BattleInstance,
    target: BattleInstance,
    payload: DamagePayload | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
) -> int:
    """Calculate damage for the real battle context, including accuracy and variance."""
    if not _real_accuracy_check(move):
        return 0

    return _calculate_modified_damage(
        _DamageInput(
            move=move,
            source=source,
            target=target,
            roll_percent=_roll_int(MIN_REAL_DAMAGE_ROLL_PERCENT, MAX_REAL_DAMAGE_ROLL_PERCENT),
            hit_count=_resolve_real_hit_count(payload),
            type_chart=type_chart,
        )
    )


def calculate_damage(  # noqa: PLR0913
    move: Movement,
    source: BattleInstance,
    target: BattleInstance,
    *,
    context: DamageContext = "simulation",
    payload: DamagePayload | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
) -> int:
    """Calculate damage using the requested decision context."""
    if context == "real":
        return calculate_real_damage(move, source, target, payload, type_chart)
    return calculate_simulated_damage(move, source, target, payload, type_chart)
