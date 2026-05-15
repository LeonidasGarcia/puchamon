"""Entity representing a Movement in the Pokedex module."""

from typing import Literal

from pydantic import Field

from .....core.domain.entities import BaseEntity


class Movement(BaseEntity):
    name: str
    type: str
    category: str
    power: int | None = None
    accuracy: int | None = None
    pp: int
    priority: int = Field(default=0)
    target: Literal[
        "target",
        "self",
        "foe_side",
        "ally_side",
        "field",
        "all",
        "all_foes",
        "all_adjacent",
        "all_sides",
    ]
    makes_contact: bool
    protectable: bool
    effect_ids: list[str] = Field(default_factory=list)

    class Settings:
        """Beanie settings for the Movement entity."""

        name = "moves"
