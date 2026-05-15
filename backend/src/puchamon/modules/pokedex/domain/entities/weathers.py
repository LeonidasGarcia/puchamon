"""Entity representing a Weather in the Pokedex module."""

from typing import Annotated, Literal

from pydantic import Field

from .....core.domain.entities import BaseEmbeddedModel, BaseEntity


class TypePowerPayload(BaseEmbeddedModel):
    type: str
    multiplier: float


class MoveAccuracyPayload(BaseEmbeddedModel):
    move_id: str
    accuracy: int


class MoveChargeModifierPayload(BaseEmbeddedModel):
    move_id: str
    power_multiplier: float


class MoveChargeOverridePayload(BaseEmbeddedModel):
    move_id: str
    skip_charge: bool


class EndTurnDamagePayload(BaseEmbeddedModel):
    ratio: float
    immune_types: list[str]


class SpecialDefensePayload(BaseEmbeddedModel):
    target_types: list[str]
    multiplier: float


class TypePowerEffect(BaseEmbeddedModel):
    kind: Literal["type_power_modifier"]
    payload: TypePowerPayload


class MoveAccuracyEffect(BaseEmbeddedModel):
    kind: Literal["move_accuracy_override"]
    payload: MoveAccuracyPayload


class MoveChargeModifierEffect(BaseEmbeddedModel):
    kind: Literal["move_charge_modifier"]
    payload: MoveChargeModifierPayload


class MoveChargeOverrideEffect(BaseEmbeddedModel):
    kind: Literal["move_charge_override"]
    payload: MoveChargeOverridePayload


class EndTurnDamageEffect(BaseEmbeddedModel):
    kind: Literal["end_turn_damage"]
    payload: EndTurnDamagePayload


class SpecialDefenseEffect(BaseEmbeddedModel):
    kind: Literal["special_defense_modifier"]
    payload: SpecialDefensePayload


WeatherEffect = Annotated[
    TypePowerEffect | MoveAccuracyEffect | MoveChargeModifierEffect | MoveChargeOverrideEffect | EndTurnDamageEffect | SpecialDefenseEffect,
    Field(discriminator="kind"),
]


class Weather(BaseEntity):
    name: str
    default_duration: int = Field(default=5)
    effects: list[WeatherEffect]

    class Settings:
        """Beanie settings for the Weather entity."""

        name = "weathers"
