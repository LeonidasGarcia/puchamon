"""Entity representing a Battle in the History module."""

from typing import Literal

from .....core.domain.entities import BaseEmbeddedModel, BaseEntity


class WeatherState(BaseEmbeddedModel):
    weather_id: str
    remaining_turns: int
    source_move_id: str | None = None


class SideState(BaseEmbeddedModel):
    hazards: list[str]
    active_pokemon_instance_ids: list[str]


class Player(BaseEmbeddedModel):
    trainer_id: str
    name: str


class TargetScope(BaseEmbeddedModel):
    scope: Literal["single", "self", "all", "field", "ally_party"]
    target_instance_id: str | None = None


class TurnAction(BaseEmbeddedModel):
    player: str
    type: Literal["move", "switch", "item"]
    user_instance_id: str
    move_id: str | None = None
    target: TargetScope | None = None


class Battle(BaseEntity):
    turn: int
    status: Literal["active", "finished", "paused"]
    weather: WeatherState | None = None
    sides: dict[str, SideState]
    players: list[Player]
    current_turn_actions: list[TurnAction]
