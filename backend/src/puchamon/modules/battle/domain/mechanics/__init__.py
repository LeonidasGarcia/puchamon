"""Pure battle mechanics helpers."""

from .damage import calculate_damage, resolve_damage_hit_count, resolve_damage_roll_percent
from .stats import build_battle_stats

__all__: list[str] = [
    "build_battle_stats",
    "calculate_damage",
    "resolve_damage_hit_count",
    "resolve_damage_roll_percent",
]
