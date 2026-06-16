"""Shared stat stage calculation utilities used across the agentia module."""

from collections.abc import Mapping
from math import floor

from ...battle.domain.entities import BattleInstance

_STAGE_ATTRIBUTE_BY_STAT: dict[str, str] = {
    "atk": "atk",
    "def_": "def_",
    "spa": "spa",
    "spd": "spd",
    "spe": "spe",
}


def get_stage(instance: BattleInstance, stat_key: str) -> int:
    """Return the stat stage for a given stat key, handling the def_/def alias."""
    stage_attribute = _STAGE_ATTRIBUTE_BY_STAT.get(stat_key)
    if stage_attribute is None:
        return 0
    if isinstance(instance.stages, Mapping):
        aliased_attribute = "def" if stage_attribute == "def_" else stage_attribute
        return int(instance.stages.get(stage_attribute, instance.stages.get(aliased_attribute, 0)) or 0)
    return getattr(instance.stages, stage_attribute, 0)


def apply_stage(base_stat: int, stage: int) -> int:
    """Apply Gen 5+ stat stage multipliers and return the effective stat."""
    bounded_stage = max(-6, min(6, stage))
    if bounded_stage >= 0:
        multiplier = (2 + bounded_stage) / 2
    else:
        multiplier = 2 / (2 - bounded_stage)
    return max(1, floor(base_stat * multiplier))
