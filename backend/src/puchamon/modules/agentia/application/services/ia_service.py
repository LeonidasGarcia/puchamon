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
    ActionSelector,
    AIDifficultyLevel,
    MinimaxActionSelector,
    RandomActionSelector,
)
from ...domain.minimax import MinimaxMetrics


def _slot_sort_value(instance: BattleInstance) -> int:
    """Return the team slot order, placing unknown slots last."""
    if isinstance(instance.slot, int):
        return instance.slot
    return 999


class IAService:
    """Service class for generating AI actions in battles."""

    async def generate_switch_action(
        self,
        player: Player,
        battle: Battle,
        instances: dict[str, BattleInstance],
        ai_level: AIDifficultyLevel = AI_LEVEL_EASY,  # noqa: ARG002
    ) -> TurnAction | None:
        """Generate a forced switch action for an AI player that needs a replacement."""
        side = battle.sides.get(player.trainer_id)
        if not side or all(slot is not None for slot in side.active_pokemon_instance_ids):
            return None

        active_ids = {instance_id for instance_id in side.active_pokemon_instance_ids if instance_id is not None}
        replacement = None
        for instance in sorted(instances.values(), key=_slot_sort_value):
            if instance.trainer_id == player.trainer_id and str(instance.id) not in active_ids and not instance.fainted and instance.current_hp > 0:
                replacement = instance
                break
        if replacement is None:
            return None

        return TurnAction(
            player=player.trainer_id,
            type="switch",
            user_instance_id="",
            replacement_instance_id=str(replacement.id),
        )

    async def generate_action(  # noqa: PLR0913
        self,
        player: Player,
        battle: Battle,
        instances: dict[str, BattleInstance],
        ai_level: AIDifficultyLevel = AI_LEVEL_EASY,
        movements: Mapping[str, Movement] | None = None,
        type_chart: Mapping[str, Type] | None = None,
        level_3_weights: Mapping[str, float] | None = None,
        minimax_depth: int = DEFAULT_MINIMAX_DEPTH,
        minimax_metrics: MinimaxMetrics | None = None,
        move_effects: Mapping[str, MoveEffect] | None = None,
    ) -> TurnAction | None:
        """Generate a TurnAction for an AI player.

        Args:
            player: The AI player entity.
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            ai_level: AI difficulty level (1=easy, 2=medium, 3=hard manual, 4=hard GA).
            movements: Dict of Movement entities keyed by ID.
            move_effects: Dict of MoveEffect entities keyed by ID.
            type_chart: Dict of Type entities keyed by ID.
            level_3_weights: Optional chromosome weights used by GA training or benchmark evaluation.
            minimax_depth: Search depth used by Minimax levels.
            minimax_metrics: Optional counters populated by Minimax levels.

        Returns:
            A TurnAction for the AI player or None if no actions available.
        """
        selector: ActionSelector
        if ai_level == AI_LEVEL_EASY:
            selector = RandomActionSelector()
        else:
            selector = MinimaxActionSelector(ai_level, depth=minimax_depth, level_3_weights=level_3_weights)

        action = selector.select(
            battle,
            instances,
            player.trainer_id,
            movements,
            type_chart,
            minimax_metrics,
            move_effects=move_effects,
        )

        if action is None:
            return None

        action_type, action_id = action

        if action_type == "MOVE":
            side = battle.sides.get(player.trainer_id)
            active_ids = [uid for uid in side.active_pokemon_instance_ids if uid is not None] if side else []
            active_instance_id = active_ids[0] if active_ids else None

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
        else:
            side = battle.sides.get(player.trainer_id)
            active_ids = [uid for uid in side.active_pokemon_instance_ids if uid is not None] if side else []
            active_instance_id = active_ids[0] if active_ids else None

            return TurnAction(
                player=player.trainer_id,
                type="switch",
                user_instance_id=str(active_instance_id) if active_instance_id else "",
                replacement_instance_id=action_id,
            )
