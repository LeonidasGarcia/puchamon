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
AI_HP_THRESHOLD = 0.5


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
            ai_level: AI difficulty level (1=easy, 2=medium, 3=hard).
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
            player, active_instance, ai_level, battle, instances, movements
        )
        if move_action:
            return move_action

        switch_action = await self.generate_switch_action(
            player, battle, instances
        )
        if switch_action:
            return switch_action

        raise ValueError("AI has no valid actions available")

    async def generate_move_action(  # noqa: PLR0913
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
            ai_level: AI difficulty level (1=easy, 2=medium, 3=hard).
            battle: The current battle state (needed for medium AI).
            instances: Dict of battle instances (needed for medium AI).
            movements: Dict of Movement entities keyed by ID.

        Returns:
            A TurnAction with type="move" or None if no moves available.
        """
        available_moves = [
            ms for ms in active_instance.move_state if ms.current_pp > 0
        ]

        if not available_moves:
            return None

        opponent_hp_percent = None
        if ai_level == AI_LEVEL_MEDIUM and battle and instances:
            opponent_hp_percent = self._get_opponent_hp_percent(player, battle, instances)

        move_id = self._select_move_by_level(available_moves, ai_level, movements, opponent_hp_percent)

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
        movements: dict | None = None,
        opponent_hp_percent: float | None = None,
    ) -> str | None:
        """Select a move based on AI difficulty level.

        Args:
            available_moves: List of MoveState with PP > 0.
            ai_level: AI difficulty level.
            movements: Dict of Movement entities keyed by ID.
            opponent_hp_percent: Opponent's HP as percentage (0.0 to 1.0).

        Returns:
            The move_id of the selected move or None if no moves available.
        """
        if not available_moves:
            return None

        if ai_level == AI_LEVEL_EASY:
            return self._select_random_move(available_moves)
        elif ai_level == AI_LEVEL_MEDIUM:
            return self._select_move_by_hp(available_moves, opponent_hp_percent, movements)
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
        opponent_hp_percent: float | None,
        movements: dict | None,
    ) -> str:
        """Select a move based on target HP (Level 2 - Medium).

        - If opponent HP > 50%: select highest power move (maximize damage)
        - If opponent HP <= 50%: select move with lowest max PP (conserve PP)

        Args:
            available_moves: List of MoveState with PP > 0.
            opponent_hp_percent: Opponent's HP as percentage (0.0 to 1.0).
            movements: Dict of Movement entities keyed by ID.

        Returns:
            The move_id of the selected move.
        """
        if not available_moves:
            return None

        if opponent_hp_percent is None or opponent_hp_percent > AI_HP_THRESHOLD:
            return self._select_highest_power_move(available_moves, movements)
        else:
            return self._select_lowest_pp_move(available_moves, movements)

    def _select_highest_power_move(self, available_moves: list, movements: dict | None) -> str:
        """Select the move with highest power value.

        Args:
            available_moves: List of MoveState with PP > 0.
            movements: Dict of Movement entities keyed by ID.

        Returns:
            The move_id with highest power.
        """
        def get_power(ms):
            if not movements:
                return 0
            move = movements.get(ms.move_id)
            return move.power if move and move.power else 0

        return max(available_moves, key=get_power).move_id

    def _select_lowest_pp_move(self, available_moves: list, movements: dict | None) -> str:
        """Select the move with lowest max PP (most uses remaining).

        Args:
            available_moves: List of MoveState with PP > 0.
            movements: Dict of Movement entities keyed by ID.

        Returns:
            The move_id with lowest max PP.
        """
        def get_pp(ms):
            if not movements:
                return 999
            move = movements.get(ms.move_id)
            return move.pp if move else 999

        return min(available_moves, key=get_pp).move_id

    def _get_opponent_hp_percent(
        self,
        player: Player,
        battle: Battle,
        instances: dict[str, BattleInstance],
    ) -> float | None:
        """Get the opponent's active Pokemon HP percentage.

        Args:
            player: The AI player.
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.

        Returns:
            HP as percentage (0.0 to 1.0) or None if not available.
        """
        for trainer_id, side in battle.sides.items():
            if trainer_id != player.trainer_id:
                active_id = side.active_pokemon_instance_ids[0]
                if active_id:
                    opponent = instances.get(active_id)
                    if opponent:
                        return opponent.current_hp / opponent.max_hp
        return None
