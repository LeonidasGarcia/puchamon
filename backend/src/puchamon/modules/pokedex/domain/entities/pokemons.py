"""Entity representing a Pokemon in the Pokedex module."""

from pydantic import Field

from .....core.domain.entities import BaseEmbeddedModel, BaseEntity


class BaseStats(BaseEmbeddedModel):
    hp: int
    atk: int
    def_: int = Field(default=0, validation_alias="def", serialization_alias="def")
    spa: int
    spd: int
    spe: int


class Pokemon(BaseEntity):
    name: str
    types: list[str]
    base_stats: BaseStats
    abilities: list[str]

    class Settings:
        """Beanie settings for the Pokemon entity."""

        name = "pokemons"
