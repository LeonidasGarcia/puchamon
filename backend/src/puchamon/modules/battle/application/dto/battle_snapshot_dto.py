"""DTOs for battle snapshot responses."""

from typing import Literal

from pydantic import Field

from .....core.domain.entities import BaseEmbeddedModel


class WeatherSnapshotDTO(BaseEmbeddedModel):
    weather_id: str
    remaining_turns: int
    source_move_id: str | None = None


class PlayerSnapshotDTO(BaseEmbeddedModel):
    trainer_id: str
    name: str
    controller_type: Literal["human", "ai"]


class SideSnapshotDTO(BaseEmbeddedModel):
    hazards: list[str]
    active_pokemon_instance_ids: list[str | None]


class MoveStateSnapshotDTO(BaseEmbeddedModel):
    move_id: str
    current_pp: int


class StatStagesSnapshotDTO(BaseEmbeddedModel):
    atk: int
    def_: int = Field(serialization_alias="def", validation_alias="def")
    spa: int
    spd: int
    spe: int
    acc: int
    eva: int


class PokemonInstanceSnapshotDTO(BaseEmbeddedModel):
    instance_id: str
    trainer_id: str
    team_slot: int
    pokemon_id: str
    level: int
    current_hp: int
    max_hp: int
    status: str | None = None
    volatile_status: list[str]
    stages: StatStagesSnapshotDTO
    move_state: list[MoveStateSnapshotDTO]
    fainted: bool
    is_revealed: bool
    revealed_moves: list[str]


class BattleResultDTO(BaseEmbeddedModel):
    winner_trainer_id: str
    reason: Literal["knockout", "forfeit", "time"]


class BattleSnapshotDTO(BaseEmbeddedModel):
    battle_id: str
    battle_type: Literal["1v1", "2v2", "3v3"]
    turn: int
    status: Literal["active", "finished", "paused"]
    phase: Literal["setup", "awaiting_actions", "resolving_turn", "awaiting_replacements"] | None = None
    weather: WeatherSnapshotDTO | None = None
    players: list[PlayerSnapshotDTO]
    sides: dict[str, SideSnapshotDTO]
    pokemon_instances: list[PokemonInstanceSnapshotDTO]
    result: BattleResultDTO | None = None
