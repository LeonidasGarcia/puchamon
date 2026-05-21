"""Strategy for `protect` move effects."""

import random

from loguru import logger

from .....pokedex.domain.entities.effects import ProtectPayload
from ...exceptions import BattleValidationError
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from ...utils import format_pokemon_name
from .base import MoveEffectStrategy


class ProtectEffectStrategy(MoveEffectStrategy):
    kind = "protect"

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Apply a protection status to the user."""
        if execution.effect.kind != self.kind:
            return

        payload = execution.effect.payload
        if not isinstance(payload, ProtectPayload):
            raise BattleValidationError("Protect effect strategies require a ProtectPayload instance")

        source = context.get_instance(execution.source_instance_id)
        if source.fainted or source.current_hp <= 0:
            return

        current_turn = context.battle.turn
        last_turn = source.turn_counters.get("_protect_last_turn", -1)

        if current_turn == last_turn + 1:
            consecutive = source.turn_counters.get("protect", 0) + 1
        else:
            consecutive = 1

        # Success rates mapping by consecutive use
        success_chances = {
            1: 1.0,
            2: 0.5,
            3: 0.25,
        }
        success_chance = success_chances.get(consecutive, 0.0)

        roll = random.random()

        logger.debug(
            f"[PROTECT] {source.pokemon_id}: turn_counters={source.turn_counters}, "
            f"consecutive={consecutive}, roll={roll:.2f}, success_chance={success_chance}"
        )

        if roll >= success_chance:
            source.turn_counters["protect"] = 0
            source.turn_counters["_protect_last_turn"] = current_turn
            logger.debug(f"[PROTECT] {source.pokemon_id}: FAILED - consecutive now=0")
            context.add_event(
                kind="move_failed",
                message=f"{format_pokemon_name(source.pokemon_id)} couldn't use Protect!",
                source_instance_id=execution.source_instance_id,
            )
            return

        source.turn_counters["protect"] = consecutive
        source.turn_counters["_protect_last_turn"] = current_turn
        logger.debug(f"[PROTECT] {source.pokemon_id}: SUCCESS - consecutive now={consecutive}")
        source.volatile_status.append("protect")
        context.add_event(
            kind="status_applied",
            message=f"{format_pokemon_name(source.pokemon_id)} protected itself!",
            target_instance_id=execution.source_instance_id,
            status_id="protect",
        )
