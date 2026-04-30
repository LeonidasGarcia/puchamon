"""Battle domain strategies and registries."""

from .actions import ActionStrategy, MoveActionStrategy, SwitchActionStrategy
from .conditions import ConditionEffectStrategy
from .context import (
    ActionExecutionInput,
    BattleStrategyContext,
    BattleStrategyEvent,
    ConditionEffectExecutionInput,
    MoveEffectExecutionInput,
    StrategyHook,
    WeatherEffectExecutionInput,
)
from .effects import MoveEffectStrategy
from .registries import (
    ActionStrategyRegistry,
    ConditionEffectStrategyRegistry,
    MoveEffectStrategyRegistry,
    WeatherEffectStrategyRegistry,
    build_default_action_strategy_registry,
    build_default_condition_effect_strategy_registry,
    build_default_move_effect_strategy_registry,
    build_default_weather_effect_strategy_registry,
)
from .weather import WeatherEffectStrategy

__all__: list[str] = [
    "ActionExecutionInput",
    "ActionStrategy",
    "ActionStrategyRegistry",
    "BattleStrategyContext",
    "BattleStrategyEvent",
    "ConditionEffectExecutionInput",
    "ConditionEffectStrategy",
    "ConditionEffectStrategyRegistry",
    "MoveActionStrategy",
    "MoveEffectExecutionInput",
    "MoveEffectStrategy",
    "MoveEffectStrategyRegistry",
    "StrategyHook",
    "SwitchActionStrategy",
    "WeatherEffectExecutionInput",
    "WeatherEffectStrategy",
    "WeatherEffectStrategyRegistry",
    "build_default_action_strategy_registry",
    "build_default_condition_effect_strategy_registry",
    "build_default_move_effect_strategy_registry",
    "build_default_weather_effect_strategy_registry",
]
