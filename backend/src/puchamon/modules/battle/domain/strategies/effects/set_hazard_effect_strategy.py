"""Strategy for `set_hazard` move effects."""

from .....pokedex.domain.entities.effects import SetHazardPayload
from ...battlefield import get_opponent_trainer_id, get_side_for_trainer
from ...exceptions import BattleValidationError
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from .pending import PendingMoveEffectStrategy


class SetHazardEffectStrategy(PendingMoveEffectStrategy):
    kind = "set_hazard"

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Add entry hazards to the target side of the field."""
        if execution.effect.kind != self.kind:
            return super().apply(context, execution)

        payload = execution.effect.payload
        if not isinstance(payload, SetHazardPayload):
            raise BattleValidationError("Set hazard effect strategies require a SetHazardPayload instance")

        source_instance = context.get_instance(execution.source_instance_id)

        # Hazards target sides, not specific pokemons.
        # Most hazard moves target the foe_side by default in Pokedex metadata.
        # But we resolve the side based on the effect's target definition.

        target_side_trainer_ids: list[str] = []
        if execution.effect.target == "foe_side":
            target_side_trainer_ids = [get_opponent_trainer_id(context.battle, source_instance.trainer_id)]
        elif execution.effect.target == "ally_side":
            target_side_trainer_ids = [source_instance.trainer_id]
        elif execution.effect.target == "field":
            target_side_trainer_ids = list(context.battle.sides.keys())
        else:
            # Default to opponent's side if not specified correctly
            target_side_trainer_ids = [get_opponent_trainer_id(context.battle, source_instance.trainer_id)]

        for trainer_id in target_side_trainer_ids:
            side = get_side_for_trainer(context.battle, trainer_id)

            current_layers = side.hazards.count(payload.hazard_id)
            if current_layers >= payload.max_layers:
                context.add_event(
                    kind="hazard_failed",
                    message=f"{payload.hazard_id.replace('_', ' ').capitalize()} failed! The maximum layers are already set.",
                    source_instance_id=execution.source_instance_id,
                )
                continue

            # Add the layers
            layers_to_add = min(payload.layers, payload.max_layers - current_layers)
            for _ in range(layers_to_add):
                side.hazards.append(payload.hazard_id)

            context.add_event(
                kind="hazard_set",
                message=f"{payload.hazard_id.replace('_', ' ').capitalize()} were set on the side!",
                source_instance_id=execution.source_instance_id,
                hazard_id=payload.hazard_id,
                total_layers=current_layers + layers_to_add,
            )
