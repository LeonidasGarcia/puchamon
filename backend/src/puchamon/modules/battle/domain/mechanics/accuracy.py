"""Mechanics for move accuracy calculation."""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....pokedex.domain.entities import Movement
    from ..entities import BattleInstance
    from ..runtime import BattleStrategyContext


def calculate_accuracy(
    context: "BattleStrategyContext",
    movement: "Movement",
    source_instance: "BattleInstance",
    target_instance: "BattleInstance",
) -> bool:
    """Determine if a move hits its target based on accuracy and evasion."""
    # 1. Moves that never miss (accuracy is None or 0 in some contexts, but usually handled by metadata)
    if movement.accuracy is None or movement.accuracy == 0:
        return True

    # 2. Base calculation (Gen 5)
    # TODO: Add support for accuracy/evasion stages and weather/ability modifiers
    # For now, we use a simple probability check based on the movement's base accuracy.
    
    # Random roll between 1 and 100
    roll = random.randint(1, 100)
    
    return roll <= movement.accuracy
