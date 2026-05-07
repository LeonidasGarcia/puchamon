"""Strategy for `end_turn_damage` weather effects."""

from math import floor

from .....pokedex.domain.entities.weathers import EndTurnDamageEffect
from ...mechanics import faint_instance
from ...runtime import BattleStrategyContext, WeatherEffectExecutionInput
from ...utils import format_pokemon_name
from .base import WeatherEffectStrategy


class EndTurnDamageWeatherEffectStrategy(WeatherEffectStrategy):
    kind = "end_turn_damage"
    hook = "end_turn"

    def apply(self, context: BattleStrategyContext, execution: WeatherEffectExecutionInput) -> None:
        """Apply damage at the end of the turn to non-immune pokemons."""
        if not isinstance(execution.effect, EndTurnDamageEffect):
            return

        payload = execution.effect.payload
        for instance in context.battle_instances.values():
            if instance.fainted or instance.current_hp <= 0:
                continue

            # Check for type immunity
            if any(t in instance.types for t in payload.immune_types):
                continue

            damage = max(1, floor(instance.max_hp * payload.ratio))
            applied_damage = min(instance.current_hp, damage)
            instance.current_hp -= applied_damage

            context.add_event(
                kind="weather_damage",
                message=f"{format_pokemon_name(instance.pokemon_id)} is buffeted by the {execution.weather.name}!",
                target_instance_id=instance.id,
                value=applied_damage,
            )

            if instance.current_hp == 0:
                faint_instance(context, instance)
