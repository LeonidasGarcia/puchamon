"""Pure battle mechanics helpers."""

from .accuracy import calculate_accuracy
from .damage import calculate_damage, resolve_damage_hit_count, resolve_damage_roll_percent
from .immunities import is_immune_to_status, is_immune_to_volatile
from .lifecycle import faint_instance, switch_in_instance
from .stats import build_battle_stats

__all__: list[str] = [
    "build_battle_stats",
    "calculate_accuracy",
    "calculate_damage",
    "faint_instance",
    "is_immune_to_status",
    "is_immune_to_volatile",
    "resolve_damage_hit_count",
    "resolve_damage_roll_percent",
    "switch_in_instance",
]
