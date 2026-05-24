"""Damage calculation utilities for AI simulation."""

from ...battle.domain.entities import BattleInstance
from ...pokedex.domain.entities import Movement


def calculate_damage(
    move: Movement,
    source: BattleInstance,
    target: BattleInstance,
) -> int:
    """Calculate damage for a move against a target.

    Simplified damage formula for AI simulation purposes.

    Args:
        move: The movement being used.
        source: The source battle instance.
        target: The target battle instance.

    Returns:
        Estimated damage value.
    """
    attack_stat_key = "atk" if move.category.lower() == "physical" else "spa"
    defense_stat_key = "def" if move.category.lower() == "physical" else "spd"

    attack = source.stats.atk if attack_stat_key == "atk" else source.stats.spa
    defense = target.stats.def_ if defense_stat_key == "def" else target.stats.spd

    level_factor = (2 * source.level) // 5 + 2
    base_damage = (level_factor * (move.power or 0) * attack) // defense // 50 + 2

    stab = 1.5 if move.type in source.types else 1.0

    base_damage = max(1, base_damage)
    return int(base_damage * stab * 1.0 * 0.85)
