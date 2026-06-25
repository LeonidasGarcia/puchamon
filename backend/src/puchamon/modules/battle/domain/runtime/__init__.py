"""Runtime data structures for battle turn resolution."""

from .context import (
    ActionExecutionInput,
    BattleStrategyContext,
    BattleStrategyEvent,
    ConditionEffectExecutionInput,
    DamageApplicationInput,
    DamageCalculationInput,
    DamageResolutionInput,
    MoveEffectExecutionInput,
    StrategyHook,
)

__all__: list[str] = [
    "ActionExecutionInput",
    "BattleStrategyContext",
    "BattleStrategyEvent",
    "ConditionEffectExecutionInput",
    "DamageApplicationInput",
    "DamageCalculationInput",
    "DamageResolutionInput",
    "MoveEffectExecutionInput",
    "StrategyHook",
]
