"""Move effect strategies for battle turn resolution."""

from .apply_major_status_effect_strategy import ApplyMajorStatusEffectStrategy
from .apply_volatile_status_effect_strategy import ApplyVolatileStatusEffectStrategy
from .base import MoveEffectStrategy
from .damage_effect_strategy import DamageEffectStrategy
from .modify_stat_effect_strategy import ModifyStatEffectStrategy
from .protect_effect_strategy import ProtectEffectStrategy

__all__: list[str] = [
    "ApplyMajorStatusEffectStrategy",
    "ApplyVolatileStatusEffectStrategy",
    "DamageEffectStrategy",
    "ModifyStatEffectStrategy",
    "MoveEffectStrategy",
    "ProtectEffectStrategy",
]
