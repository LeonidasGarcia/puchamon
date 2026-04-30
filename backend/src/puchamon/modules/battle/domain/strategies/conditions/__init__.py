"""Condition effect strategies for battle turn resolution."""

from .base import ConditionEffectStrategy
from .condition_effect_strategies import (
    BadPoisonConditionEffectStrategy,
    BlockProtectableMovesConditionEffectStrategy,
    BlockStatusMovesConditionEffectStrategy,
    CannotMoveConditionEffectStrategy,
    EndTurnDamageConditionEffectStrategy,
    EndTurnDrainConditionEffectStrategy,
    FaintOnExpireConditionEffectStrategy,
    FullParalysisChanceConditionEffectStrategy,
    PhysicalAttackModifierConditionEffectStrategy,
    ProxyHpConditionEffectStrategy,
    SelfHitChanceConditionEffectStrategy,
    SkipActionConditionEffectStrategy,
    SpeedModifierConditionEffectStrategy,
)

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
