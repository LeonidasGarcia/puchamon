"""Move selection strategies for AI."""

import random
from abc import ABC, abstractmethod

from ...battle.domain.entities import Battle, BattleInstance, MoveState
from .heuristics import calculate_hp_score, get_opponent_hp_values


class MoveSelector(ABC):
    """Abstract base class for move selection strategies."""

    @abstractmethod
    def select(self, available_moves: list[MoveState]) -> str | None:
        """Select a move from available moves.

        Args:
            available_moves: List of MoveState with PP > 0.

        Returns:
            The move_id selected or None if no move available.
        """
        pass


class RandomMoveSelector(MoveSelector):
    """Select a move randomly (Level 1 - Easy)."""

    def select(self, available_moves: list[MoveState]) -> str | None:
        """Select a random move.

        Args:
            available_moves: List of MoveState with PP > 0.

        Returns:
            A random move_id or None if no moves available.
        """
        return random.choice(available_moves).move_id if available_moves else None


class GreedyHPMoveSelector(MoveSelector):
    """Select move using greedy best-first with HP-based heuristic.

    Heuristic: h(move) = 1 - HP_oponente_post_percent
    Objective: Minimize opponent HP after attack (maximize damage).
    """

    def __init__(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        movements: dict | None = None,
    ):
        self.battle = battle
        self.instances = instances
        self.movements = movements

    def select(self, available_moves: list[MoveState]) -> str | None:
        """Select move with highest damage potential.

        Args:
            available_moves: List of MoveState with PP > 0.

        Returns:
            The move_id with best h-score or None if no moves available.
        """
        if not available_moves:
            return None

        if not self.battle or not self.instances:
            return available_moves[0].move_id

        opponent_hp = get_opponent_hp_values(self.battle, self.instances)
        if not opponent_hp:
            return available_moves[0].move_id

        opponent_current, opponent_max = opponent_hp

        def get_h_score(ms: MoveState) -> float:
            move = self.movements.get(ms.move_id) if self.movements else None
            if not move or not move.power:
                return 0.0
            return calculate_hp_score(move.power, opponent_current, opponent_max)

        best_move_state = max(available_moves, key=get_h_score)
        return best_move_state.move_id
