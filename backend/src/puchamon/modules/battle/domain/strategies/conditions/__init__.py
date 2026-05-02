"""Condition effect strategies for battle turn resolution."""

from .bad_poison_condition_effect_strategy import BadPoisonConditionEffectStrategy
from .base import ConditionEffectStrategy
from .block_protectable_moves_condition_effect_strategy import BlockProtectableMovesConditionEffectStrategy
from .block_status_moves_condition_effect_strategy import BlockStatusMovesConditionEffectStrategy
from .cannot_move_condition_effect_strategy import CannotMoveConditionEffectStrategy
from .end_turn_damage_condition_effect_strategy import EndTurnDamageConditionEffectStrategy
from .end_turn_drain_condition_effect_strategy import EndTurnDrainConditionEffectStrategy
from .faint_on_expire_condition_effect_strategy import FaintOnExpireConditionEffectStrategy
from .full_paralysis_chance_condition_effect_strategy import FullParalysisChanceConditionEffectStrategy
from .physical_attack_modifier_condition_effect_strategy import PhysicalAttackModifierConditionEffectStrategy
from .proxy_hp_condition_effect_strategy import ProxyHpConditionEffectStrategy
from .self_hit_chance_condition_effect_strategy import SelfHitChanceConditionEffectStrategy
from .skip_action_condition_effect_strategy import SkipActionConditionEffectStrategy
from .speed_modifier_condition_effect_strategy import SpeedModifierConditionEffectStrategy

__all__: list[str] = [
    "BadPoisonConditionEffectStrategy",
    "BlockProtectableMovesConditionEffectStrategy",
    "BlockStatusMovesConditionEffectStrategy",
    "CannotMoveConditionEffectStrategy",
    "ConditionEffectStrategy",
    "EndTurnDamageConditionEffectStrategy",
    "EndTurnDrainConditionEffectStrategy",
    "FaintOnExpireConditionEffectStrategy",
    "FullParalysisChanceConditionEffectStrategy",
    "PhysicalAttackModifierConditionEffectStrategy",
    "ProxyHpConditionEffectStrategy",
    "SelfHitChanceConditionEffectStrategy",
    "SkipActionConditionEffectStrategy",
    "SpeedModifierConditionEffectStrategy",
]
