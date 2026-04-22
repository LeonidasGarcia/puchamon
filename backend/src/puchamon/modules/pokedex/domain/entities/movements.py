"""Entity representing a Movement in the Pokedex module."""

from pydantic import Field

from .....core.domain.entities import BaseEntity


class Movement(BaseEntity):
    name: str
    type: str
    category: str
    power: int
    accuracy: int
    pp: int
    priority: int = Field(default=0)
    target: str
    makes_contact: bool
    protectable: bool
    effect_ids: list[str] = Field(default_factory=list)

    class Settings:
        """Beanie settings for the Movement entity."""

        name = "movements"
