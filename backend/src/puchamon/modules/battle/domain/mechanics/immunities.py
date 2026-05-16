"""Pure mechanics for status and type immunities."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities import BattleInstance


def is_immune_to_status(instance: "BattleInstance", status_id: str) -> bool:
    """Check if a pokemon is immune to a major status condition based on its types."""
    # Gen 5 Rules:
    # Fire types cannot be burned.
    if status_id == "burn" and "fire" in instance.types:
        return True

    # Poison and Steel types cannot be poisoned (Poison/Toxic).
    if status_id in {"poison", "toxic"} and ("poison" in instance.types or "steel" in instance.types):
        return True

    # Electric types cannot be paralyzed by Electric moves (Gen 6+),
    # but in Gen 5 they CAN be paralyzed (except by Thunder Wave if they are Ground, etc.).
    # For now, following strict Gen 5, Electric types have no inherent status immunity to paralysis.

    # Ice types cannot be frozen.
    return status_id == "freeze" and "ice" in instance.types


def is_immune_to_volatile(instance: "BattleInstance", volatile_id: str) -> bool:
    """Check if a pokemon is immune to a volatile status condition."""
    # Grass types are immune to Leech Seed (seeded).
    return volatile_id == "seeded" and "grass" in instance.types
