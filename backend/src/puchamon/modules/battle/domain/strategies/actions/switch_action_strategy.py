"""Strategy for executing switch actions."""

from ...battlefield import get_active_slot_for_instance, get_side_for_trainer, set_active_instance_for_slot
from ...exceptions import BattleConflictError, BattleValidationError
from ...runtime import ActionExecutionInput, BattleStrategyContext
from ...utils import format_pokemon_name
from .base import ActionStrategy


class SwitchActionStrategy(ActionStrategy):
    """Execute a turn action whose type is `switch`."""

    action_type = "switch"

    def execute(self, context: BattleStrategyContext, execution: ActionExecutionInput) -> None:
        """Resolve a switch action against the current mutable battle state."""
        if execution.action.type != self.action_type:
            raise BattleValidationError(f"SwitchActionStrategy cannot execute action type '{execution.action.type}'")

        if execution.replacement_instance_id is None:
            raise BattleValidationError("Switch actions require a replacement instance id")

        if execution.action.user_instance_id == "":
            replacement_instance = context.get_instance(execution.replacement_instance_id)
            side = get_side_for_trainer(context.battle, replacement_instance.trainer_id)

            try:
                empty_slot = side.active_pokemon_instance_ids.index(None)
            except ValueError as exc:
                raise BattleConflictError("There is no empty slot available for the replacement") from exc

            set_active_instance_for_slot(side, empty_slot, execution.replacement_instance_id)
            replacement_instance.is_revealed = True

            context.add_event(
                kind="replacement",
                message=f"{format_pokemon_name(replacement_instance.pokemon_id)} entered the battlefield",
                source_instance_id=None,
                target_instance_id=execution.replacement_instance_id,
                active_slot=empty_slot,
            )
            return

        source_instance = context.get_instance(execution.action.user_instance_id)
        replacement_instance = context.get_instance(execution.replacement_instance_id)

        if execution.action.player != source_instance.trainer_id:
            raise BattleValidationError("Switch actions must be declared by the trainer that owns the source instance")

        if source_instance.trainer_id != replacement_instance.trainer_id:
            raise BattleValidationError("Switch replacements must belong to the same trainer as the source instance")

        if replacement_instance.fainted or replacement_instance.current_hp <= 0:
            raise BattleConflictError("A fainted pokemon cannot enter the battlefield as a switch replacement")

        side = get_side_for_trainer(context.battle, source_instance.trainer_id)

        if source_instance.fainted or source_instance.current_hp <= 0:
            try:
                empty_slot = side.active_pokemon_instance_ids.index(None)
            except ValueError:
                empty_slot = 0
            set_active_instance_for_slot(side, empty_slot, execution.replacement_instance_id)
            replacement_instance.is_revealed = True
            context.add_event(
                kind="switch",
                message=(f"{format_pokemon_name(replacement_instance.pokemon_id)} entered the battlefield"),
                source_instance_id=None,
                target_instance_id=execution.replacement_instance_id,
                active_slot=empty_slot,
            )
            return

        source_active_slot = get_active_slot_for_instance(side, execution.action.user_instance_id)

        if execution.replacement_instance_id in side.active_pokemon_instance_ids:
            raise BattleConflictError("The requested replacement instance is already active on the battlefield")

        set_active_instance_for_slot(side, source_active_slot, execution.replacement_instance_id)
        replacement_instance.is_revealed = True

        context.add_event(
            kind="switch",
            message=(
                f"{format_pokemon_name(source_instance.pokemon_id)} switched out and "
                f"{format_pokemon_name(replacement_instance.pokemon_id)} entered the battlefield"
            ),
            source_instance_id=execution.action.user_instance_id,
            target_instance_id=execution.replacement_instance_id,
            active_slot=source_active_slot,
        )
