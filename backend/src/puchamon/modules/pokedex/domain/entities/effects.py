"""Entity representing a Movement in the Pokedex module."""

from typing import Literal

from .....core.domain.entities import BaseEmbeddedModel, BaseEntity


class RandomRange(BaseEmbeddedModel):
    """Handles multi-hit moves like Icicle Spear (2 to 5 hits)."""

    mode: Literal["random_range"]
    min: int
    max: int


class StatChange(BaseEmbeddedModel):
    """Handles stat drops/boosts."""

    stat: str
    stages: int


class DamagePayload(BaseEmbeddedModel):
    hits: int | RandomRange
    on_switch_multiplier: int | None = None
    mode: str | None = None
    requires_focus: bool | None = None
    use_target_defense_stat: str | None = None


class StatusPayload(BaseEmbeddedModel):
    condition_id: str
    duration: int | None = None
    hp_cost_ratio: float | None = None
    scope: str | None = None


class ModifyStatPayload(BaseEmbeddedModel):
    changes: list[StatChange]


class SetHazardPayload(BaseEmbeddedModel):
    hazard_id: str
    layers: int
    max_layers: int


class RemoveHazardPayload(BaseEmbeddedModel):
    hazard_ids: list[str]
    clear_conditions: list[str]


class HealPayload(BaseEmbeddedModel):
    ratio: float


class ProtectPayload(BaseEmbeddedModel):
    duration: int


class EmptyPayload(BaseEmbeddedModel):
    pass


class MoveEffect(BaseEntity):
    kind: Literal[
        "damage",
        "apply_major_status",
        "apply_volatile_status",
        "modify_stat",
        "set_hazard",
        "remove_hazard",
        "protect",
        "heal_hp",
        "self_switch",
        "swap_item",
        "pain_split",
    ]

    target: Literal["target", "user", "opponent_side", "user_side", "field"]
    chance: int
    order: int

    payload: DamagePayload | StatusPayload | ModifyStatPayload | SetHazardPayload | RemoveHazardPayload | HealPayload | ProtectPayload | EmptyPayload

    class Settings:
        """Beanie settings for the Move Effect entity."""

        name = "move_effects"
