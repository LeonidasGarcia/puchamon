"""Strategy for `remove_hazard` move effects."""

from .....pokedex.domain.entities.effects import RemoveHazardPayload
from ...battlefield import get_opponent_trainer_id, get_side_for_trainer
from ...exceptions import BattleValidationError
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from .pending import PendingMoveEffectStrategy


class RemoveHazardEffectStrategy(PendingMoveEffectStrategy):
    kind = "remove_hazard"

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Remove entry hazards from the field (e.g. Rapid Spin, Defog)."""
        if execution.effect.kind != self.kind:
            return super().apply(context, execution)

        payload = execution.effect.payload
        if not isinstance(payload, RemoveHazardPayload):
            raise BattleValidationError("Remove hazard effect strategies require a RemoveHazardPayload instance")

        source_instance = context.get_instance(execution.source_instance_id)

        # Resolve which sides to clear based on the move's target and payload
        # Rapid Spin clears the ally side. Defog clears both.
        target_side_trainer_ids: list[str] = []
        if execution.effect.target in {"self", "ally_side"}:
            target_side_trainer_ids = [source_instance.trainer_id]
        elif execution.effect.target == "foe_side":
            target_side_trainer_ids = [get_opponent_trainer_id(context.battle, source_instance.trainer_id)]
        elif execution.effect.target == "field":
            target_side_trainer_ids = list(context.battle.sides.keys())
        else:
            # For remove_hazard, Rapid Spin is usually 'self' target in metadata,
            # but it clears hazards on the ally_side.
            target_side_trainer_ids = [source_instance.trainer_id]

        for trainer_id in target_side_trainer_ids:
            side = get_side_for_trainer(context.battle, trainer_id)

            # If hazard_ids is empty, it means "clear everything" (like Rapid Spin/Defog in most cases)
            if not payload.hazard_ids:
                hazards_to_remove = list(set(side.hazards))
                side.hazards = []
            else:
                hazards_to_remove = [h for h in side.hazards if h in payload.hazard_ids]
                side.hazards = [h for h in side.hazards if h not in payload.hazard_ids]

            if hazards_to_remove:
                context.add_event(
                    kind="hazards_removed",
                    message="The hazards were removed from the field!",
                    source_instance_id=execution.source_instance_id,
                    removed_hazards=hazards_to_remove,
                )
