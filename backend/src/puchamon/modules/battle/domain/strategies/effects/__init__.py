"""Move effect strategies for battle turn resolution."""

from .base import MoveEffectStrategy
from .move_effect_strategies import (
    ApplyMajorStatusEffectStrategy,
    ApplyVolatileStatusEffectStrategy,
    DamageEffectStrategy,
    HealHpEffectStrategy,
    ModifyStatEffectStrategy,
    PainSplitEffectStrategy,
    ProtectEffectStrategy,
    RemoveHazardEffectStrategy,
    SelfSwitchEffectStrategy,
    SetHazardEffectStrategy,
    SwapItemEffectStrategy,
)

__all__: list[str] = [
    "ApplyMajorStatusEffectStrategy",
    "ApplyVolatileStatusEffectStrategy",
    "DamageEffectStrategy",
    "HealHpEffectStrategy",
    "ModifyStatEffectStrategy",
    "MoveEffectStrategy",
    "PainSplitEffectStrategy",
    "ProtectEffectStrategy",
    "RemoveHazardEffectStrategy",
    "SelfSwitchEffectStrategy",
    "SetHazardEffectStrategy",
    "SwapItemEffectStrategy",
]
