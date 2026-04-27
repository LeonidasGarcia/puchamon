"""DTOs for battle turn resolution."""

from typing import Literal

from .....core.domain.entities import BaseEmbeddedModel
from .battle_snapshot_dto import BattleSnapshotDTO


class TurnActionTargetDTO(BaseEmbeddedModel):
    scope: Literal["target", "self", "all", "field", "ally_party"]
    target_side: Literal["ally_side", "foe_side"] | None = None
    target_active_slot: int | None = None


class DeclaredTurnActionDTO(BaseEmbeddedModel):
    trainer_id: str
    action_type: Literal["move", "switch"]
    user_instance_id: str
    move_id: str | None = None
    target: TurnActionTargetDTO | None = None


class ExecutedTurnActionDTO(BaseEmbeddedModel):
    order: int
    trainer_id: str
    action_type: Literal["move", "switch"]
    user_instance_id: str
    move_id: str | None = None
    target: TurnActionTargetDTO | None = None
    hit: bool | None = None
    skipped_reason: str | None = None
    revealed_move: bool = False


class BattleTurnEventDTO(BaseEmbeddedModel):
    order: int
    kind: str
    source_instance_id: str | None = None
    target_instance_id: str | None = None
    move_id: str | None = None
    value: int | None = None
    status_id: str | None = None
    hazard_id: str | None = None
    weather_id: str | None = None
    message: str


class ForcedReplacementDTO(BaseEmbeddedModel):
    trainer_id: str
    active_slot: int
    fainted_instance_id: str
    available_instance_ids: list[str]


class BattleTurnDTO(BaseEmbeddedModel):
    battle_id: str
    turn: int
    declared_actions: list[DeclaredTurnActionDTO]
    executed_actions: list[ExecutedTurnActionDTO]
    events: list[BattleTurnEventDTO]
    fainted_instance_ids: list[str]
    required_replacements: list[ForcedReplacementDTO]
    post_turn_snapshot: BattleSnapshotDTO
