"""Registries for battle domain strategies."""

from collections.abc import Iterable

from ..exceptions import BattleValidationError
from ..runtime import StrategyHook
from ..strategies.actions import ActionStrategy, MoveActionStrategy, SwitchActionStrategy
from ..strategies.conditions import (
    BadPoisonConditionEffectStrategy,
    BlockProtectableMovesConditionEffectStrategy,
    BlockStatusMovesConditionEffectStrategy,
    CannotMoveConditionEffectStrategy,
    ConditionEffectStrategy,
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
from ..strategies.effects import (
    ApplyMajorStatusEffectStrategy,
    ApplyVolatileStatusEffectStrategy,
    DamageEffectStrategy,
    HealHpEffectStrategy,
    ModifyStatEffectStrategy,
    MoveEffectStrategy,
    PainSplitEffectStrategy,
    ProtectEffectStrategy,
    RemoveHazardEffectStrategy,
    SelfSwitchEffectStrategy,
    SetHazardEffectStrategy,
)
from ..strategies.weather import (
    EndTurnDamageWeatherEffectStrategy,
    MoveAccuracyOverrideWeatherEffectStrategy,
    MoveChargeModifierWeatherEffectStrategy,
    MoveChargeOverrideWeatherEffectStrategy,
    SpecialDefenseModifierWeatherEffectStrategy,
    TypePowerModifierWeatherEffectStrategy,
    WeatherEffectStrategy,
)


class ActionStrategyRegistry:
    """Registry used to dispatch turn actions by action type."""

    def __init__(self, strategies: Iterable[ActionStrategy]):
        self._strategies: dict[str, ActionStrategy] = {strategy.action_type: strategy for strategy in strategies}

    def get(self, action_type: str) -> ActionStrategy:
        """Return the strategy registered for a given turn action type."""
        try:
            return self._strategies[action_type]
        except KeyError as exc:
            raise BattleValidationError(f"Unsupported battle action strategy '{action_type}'") from exc


class MoveEffectStrategyRegistry:
    """Registry used to dispatch move effects by effect kind."""

    def __init__(self, strategies: Iterable[MoveEffectStrategy]):
        self._strategies: dict[str, MoveEffectStrategy] = {strategy.kind: strategy for strategy in strategies}

    def get(self, kind: str) -> MoveEffectStrategy:
        """Return the strategy registered for a given move effect kind."""
        try:
            return self._strategies[kind]
        except KeyError as exc:
            raise BattleValidationError(f"Unsupported move effect strategy '{kind}'") from exc


class ConditionEffectStrategyRegistry:
    """Registry used to dispatch condition hooks by effect kind."""

    def __init__(self, strategies: Iterable[ConditionEffectStrategy]):
        self._strategies: dict[str, ConditionEffectStrategy] = {strategy.kind: strategy for strategy in strategies}

    def get(self, kind: str) -> ConditionEffectStrategy:
        """Return the strategy registered for a given condition effect kind."""
        try:
            return self._strategies[kind]
        except KeyError as exc:
            raise BattleValidationError(f"Unsupported condition effect strategy '{kind}'") from exc

    def for_hook(self, hook: StrategyHook) -> list[ConditionEffectStrategy]:
        """Return all condition strategies that are meant to run on a specific hook."""
        return [strategy for strategy in self._strategies.values() if strategy.hook == hook]


class WeatherEffectStrategyRegistry:
    """Registry used to dispatch weather hooks by effect kind."""

    def __init__(self, strategies: Iterable[WeatherEffectStrategy]):
        self._strategies: dict[str, WeatherEffectStrategy] = {strategy.kind: strategy for strategy in strategies}

    def get(self, kind: str) -> WeatherEffectStrategy:
        """Return the strategy registered for a given weather effect kind."""
        try:
            return self._strategies[kind]
        except KeyError as exc:
            raise BattleValidationError(f"Unsupported weather effect strategy '{kind}'") from exc

    def for_hook(self, hook: StrategyHook) -> list[WeatherEffectStrategy]:
        """Return all weather strategies that are meant to run on a specific hook."""
        return [strategy for strategy in self._strategies.values() if strategy.hook == hook]


def build_default_action_strategy_registry() -> ActionStrategyRegistry:
    """Build the default registry for battle turn actions."""
    return ActionStrategyRegistry([MoveActionStrategy(), SwitchActionStrategy()])


def build_default_move_effect_strategy_registry() -> MoveEffectStrategyRegistry:
    """Build the default registry for move effect kinds."""
    return MoveEffectStrategyRegistry(
        [
            DamageEffectStrategy(),
            ApplyMajorStatusEffectStrategy(),
            ApplyVolatileStatusEffectStrategy(),
            ModifyStatEffectStrategy(),
            SetHazardEffectStrategy(),
            RemoveHazardEffectStrategy(),
            ProtectEffectStrategy(),
            # HealHpEffectStrategy(),
            SelfSwitchEffectStrategy(),
            # SwapItemEffectStrategy(),
            # PainSplitEffectStrategy(),
        ]
    )


def build_default_condition_effect_strategy_registry() -> ConditionEffectStrategyRegistry:
    """Build the default registry for condition effect kinds."""
    return ConditionEffectStrategyRegistry(
        [
            EndTurnDamageConditionEffectStrategy(),
            BadPoisonConditionEffectStrategy(),
            PhysicalAttackModifierConditionEffectStrategy(),
            SpeedModifierConditionEffectStrategy(),
            FullParalysisChanceConditionEffectStrategy(),
            SelfHitChanceConditionEffectStrategy(),
            CannotMoveConditionEffectStrategy(),
            SkipActionConditionEffectStrategy(),
            BlockProtectableMovesConditionEffectStrategy(),
            BlockStatusMovesConditionEffectStrategy(),
            FaintOnExpireConditionEffectStrategy(),
            ProxyHpConditionEffectStrategy(),
            EndTurnDrainConditionEffectStrategy(),
        ]
    )


def build_default_weather_effect_strategy_registry() -> WeatherEffectStrategyRegistry:
    """Build the default registry for weather effect kinds."""
    return WeatherEffectStrategyRegistry(
        [
            TypePowerModifierWeatherEffectStrategy(),
            MoveAccuracyOverrideWeatherEffectStrategy(),
            MoveChargeModifierWeatherEffectStrategy(),
            MoveChargeOverrideWeatherEffectStrategy(),
            EndTurnDamageWeatherEffectStrategy(),
            SpecialDefenseModifierWeatherEffectStrategy(),
        ]
    )


__all__: list[str] = [
    "ActionStrategyRegistry",
    "ConditionEffectStrategyRegistry",
    "MoveEffectStrategyRegistry",
    "WeatherEffectStrategyRegistry",
    "build_default_action_strategy_registry",
    "build_default_condition_effect_strategy_registry",
    "build_default_move_effect_strategy_registry",
    "build_default_weather_effect_strategy_registry",
]
