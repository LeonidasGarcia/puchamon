"""Action selection strategies for AI."""

import copy
import random
from abc import ABC, abstractmethod
from typing import Literal

from ...battle.domain.entities import Battle, BattleInstance
from .action_utils import get_available_actions, get_opponent_trainer_id
from .heuristics import evaluate_level_2, evaluate_level_3
from .minimax import minimax
from .state_simulator import simulate_action

Action = tuple[str, str]

AIDifficultyLevel = Literal[1, 2, 3]
AI_LEVEL_EASY = 1
AI_LEVEL_MEDIUM = 2
AI_LEVEL_HARD = 3

DEFAULT_MINIMAX_DEPTH = 3


class ActionSelector(ABC):
    """Abstract base class for action selection strategies."""

    @abstractmethod
    def select(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        trainer_id: str,
        movements: dict | None = None,
    ) -> Action | None:
        """Select an action (move or switch) from available options.

        Args:
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            trainer_id: The trainer ID of the AI player.
            movements: Dict of Movement entities keyed by ID.

        Returns:
            Action tuple (action_type, action_id) or None if no action available.
            action_type is "MOVE" or "SWITCH".
            action_id is move_id or instance_id respectively.
        """
        pass


class RandomActionSelector(ActionSelector):
    """Select action randomly (Level 1 - Easy)."""

    def select(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        trainer_id: str,
        movements: dict | None = None,
    ) -> Action | None:
        """Select a random action from available moves and switches."""
        actions = get_available_actions(battle, instances, trainer_id)
        if not actions:
            return None
        return random.choice(actions)


class MinimaxActionSelector(ActionSelector):
    """Select action using Minimax algorithm with Alpha-Beta pruning.

    This selector evaluates both attacks and switch actions in the same
    decision tree, enabling tactical switches that are not just reactive
    to fainted Pokemon.

    Args:
        ai_level: AI difficulty level (2 = MEDIUM, 3 = HARD).
        depth: Maximum search depth (default 3).
    """

    def __init__(
        self,
        ai_level: AIDifficultyLevel,
        depth: int = DEFAULT_MINIMAX_DEPTH,
    ):
        self.ai_level = ai_level
        self.depth = depth
        self.heuristic_func = evaluate_level_2 if ai_level == AI_LEVEL_MEDIUM else evaluate_level_3

    def select(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        trainer_id: str,
        movements: dict | None = None,
    ) -> Action | None:
        """Select the best action using Minimax with Alpha-Beta pruning."""
        opponent_trainer_id = get_opponent_trainer_id(battle, trainer_id)
        if opponent_trainer_id is None:
            return None

        actions = get_available_actions(battle, instances, trainer_id)
        if not actions:
            return None

        best_action = None
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for action in actions:
            state_copy = simulate_action(
                copy.deepcopy(battle),
                copy.deepcopy(instances),
                action,
                trainer_id,
                opponent_trainer_id,
                movements,
            )
            score = minimax(
                state_copy[0],
                state_copy[1],
                trainer_id,
                self.depth - 1,
                alpha,
                beta,
                False,
                self.heuristic_func,
                movements,
            )
            if score > best_score:
                best_score = score
                best_action = action
            alpha = max(alpha, score)

        return best_action
