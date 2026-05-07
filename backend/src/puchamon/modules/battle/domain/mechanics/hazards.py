"""Mechanics for calculating and applying entry hazards."""

import math
from typing import TYPE_CHECKING

from ..rules import (
    SPIKES_LAYER_1,
    SPIKES_LAYER_1_RATIO,
    SPIKES_LAYER_2,
    SPIKES_LAYER_2_RATIO,
    SPIKES_LAYER_3_RATIO,
    STEALTH_ROCK_BASE_RATIO,
    TOXIC_SPIKES_TOXIC_THRESHOLD,
)
from ..utils import format_pokemon_name

if TYPE_CHECKING:
    from ....pokedex.domain.entities import Type
    from ..entities import BattleInstance, SideState
    from ..runtime import BattleStrategyContext


def calculate_stealth_rock_damage(instance: "BattleInstance", type_chart: dict[str, "Type"]) -> int:
    """Calculate Stealth Rock damage based on type effectiveness."""
    rock_type = type_chart.get("rock")
    effectiveness = 1.0
    if rock_type:
        for t in instance.types:
            if t in rock_type.super_effective:
                effectiveness *= 2.0
            elif t in rock_type.not_very_effective:
                effectiveness *= 0.5
            elif t in rock_type.no_effect:
                effectiveness *= 0.0

    if effectiveness <= 0:
        return 0

    return max(1, math.floor(instance.max_hp * STEALTH_ROCK_BASE_RATIO * effectiveness))


def calculate_spikes_damage(instance: "BattleInstance", side: "SideState") -> int:
    """Calculate Spikes damage based on the number of layers."""
    spikes_layers = side.hazards.count("spikes")
    if spikes_layers <= 0:
        return 0

    if spikes_layers == SPIKES_LAYER_1:
        fraction = SPIKES_LAYER_1_RATIO
    elif spikes_layers == SPIKES_LAYER_2:
        fraction = SPIKES_LAYER_2_RATIO
    else:
        fraction = SPIKES_LAYER_3_RATIO

    return max(1, math.floor(instance.max_hp * fraction))


def apply_entry_hazards(
    context: "BattleStrategyContext",
    instance_id: str,
    type_chart: dict[str, "Type"],
) -> None:
    """Calculate and apply damage/status from entry hazards to an instance."""
    instance = context.get_instance(instance_id)
    if instance.fainted or instance.current_hp <= 0:
        return

    # Find the side the pokemon belongs to
    side = next((s for s in context.battle.sides.values() if instance.id in s.active_pokemon_instance_ids), None)

    if not side or not side.hazards:
        return

    # Grounded check: Flying types and Levitate
    # TODO: Check item/ability modifiers for grounding later
    is_grounded = "flying" not in instance.types and instance.ability != "levitate"

    # 1. Stealth Rock
    if "stealth_rock" in side.hazards:
        damage = calculate_stealth_rock_damage(instance, type_chart)
        if damage > 0:
            applied_damage = min(instance.current_hp, damage)
            instance.current_hp -= applied_damage
            context.add_event(
                kind="hazard_damage",
                message=f"Pointed stones dug into {format_pokemon_name(instance.pokemon_id)}!",
                target_instance_id=instance.id,
                value=applied_damage,
            )
            if instance.current_hp <= 0:
                instance.fainted = True
                context.mark_fainted(instance.id)
                return

    # 2. Spikes
    if "spikes" in side.hazards and is_grounded:
        damage = calculate_spikes_damage(instance, side)
        if damage > 0:
            applied_damage = min(instance.current_hp, damage)
            instance.current_hp -= applied_damage
            context.add_event(
                kind="hazard_damage",
                message=f"{format_pokemon_name(instance.pokemon_id)} was hurt by spikes!",
                target_instance_id=instance.id,
                value=applied_damage,
            )
            if instance.current_hp <= 0:
                instance.fainted = True
                context.mark_fainted(instance.id)
                return

    # 3. Toxic Spikes
    if "toxic_spikes" in side.hazards and is_grounded:
        if "poison" in instance.types:
            # Poison types absorb Toxic Spikes
            side.hazards = [h for h in side.hazards if h != "toxic_spikes"]
            context.add_event(
                kind="hazard_cleared",
                message=f"{format_pokemon_name(instance.pokemon_id)} absorbed the Toxic Spikes!",
                target_instance_id=instance.id,
                hazard_id="toxic_spikes",
            )
        elif instance.status is None:
            toxic_spikes_layers = side.hazards.count("toxic_spikes")
            status_to_apply = "toxic" if toxic_spikes_layers >= TOXIC_SPIKES_TOXIC_THRESHOLD else "poison"
            instance.status = status_to_apply
            context.add_event(
                kind="status_applied",
                message=f"{format_pokemon_name(instance.pokemon_id)} was poisoned by the Toxic Spikes!",
                target_instance_id=instance.id,
                status_id=status_to_apply,
            )
