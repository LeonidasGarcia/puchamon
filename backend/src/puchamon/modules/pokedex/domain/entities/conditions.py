"""Entity representing a Condition in the Pokedex module."""

from typing import Annotated, Literal

from pydantic import Field

from .....core.domain.entities import BaseEmbeddedModel, BaseEntity


class EmptyPayload(BaseEmbeddedModel):
    """Payload for effects that don't require additional data (e.g., {})."""

    pass


class MultiplierPayload(BaseEmbeddedModel):
    """Reusable payload for stat modifiers."""

    multiplier: float


class RatioPayload(BaseEmbeddedModel):
    """Reusable payload for HP draining or proxy HP."""

    ratio: float


class ChancePayload(BaseEmbeddedModel):
    """Reusable payload for RNG-based effects."""

    chance: int


class BadPoisonPayload(BaseEmbeddedModel):
    """Specific payload for Toxic."""

    base_ratio: float


class EndTurnDamageEffect(BaseEmbeddedModel):
    kind: Literal["end_turn_damage"]
    payload: RatioPayload


class BadPoisonEffect(BaseEmbeddedModel):
    kind: Literal["end_turn_bad_poison_damage"]
    payload: BadPoisonPayload


class PhysicalAttackModifierEffect(BaseEmbeddedModel):
    kind: Literal["physical_attack_modifier"]
    payload: MultiplierPayload


class SpeedModifierEffect(BaseEmbeddedModel):
    kind: Literal["speed_modifier"]
    payload: MultiplierPayload


class FullParalysisChanceEffect(BaseEmbeddedModel):
    kind: Literal["full_paralysis_chance"]
    payload: ChancePayload


class SelfHitChanceEffect(BaseEmbeddedModel):
    kind: Literal["self_hit_chance"]
    payload: ChancePayload


class CannotMoveEffect(BaseEmbeddedModel):
    kind: Literal["cannot_move"]
    payload: EmptyPayload


class BlockProtectableMovesEffect(BaseEmbeddedModel):
    kind: Literal["block_protectable_moves"]
    payload: EmptyPayload


class BlockStatusMovesEffect(BaseEmbeddedModel):
    kind: Literal["block_status_moves"]
    payload: EmptyPayload


ConditionEffect = Annotated[
    EndTurnDamageEffect
    | BadPoisonEffect
    | PhysicalAttackModifierEffect
    | SpeedModifierEffect
    | FullParalysisChanceEffect
    | SelfHitChanceEffect
    | CannotMoveEffect
    | BlockProtectableMovesEffect
    | BlockStatusMovesEffect,
    Field(discriminator="kind"),
]


class Condition(BaseEntity):
    name: str
    category: Literal["major", "volatile"]

    default_duration: int | None = Field(default=None)

    effects: list[ConditionEffect]

    class Settings:
        """Beanie settings for the Condition entity."""

        name = "conditions"
