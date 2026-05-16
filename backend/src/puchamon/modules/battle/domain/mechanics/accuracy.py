"""Mechanics for move accuracy calculation."""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....pokedex.domain.entities import Movement
    from ..entities import BattleInstance


def calculate_accuracy(
    movement: "Movement",
    target_instance: "BattleInstance",
) -> bool:
    """Determine if a move hits its target based on accuracy and evasion."""
    del target_instance  # reserved for future accuracy/evasion stage support
    if movement.accuracy is None or movement.accuracy == 0:
        return True

    roll = random.randint(1, 100)
    return roll <= movement.accuracy
