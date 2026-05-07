"""Service for handling IA-related logic."""

import random
from typing import Literal

from ....battle.domain.entities import (
    Battle,
    BattleInstance,
    Player,
    TargetScope,
    TurnAction,
)

AIDifficultyLevel = Literal[1, 2, 3]
AI_LEVEL_EASY = 1
AI_LEVEL_MEDIUM = 2
AI_LEVEL_HARD = 3


class IAService:
    """Service class for generating AI actions in battles."""

    async def generate_action(
        self,
        player: Player,
        battle: Battle,
        instances: dict[str, BattleInstance],
        ai_level: AIDifficultyLevel = AI_LEVEL_EASY,
    ) -> TurnAction:
        """Generate a TurnAction for an AI player.

        Args:
            player: The AI player entity.
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            ai_level: AI difficulty level (1=easy, 2=medium, 3=hard).

        Returns:
            A TurnAction for the AI player.
        """
        side = battle.sides.get(player.trainer_id)
        if not side:
            raise ValueError(f"Player {player.trainer_id} not found in battle sides")

        active_ids = side.active_pokemon_instance_ids
        active_instance_ids = [uid for uid in active_ids if uid is not None]

        if not active_instance_ids:
            raise ValueError(f"Player {player.trainer_id} has no active pokemon")

        active_instance = instances.get(active_instance_ids[0])
        if not active_instance:
            raise ValueError(f"Active instance {active_instance_ids[0]} not found")

        if active_instance.fainted:
            switch_action = await self.generate_switch_action(
                player, battle, instances
            )
            if switch_action:
                return switch_action

        move_action = await self.generate_move_action(
            player, active_instance, ai_level
        )
        if move_action:
            return move_action

        switch_action = await self.generate_switch_action(
            player, battle, instances
        )
        if switch_action:
            return switch_action

        raise ValueError("AI has no valid actions available")

    async def generate_move_action(
        self,
        player: Player,
        active_instance: BattleInstance,
        ai_level: AIDifficultyLevel = AI_LEVEL_EASY,
    ) -> TurnAction | None:
        """Generate a move action for the AI.

        Args:
            player: The AI player entity.
            active_instance: The active BattleInstance.
            ai_level: AI difficulty level (1=easy, 2=medium, 3=hard).

        Returns:
            A TurnAction with type="move" or None if no moves available.
        """
        available_moves = [
            ms for ms in active_instance.move_state if ms.current_pp > 0
        ]

        if not available_moves:
            return None

        move_id = self._select_move_by_level(available_moves, ai_level)

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
    ) -> TurnAction | None:
        """Generate a switch action for the AI.

        Args:
            player: The AI player entity.
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.

        Returns:
            A TurnAction with type="switch" or None if no replacements available.
        """
        side = battle.sides.get(player.trainer_id)
        if not side:
            return None

        active_ids = set(
            uid for uid in side.active_pokemon_instance_ids if uid is not None
        )

        available_replacements = [
            inst
            for inst in instances.values()
            if inst.trainer_id == player.trainer_id
            and not inst.fainted
            and inst.id not in active_ids
        ]

        if not available_replacements:
            return None

        replacement = available_replacements[0]

        return TurnAction(
            player=player.trainer_id,
            type="switch",
            user_instance_id=str(next(iter(active_ids))) if active_ids else "",
            replacement_instance_id=str(replacement.id),
        )

    def _select_move_by_level(
        self,
        available_moves: list,
        ai_level: AIDifficultyLevel,
    ) -> str | None:
        """Select a move based on AI difficulty level.

        Args:
            available_moves: List of MoveState with PP > 0.
            ai_level: AI difficulty level.

        Returns:
            The move_id of the selected move or None if no moves available.
        """
        if not available_moves:
            return None

        if ai_level == AI_LEVEL_EASY:
            return self._select_random_move(available_moves)
        elif ai_level == AI_LEVEL_MEDIUM:
            return self._select_move_by_hp(available_moves)
        else:
            return self._select_random_move(available_moves)

    def _select_random_move(self, available_moves: list) -> str:
        """Select a random move (Level 1 - Easy).

        Args:
            available_moves: List of MoveState with PP > 0.

        Returns:
            A random move_id.
        """
        return random.choice(available_moves).move_id

    def _select_move_by_hp(
        self,
        available_moves: list,
    ) -> str:
        """Select a move based on target HP (Level 2 - Medium).

        Selects the move of the opponent with the lowest HP percentage,
        then picks a random available move. This is a placeholder
        for a more sophisticated HP-based selection.

        Args:
            available_moves: List of MoveState with PP > 0.

        Returns:
            A random move_id (placeholder for HP-based logic).
        """
        return random.choice(available_moves).move_id
