"""Entity representing a Moveset in the Pokedex module."""

from .....core.domain.entities import BaseEntity


class Moveset(BaseEntity):
    pokemon_id: str
    moveset_name: str
    nature: str
    evs: dict[str, int]
    item: str
    ability: str
    moves: list[str]

    class Settings:
        """Beanie settings for the Moveset entity."""

        name = "movesets"
