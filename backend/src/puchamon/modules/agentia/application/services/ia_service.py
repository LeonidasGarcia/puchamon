"""Service for handling IA-related logic."""

from collections.abc import Mapping

from ....battle.domain.entities import (
    Battle,
    BattleInstance,
    Player,
    TargetScope,
    TurnAction,
)
from ....pokedex.domain.entities import MoveEffect, Movement, Type
from ...domain.action_selectors import (
    AI_LEVEL_EASY,
    DEFAULT_MINIMAX_DEPTH,
    Action,
    ActionSelector,
    AIDifficultyLevel,
    MinimaxActionSelector,
    RandomActionSelector,
)
from ...domain.minimax import MinimaxMetrics


def _slot_sort_value(instance: BattleInstance) -> int:
    if isinstance(instance.slot, int):
        return instance.slot
    return 999


def _needs_replacement(side_instance_ids: list[str | None], instances: dict[str, BattleInstance]) -> bool:
    for instance_id in side_instance_ids:
        if instance_id is None:
            return True
        instance = instances.get(instance_id)
        if instance is None or instance.fainted or instance.current_hp <= 0:
            return True
    return False


def _available_replacement_actions(player: Player, battle: Battle, instances: dict[str, BattleInstance]) -> list[Action]:
    side = battle.sides.get(player.trainer_id)
    if side is None:
        return []

    active_ids = {instance_id for instance_id in side.active_pokemon_instance_ids if instance_id is not None}
    actions: list[Action] = []
    for instance in sorted(instances.values(), key=_slot_sort_value):
        if instance.trainer_id == player.trainer_id and str(instance.id) not in active_ids and not instance.fainted and instance.current_hp > 0:
            actions.append(("SWITCH", str(instance.id)))
    return actions


class IAService:
    """Service class for generating AI actions in battles."""

    def generate_switch_action(  # noqa: PLR0913
        self,
        player: Player,
        battle: Battle,
        instances: dict[str, BattleInstance],
        ai_level: AIDifficultyLevel = AI_LEVEL_EASY,
        movements: Mapping[str, Movement] | None = None,
        type_chart: Mapping[str, Type] | None = None,
        move_effects: Mapping[str, MoveEffect] | None = None,
        level_3_weights: Mapping[str, float] | None = None,
        minimax_depth: int = DEFAULT_MINIMAX_DEPTH,
        minimax_metrics: MinimaxMetrics | None = None,
    ) -> TurnAction | None:
        """Generate a forced switch action for an AI player that needs a replacement."""
        side = battle.sides.get(player.trainer_id)
        if not side or not _needs_replacement(side.active_pokemon_instance_ids, instances):
            return None

        replacement_actions = _available_replacement_actions(player, battle, instances)
        if not replacement_actions:
            return None

        action = replacement_actions[0]
        if ai_level != AI_LEVEL_EASY:
            selector = MinimaxActionSelector(ai_level, depth=minimax_depth, level_3_weights=level_3_weights)
            selected_action = selector.select_from_actions(
                battle,
                instances,
                player.trainer_id,
                replacement_actions,
                movements,
                type_chart,
                move_effects=move_effects,
                metrics=minimax_metrics,
            )
            if selected_action is not None and selected_action[0] == "SWITCH":
                action = selected_action

        return TurnAction(
            player=player.trainer_id,
            type="switch",
            user_instance_id="",
            replacement_instance_id=action[1],
        )

    def generate_action(  # noqa: PLR0913
        self,
        player: Player,
        battle: Battle,
        instances: dict[str, BattleInstance],
        ai_level: AIDifficultyLevel = AI_LEVEL_EASY,
        movements: Mapping[str, Movement] | None = None,
        type_chart: Mapping[str, Type] | None = None,
        move_effects: Mapping[str, MoveEffect] | None = None,
        level_3_weights: Mapping[str, float] | None = None,
        minimax_depth: int = DEFAULT_MINIMAX_DEPTH,
        minimax_metrics: MinimaxMetrics | None = None,
    ) -> TurnAction | None:
        """Generate a TurnAction for an AI player."""
        selector: ActionSelector
        if ai_level == AI_LEVEL_EASY:
            selector = RandomActionSelector()
        else:
            selector = MinimaxActionSelector(ai_level, depth=minimax_depth, level_3_weights=level_3_weights)

        action = selector.select(battle, instances, player.trainer_id, movements, type_chart, move_effects=move_effects, metrics=minimax_metrics)

        if action is None:
            return None

        action_type, action_id = action

        side = battle.sides.get(player.trainer_id)
        active_ids = [uid for uid in side.active_pokemon_instance_ids if uid is not None] if side else []
        active_instance_id = active_ids[0] if active_ids else None

        if action_type == "MOVE":
            return TurnAction(
                player=player.trainer_id,
                type="move",
                user_instance_id=str(active_instance_id) if active_instance_id else "",
                move_id=action_id,
                target=TargetScope(
                    scope="target",
                    target_side="foe_side",
                    target_active_slot=0,
                ),
            )
        if action_type == "SWITCH":
            return TurnAction(
                player=player.trainer_id,
                type="switch",
                user_instance_id=str(active_instance_id) if active_instance_id else "",
                replacement_instance_id=action_id,
            )
