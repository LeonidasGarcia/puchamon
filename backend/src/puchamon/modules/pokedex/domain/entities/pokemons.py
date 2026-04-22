"""Entity representing a Pokemon in the Pokedex module."""

from .....core.domain.entities import BaseEntity


class Pokemon(BaseEntity):
    name: str
    types: list[str]
    base_stats: dict[str, int]
    abilities: list[str]

    class Settings:
        """Beanie settings for the Pokemon entity."""

        name = "pokemons"
