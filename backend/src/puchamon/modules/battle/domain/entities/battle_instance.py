"""Entity representing a Battle Instance in the History module."""

from pydantic import Field

from .....core.domain.entities import BaseEmbeddedModel, BaseEntity


class MoveState(BaseEmbeddedModel):
    move_id: str
    current_pp: int


class StatStages(BaseEmbeddedModel):
    atk: int = 0
    def_: int = Field(default=0, validation_alias="def", serialization_alias="def")
    spa: int = 0
    spd: int = 0
    spe: int = 0
    acc: int = 0
    eva: int = 0


class BattleInstance(BaseEntity):
    battle_id: str
    trainer_id: str
    slot: int
    pokemon_id: str
    moveset_id: str
    level: int
    current_hp: int
    max_hp: int
    ability: str
    item: str | None = None
    status: str | None = None
    volatile_status: list[str]
    stages: StatStages
    move_state: list[MoveState]
    fainted: bool
    is_revealed: bool
    revealed_moves: list[str]
