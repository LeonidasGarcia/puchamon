"""Entity representing a Type in the Pokedex module."""

from .....core.domain.entities import BaseEntity


class Type(BaseEntity):
    super_effective: list[str]
    not_very_effective: list[str]
    no_effect: list[str]

    class Settings:
        """Beanie settings for the Type entity."""

        name = "type_chart"
