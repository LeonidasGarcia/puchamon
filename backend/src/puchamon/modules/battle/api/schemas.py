"""Schemas for battle-related API endpoints."""

from typing import Literal

from pydantic import BaseModel


class ConnectionRequest(BaseModel):
    name: str
    controller_type: Literal["human", "ai"]
    battle_type: Literal["1v1", "2v2", "3v3"]
    difficulty: int | None = 1


class TurnActionTarget(BaseModel):
    scope: Literal["target", "self", "all", "field", "ally_party"] = "target"
    target_side: Literal["ally_side", "foe_side"] | None = None
    target_active_slot: int | None = None


class TurnAction(BaseModel):
    type: Literal["move", "switch"]
    user_instance_id: str
    move_id: str | None = None
    target: TurnActionTarget | None = None
    replacement_instance_id: str | None = None


class TurnSubmit(BaseModel):
    trainer_id: str
    action: TurnAction


class ErrorPayload(BaseModel):
    code: str
    message: str
