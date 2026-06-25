"""Strategy for `self_hit_chance` condition effects."""

import random
from math import floor

from .....pokedex.domain.entities.conditions import SelfHitChanceEffect
from ...mechanics import faint_instance, resolve_damage_roll_percent
from ...runtime import BattleStrategyContext, ConditionEffectExecutionInput
from ...utils import format_pokemon_name
from .base import ConditionEffectStrategy


class SelfHitChanceConditionEffectStrategy(ConditionEffectStrategy):
    kind = "self_hit_chance"
    hook = "before_action"

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Apply confusion effect that may cause the Pokemon to hit itself."""
        if not isinstance(execution.effect, SelfHitChanceEffect):
            return

        instance = context.get_instance(execution.holder_instance_id)
        if instance.fainted or instance.current_hp <= 0:
            return

        chance = execution.effect.payload.chance / 100.0

        if random.random() < chance:
            self._handle_confusion_damage(context, execution, instance)
        else:
            # Emits the message that it is confused, but the attack proceeds
            context.add_event(
                kind="condition_message",
                message=f"¡{format_pokemon_name(instance.pokemon_id)} está confuso!",
                target_instance_id=str(instance.id),
                condition_id=execution.condition.id,
            )

    def _handle_confusion_damage(self, context, execution, instance):
        context.mark_action_blocked(execution.holder_instance_id, self.kind)

        # Confusion damage is a 40 BP typeless physical attack without STAB, calculated normally
        # For simplicity here we'll approximate confusion damage if full damage formula isn't available easily
        # But the correct way is using level, attack, and defense

        level = getattr(instance, "level", 50)
        attack = getattr(instance.stats, "atk", 50) if getattr(instance, "stats", None) else 50
        defense = getattr(instance.stats, "def_", 50) if getattr(instance, "stats", None) else 50

        # Simplified damage formula: (((2 * level / 5 + 2) * 40 * atk / def) / 50 + 2)
        power = 40
        base_damage = floor(floor(floor(2 * level / 5 + 2) * power * attack / defense) / 50 + 2)

        roll_percent = resolve_damage_roll_percent()
        damage = max(1, floor((base_damage * roll_percent) / 100.0))

        applied_damage = min(instance.current_hp, damage)
        instance.current_hp -= applied_damage

        context.add_event(
            kind="action_skipped",
            message=f"¡{format_pokemon_name(instance.pokemon_id)} está tan confuso que se hirió a sí mismo!",
            target_instance_id=str(instance.id),
            condition_id=execution.condition.id,
        )
        context.add_event(
            kind="condition_damage",
            message="",
            target_instance_id=str(instance.id),
            condition_id=execution.condition.id,
            value=applied_damage,
        )

        if instance.current_hp == 0:
            faint_instance(context, instance)
