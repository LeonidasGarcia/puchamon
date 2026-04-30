"""Shared runtime context for battle domain strategies."""

from dataclasses import dataclass, field
from typing import Any, Literal

from ....pokedex.domain.entities import Condition, MoveEffect, Movement, Weather
from ....pokedex.domain.entities.conditions import ConditionEffect
from ....pokedex.domain.entities.weathers import WeatherEffect
from ..entities import Battle, BattleInstance, TurnAction
from ..exceptions import BattleValidationError

StrategyHook = Literal[
    "before_action",
    "validate_move",
    "modify_speed",
    "modify_accuracy",
    "modify_damage",
    "modify_charge",
    "modify_special_defense",
    "end_turn",
    "on_expire",
]


@dataclass(slots=True)
class BattleStrategyEvent:
    """Domain event emitted while a strategy mutates the battle state."""

    kind: str
    message: str
    source_instance_id: str | None = None
    target_instance_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BattleStrategyContext:
    """Mutable runtime context shared by battle strategies."""

    battle: Battle
    battle_instances: dict[str, BattleInstance]
    events: list[BattleStrategyEvent] = field(default_factory=list)

    def get_instance(self, instance_id: str) -> BattleInstance:
        """Return a battle instance from the current runtime context."""
        try:
            return self.battle_instances[instance_id]
        except KeyError as exc:
            raise BattleValidationError(f"Battle instance '{instance_id}' is not available in the current strategy context") from exc

    def add_event(
        self,
        *,
        kind: str,
        message: str,
        source_instance_id: str | None = None,
        target_instance_id: str | None = None,
        **payload: Any,
    ) -> None:
        """Append a structured event to the current runtime context."""
        self.events.append(
            BattleStrategyEvent(
                kind=kind,
                message=message,
                source_instance_id=source_instance_id,
                target_instance_id=target_instance_id,
                payload=payload,
            )
        )


@dataclass(slots=True)
class ActionExecutionInput:
    """Resolved inputs required to execute a turn action."""

    action: TurnAction
    movement: Movement | None = None
    move_effects: list[MoveEffect] = field(default_factory=list)
    replacement_instance_id: str | None = None


@dataclass(slots=True)
class MoveEffectExecutionInput:
    """Resolved inputs required to apply a move effect."""

    effect: MoveEffect
    source_instance_id: str
    target_instance_ids: list[str]
    movement: Movement | None = None


@dataclass(slots=True)
class ConditionEffectExecutionInput:
    """Resolved inputs required to apply a condition effect hook."""

    condition: Condition
    effect: ConditionEffect
    holder_instance_id: str
    source_instance_id: str | None = None
    target_instance_id: str | None = None
    movement: Movement | None = None


@dataclass(slots=True)
class WeatherEffectExecutionInput:
    """Resolved inputs required to apply a weather effect hook."""

    weather: Weather
    effect: WeatherEffect
    source_instance_id: str | None = None
    target_instance_id: str | None = None
    movement: Movement | None = None
