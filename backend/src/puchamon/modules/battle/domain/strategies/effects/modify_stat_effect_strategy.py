"""Strategy for `modify_stat` move effects."""

from .....pokedex.domain.entities.effects import ModifyStatPayload
from ...exceptions import BattleValidationError
from ...rules import MAX_STAT_STAGE, MIN_STAT_STAGE
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from ...utils import format_pokemon_name
from .base import MoveEffectStrategy

DRASTIC_RISE = 3
SHARP_RISE = 2
NORMAL_RISE = 1
NORMAL_FALL = -1
HARSH_FALL = -2


def _get_stage_change_description(change_amount: int) -> str:
    """Return a descriptive message based on the amount of stage change."""
    if change_amount >= DRASTIC_RISE:
        return "subió drásticamente"
    if change_amount == SHARP_RISE:
        return "subió mucho"
    if change_amount == NORMAL_RISE:
        return "subió"
    if change_amount == NORMAL_FALL:
        return "bajó"
    return "bajó mucho" if change_amount == HARSH_FALL else "bajó severamente"


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
            self._apply_to_target(context, target_id, payload)

    def _apply_to_target(self, context: BattleStrategyContext, target_id: str, payload: ModifyStatPayload) -> None:
        target = context.get_instance(target_id)
        if target.fainted or target.current_hp <= 0:
            return

        for change in payload.changes:
            stat_key = "def_" if change.stat == "def" else change.stat

            # Check if stat exists in StatStages
            if not hasattr(target.stages, stat_key):
                continue

            current_stage = getattr(target.stages, stat_key)

            # Pokémon Gen 5 rules: Stages are capped between MIN_STAT_STAGE and MAX_STAT_STAGE
            new_stage = max(MIN_STAT_STAGE, min(MAX_STAT_STAGE, current_stage + change.stages))

            if new_stage == current_stage:
                # No change occurred (already at max/min)
                direction = "subir" if change.stages > 0 else "bajar"
                stat_name = change.stat.upper()
                pkmn_name = format_pokemon_name(target.pokemon_id)
                message = f"¡El {stat_name} de {pkmn_name} no puede {direction} más!"
                context.add_event(
                    kind="stat_change_failed",
                    message=message,
                    target_instance_id=target_id,
                    stat=change.stat,
                )
                continue

            setattr(target.stages, stat_key, new_stage)

            desc = _get_stage_change_description(change.stages)

            context.add_event(
                kind="stat_changed",
                message=f"¡El {change.stat.upper()} de {format_pokemon_name(target.pokemon_id)} {desc}!",
                target_instance_id=target_id,
                stat=change.stat,
                change=change.stages,
                new_stage=new_stage,
            )
