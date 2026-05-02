"""Move effect strategies for battle turn resolution."""

from .apply_major_status_effect_strategy import ApplyMajorStatusEffectStrategy
from .apply_volatile_status_effect_strategy import ApplyVolatileStatusEffectStrategy
from .base import MoveEffectStrategy
from .damage_effect_strategy import DamageEffectStrategy
from .heal_hp_effect_strategy import HealHpEffectStrategy
from .modify_stat_effect_strategy import ModifyStatEffectStrategy
from .pain_split_effect_strategy import PainSplitEffectStrategy
from .protect_effect_strategy import ProtectEffectStrategy
from .remove_hazard_effect_strategy import RemoveHazardEffectStrategy
from .self_switch_effect_strategy import SelfSwitchEffectStrategy
from .set_hazard_effect_strategy import SetHazardEffectStrategy
from .swap_item_effect_strategy import SwapItemEffectStrategy

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
