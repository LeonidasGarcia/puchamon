"""Strategy for `modify_stat` move effects."""

from .....pokedex.domain.entities.effects import ModifyStatPayload
from ...exceptions import BattleValidationError
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from .base import MoveEffectStrategy


class ModifyStatEffectStrategy(MoveEffectStrategy):
    kind = "modify_stat"

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Modify the stat stages of target pokemons."""
        if execution.effect.kind != self.kind:
            return

        payload = execution.effect.payload
        if not isinstance(payload, ModifyStatPayload):
            raise BattleValidationError("Modify stat effect strategies require a ModifyStatPayload instance")

        for target_id in execution.target_instance_ids:
            target = context.get_instance(target_id)
            if target.fainted or target.current_hp <= 0:
                continue

            for change in payload.changes:
                stat_key = "def_" if change.stat == "def" else change.stat

                # Check if stat exists in StatStages
                if not hasattr(target.stages, stat_key):
                    continue

                current_stage = getattr(target.stages, stat_key)

                # Pokémon Gen 5 rules: Stages are capped between -6 and +6
                new_stage = max(-6, min(6, current_stage + change.stages))

                if new_stage == current_stage:
                    # No change occurred (already at max/min)
                    message = f"{target.pokemon_id}'s {change.stat.upper()} won't go any {'higher' if change.stages > 0 else 'lower'}!"
                    context.add_event(
                        kind="stat_change_failed",
                        message=message,
                        target_instance_id=target_id,
                        stat=change.stat,
                    )
                    continue

                setattr(target.stages, stat_key, new_stage)

                # Descriptive messages based on the amount of change
                if change.stages >= 3:
                    desc = "rose drastically"
                elif change.stages == 2:
                    desc = "rose sharply"
                elif change.stages == 1:
                    desc = "rose"
                elif change.stages == -1:
                    desc = "fell"
                elif change.stages == -2:
                    desc = "fell harshly"
                else: # -3 or lower
                    desc = "fell severely"

                context.add_event(
                    kind="stat_changed",
                    message=f"{target.pokemon_id}'s {change.stat.upper()} {desc}!",
                    target_instance_id=target_id,
                    stat=change.stat,
                    change=change.stages,
                    new_stage=new_stage,
                )
