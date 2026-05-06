"""Entity representing a Battle in the History module."""

from typing import Literal

from .....core.domain.entities import BaseEmbeddedModel, BaseEntity


class WeatherState(BaseEmbeddedModel):
    weather_id: str
    remaining_turns: int
    source_move_id: str | None = None


class SideState(BaseEmbeddedModel):
    hazards: list[str]
    active_pokemon_instance_ids: list[str | None]


class Player(BaseEmbeddedModel):
    trainer_id: str
    name: str
    controller_type: Literal["human", "ai"]


class TargetScope(BaseEmbeddedModel):
    scope: Literal["target", "self", "all", "field", "ally_party"]
    target_side: Literal["ally_side", "foe_side"] | None = None
    target_active_slot: int | None = None


class TurnAction(BaseEmbeddedModel):
    player: str
    type: Literal["move", "switch"]
    user_instance_id: str
    move_id: str | None = None
    target: TargetScope | None = None
    replacement_instance_id: str | None = None


class BattleResult(BaseEmbeddedModel):
    winner_trainer_id: str
    reason: Literal["knockout", "forfeit", "time"]


class Battle(BaseEntity):
    battle_type: Literal["1v1", "2v2", "3v3"]
    turn: int
    status: Literal["active", "finished", "paused"]
    phase: Literal["setup", "awaiting_actions", "resolving_turn", "awaiting_replacements"] | None = None
    weather: WeatherState | None = None
    sides: dict[str, SideState]
    players: list[Player]
    current_turn_actions: list[TurnAction]
    result: BattleResult | None = None
