"""Strategy for `self_switch` move effects."""

from ...battlefield import get_active_slot_for_instance, get_side_for_trainer, set_active_instance_for_slot
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from .base import MoveEffectStrategy


class SelfSwitchEffectStrategy(MoveEffectStrategy):
    kind = "self_switch"

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Handle moves that cause the user to switch out (e.g. Volt Switch, U-turn)."""
        if execution.effect.kind != self.kind:
            return

        source = context.get_instance(execution.source_instance_id)
        if source.fainted or source.current_hp <= 0:
            return

        # In Gen 5, self-switch effects (Volt Switch, U-turn) trigger after damage.
        # The user returns to the party.

        side = get_side_for_trainer(context.battle, source.trainer_id)
        slot = get_active_slot_for_instance(side, source.id)

        # Remove from active slot
        set_active_instance_for_slot(side, slot, None)

        context.add_event(
            kind="self_switch",
            message=f"{source.pokemon_id} went back to its trainer!",
            source_instance_id=execution.source_instance_id,
            active_slot=slot,
        )
