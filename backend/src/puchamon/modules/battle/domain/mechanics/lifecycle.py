"""Mechanics for battle instance lifecycle events (fainting, etc.)."""
from typing import TYPE_CHECKING

from ..battlefield import get_active_slot_for_instance, get_side_for_trainer, set_active_instance_for_slot

if TYPE_CHECKING:
    from ....pokedex.domain.entities import Type
    from ..entities import BattleInstance
    from ..runtime import BattleStrategyContext


def faint_instance(context: "BattleStrategyContext", instance: "BattleInstance") -> None:
    """Mark an instance as fainted and remove it from the active battlefield slots."""
    if instance.fainted:
        return

    instance.fainted = True
    instance.current_hp = 0

    side = get_side_for_trainer(context.battle, instance.trainer_id)
    try:
        slot = get_active_slot_for_instance(side, str(instance.id))
        set_active_instance_for_slot(side, slot, None)
    except Exception:
        # If the instance is not in an active slot, we just mark it as fainted
        slot = None

    context.mark_fainted(str(instance.id))
    context.add_event(
        kind="pokemon_fainted",
        message=f"{instance.pokemon_id} fainted!",
        target_instance_id=str(instance.id),
        active_slot=slot,
    )


def switch_in_instance(
    context: "BattleStrategyContext",
    instance_id: str,
    trainer_id: str,
    slot_index: int,
    type_chart: dict[str, "Type"],
) -> None:
    """Handle a pokemon entering the field."""
    from .hazards import apply_entry_hazards

    instance = context.get_instance(instance_id)
    side = get_side_for_trainer(context.battle, trainer_id)

    # 1. Update battlefield state
    set_active_instance_for_slot(side, slot_index, instance_id)
    instance.is_revealed = True

    # 2. Add entry event
    context.add_event(
        kind="switch_in",
        message=f"Go! {instance.pokemon_id}!",
        target_instance_id=instance_id,
        active_slot=slot_index,
    )

    # 3. Apply Entry Hazards
    apply_entry_hazards(context, instance_id, type_chart)

