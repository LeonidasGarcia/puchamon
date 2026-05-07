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
            ai_level: AI difficulty level (1=easy, 2=medium).
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

        move_id = self._select_move_by_level(
            available_moves, ai_level, battle, instances, movements
        )

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
        battle: Battle | None = None,
        instances: dict[str, BattleInstance] | None = None,
        movements: dict | None = None,
    ) -> str | None:
        """Select a move based on AI difficulty level.

        Args:
            available_moves: List of MoveState with PP > 0.
            ai_level: AI difficulty level.
            battle: The current battle state (needed for medium AI).
            instances: Dict of battle instances (needed for medium AI).
            movements: Dict of Movement entities keyed by ID.

        Returns:
            The move_id of the selected move or None if no moves available.
        """
        if not available_moves:
            return None

        if ai_level == AI_LEVEL_EASY:
            return self._select_random_move(available_moves)
        else:
            return self._greedy_hp(
                available_moves, battle, instances, movements
            )

    def _select_random_move(self, available_moves: list) -> str:
        """Select a random move (Level 1 - Easy).

        Args:
            available_moves: List of MoveState with PP > 0.

        Returns:
            A random move_id.
        """
        return random.choice(available_moves).move_id

    def _greedy_hp(
        self,
        available_moves: list,
        battle: Battle | None,
        instances: dict[str, BattleInstance] | None,
        movements: dict | None,
    ) -> str | None:
        """Select a move using greedy best-first with HP-based heuristic.

        =============================================================
        HEURÍSTICA: h(move) = 1 - HP_oponente_post_percent
        =============================================================

        El objetivo es minimizar el HP del oponente después del ataque.
        Esto se logra maximizando el daño inflicted.

        Formula detallada:
            HP_oponente_post = max(0, HP_oponente_actual - damage)
            HP_percent_post   = HP_oponente_post / HP_max_oponente
            h(move)           = 1 - HP_percent_post

        Equivalencia (para ordenamiento relativo):
            argmax(h(move)) = argmax(damage)
            Ya que h es monotonic con damage

        Algoritmo Best-First Greedy:
            1. Evaluar cada move disponible
            2. Seleccionar el move con mayor h(move)
            3. Retornar ese move

        Args:
            available_moves: List of MoveState with PP > 0.
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            movements: Dict of Movement entities keyed by ID.

        Returns:
            The move_id of the selected move.
        """
        if not available_moves:
            return None

        if not battle or not instances:
            return available_moves[0].move_id

        def get_h_score(ms) -> float:
            """Calcular score heurístico para un movimiento.

            Formula:
                h(move) = 1 - HP_oponente_post_percent

            Returns:
                Score heurístico (mayor = mejor movimiento)
            """
            move = movements.get(ms.move_id) if movements else None

            if not move or not move.power:
                return 0.0

            opponent_hp = self._get_opponent_hp_values(battle, instances)
            if not opponent_hp:
                return 0.0

            opponent_current, opponent_max = opponent_hp
            damage = move.power

            hp_post = opponent_current - damage
            hp_percent_post = max(0, hp_post) / opponent_max

            return 1.0 - hp_percent_post

        best_move_state = max(available_moves, key=get_h_score)
        return best_move_state.move_id

    def _get_opponent_hp_values(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
    ) -> tuple[int, int] | None:
        """Get the opponent's current and max HP.

        Busca el primer pokemon activo del rival (no el del jugador actual).

        Returns:
            Tuple of (current_hp, max_hp) or None if no opponent found.
        """
        for _trainer_id, side in battle.sides.items():
            active_id = side.active_pokemon_instance_ids[0]
            if active_id:
                opponent = instances.get(active_id)
                if opponent and not opponent.fainted:
                    return (opponent.current_hp, opponent.max_hp)
        return None
