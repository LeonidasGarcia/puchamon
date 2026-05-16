"""Service for handling IA-related logic."""

from typing import Literal

from ....battle.domain.entities import (
    Battle,
    BattleInstance,
    Player,
    TargetScope,
    TurnAction,
)
from ...domain.move_selectors import GreedyHPMoveSelector, MoveSelector, RandomMoveSelector
from ...domain.switch_selectors import BestHPSwitchSelector, RandomSwitchSelector, SwitchSelector

AIDifficultyLevel = Literal[1, 2]
AI_LEVEL_EASY = 1
AI_LEVEL_MEDIUM = 2


class IAService:
    """Service class for generating AI actions in battles."""

    async def generate_action(
        self,
        player: Player,
        battle: Battle,
        instances: dict[str, BattleInstance],
        ai_level: AIDifficultyLevel = AI_LEVEL_EASY,
        movements: dict | None = None,
    ) -> TurnAction:
        """Generate a TurnAction for an AI player.

        Args:
            player: The AI player entity.
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            ai_level: AI difficulty level (1=easy, 2=medium).
            movements: Dict of Movement entities keyed by ID.

        Returns:
            A TurnAction for the AI player.
        """
        side = battle.sides.get(player.trainer_id)
        if not side:
            raise ValueError(f"Player {player.trainer_id} not found in battle sides")

        active_ids = side.active_pokemon_instance_ids
        active_instance_ids = [uid for uid in active_ids if uid is not None]

        if not active_instance_ids:
            switch_action = await self.generate_switch_action(player, battle, instances, ai_level)
            if switch_action:
                return switch_action
            raise ValueError(f"Player {player.trainer_id} has no active pokemon and no replacements available")

        active_instance = instances.get(active_instance_ids[0])
        if not active_instance:
            raise ValueError(f"Active instance {active_instance_ids[0]} not found")

        if active_instance.fainted:
            switch_action = await self.generate_switch_action(player, battle, instances, ai_level)
            if switch_action:
                return switch_action

        move_action = await self.generate_move_action(player, active_instance, ai_level, battle, instances, movements)
        if move_action:
            return move_action

        switch_action = await self.generate_switch_action(player, battle, instances, ai_level)
        if switch_action:
            return switch_action

        raise ValueError("AI has no valid actions available")

    async def generate_move_action(
        self,
        player: Player,
        active_instance: BattleInstance,
        ai_level: AIDifficultyLevel = AI_LEVEL_EASY,
        battle: Battle | None = None,
        instances: dict[str, BattleInstance] | None = None,
        movements: dict | None = None,
    ) -> TurnAction | None:
        """Generate a move action for the AI.

        Args:
            player: The AI player entity.
            active_instance: The active BattleInstance.
            ai_level: AI difficulty level (1=easy, 2=medium).
            battle: The current battle state (needed for medium AI).
            instances: Dict of battle instances (needed for medium AI).
            movements: Dict of Movement entities keyed by ID.

        Returns:
            A TurnAction with type="move" or None if no moves available.
        """
        available_moves = [ms for ms in active_instance.move_state if ms.current_pp > 0]

        if not available_moves:
            return None

        selector: MoveSelector
        if ai_level == AI_LEVEL_EASY or not battle or not instances:
            selector = RandomMoveSelector()
        else:
            selector = GreedyHPMoveSelector(battle, instances, movements)
        move_id = selector.select(available_moves)

        if move_id is None:
            return None

        return TurnAction(
            player=player.trainer_id,
            type="move",
            user_instance_id=str(active_instance.id),
            move_id=move_id,
            target=TargetScope(
                scope="target",
                target_side="foe_side",
                target_active_slot=0,
            ),
        )

    async def generate_switch_action(
        self,
        player: Player,
        battle: Battle,
        instances: dict[str, BattleInstance],
        ai_level: AIDifficultyLevel = AI_LEVEL_EASY,
    ) -> TurnAction | None:
        """Generate a switch action for the AI.

        Args:
            player: The AI player entity.
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            ai_level: AI difficulty level (1=easy, 2=medium).

        Returns:
            A TurnAction with type="switch" or None if no replacements available.
        """
        side = battle.sides.get(player.trainer_id)
        if not side:
            return None

        selector: SwitchSelector
        if ai_level == AI_LEVEL_EASY:
            selector = RandomSwitchSelector()
        else:
            selector = BestHPSwitchSelector()

        replacement_id = selector.select(battle, instances, player.trainer_id)

        if replacement_id is None:
            return None

        active_ids = {
            uid for uid in side.active_pokemon_instance_ids if uid is not None
        }

        return TurnAction(
            player=player.trainer_id,
            type="switch",
            user_instance_id=str(next(iter(active_ids))) if active_ids else "",
            replacement_instance_id=replacement_id,
        )
