"""Shared runtime context for battle domain resolution."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from ....pokedex.domain.entities import Condition, MoveEffect, Movement
from ....pokedex.domain.entities.conditions import ConditionEffect
from ....pokedex.domain.entities.effects import DamagePayload
from ..entities import Battle, BattleInstance, TurnAction
from ..exceptions import BattleValidationError

if TYPE_CHECKING:
    from ....pokedex.domain.entities import Type
    from ..registries import MoveEffectStrategyRegistry


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
class DamageCalculationInput:
    """Parameters for calculating move damage."""

    movement: Movement
    payload: DamagePayload
    source: BattleInstance
    target: BattleInstance
    roll_percent: int
    type_chart: dict[str, "Type"]


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
    transient: dict[str, Any] = field(default_factory=dict)

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

    def mark_action_blocked(self, instance_id: str, reason: str) -> None:
        """Mark an instance action as blocked for the current turn resolution step."""
        blocked_actions: dict[str, str] = self.transient.setdefault("blocked_actions", {})
        blocked_actions[instance_id] = reason

    def get_action_block_reason(self, instance_id: str) -> str | None:
        """Return the reason why an instance cannot execute its action, if any."""
        blocked_actions: dict[str, str] = self.transient.get("blocked_actions", {})
        return blocked_actions.get(instance_id)

    def clear_action_block(self, instance_id: str) -> None:
        """Remove a previously registered action block for an instance."""
        blocked_actions: dict[str, str] = self.transient.get("blocked_actions", {})
        blocked_actions.pop(instance_id, None)

    def mark_fainted(self, instance_id: str) -> None:
        """Track that an instance fainted during the current resolution step."""
        fainted_instance_ids: list[str] = self.transient.setdefault("fainted_instance_ids", [])
        if instance_id not in fainted_instance_ids:
            fainted_instance_ids.append(instance_id)

    def get_fainted_instance_ids(self) -> list[str]:
        """Return the list of instances that fainted during this resolution step."""
        return list(self.transient.get("fainted_instance_ids", []))


@dataclass(slots=True)
class ActionExecutionInput:
    """Resolved inputs required to execute a turn action."""

    action: TurnAction
    movement: Movement | None = None
    move_effects: list[MoveEffect] = field(default_factory=list)
    replacement_instance_id: str | None = None
    move_effect_strategy_registry: "MoveEffectStrategyRegistry | None" = None
    condition_effect_strategy_registry: "Any | None" = None
    conditions: "dict[str, Condition] | None" = None

    def build_move_effect_execution(
        self,
        *,
        effect: MoveEffect,
        target_instance_ids: list[str],
        metadata: dict[str, "Any"] | None = None,
    ) -> "MoveEffectExecutionInput":
        """Build the effect execution input derived from the current action resolution."""
        return MoveEffectExecutionInput(
            effect=effect,
            source_instance_id=self.action.user_instance_id,
            target_instance_ids=target_instance_ids,
            movement=self.movement,
            metadata=metadata if metadata is not None else {},
        )


@dataclass(slots=True)
class MoveEffectExecutionInput:
    """Resolved inputs required to apply a move effect."""

    effect: MoveEffect
    source_instance_id: str
    target_instance_ids: list[str]
    movement: Movement | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ConditionEffectExecutionInput:
    """Resolved inputs required to apply a condition effect hook."""

    condition: Condition
    effect: ConditionEffect
    holder_instance_id: str
    source_instance_id: str | None = None
    target_instance_id: str | None = None
    movement: Movement | None = None
