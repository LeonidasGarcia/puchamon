"""Service for handling IA-related logic."""

from ....battle.domain.entities import (
    Battle,
    BattleInstance,
    Player,
    TargetScope,
    TurnAction,
)
from ...domain.action_selectors import (
    AI_LEVEL_EASY,
    ActionSelector,
    AIDifficultyLevel,
    MinimaxActionSelector,
    RandomActionSelector,
)


class IAService:
    """Service class for generating AI actions in battles."""

    async def generate_action(
        self,
        player: Player,
        battle: Battle,
        instances: dict[str, BattleInstance],
        ai_level: AIDifficultyLevel = AI_LEVEL_EASY,
        movements: dict | None = None,
    ) -> TurnAction | None:
        """Generate a TurnAction for an AI player.

        Args:
            player: The AI player entity.
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            ai_level: AI difficulty level (1=easy, 2=medium, 3=hard).
            movements: Dict of Movement entities keyed by ID.

        Returns:
            A TurnAction for the AI player or None if no actions available.
        """
        selector: ActionSelector
        if ai_level == AI_LEVEL_EASY:
            selector = RandomActionSelector()
        else:
            selector = MinimaxActionSelector(ai_level)

        action = selector.select(battle, instances, player.trainer_id, movements)

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
