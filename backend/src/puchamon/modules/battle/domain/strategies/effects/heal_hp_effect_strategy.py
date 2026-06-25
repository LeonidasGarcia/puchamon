"""Strategy for `heal_hp` move effects."""

from .....pokedex.domain.entities.effects import HealPayload
from ...runtime import BattleStrategyContext, MoveEffectExecutionInput
from ...utils import format_pokemon_name
from .base import MoveEffectStrategy


class HealHpEffectStrategy(MoveEffectStrategy):
    kind = "heal_hp"

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Apply HP recovery to targets based on heal ratio."""
        if execution.effect.kind != self.kind:
            return

        payload = execution.effect.payload
        if not isinstance(payload, HealPayload):
            return

        if not execution.target_instance_ids:
            return

        for target_id in execution.target_instance_ids:
            target = context.get_instance(target_id)
            if target.fainted or target.current_hp <= 0 or target.stats is None:
                continue

            heal_amount = int(target.stats.hp * payload.ratio)
            if heal_amount <= 0:
                continue

            actual_heal = min(heal_amount, target.stats.hp - target.current_hp)
            target.current_hp += actual_heal

            context.add_event(
                kind="heal_hp",
                message=f"¡{format_pokemon_name(target.pokemon_id)} recuperó {actual_heal} PS!",
                target_instance_id=target_id,
                value=actual_heal,
            )
