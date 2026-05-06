"""Mechanics for battle instance lifecycle events (fainting, etc.)."""

from typing import TYPE_CHECKING

from ..battlefield import get_active_slot_for_instance, get_side_for_trainer, set_active_instance_for_slot

if TYPE_CHECKING:
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
        slot = None

    context.mark_fainted(str(instance.id))
    context.add_event(
        kind="pokemon_fainted",
        message=f"{instance.pokemon_id} fainted!",
        target_instance_id=str(instance.id),
        active_slot=slot,
    )
