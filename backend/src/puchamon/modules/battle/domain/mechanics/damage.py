"""Helpers for battle damage calculation."""

from math import floor
from random import randint
from typing import TYPE_CHECKING

from ....pokedex.domain.entities import Movement
from ....pokedex.domain.entities.effects import DamagePayload, RandomRange
from ..entities import BattleInstance
from ..exceptions import BattleValidationError
from ..rules import MAX_DAMAGE_ROLL_PERCENT, MIN_DAMAGE_ROLL_PERCENT

if TYPE_CHECKING:
    from ....pokedex.domain.entities import Type

_ATTACK_STAT_BY_CATEGORY: dict[str, str] = {
    "physical": "atk",
    "special": "spa",
}

_DEFAULT_DEFENSE_STAT_BY_CATEGORY: dict[str, str] = {
    "physical": "def",
    "special": "spd",
}

_STAGE_ATTRIBUTE_BY_STAT: dict[str, str] = {
    "atk": "atk",
    "def": "def_",
    "def_": "def_",
    "spa": "spa",
    "spd": "spd",
    "spe": "spe",
}


def resolve_damage_hit_count(payload: DamagePayload) -> int:
    """Return the deterministic hit count used for a damage effect."""
    if isinstance(payload.hits, RandomRange):
        return max(1, payload.hits.min)
    return max(1, payload.hits)


def resolve_damage_roll_percent(damage_roll_percent: int | None = None) -> int:
    """Return a validated damage roll percent or sample one from the battle rules."""
    if damage_roll_percent is None:
        return randint(MIN_DAMAGE_ROLL_PERCENT, MAX_DAMAGE_ROLL_PERCENT)

    if isinstance(damage_roll_percent, bool) or not isinstance(damage_roll_percent, int):
        raise BattleValidationError("Damage roll percent must be an integer between 85 and 100")
    if damage_roll_percent < MIN_DAMAGE_ROLL_PERCENT or damage_roll_percent > MAX_DAMAGE_ROLL_PERCENT:
        raise BattleValidationError("Damage roll percent must be between 85 and 100")
    return damage_roll_percent


def _resolve_attack_stat_key(movement: Movement) -> str:
    """Resolve the attacking stat used by the movement category."""
    return _ATTACK_STAT_BY_CATEGORY.get(movement.category.lower(), "atk")


def _resolve_defense_stat_key(movement: Movement, payload: DamagePayload) -> str:
    """Resolve the defensive stat used by the target for this move."""
    defense_stat = payload.use_target_defense_stat or _DEFAULT_DEFENSE_STAT_BY_CATEGORY.get(movement.category.lower(), "def")
    return "def" if defense_stat == "def_" else defense_stat


def _require_battle_stat(instance: BattleInstance, stat_key: str) -> int:
    """Return a resolved battle stat from the current battle instance."""
    if instance.stats is None:
        raise BattleValidationError(f"Battle instance '{instance.id or instance.pokemon_id}' is missing resolved battle stats")

    stat_attribute = "def_" if stat_key == "def" else stat_key
    try:
        value = getattr(instance.stats, stat_attribute)
    except AttributeError as exc:
        raise BattleValidationError(f"Battle instance '{instance.id or instance.pokemon_id}' is missing stat '{stat_key}'") from exc

    if value <= 0:
        raise BattleValidationError(f"Battle instance '{instance.id or instance.pokemon_id}' has invalid stat '{stat_key}'={value}")
    return value


def _require_stage(instance: BattleInstance, stat_key: str) -> int:
    """Return the stage modifier used for the requested stat key."""
    stage_attribute = _STAGE_ATTRIBUTE_BY_STAT.get(stat_key)
    if stage_attribute is None:
        raise BattleValidationError(f"Damage calculation does not support staged stat '{stat_key}'")
    return getattr(instance.stages, stage_attribute)


def _apply_stage(base_stat: int, stage: int) -> int:
    """Apply battle stat stages using Pokemon-style stage multipliers."""
    bounded_stage = max(-6, min(6, stage))
    if bounded_stage >= 0:
        multiplier = (2 + bounded_stage) / 2
    else:
        multiplier = 2 / (2 - bounded_stage)
    return max(1, floor(base_stat * multiplier))


def calculate_type_effectiveness(movement_type: str, target_types: list[str], type_chart: dict[str, "Type"]) -> float:
    """Calculate the cumulative type effectiveness multiplier."""
    effectiveness = 1.0
    type_data = type_chart.get(movement_type)

    if not type_data:
        return effectiveness

    for target_type in target_types:
        if target_type in type_data.super_effective:
            effectiveness *= 2.0
        elif target_type in type_data.not_very_effective:
            effectiveness *= 0.5
        elif target_type in type_data.no_effect:
            effectiveness *= 0.0

    return effectiveness


def calculate_damage(  # noqa: PLR0913
    *,
    movement: Movement,
    payload: DamagePayload,
    source_instance: BattleInstance,
    target_instance: BattleInstance,
    damage_roll_percent: int,
    type_chart: dict[str, "Type"],
) -> int:
    """Calculate deterministic damage for a resolved source, target and movement."""
    attack_stat_key = _resolve_attack_stat_key(movement)
    defense_stat_key = _resolve_defense_stat_key(movement, payload)

    attack = _apply_stage(
        _require_battle_stat(source_instance, attack_stat_key),
        _require_stage(source_instance, attack_stat_key),
    )
    defense = _apply_stage(
        _require_battle_stat(target_instance, defense_stat_key),
        _require_stage(target_instance, defense_stat_key),
    )
    if movement.power is None:
        raise BattleValidationError(f"Cannot calculate damage for movement '{movement.name}' with null power")
    level_factor = floor((2 * source_instance.level) / 5) + 2
    base_damage = floor((((level_factor * max(1, movement.power) * attack) / defense) / 50) + 2)

    stab = 1.5 if movement.type in source_instance.types else 1.0

    effectiveness = calculate_type_effectiveness(movement.type, target_instance.types, type_chart)

    hit_count = resolve_damage_hit_count(payload)

    # Apply STAB, Effectiveness and Roll
    per_hit_damage = max(1, floor((base_damage * stab * effectiveness * damage_roll_percent) / MAX_DAMAGE_ROLL_PERCENT))

    return per_hit_damage * hit_count
